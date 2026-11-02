"""Reproduce every committed output in one go, in the right order.

    python scripts/run_all.py [--data data/raw/gaitpdb]

Runs, each as a separate process and stopping at the first failure:
verify_data, make_table1, make_figure1, check_event_detection,
check_data_quality, check_dual_task, make_figure2 and make_clean_strides (the
stride tables in data/interim/); make_features and check_features; the models
(run_logreg, run_random_forest, run_baselines), compare_models and
run_cross_cohort; check_weargait_participants and check_weargait_threshold
(which read data/raw/weargait_pd and skip themselves without its files); and
last the 20 N sensitivity analysis of D-012 (the cleaning, the features, their
checks and the cross-cohort test at a fixed 20 N, into results/fixed_20N/).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

READS_RECORDS = [  # these take --data: they read the PhysioNet record files
    "verify_data.py",
    "make_table1.py",
    "make_figure1.py",
    "check_event_detection.py",
    "check_data_quality.py",
    "check_dual_task.py",
    "make_figure2.py",
    "make_clean_strides.py",  # also reads data/raw/weargait_pd if present
]
READS_CLEAN_STRIDES = [  # read data/interim/ (make_clean_strides.py, T-017)
    "make_features.py",  # takes --data for gaitpdb's demographics.txt
    "check_features.py",
]
READS_RESULTS = [  # these read what the steps above wrote to results/
    "run_logreg.py",
    "run_random_forest.py",
    "run_baselines.py",
    "compare_models.py",
    "run_cross_cohort.py",  # needs both feature tables and the clean strides
]
READS_WEARGAIT = [  # read data/raw/weargait_pd; skip themselves without its files
    "check_weargait_participants.py",
    "check_weargait_threshold.py",
]
SENSITIVITY_20N = [  # D-012's sensitivity analysis at a fixed 20 N, in its own folders
    (
        "make_clean_strides.py",
        ["--fixed-threshold", "20", "--out", "data/interim/fixed_20N"]
        + ["--summary", "results/fixed_20N/clean_strides_summary.txt"],
    ),
    (
        "make_features.py",
        ["--interim", "data/interim/fixed_20N", "--out", "results/fixed_20N"],
    ),
    (
        "check_features.py",
        ["--interim", "data/interim/fixed_20N", "--results", "results/fixed_20N"]
        + ["--figures", "figures/fixed_20N"],
    ),
    (
        "run_cross_cohort.py",
        ["--interim", "data/interim/fixed_20N", "--results", "results/fixed_20N"]
        + ["--cross-cohort-only"],
    ),
]
STEPS = READS_RECORDS + READS_CLEAN_STRIDES + READS_RESULTS + READS_WEARGAIT
TAKE_DATA = {*READS_RECORDS, "make_features.py"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    runs = [(step, []) for step in STEPS] + SENSITIVITY_20N
    for step, extra in runs:
        cmd = [sys.executable, str(here / step)]
        if step in TAKE_DATA:
            cmd += ["--data", args.data]
        cmd += extra
        print(f"== {step} {' '.join(extra)}".rstrip(), flush=True)
        t0 = time.time()
        result = subprocess.run(cmd, cwd=here.parent)
        if result.returncode != 0:
            raise SystemExit(f"{step} failed with exit code {result.returncode}")
        print(f"   done in {time.time() - t0:.0f} s", flush=True)
    print("all outputs regenerated; git status shows what changed")


if __name__ == "__main__":
    main()
