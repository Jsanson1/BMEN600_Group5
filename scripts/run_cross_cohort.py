"""Cross-dataset analyses for every model (DECISIONS.md D-007, task T-022).

Reads the participant feature tables of scripts/make_features.py
(results/features_gaitpdb.csv and results/features_weargait.csv) and, for the
stride-matched reference, the clean strides of scripts/make_clean_strides.py
(data/interim/clean_strides_{gaitpdb,weargait}.csv). Every model whose script is
present joins through that script's ``make_factory``: the logistic regression
(scripts/run_logreg.py), the random forest (scripts/run_random_forest.py) and the
support vector machine (scripts/run_svm.py). Each model is run on these input
sets (``input_sets``): the gait features of gaitpdb.evaluation.MODEL_FEATURES
(the main model); the same with age and sex; the gait features without the two
variability measures; and the gait features with the robust variability in place
of the coefficients of variation.

Analyses (the Midterm Research Plan's Section IV and Table III, D-007, D-011):

1. pooled: both datasets combined in repeated participant-grouped
   cross-validation, stratified by diagnosis within dataset, with each
   dataset's AUC inside every test fold (gaitpdb.crosscohort.run_pooled); main
   model and gait + covariates only;
2. cross-cohort: fitted once on every gaitpdb participant and applied once to
   every WearGait-PD participant (gaitpdb.crosscohort.cross_cohort): AUC with a
   participant-bootstrap interval; sensitivity at 90% specificity read off
   WearGait-PD's ROC curve, and the sensitivity and specificity of the threshold
   carried over from gaitpdb's out-of-fold predictions; PPV and NPV of that
   threshold at 1% prevalence; every input set;
3. cross-cohort at VA Puget Sound only (sites WPD and WHC), the one WearGait-PD
   site that recruited both groups; at the two Johns Hopkins sites diagnosis and
   site coincide;
4. cross-cohort with age-matched WearGait-PD groups: each PD participant paired
   with the nearest unpaired control of the same sex within AGE_CALIPER years
   (WearGait-PD's controls are older than its patients; gaitpdb's are younger);
5. cross-cohort with every input standardised within its own dataset (each
   dataset's mean and SD, no labels; inputs the logistic regression takes as
   log(1 + x) are logged first): separates a shift in the level of the features
   between datasets from a loss of the ranking the model learned;
6. dataset of origin: can a model tell the datasets apart from the same inputs
   (gaitpdb.crosscohort.dataset_of_origin); main model only;
7. stride-matched reference: gaitpdb's within-protocol AUC (the shared splits of
   gaitpdb.evaluation) when the test participants' features are recomputed from
   as many clean strides per foot as a randomly drawn WearGait-PD participant
   has, taken as runs from as many stretches of the walk as WearGait-PD's median
   number of straight bouts per foot (gaitpdb.crosscohort.stride_matched_tables),
   with the models trained on full-length features as in the cross-cohort test;
   main model only. The drop from the full-length AUC is what stride count alone
   costs.

The analyses and input sets were fixed before any model was applied to
WearGait-PD's diagnosis labels. ``--shuffle-labels`` permutes WearGait-PD's
labels first and writes to crosscohort_shuffled_*: a check that the whole
pipeline returns chance-level results when there is nothing to find.

Writes results/crosscohort_summary.txt, results/crosscohort_results.csv (one row
per model, input set and analysis), results/crosscohort_pooled_folds.csv and
results/crosscohort_predictions.csv (every WearGait-PD prediction).

    python scripts/run_cross_cohort.py [--models logreg rf svm] [--shuffle-labels]
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb.crosscohort import (  # noqa: E402
    TARGET_SPECIFICITY,
    cross_cohort,
    dataset_of_origin,
    predictive_values,
    run_pooled,
    sensitivity_at_specificity,
    stride_matched_tables,
)
from gaitpdb.evaluation import (  # noqa: E402
    COVARIATES,
    LOG_TRANSFORMED,
    MODEL_FEATURES,
    N_REPEATS,
    N_SPLITS,
    SEED,
    bootstrap_auc,
    corrected_interval,
    load_feature_table,
    repeated_grouped_cv,
    summarise,
)
from gaitpdb.features import participant_features  # noqa: E402

MODEL_SCRIPTS = {
    "logreg": "run_logreg.py",
    "rf": "run_random_forest.py",
    "svm": "run_svm.py",
}
SCREENING_PREVALENCE = 0.01
"""The plan's screening prevalence (about 1% of people over 60 have PD)."""
VA_SITES = ("WPD", "WHC")
AGE_CALIPER = 3.0
N_STRIDE_DRAWS = 20
POOLED_SETS = ("gait", "gait + covariates")
REPEATS = N_REPEATS
"""Repeats of the pooled, dataset-of-origin and stride-matched cross-validation."""
MODEL_DIR = ROOT / "scripts"
"""Where the model scripts are looked for."""


def input_sets(features: list[str] = MODEL_FEATURES) -> dict[str, list[str]]:
    """The input sets every model is run on, derived from the main feature list."""
    return {
        "gait": list(features),
        "gait + covariates": list(features) + COVARIATES,
        "gait without variability": [c for c in features if not c.endswith("_cv_pct")],
        "gait, robust variability": [
            c.replace("_cv_pct", "_madcv_pct") for c in features
        ],
    }


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_tables(results: Path) -> pd.DataFrame:
    """Both feature tables, through the shared loader (age rule, sex_male, y)."""
    frames = []
    for ds in ("gaitpdb", "weargait"):
        t = load_feature_table(str(results / f"features_{ds}.csv"))
        if (t["dataset"] != ds).any():
            raise ValueError(f"features_{ds}.csv holds rows of another dataset")
        frames.append(t)
    return pd.concat(frames, ignore_index=True)


def standardise_within_dataset(
    df: pd.DataFrame, columns: list[str]
) -> tuple[pd.DataFrame, list[str]]:
    """Each column standardised with its own dataset's mean and SD (no labels).

    Columns the logistic regression takes as log(1 + x) are logged first, and the
    new columns get new names so no model step logs them again.
    """
    out = df.copy()
    names = []
    for c in columns:
        x = out[c].astype(float)
        if c in LOG_TRANSFORMED:
            x = np.log1p(x)
        name = f"{c}, standardised within dataset"
        out[name] = x.groupby(out["dataset"]).transform(
            lambda s: (s - s.mean()) / s.std(ddof=1)
        )
        names.append(name)
    return out, names


def age_matched(test: pd.DataFrame, caliper: float = AGE_CALIPER) -> list[str]:
    """Participants of 1:1 pairs: each PD participant, youngest first, with the
    nearest-aged unpaired control of the same sex within ``caliper`` years."""
    patients = test[test["y"] == 1].sort_values(["Age", "participant"])
    controls = test[test["y"] == 0].sort_values(["Age", "participant"])
    used: set[str] = set()
    keep = []
    for r in patients.itertuples(index=False):
        c = controls[(controls["sex"] == r.sex) & ~controls["participant"].isin(used)]
        if c.empty:
            continue
        gap = (c["Age"] - r.Age).abs()
        j = gap.idxmin()
        if gap[j] <= caliper:
            used.add(c.at[j, "participant"])
            keep += [r.participant, c.at[j, "participant"]]
    return keep


def operating_point(y: np.ndarray, p: np.ndarray, threshold: float) -> dict:
    """AUC with its interval, the ROC-read sensitivity at the target specificity,
    and what a fixed ``threshold`` gives, with its predictive values."""
    auc, lo, hi = bootstrap_auc(y, p, seed=SEED)
    sens_roc, spec_roc, _ = sensitivity_at_specificity(y, p, TARGET_SPECIFICITY)
    called = p >= threshold
    sens, spec = float(called[y == 1].mean()), float((~called[y == 0]).mean())
    ppv, npv = predictive_values(sens, spec, SCREENING_PREVALENCE)
    return {
        "n": int(len(y)),
        "n_pd": int(y.sum()),
        "auc": auc,
        "auc_low": lo,
        "auc_high": hi,
        "sensitivity_at_spec": sens_roc,
        "specificity_roc": spec_roc,
        "threshold": threshold,
        "sensitivity_transferred": sens,
        "specificity_transferred": spec,
        "ppv_at_prevalence": ppv,
        "npv_at_prevalence": npv,
    }


def cross_cohort_rows(factory, df, columns, model, inputs) -> tuple[list, pd.DataFrame]:
    """The cross-cohort test and its VA-only and age-matched subsets."""
    res = cross_cohort(factory, df, columns)
    pred = res["predictions"].merge(
        df.loc[df["dataset"] == "weargait", ["participant", "Age", "sex"]],
        on="participant",
    )
    y, p, t = pred["y"].to_numpy(), pred["p"].to_numpy(), res["threshold"]
    rows = [{"analysis": "cross-cohort", **operating_point(y, p, t)}]
    va = pred["study"].isin(VA_SITES).to_numpy()
    rows.append(
        {
            "analysis": "cross-cohort, VA Puget Sound only",
            **operating_point(y[va], p[va], t),
        }
    )
    matched = pred["participant"].isin(age_matched(pred)).to_numpy()
    rows.append(
        {
            "analysis": "cross-cohort, age-matched",
            **operating_point(y[matched], p[matched], t),
        }
    )
    for r in rows:
        r.update(model=model, inputs=inputs)
    return rows, pred.assign(model=model, inputs=inputs)


def bouts_per_foot(strides: pd.DataFrame) -> int:
    """WearGait-PD's median number of straight bouts per participant and foot
    (scripts/check_features.py defines a bout)."""
    check = load_script(ROOT / "scripts" / "check_features.py")
    b = check.bout_positions(strides, ["participant", "task", "foot"])
    n = (
        b.drop_duplicates(["participant", "task", "foot", "bout"])
        .groupby(["participant", "foot"])
        .size()
    )
    return int(round(n.median()))


def stride_matched_reference(
    factory,
    g: pd.DataFrame,
    strides: pd.DataFrame,
    counts: np.ndarray,
    runs: int,
    columns: list[str],
) -> dict:
    """Within-gaitpdb AUC on the shared splits, full-length test features against
    test features recomputed at WearGait-PD's stride counts (models trained on
    full-length features)."""
    use = strides[strides["clean"].astype(bool) & strides["included"].astype(bool)]
    order = g["participant"].to_numpy()
    draws = [
        participant_features(t)
        .set_index("participant")
        .loc[order, columns]
        .to_numpy(dtype=float)
        for t in stride_matched_tables(use, counts, N_STRIDE_DRAWS, SEED, runs)
    ]
    X, y = g[columns].to_numpy(dtype=float), g["y"].to_numpy()
    full, short = [], []
    for _, _, tr, te in repeated_grouped_cv(g, N_SPLITS, REPEATS, SEED):
        m = factory().fit(X[tr], y[tr])
        full.append(roc_auc_score(y[te], m.predict_proba(X[te])[:, 1]))
        short.append(
            [roc_auc_score(y[te], m.predict_proba(D[te])[:, 1]) for D in draws]
        )
    short = np.array(short)  # folds x draws
    per_draw = short.mean(axis=0)
    return {
        "auc_full": float(np.mean(full)),
        "auc_matched": float(per_draw.mean()),
        "auc_matched_low": float(np.percentile(per_draw, 2.5)),
        "auc_matched_high": float(np.percentile(per_draw, 97.5)),
        "drop": float(np.mean(full) - per_draw.mean()),
        "runs": runs,
        "n_draws": N_STRIDE_DRAWS,
    }


def interval(folds: pd.DataFrame, column: str) -> tuple[float, float, float]:
    v = folds[column].dropna()
    return corrected_interval(v, folds["n_train"].mean(), folds["n_test"].mean())


def row_text(r: pd.Series) -> str:
    """One line of the summary for a cross-cohort row."""
    return (
        f"AUC {r['auc']:.3f} ({r['auc_low']:.3f} to {r['auc_high']:.3f}), n = {r['n']:.0f} "
        f"({r['n_pd']:.0f} PD); sensitivity at {100 * TARGET_SPECIFICITY:.0f}% specificity "
        f"(its own ROC) {r['sensitivity_at_spec']:.2f}; gaitpdb's threshold carried over: "
        f"sensitivity {r['sensitivity_transferred']:.2f}, specificity "
        f"{r['specificity_transferred']:.2f}, PPV {r['ppv_at_prevalence']:.3f} and NPV "
        f"{r['npv_at_prevalence']:.4f} at {100 * SCREENING_PREVALENCE:g}% prevalence"
    )


def summary_lines(table: pd.DataFrame, header: list[str]) -> list[str]:
    lines = list(header)
    for model, m in table.groupby("model", sort=False):
        lines.append(f"[{model}]")
        for inputs, t in m.groupby("inputs", sort=False):
            lines.append(f"  {inputs}:")
            for r in t.itertuples(index=False):
                r = pd.Series(r._asdict())
                if r["analysis"].startswith("cross-cohort"):
                    lines.append(f"    {r['analysis']}: {row_text(r)}")
                elif r["analysis"] == "stride-matched reference":
                    lines.append(
                        f"    {r['analysis']} (within gaitpdb, shared splits): full-length "
                        f"test features AUC {r['auc_full']:.3f}; at WearGait-PD's stride counts "
                        f"{r['auc']:.3f} ({r['auc_low']:.3f} to {r['auc_high']:.3f} over "
                        f"{r['n_draws']:.0f} draws, {r['runs']:.0f} runs per foot); drop "
                        f"{r['drop']:.3f}"
                    )
                else:
                    lines.append(
                        f"    {r['analysis']}: AUC {r['auc']:.3f} ({r['auc_low']:.3f} to "
                        f"{r['auc_high']:.3f})"
                    )
        lines.append("")
    return lines


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--interim", default=str(ROOT / "data" / "interim"))
    ap.add_argument("--models", nargs="+", default=list(MODEL_SCRIPTS))
    ap.add_argument("--shuffle-labels", action="store_true")
    args = ap.parse_args()
    results, interim = Path(args.results), Path(args.interim)
    prefix = "crosscohort_shuffled" if args.shuffle_labels else "crosscohort"
    df = load_tables(results)
    if args.shuffle_labels:
        wg = (df["dataset"] == "weargait").to_numpy()
        rng = np.random.default_rng(SEED)
        df.loc[wg, "y"] = rng.permutation(df.loc[wg, "y"].to_numpy())
    strides = {
        ds: pd.read_csv(interim / f"clean_strides_{ds}.csv", low_memory=False)
        for ds in ("gaitpdb", "weargait")
    }
    wg_table = df[df["dataset"] == "weargait"]
    counts = wg_table[["n_strides_left", "n_strides_right"]].to_numpy(dtype=int)
    runs = bouts_per_foot(strides["weargait"])
    g = df[df["dataset"] == "gaitpdb"].reset_index(drop=True)
    header = [
        "Cross-dataset analyses (scripts/run_cross_cohort.py, gaitpdb.crosscohort)"
        + (
            " WITH WEARGAIT-PD LABELS SHUFFLED: a pipeline check, not a result"
            if args.shuffle_labels
            else ""
        ),
        f"Training dataset gaitpdb: {len(g)} participants ({int(g['y'].sum())} PD); test "
        f"dataset WearGait-PD: {len(wg_table)} participants ({int(wg_table['y'].sum())} PD).",
        f"Main inputs: {', '.join(MODEL_FEATURES)}.",
        "Intervals: cross-cohort, 95% participant bootstrap; pooled and dataset of origin, "
        f"the corrected interval over {N_SPLITS} folds x {REPEATS} repeats.",
        "",
    ]
    rows, preds, pooled_folds = [], [], []
    for name in args.models:
        path = MODEL_DIR / MODEL_SCRIPTS[name]
        if not path.exists():
            header.append(f"{name}: {path.name} not found, skipped")
            continue
        module = load_script(path)
        for inputs, cols in input_sets().items():
            factory = module.make_factory(cols)
            r, p = cross_cohort_rows(factory, df, cols, name, inputs)
            rows += r
            preds.append(p)
            if inputs in POOLED_SETS:
                folds, _ = run_pooled(factory, df, cols, n_repeats=REPEATS)
                pooled_folds.append(folds.assign(model=name, inputs=inputs))
                for col, label in (
                    ("auc", "pooled"),
                    ("auc_gaitpdb", "pooled, gaitpdb test participants"),
                    ("auc_weargait", "pooled, WearGait-PD test participants"),
                ):
                    mean, lo, hi = interval(folds, col)
                    rows.append(
                        dict(
                            model=name,
                            inputs=inputs,
                            analysis=label,
                            auc=mean,
                            auc_low=lo,
                            auc_high=hi,
                        )
                    )
            if inputs != "gait":
                continue
            sdf, scols = standardise_within_dataset(df, cols)
            r, p = cross_cohort_rows(
                module.make_factory(scols),
                sdf,
                scols,
                name,
                "gait, standardised within dataset",
            )
            rows += r
            preds.append(p)
            origin = summarise(
                dataset_of_origin(factory, df, cols, n_repeats=REPEATS)
            ).loc["auc"]
            rows.append(
                dict(
                    model=name,
                    inputs=inputs,
                    analysis="dataset of origin",
                    auc=origin["mean"],
                    auc_low=origin["ci_low"],
                    auc_high=origin["ci_high"],
                )
            )
            sm = stride_matched_reference(
                factory, g, strides["gaitpdb"], counts, runs, cols
            )
            rows.append(
                dict(
                    model=name,
                    inputs=inputs,
                    analysis="stride-matched reference",
                    auc=sm["auc_matched"],
                    auc_low=sm["auc_matched_low"],
                    auc_high=sm["auc_matched_high"],
                    auc_full=sm["auc_full"],
                    drop=sm["drop"],
                    runs=sm["runs"],
                    n_draws=sm["n_draws"],
                )
            )
    table = pd.DataFrame(rows)
    results.mkdir(parents=True, exist_ok=True)
    table.to_csv(results / f"{prefix}_results.csv", index=False)
    if pooled_folds:
        pd.concat(pooled_folds, ignore_index=True).to_csv(
            results / f"{prefix}_pooled_folds.csv", index=False
        )
    if preds:
        pd.concat(preds, ignore_index=True).to_csv(
            results / f"{prefix}_predictions.csv", index=False
        )
    text = "\n".join(summary_lines(table, header)) + "\n"
    (results / f"{prefix}_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
