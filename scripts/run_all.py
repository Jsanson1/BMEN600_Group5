"""Reproduce every committed output in one go, in the right order.

    python scripts/run_all.py [--data data/raw/gaitpdb]

Runs verify_data, make_table1, make_figure1, check_event_detection,
check_data_quality, check_dual_task, run_logreg and make_figure2 as separate
processes and stops at the first failure. About five minutes on a laptop.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

STEPS = [
    "verify_data.py",
    "make_table1.py",
    "make_figure1.py",
    "check_event_detection.py",
    "check_data_quality.py",
    "check_dual_task.py",
    "run_logreg.py",
    "make_figure2.py",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    for step in STEPS:
        cmd = [sys.executable, str(here / step)]
        if (
            step != "run_logreg.py"
        ):  # that one reads the feature table make_figure1 writes
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
