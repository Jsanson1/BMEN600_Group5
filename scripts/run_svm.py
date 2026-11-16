"""Support vector machine under the shared evaluation (model 2 of the project plan, T-020).

Two input sets, as for the random forest:

* gait only: the timing features in gaitpdb.evaluation.MODEL_FEATURES;
* gait + covariates: the same plus age and sex.

The model is gaitpdb.svm.make_svm: swing-time asymmetry as log(1 + x) (as in the
logistic regression), standardisation, then an SVM whose kernel (linear or RBF),
cost C and, for the RBF kernel, gamma (17 values each from 1e-4 to 1e4, the
Midterm Research Plan's range) are chosen inside each outer training set by the
log-loss of Platt-scaled inner 5-fold distances; its probabilities come from the
chosen setting's Platt curve. It is evaluated under repeated participant-grouped
cross-validation (5 folds x 20 repeats) and leave-one-study-out, on the splits
fixed in gaitpdb.evaluation, so its results line up fold by fold with every
other model's.

The summary reports the setting chosen in each leave-one-study-out fit, in each
fold of the first cross-validation repeat and on all participants, and the
permutation importance of each input: the drop in test-fold AUC when one input is
shuffled among the test participants (10 shuffles), averaged over the 5 folds of
the first repeat (an RBF SVM has no coefficients to read).

Reads the feature table through gaitpdb.evaluation.load_feature_table (by default
results/features_usual_walk.csv, the table the other models read), which keeps
the participants aged 50 or over (DECISIONS.md D-006), and writes
results/svm_summary.txt; results/svm_folds.csv, results/svm_cv_predictions.csv and
results/svm_loso_predictions.csv (scripts/compare_models.py reads all three); and
results/svm_importances.csv.

    python scripts/run_svm.py [--features results/features_usual_walk.csv]
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb.cohort import MIN_AGE_YEARS  # noqa: E402
from gaitpdb.evaluation import (  # noqa: E402
    COVARIATES,
    MODEL_FEATURES,
    N_REPEATS,
    N_SPLITS,
    SEED,
    bootstrap_auc,
    calibration_table,
    cv_predictions,
    evaluate_model,
    leave_one_study_out,
    load_feature_table,
    log_transform,
    repeated_grouped_cv,
    summarise,
    write_model_outputs,
)
from gaitpdb.svm import C_GRID, GAMMA_GRID, N_INNER, make_svm, param_grid  # noqa: E402

INPUT_SETS = {
    "gait only": MODEL_FEATURES,
    "gait + covariates": MODEL_FEATURES + COVARIATES,
}
N_SHUFFLES = 10


def make_factory(columns: list[str]):
    """Return a zero-argument factory for a fresh, unfitted SVM pipeline on these inputs."""

    def factory():
        return make_svm(log_transform(columns), random_state=SEED)

    return factory


def describe_setting(model) -> str:
    s = model.named_steps["svm"].best_params_
    text = f"{s['kernel']}, C {s['C']:.3g}"
    return text + (f", gamma {s['gamma']:.3g}" if s["kernel"] == "rbf" else "")


def importances_and_settings(df: pd.DataFrame, columns: list[str], factory):
    """Permutation importance (mean and SD of the test-fold AUC drop) over the folds
    of repeat 0, and the setting chosen in each of those folds."""
    X, y = df[columns].to_numpy(dtype=float), df["y"].to_numpy()
    drops, settings = [], []
    for _, _, tr, te in repeated_grouped_cv(df, N_SPLITS, 1, SEED):
        model = factory().fit(X[tr], y[tr])
        settings.append(describe_setting(model))
        r = permutation_importance(
            model,
            X[te],
            y[te],
            scoring="roc_auc",
            n_repeats=N_SHUFFLES,
            random_state=SEED,
        )
        drops.append(r.importances_mean)
    drops = np.array(drops)
    imp = pd.DataFrame(
        {
            "input": columns,
            "permutation_auc_drop": drops.mean(axis=0),
            "permutation_auc_drop_sd": drops.std(axis=0, ddof=1),
        }
    )
    return imp, settings


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
    start = time.time()
    df = load_feature_table(args.features)
    n_rbf = sum(s["kernel"] == "rbf" for s in param_grid())
    lines = [
        f"Support vector machine (kernel, C and gamma chosen inside each outer training "
        f"set by the log-loss of Platt-scaled inner {N_INNER}-fold distances; linear "
        f"kernel at {len(C_GRID)} values of C, RBF kernel at {n_rbf} pairs of C and gamma, "
        f"each from {min(C_GRID):g} to {max(C_GRID):g} ({len(GAMMA_GRID)} values of gamma); "
        "swing-time asymmetry as log(1 + x), inputs standardised; gaitpdb.svm) on "
        f"{len(df)} participants aged {MIN_AGE_YEARS} or over ({int(df['y'].sum())} PD, "
        f"{int((1 - df['y']).sum())} controls; DECISIONS.md D-006), one row each, from "
        f"{args.features}.",
        f"Inputs: {', '.join(MODEL_FEATURES)}; with covariates also {', '.join(COVARIATES)}.",
        f"Outer evaluation: {N_SPLITS}-fold participant-grouped cross-validation repeated "
        f"{N_REPEATS} times, and leave-one-study-out. Cross-validation: mean over the "
        f"{N_SPLITS * N_REPEATS} test folds, 95% interval corrected for the overlap between "
        "training sets (Nadeau and Bengio 2003), then in brackets the 2.5th to 97.5th "
        f"percentile of the {N_REPEATS} repeat means. Leave-one-study-out: 95% interval "
        "from a bootstrap over the held-out participants.",
        "",
    ]
    outputs, importances = [], []
    y = df["y"].to_numpy()
    for name, cols in INPUT_SETS.items():
        factory = make_factory(cols)
        result = evaluate_model(factory, df, cols, f"svm: {name}")
        outputs.append(result)
        s = summarise(result["folds"])
        lines.append(f"[{name}] repeated grouped CV:")
        for m in ("auc", "brier", "balanced_accuracy", "sensitivity", "specificity"):
            lines.append(
                f"    {m}: {s.loc[m, 'mean']:.3f} ({s.loc[m, 'ci_low']:.3f} to "
                f"{s.loc[m, 'ci_high']:.3f}) [repeats {s.loc[m, 'repeat_low']:.3f} to "
                f"{s.loc[m, 'repeat_high']:.3f}]"
            )
        if name == "gait only":
            oof = cv_predictions(factory, df, cols, N_SPLITS, SEED)
            lines.append(
                "[gait only] calibration of the out-of-fold probabilities (one CV repeat), "
                "quintiles of predicted probability: mean predicted vs observed PD fraction:"
            )
            for r in calibration_table(oof["y"], oof["p"]).itertuples():
                lines.append(
                    f"    n = {r.n}: predicted {r.mean_predicted:.2f}, observed {r.observed_pd:.2f}"
                )
        pred = result["loso_predictions"]
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
        X = df[cols].to_numpy(dtype=float)
        picked = [
            f"{study} held out: {describe_setting(factory().fit(X[tr], y[tr]))}"
            for study, tr, _ in leave_one_study_out(df)
        ]
        lines.append(f"    setting chosen by inner log-loss: {'; '.join(picked)}")

        imp, settings = importances_and_settings(df, cols, factory)
        full = factory().fit(X, y)
        imp.insert(0, "model", f"svm: {name}")
        importances.append(imp)
        lines.append(
            f"[{name}] setting chosen in the {N_SPLITS} folds of repeat 0: "
            f"{'; '.join(settings)}; on all participants: {describe_setting(full)}"
        )
        lines.append(
            f"[{name}] importance: test-fold AUC drop when the input is shuffled (mean "
            f"(SD) over the {N_SPLITS} folds of repeat 0, {N_SHUFFLES} shuffles each):"
        )
        for r in imp.sort_values("permutation_auc_drop", ascending=False).itertuples():
            lines.append(
                f"    {r.input}: AUC drop {r.permutation_auc_drop:.3f} "
                f"({r.permutation_auc_drop_sd:.3f})"
            )
        lines.append("")
    write_model_outputs(outputs, out, "svm")
    pd.concat(importances, ignore_index=True).to_csv(
        out / "svm_importances.csv", index=False
    )
    text = "\n".join(lines) + "\n"
    (out / "svm_summary.txt").write_text(text, encoding="utf-8")
    print(text)
    print(f"({time.time() - start:.0f} s)")


if __name__ == "__main__":
    main()
