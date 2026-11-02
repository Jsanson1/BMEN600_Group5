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

Reads results/features_gaitpdb.csv and results/features_weargait.csv; writes
results/weargait_signal_check.txt.

    python scripts/check_weargait_signal.py
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pandas as pd
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


def load_script(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def single_aucs(t: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    """AUC of each column alone for PD (y = 1) against controls."""
    return {c: float(roc_auc_score(t["y"], t[c])) for c in columns}


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
    text = "\n".join(lines)
    (results / "weargait_signal_check.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
