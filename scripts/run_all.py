"""Reproduce every committed output in one go, in the right order.

    python scripts/run_all.py [--data data/raw/gaitpdb]

Runs verify_data, make_table1, make_figure1, check_event_detection,
check_data_quality, check_dual_task and make_figure2; then make_features and
check_features, which read the clean-stride tables in data/interim/ and skip a
dataset whose table is missing; then the models (run_logreg,
run_random_forest, run_svm, run_baselines) and compare_models; and last
check_weargait_participants, which reads data/raw/weargait_pd and skips itself
if the WearGait-PD sheets are not there. Each runs as a separate process, and
the run stops at the first failure. About 30 minutes on a two-core machine,
25 of them the random forest.
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
]
READS_CLEAN_STRIDES = [  # read data/interim/ (make_clean_strides.py, T-017)
    "make_features.py",  # takes --data for gaitpdb's demographics.txt
    "check_features.py",
]
READS_RESULTS = [  # these read what the steps above wrote to results/
    "run_logreg.py",
    "run_random_forest.py",
    "run_svm.py",
    "run_baselines.py",
    "compare_models.py",
]
READS_WEARGAIT = [  # reads data/raw/weargait_pd; skips itself without the sheets
    "check_weargait_participants.py",
]
STEPS = READS_RECORDS + READS_CLEAN_STRIDES + READS_RESULTS + READS_WEARGAIT
TAKE_DATA = {*READS_RECORDS, "make_features.py"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    for step in STEPS:
        cmd = [sys.executable, str(here / step)]
        if step in TAKE_DATA:
            cmd += ["--data", args.data]
        print(f"== {step}", flush=True)
        t0 = time.time()
        result = subprocess.run(cmd, cwd=here.parent)
        if result.returncode != 0:
            raise SystemExit(f"{step} failed with exit code {result.returncode}")
        print(f"   done in {time.time() - t0:.0f} s", flush=True)
    print("all outputs regenerated; git status shows what changed")


if __name__ == "__main__":
    main()
