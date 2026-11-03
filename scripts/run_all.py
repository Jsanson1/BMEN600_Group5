"""Reproduce every committed output in one go, in the right order.

    python scripts/run_all.py [--data data/raw/gaitpdb]

Runs, each as a separate process and stopping at the first failure:
verify_data, make_table1, make_figure1, check_event_detection,
check_data_quality, check_dual_task and make_clean_strides (the stride tables in
data/interim/); make_features and check_features; make_figure2 (from the feature
tables), the models (run_logreg, run_random_forest, run_baselines),
compare_models, run_cross_cohort and the post hoc check_weargait_signal;
check_weargait_participants and check_weargait_threshold; and last the 20 N
sensitivity analysis of D-012 (the cleaning, the features, the logistic
regression within gaitpdb, the feature checks and the cross-cohort test at a
fixed 20 N, into results/fixed_20N/).

WearGait-PD needs a free Synapse account (data/raw/README.md). Without its two
participant sheets and its task files in data/raw/weargait_pd/, only the steps
that need PhysioNet alone run: the first six above, the cleaning and the
features of gaitpdb, make_figure2 (which reads the committed WearGait-PD feature
table), the models and compare_models. The two summaries that
describe both datasets (clean_strides_summary.txt and features_summary.txt) then
go to data/interim/physionet_only/ instead of results/, so every committed output
that needs WearGait-PD keeps its committed version.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb.weargait import SHEETS  # noqa: E402

WEARGAIT_DIR = ROOT / "data" / "raw" / "weargait_pd"
PHYSIONET_ONLY_DIR = "data/interim/physionet_only"  # git-ignored, like data/interim/

READS_RECORDS = [  # these take --data: they read the PhysioNet record files
    "verify_data.py",
    "make_table1.py",
    "make_figure1.py",
    "check_event_detection.py",
    "check_data_quality.py",
    "check_dual_task.py",
    "make_clean_strides.py",  # also reads data/raw/weargait_pd if present
]
READS_CLEAN_STRIDES = [  # read data/interim/ (make_clean_strides.py, T-017)
    "make_features.py",  # takes --data for gaitpdb's demographics.txt
    "check_features.py",
]
READS_RESULTS = [  # these read what the steps above wrote to results/
    "make_figure2.py",  # draws its counts from the two feature tables
    "run_logreg.py",
    "run_random_forest.py",
    "run_baselines.py",
    "compare_models.py",
    "run_cross_cohort.py",  # needs both feature tables and the clean strides
    "check_weargait_signal.py",  # post hoc, after the cross-cohort test
]
READS_WEARGAIT = [  # read data/raw/weargait_pd
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
        "run_logreg.py",
        ["--features", "results/fixed_20N/features_gaitpdb.csv"]
        + ["--out", "results/fixed_20N"],
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

# Without WearGait-PD's files: the steps that need it are skipped (with the whole
# 20 N analysis, a cross-cohort check), and the two steps whose summaries
# describe both datasets write those summaries outside results/.
NEEDS_WEARGAIT = {
    "check_features.py",
    "run_cross_cohort.py",
    "check_weargait_signal.py",
    *READS_WEARGAIT,
}
SUMMARY_ELSEWHERE = {
    "make_clean_strides.py": [
        "--summary",
        f"{PHYSIONET_ONLY_DIR}/clean_strides_summary.txt",
    ],
    "make_features.py": ["--summary", f"{PHYSIONET_ONLY_DIR}/features_summary.txt"],
}


def weargait_present(folder: Path = WEARGAIT_DIR) -> bool:
    """True when ``folder`` holds WearGait-PD's two participant sheets and at least
    one SelfPace task file, in the layout data/raw/README.md describes."""
    sheets = all((folder / name).exists() for name, _ in SHEETS.values())
    return sheets and any((folder / "csv").glob("*_SelfPace*.csv"))


def plan(with_weargait: bool) -> list[tuple[str, list[str]]]:
    """The steps to run, in order, each with its extra arguments."""
    if with_weargait:
        return [(step, []) for step in STEPS] + SENSITIVITY_20N
    return [
        (step, SUMMARY_ELSEWHERE.get(step, []))
        for step in STEPS
        if step not in NEEDS_WEARGAIT
    ]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data/raw/gaitpdb")
    args = ap.parse_args()
    with_weargait = weargait_present()
    if not with_weargait:
        skipped = [step for step in STEPS if step in NEEDS_WEARGAIT]
        print(
            f"WearGait-PD's files are not in {WEARGAIT_DIR.relative_to(ROOT)}/ (see "
            "data/raw/README.md), so only the steps that need PhysioNet alone run. "
            f"Skipped: {', '.join(skipped)} and the 20 N sensitivity analysis; "
            "their committed outputs are left as they are.",
            flush=True,
        )
    for step, extra in plan(with_weargait):
        cmd = [sys.executable, str(ROOT / "scripts" / step)]
        if step in TAKE_DATA:
            cmd += ["--data", args.data]
        cmd += extra
        print(f"== {step} {' '.join(extra)}".rstrip(), flush=True)
        t0 = time.time()
        result = subprocess.run(cmd, cwd=ROOT)
        if result.returncode != 0:
            raise SystemExit(f"{step} failed with exit code {result.returncode}")
        print(f"   done in {time.time() - t0:.0f} s", flush=True)
    done = "all outputs" if with_weargait else "the PhysioNet outputs"
    print(f"{done} regenerated; git status shows what changed")


if __name__ == "__main__":
    main()
