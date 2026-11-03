"""Post hoc: how much do the gait features separate the groups inside each dataset? (T-022)

Written after the pre-specified cross-cohort test (scripts/run_cross_cohort.py)
had been run, to help interpret it, so everything here is exploratory and is
reported as such. For each dataset, and for WearGait-PD's one site with both
groups (VA Puget Sound, sites WPD and WHC):

* each model input alone, and age: the AUC for PD against controls (above 0.5
  means higher in PD), and the median age of each group;
* a logistic regression trained and tested inside the dataset under the shared
  participant-grouped cross-validation (5 folds x 20 repeats), with the main
  inputs (gaitpdb.evaluation.MODEL_FEATURES) and the model of
  scripts/run_logreg.py: the mean test-fold AUC with its corrected interval.

Then two checks of the age-matched analysis, because WearGait-PD's controls are
older than its patients (the reverse of gaitpdb) and two of its three sites hold
one group each:

* the sites of the age-matched pairs (age_matched in scripts/run_cross_cohort.py,
  the same pairs as the cross-cohort test), patient's site first;
* from the cross-cohort test's predictions on WearGait-PD with the main inputs
  (results/crosscohort_predictions.csv), the Spearman correlation of each
  model's predicted probability of PD with age, within each group.

Reads results/features_gaitpdb.csv, results/features_weargait.csv and
results/crosscohort_predictions.csv; writes results/weargait_signal_check.txt.

    python scripts/check_weargait_signal.py
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb.evaluation import (  # noqa: E402
    MODEL_FEATURES,
    evaluate,
    load_feature_table,
    summarise,
)

VA_SITES = ("WPD", "WHC")
MAIN_INPUTS = "gait"
"""The input set of scripts/run_cross_cohort.py that uses MODEL_FEATURES."""


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def single_aucs(t: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    """AUC of each column alone for PD (y = 1) against controls."""
    return {c: float(roc_auc_score(t["y"], t[c])) for c in columns}


def same_site(a: str, b: str) -> bool:
    """Sites are the participant ID prefixes; WPD and WHC are both VA Puget Sound."""
    return a == b or {a, b} <= set(VA_SITES)


def pair_sites(t: pd.DataFrame, pairs: list[str]) -> pd.Series:
    """Number of age-matched pairs per "patient site-control site", from the flat
    [patient, control, patient, control, ...] list that age_matched returns;
    most frequent first, ties in alphabetical order."""
    site = t.set_index("participant")["study"]
    labels = [f"{site[a]}-{site[b]}" for a, b in zip(pairs[0::2], pairs[1::2])]
    counts = pd.Series(labels, dtype=str).value_counts().sort_index()
    return counts.sort_values(ascending=False, kind="stable")


def age_correlations(pred: pd.DataFrame) -> dict[int, tuple[float, float, int]]:
    """Spearman correlation of the predicted probability (p) with age within each
    group (y): {group: (rho, p value, n)}."""
    out = {}
    for g, q in pred.groupby("y"):
        r = spearmanr(q["Age"], q["p"])
        out[int(g)] = (float(r.statistic), float(r.pvalue), len(q))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default=str(ROOT / "results"))
    args = ap.parse_args()
    results = Path(args.results)
    logreg = load_script(ROOT / "scripts" / "run_logreg.py")
    tables = {
        ds: load_feature_table(str(results / f"features_{ds}.csv"))
        for ds in ("gaitpdb", "weargait")
    }
    w = tables["weargait"]
    tables["WearGait-PD, VA Puget Sound only"] = w[w["study"].isin(VA_SITES)]
    lines = [
        "Post hoc check, written after the pre-specified cross-cohort test: how much",
        "the inputs separate PD from controls inside each dataset (exploratory).",
        "",
    ]
    for name, t in tables.items():
        t = t.reset_index(drop=True)
        n_pd, n_c = int(t["y"].sum()), int((1 - t["y"]).sum())
        ages = t.groupby("y")["Age"].median()
        lines.append(
            f"{name}: {len(t)} participants ({n_pd} PD, {n_c} controls); median age "
            f"controls {ages[0]:g}, PD {ages[1]:g}"
        )
        lines.append("  AUC of each input alone (above 0.5: higher in PD):")
        for c, a in single_aucs(t, MODEL_FEATURES + ["Age"]).items():
            lines.append(f"    {c}: {a:.3f}")
        if name in ("gaitpdb", "weargait"):
            folds = evaluate(logreg.make_factory(MODEL_FEATURES), t, MODEL_FEATURES)
            s = summarise(folds).loc["auc"]
            lines.append(
                "  logistic regression trained and tested inside this dataset "
                f"(5 x 20 participant-grouped CV): AUC {s['mean']:.3f} "
                f"({s['ci_low']:.3f} to {s['ci_high']:.3f})"
            )
        lines.append("")

    cross = load_script(ROOT / "scripts" / "run_cross_cohort.py")
    w = w.reset_index(drop=True)
    pairs = cross.age_matched(w)
    counts = pair_sites(w, pairs)
    n_same = sum(int(n) for k, n in counts.items() if same_site(*k.split("-")))
    lines += [
        "Age-matched pairs of the cross-cohort test (same sex, age within "
        f"{cross.AGE_CALIPER:g} years): {len(pairs) // 2} pairs, by patient's and "
        "control's site: " + ", ".join(f"{k} {n}" for k, n in counts.items()),
        f"  {n_same} pairs within one site (VA Puget Sound is WPD and WHC; NLS and HC "
        "are the two Johns Hopkins sites)",
        "",
    ]
    pred_path = results / "crosscohort_predictions.csv"
    if pred_path.exists():
        pred = pd.read_csv(pred_path)
        lines.append(
            "Cross-cohort predictions on WearGait-PD (main inputs): Spearman "
            "correlation of the predicted probability of PD with age, within each group"
        )
        main_inputs = pred[pred["inputs"] == MAIN_INPUTS]
        for model, p in main_inputs.groupby("model", sort=True):
            r = age_correlations(p)
            lines.append(
                f"  {model}: controls {r[0][0]:.3f} (p = {r[0][1]:.2g}, n = {r[0][2]}); "
                f"PD {r[1][0]:.3f} (p = {r[1][1]:.2g}, n = {r[1][2]})"
            )
        lines.append("")
    text = "\n".join(lines)
    (results / "weargait_signal_check.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
