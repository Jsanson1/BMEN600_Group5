"""Build the derived stride tables: every stride of both datasets, marked clean or not.

Reads the raw data and writes only to data/interim/ (ignored by git; rebuilt by
scripts/run_all.py, never edited by hand). The cleaning is gaitpdb.clean_data:
timing-based turns for gaitpdb (DECISIONS.md D-008), the video labels for
WearGait-PD with its three straight-walking tasks pooled, and the minimum number
of clean strides per foot (D-011). Analysed participants only (aged 50 or over,
D-006). Contact threshold: 5% of each recording's force level (D-012), or a
fixed threshold with --fixed-threshold, for the 20 N sensitivity analysis, whose
tables go to their own folder:

    python scripts/make_clean_strides.py [--data data/raw/gaitpdb]
    python scripts/make_clean_strides.py --fixed-threshold 20 \
        --out data/interim/fixed_20N --summary results/fixed_20N/clean_strides_summary.txt

Writes, in data/interim/:
  clean_strides_gaitpdb.csv     one row per stride of each analysed usual walk
  clean_strides_weargait.csv    one row per stride of each analysed participant's
                                SelfPace, SelfPace_mat and SelfPace_matTURN
  clean_strides_turns_gaitpdb.csv  the turns found in each gaitpdb walk
  clean_strides_provenance.json the code version and every cleaning parameter
and the summary results/clean_strides_summary.txt (committed: participants
included and strides removed, by reason). Without the WearGait-PD files, the
WearGait-PD part is skipped with a note.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb import clean_data as cd  # noqa: E402
from gaitpdb import (  # noqa: E402
    cohort_manifest,
    find_data_dir,
    load_demographics,
    load_record,
    meets_age_rule,
)
from gaitpdb.weargait import load_participants  # noqa: E402

OUT_DIR = ROOT / "data" / "interim"
SUMMARY = ROOT / "results" / "clean_strides_summary.txt"
WG_DIR = ROOT / "data" / "raw" / "weargait_pd"
WG_TASKS = ["SelfPace", "SelfPace_mat", "SelfPace_matTURN"]
WG_COLUMNS = ["GeneralEvent", "LTotalForce", "RTotalForce"]

FIXED_THRESHOLD_N: float | None = None  # set from --fixed-threshold in main()

lines: list[str] = []


def say(text: str = "") -> None:
    print(text)
    lines.append(text)


def gaitpdb_strides(
    data: Path, threshold_n: float | None = None
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    walks = cohort_manifest(data)
    walks = walks[walks["walk"] == 1]
    speed = load_demographics(data).set_index("ID")["Speed_01"]
    tables, turns, skipped = [], [], []
    for w in walks.sort_values("record").itertuples(index=False):
        v = speed.get(w.participant)
        if not (pd.notna(v) and v > 0):
            skipped.append(
                f"{w.participant} ({w.group}): no Speed_01, turns cannot be located"
            )
            continue
        strides, info = cd.clean_gaitpdb(
            load_record(Path(w.path)), w.study, float(v), threshold_n
        )
        strides.insert(0, "group", w.group)
        strides.insert(0, "study", w.study)
        strides.insert(0, "record", w.record)
        strides.insert(0, "participant", w.participant)
        strides["included"] = cd.meets_minimum(strides, "gaitpdb")
        tables.append(strides)
        turns.append(
            dict(
                participant=w.participant,
                record=w.record,
                expected_interval_s=round(info["expected_interval_s"], 3),
                interval_s=round(info["interval_s"], 3),
                used_rhythm=info["used_rhythm"],
                turn_centres_s=" ".join(f"{c:.2f}" for c in info["turn_centres_s"]),
            )
        )
    return pd.concat(tables, ignore_index=True), pd.DataFrame(turns), skipped


def weargait_strides(
    threshold_n: float | None = None,
) -> tuple[pd.DataFrame | None, list[str]]:
    try:
        people = load_participants(WG_DIR)
    except FileNotFoundError as err:
        return None, [f"WearGait-PD skipped: {err}"]
    people = people[meets_age_rule(people["age"])]
    tables, skipped = [], []
    for p in people.sort_values("participant").itertuples(index=False):
        parts = []
        for task in WG_TASKS:
            path = WG_DIR / "csv" / f"{p.participant}_{task}.csv"
            if not path.exists():
                continue
            if not set(WG_COLUMNS) <= set(pd.read_csv(path, nrows=0).columns):
                continue
            df = pd.read_csv(path, usecols=WG_COLUMNS, low_memory=False)
            parts.append(cd.clean_weargait(df, threshold_n).assign(task=task))
        if not parts:
            skipped.append(f"{p.participant} ({p.group}): no insole data in any task")
            continue
        strides = pd.concat(parts, ignore_index=True)
        strides.insert(0, "group", p.group)
        strides.insert(0, "site", p.site)
        strides.insert(0, "participant", p.participant)
        strides["included"] = cd.meets_minimum(strides, "weargait")
        tables.append(strides)
    if not tables:
        return None, skipped + ["WearGait-PD skipped: no SelfPace task files found"]
    return pd.concat(tables, ignore_index=True), skipped


def summarise(
    name: str, d: pd.DataFrame, minimum: int, skipped: list[str], recording: list[str]
) -> None:
    people = d.groupby("participant").agg(
        group=("group", "first"), included=("included", "first")
    )
    say(f"{name}: minimum {minimum} clean strides per foot (D-011)")
    t = d.drop_duplicates(recording)["threshold_n"]
    say(
        f"  contact threshold per recording: median {t.median():.1f} N "
        f"(range {t.min():.1f} to {t.max():.1f} N, {len(t)} recordings)"
    )
    for group, g in people.groupby("group"):
        say(f"  {group}: {int(g['included'].sum())} of {len(g)} participants included")
    for x in skipped:
        say(f"  not processed: {x}")
    excluded = people[~people["included"]].index.tolist()
    if excluded:
        say(
            f"  excluded (fewer than {minimum} on a foot): {', '.join(sorted(excluded))}"
        )
    reasons = d["reason"].replace("", "kept (clean)")
    t = pd.crosstab(reasons, d["group"], margins=True, margins_name="all")
    pct = (100 * t / t.loc[t.index != "all"].sum()).round(1)
    say("  strides by outcome (count, % of all strides in the group):")
    for r in [*cd.REASONS, "kept (clean)"]:
        if r in t.index:
            cells = ", ".join(
                f"{c} {int(t.loc[r, c])} ({pct.loc[r, c]}%)" for c in t.columns
            )
            say(f"    {r}: {cells}")
    say()


def provenance() -> dict:
    def git(*args: str) -> str:
        try:
            return subprocess.run(
                ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
            ).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return "unknown"

    params = {
        k: getattr(cd, k)
        for k in dir(cd)
        if k.isupper() and isinstance(getattr(cd, k), (int, float, tuple, dict, str))
    }
    return dict(
        script="scripts/make_clean_strides.py",
        module="src/gaitpdb/clean_data.py",
        commit=git("rev-parse", "HEAD"),
        uncommitted_changes=bool(git("status", "--porcelain", "--", "src", "scripts")),
        decisions=["D-006", "D-008", "D-009", "D-011", "D-012"],
        contact_threshold=(
            f"fixed {FIXED_THRESHOLD_N:g} N (sensitivity analysis)"
            if FIXED_THRESHOLD_N is not None
            else "D-012: 5% of each recording's force level"
        ),
        parameters={
            k: list(v) if isinstance(v, tuple) else v for k, v in params.items()
        },
    )


def main() -> None:
    global FIXED_THRESHOLD_N
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(ROOT / "data" / "raw" / "gaitpdb"))
    ap.add_argument("--fixed-threshold", type=float, default=None)
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--summary", default=str(SUMMARY))
    args = ap.parse_args()
    data = find_data_dir(args.data)
    out, summary = Path(args.out), Path(args.summary)
    FIXED_THRESHOLD_N = args.fixed_threshold
    out.mkdir(parents=True, exist_ok=True)
    summary.parent.mkdir(parents=True, exist_ok=True)

    say("Clean strides (scripts/make_clean_strides.py, cleaning in gaitpdb.clean_data)")
    say("Derived tables in data/interim/ (not committed); analysed participants only.")
    if FIXED_THRESHOLD_N is None:
        say(
            "Contact threshold: 5% of each recording's force level (DECISIONS.md D-012)."
        )
    else:
        say(f"Contact threshold: fixed {FIXED_THRESHOLD_N:g} N (sensitivity analysis).")
    say()
    g, turns, g_skipped = gaitpdb_strides(data, FIXED_THRESHOLD_N)
    g.to_csv(out / "clean_strides_gaitpdb.csv", index=False)
    turns.to_csv(out / "clean_strides_turns_gaitpdb.csv", index=False)
    summarise(
        "gaitpdb, usual walk", g, cd.MIN_STRIDES["gaitpdb"], g_skipped, ["record"]
    )

    w, w_skipped = weargait_strides(FIXED_THRESHOLD_N)
    if w is None:
        for x in w_skipped:
            say(x)
    else:
        w.to_csv(out / "clean_strides_weargait.csv", index=False)
        summarise(
            "WearGait-PD, three straight-walking tasks pooled",
            w,
            cd.MIN_STRIDES["weargait"],
            w_skipped,
            ["participant", "task"],
        )
    (out / "clean_strides_provenance.json").write_text(
        json.dumps(provenance(), indent=2) + "\n", encoding="utf-8"
    )
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
