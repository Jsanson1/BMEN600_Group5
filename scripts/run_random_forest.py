"""Random forest under the shared evaluation (model 1 of the project plan, T-019).

Two input sets, as for the logistic regression's main comparison:

* gait only: the timing features in gaitpdb.evaluation.MODEL_FEATURES;
* gait + covariates: the same plus age and sex.

(The covariates-only baseline is the logistic regression's; a forest on two
inputs, one of them binary, adds nothing to it.)

The model is gaitpdb.forest.OOBTunedForest: 300 trees, with the depth of the
trees and the number of inputs tried at each split chosen inside each outer
training set by out-of-bag log-loss. It is evaluated under repeated
participant-grouped cross-validation (5 folds x 20 repeats) and
leave-one-study-out, on the splits fixed in gaitpdb.evaluation, so its results
line up fold by fold with every other model's.

Feature importance is reported two ways for each input set:

* permutation importance: the drop in test-fold AUC when one input is shuffled
  among the test participants (10 shuffles), averaged over the 5 folds of the
  first cross-validation repeat; only test participants are shuffled, so it
  measures what the model uses on people it has not seen;
* impurity importance of the forest fitted on all participants (the mean
  decrease in Gini impurity, scikit-learn's ``feature_importances_``), which is
  widely reported but favours inputs with many distinct values.

A check of the number of trees: the forest fitted on all participants at its
chosen setting is regrown with 1000 trees, and the two out-of-bag log-losses and
AUCs are compared.

Reads the feature table through gaitpdb.evaluation.load_feature_table (by default
results/features_usual_walk.csv, the table the logistic regression reads, so the
two models are compared on the same inputs), which keeps the participants aged
50 or over (DECISIONS.md D-006), and writes results/rf_summary.txt;
results/rf_folds.csv, results/rf_cv_predictions.csv and
results/rf_loso_predictions.csv (scripts/compare_models.py reads all three); and
results/rf_importances.csv.

    python scripts/run_random_forest.py [--features results/features_usual_walk.csv]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import log_loss, roc_auc_score

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
    repeated_grouped_cv,
    summarise,
    write_model_outputs,
)
from gaitpdb.forest import MAX_DEPTHS, N_TREES, OOBTunedForest  # noqa: E402

INPUT_SETS = {
    "gait only": MODEL_FEATURES,
    "gait + covariates": MODEL_FEATURES + COVARIATES,
}
N_SHUFFLES = 10
CHECK_TREES = 1000


def make_factory(columns: list[str], n_jobs: int | None = -1):
    """Return a zero-argument factory for a fresh, unfitted forest on these inputs
    (``columns`` only fixes the number of inputs, which sets the grid)."""

    def factory():
        return OOBTunedForest(random_state=SEED, n_jobs=n_jobs)

    return factory


def describe_setting(params: dict) -> str:
    depth = "full" if params["max_depth"] is None else params["max_depth"]
    return f"depth {depth}, {params['max_features']} per split"


def permutation_importances(
    df: pd.DataFrame, columns: list[str], factory
) -> pd.DataFrame:
    """Mean and SD of the test-fold AUC drop per input over the folds of repeat 0."""
    X, y = df[columns].to_numpy(dtype=float), df["y"].to_numpy()
    drops = []
    for _, _, tr, te in repeated_grouped_cv(df, N_SPLITS, 1, SEED):
        model = factory().fit(X[tr], y[tr])
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
    return pd.DataFrame(
        {
            "input": columns,
            "permutation_auc_drop": drops.mean(axis=0),
            "permutation_auc_drop_sd": drops.std(axis=0, ddof=1),
        }
    )


def tree_count_check(model: OOBTunedForest, X: np.ndarray, y: np.ndarray) -> dict:
    """OOB log-loss and AUC of the chosen setting with N_TREES and CHECK_TREES trees."""
    out = {}
    for n in (N_TREES, CHECK_TREES):
        f = RandomForestClassifier(
            n_estimators=n,
            oob_score=True,
            random_state=SEED,
            n_jobs=-1,
            **model.best_params_,
        ).fit(X, y)
        p = f.oob_decision_function_[:, 1]
        out[n] = (log_loss(y, np.clip(p, 1e-6, 1 - 1e-6)), roc_auc_score(y, p))
    return out


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
    depths = ", ".join("full" if d is None else str(d) for d in MAX_DEPTHS)
    lines = [
        f"Random forest ({N_TREES} trees; depth ({depths}) and inputs per split (1, "
        "the square root of the number of inputs, all) chosen inside each outer "
        "training set by out-of-bag log-loss; gaitpdb.forest) on "
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
        result = evaluate_model(factory, df, cols, f"rf: {name}")
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
        picked = []
        for study, tr, _ in leave_one_study_out(df):
            fitted = factory().fit(X[tr], y[tr])
            picked.append(f"{study} held out: {describe_setting(fitted.best_params_)}")
        lines.append(f"    setting chosen by out-of-bag log-loss: {'; '.join(picked)}")

        full = factory().fit(X, y)
        imp = permutation_importances(df, cols, factory)
        imp["impurity_importance"] = full.feature_importances_
        imp.insert(0, "model", f"rf: {name}")
        importances.append(imp)
        lines.append(
            f"[{name}] importance: test-fold AUC drop when the input is shuffled (mean "
            f"(SD) over the {N_SPLITS} folds of repeat 0, {N_SHUFFLES} shuffles each); "
            f"impurity importance of the forest fitted on all participants "
            f"({describe_setting(full.best_params_)}):"
        )
        for r in imp.sort_values("permutation_auc_drop", ascending=False).itertuples():
            lines.append(
                f"    {r.input}: AUC drop {r.permutation_auc_drop:.3f} "
                f"({r.permutation_auc_drop_sd:.3f}); impurity {r.impurity_importance:.3f}"
            )
        check = tree_count_check(full, X, y)
        lines.append(
            "    number of trees, out-of-bag log-loss and AUC on all participants at that "
            f"setting: {N_TREES} trees {check[N_TREES][0]:.3f} and {check[N_TREES][1]:.3f}; "
            f"{CHECK_TREES} trees {check[CHECK_TREES][0]:.3f} and {check[CHECK_TREES][1]:.3f}"
        )
        lines.append("")
    write_model_outputs(outputs, out, "rf")
    pd.concat(importances, ignore_index=True).to_csv(
        out / "rf_importances.csv", index=False
    )
    text = "\n".join(lines) + "\n"
    (out / "rf_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
