"""Logistic regression under the shared evaluation (model 3 of the project plan).

Three input sets are run so the value of the gait features is visible:

* covariates only (age, sex): what the group imbalance alone predicts;
* gait only: the six timing features in gaitpdb.evaluation.MODEL_FEATURES;
* gait + covariates: the model the plan calls for.

Each is a Pipeline of standardisation and an L2-penalised logistic regression
whose penalty strength is chosen by an inner participant-grouped
cross-validation on the training participants of each outer fold. Evaluated
under repeated participant-grouped cross-validation (5 folds x 20 repeats) and
leave-one-study-out.

Reads results/features_usual_walk.csv (made by scripts/make_figure1.py) and
writes results/logreg_folds.csv (every fold), results/logreg_summary.txt,
results/logreg_coefficients.csv (odds ratios per SD with bootstrap intervals,
model fitted on all participants) and results/logreg_loso_predictions.csv.

    python scripts/run_logreg.py [--features results/features_usual_walk.csv]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb.evaluation import (  # noqa: E402
    COVARIATES,
    MODEL_FEATURES,
    bootstrap_auc,
    calibration_table,
    cv_predictions,
    evaluate,
    load_feature_table,
    loso_predictions,
    summarise,
)

C_GRID = np.logspace(-3, 2, 11)
INPUT_SETS = {
    "covariates only": COVARIATES,
    "gait only": MODEL_FEATURES,
    "gait + covariates": MODEL_FEATURES + COVARIATES,
}
N_SPLITS, N_REPEATS, SEED = 5, 20, 0


def factory():
    """Fresh, unfitted model: standardise, then logistic regression with C tuned inside."""
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "logreg",
                LogisticRegressionCV(
                    Cs=C_GRID,
                    cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED),
                    penalty="l2",
                    scoring="roc_auc",
                    max_iter=5000,
                ),
            ),
        ]
    )


def variance_inflation(X: np.ndarray) -> np.ndarray:
    """VIF of each column: 1 / (1 - R^2 of that column regressed on the others)."""
    Xc = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)
    vifs = []
    for j in range(Xc.shape[1]):
        others = np.delete(Xc, j, axis=1)
        beta, *_ = np.linalg.lstsq(others, Xc[:, j], rcond=None)
        resid = Xc[:, j] - others @ beta
        r2 = 1 - resid.var() / Xc[:, j].var()
        vifs.append(1.0 / max(1 - r2, 1e-12))
    return np.array(vifs)


def odds_ratios(
    df: pd.DataFrame, columns: list[str], n_boot: int = 1000, seed: int = 0
):
    """Fit on all participants at the C chosen by inner CV; bootstrap the coefficients."""
    X = df[columns].to_numpy(dtype=float)
    y = df["y"].to_numpy()
    full = factory().fit(X, y)
    C = float(full.named_steps["logreg"].C_[0])
    coef = full.named_steps["logreg"].coef_[0]
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        if y[idx].min() == y[idx].max():
            continue
        m = Pipeline(
            [
                ("scale", StandardScaler()),
                ("logreg", LogisticRegression(C=C, penalty="l2", max_iter=5000)),
            ]
        ).fit(X[idx], y[idx])
        boots.append(m.named_steps["logreg"].coef_[0])
    boots = np.array(boots)
    out = pd.DataFrame(
        {
            "input": columns,
            "odds_ratio_per_sd": np.exp(coef),
            "ci_low": np.exp(np.percentile(boots, 2.5, axis=0)),
            "ci_high": np.exp(np.percentile(boots, 97.5, axis=0)),
            "vif": variance_inflation(X),
        }
    )
    return out, C


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="results/features_usual_walk.csv")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not Path(args.features).exists():
        raise SystemExit(
            f"{args.features} not found: run scripts/make_figure1.py first"
        )
    df = load_feature_table(args.features)

    lines = [
        f"Logistic regression (L2, C tuned by inner cross-validation over {len(C_GRID)} values) on "
        f"{len(df)} participants ({int(df['y'].sum())} PD, {int((1 - df['y']).sum())} controls), "
        "one usual-walk recording each.",
        f"Outer evaluation: {N_SPLITS}-fold participant-grouped cross-validation repeated "
        f"{N_REPEATS} times (interval = 2.5th to 97.5th percentile over repeats), and "
        "leave-one-study-out (interval = bootstrap over the held-out participants).",
        "",
    ]
    all_folds = []
    for name, cols in INPUT_SETS.items():
        folds = evaluate(factory, df, cols, "cv", N_SPLITS, N_REPEATS, SEED)
        folds.insert(0, "model", f"logreg: {name}")
        all_folds.append(folds)
        s = summarise(folds)
        lines.append(f"[{name}] repeated grouped CV:")
        for m in ("auc", "brier", "balanced_accuracy", "sensitivity", "specificity"):
            lines.append(
                f"    {m}: {s.loc[m, 'mean']:.3f} ({s.loc[m, 'ci_low']:.3f} to {s.loc[m, 'ci_high']:.3f})"
            )
        if name == "gait only":
            oof = cv_predictions(factory, df, cols, N_SPLITS, SEED)
            cal = calibration_table(oof["y"], oof["p"])
            lines.append(
                "[gait only] calibration of the out-of-fold probabilities (one CV repeat), "
                "quintiles of predicted probability: mean predicted vs observed PD fraction:"
            )
            for r in cal.itertuples():
                lines.append(
                    f"    n = {r.n}: predicted {r.mean_predicted:.2f}, observed {r.observed_pd:.2f}"
                )
        pred = loso_predictions(factory, df, cols)
        if name == "gait + covariates":
            pred.to_csv(out / "logreg_loso_predictions.csv", index=False)
        lines.append(f"[{name}] leave-one-study-out AUC (train on the other two):")
        for study in ("Ga", "Ju", "Si"):
            sub = pred[pred["study"] == study]
            point, lo, hi = bootstrap_auc(sub["y"], sub["p"], seed=SEED)
            lines.append(
                f"    held-out {study}: {point:.3f} ({lo:.3f} to {hi:.3f}), "
                f"n = {len(sub)} ({int(sub['y'].sum())} PD)"
            )
        point, lo, hi = bootstrap_auc(pred["y"], pred["p"], seed=SEED)
        lines.append(
            f"    all out-of-study predictions pooled: {point:.3f} ({lo:.3f} to {hi:.3f})"
        )
        lines.append("")
    pd.concat(all_folds).to_csv(out / "logreg_folds.csv", index=False)

    coefs, C = odds_ratios(df, MODEL_FEATURES + COVARIATES)
    coefs.to_csv(out / "logreg_coefficients.csv", index=False)
    lines.append(
        f"Gait + covariates model fitted on all participants (C = {C:g}): odds ratio of PD per "
        "1 SD increase, with a 95% participant-bootstrap interval, and the variance inflation "
        "factor of each input (collinearity check; above 5 is a concern):"
    )
    for r in coefs.itertuples():
        lines.append(
            f"    {r.input}: OR {r.odds_ratio_per_sd:.2f} ({r.ci_low:.2f} to {r.ci_high:.2f}), VIF {r.vif:.1f}"
        )
    text = "\n".join(lines) + "\n"
    (out / "logreg_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
