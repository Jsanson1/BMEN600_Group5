"""Reproduce every committed output in one go, in the right order.

    python scripts/run_all.py [--data data/raw/gaitpdb]

Runs verify_data, make_table1, make_figure1, check_event_detection,
check_data_quality, check_dual_task, make_figure2, then the models
(run_logreg, run_baselines) and compare_models, as separate processes, and
stops at the first failure. About five minutes on a laptop.
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
READS_RESULTS = [  # these read what the steps above wrote to results/
    "run_logreg.py",
    "run_baselines.py",
    "compare_models.py",
]
STEPS = READS_RECORDS + READS_RESULTS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    for step in STEPS:
        cmd = [sys.executable, str(here / step)]
        if step in READS_RECORDS:
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
