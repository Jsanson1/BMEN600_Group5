"""Check the insole contact threshold against the WearGait-PD walkway (task T-025).

The Midterm Research Plan (Section IV) carries gaitpdb's 20 N contact threshold
over to WearGait-PD's insoles only after checking it against the walkway's own
foot contacts, and uses for both datasets the threshold that agrees best with
the walkway, chosen on that agreement and never on classification results.

For every participant aged 50 or over (DECISIONS.md D-006) and each of the
three straight-walking tasks pooled under D-011 (SelfPace, SelfPace_mat,
SelfPace_matTURN), the insole contacts found at each candidate threshold are
matched to the walkway's complete footfalls (gaitpdb.walkway): fixed 10, 20 and
50 N, 2.5% and 5% of the recording's force level and, when the participant's
weight is known, 2.5% and 5% of body weight (the same kinds as
scripts/check_event_detection.py for gaitpdb). For each threshold the script
reports, overall, by group and by site, the share of walkway footfalls the
insole matches one to one and the bias, median absolute difference and
Bland-Altman limits of stance, stride and swing times (insole minus walkway),
and it lists the participants whose insoles match worst at 20 N. The threshold
recommended is the one with the highest one-to-one share overall, ties broken by
the smaller median absolute stance difference.

Reads data/raw/weargait_pd/ (the two participant sheets and csv/<ID>_<task>.csv;
see data/raw/README.md) and writes results/weargait_threshold_check.txt and
.csv (one row per threshold and subgroup) and
results/weargait_threshold_participants.csv (one row per participant and
threshold).

    python scripts/check_weargait_threshold.py [--data data/raw/weargait_pd]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb.cohort import MIN_AGE_YEARS, meets_age_rule  # noqa: E402
from gaitpdb.walkway import (  # noqa: E402
    CONTACT_COLUMNS,
    FORCE_COLUMNS,
    agreement,
    compare_task,
    threshold_candidates,
)
from gaitpdb.weargait import load_participants  # noqa: E402

TASKS = ("SelfPace", "SelfPace_mat", "SelfPace_matTURN")
COLUMNS = list(CONTACT_COLUMNS.values()) + list(FORCE_COLUMNS.values())
WORST_SHOWN = 10


def task_path(data: Path, participant: str, task: str) -> Path:
    return data / "csv" / f"{participant}_{task}.csv"


def read_task(path: Path) -> tuple[pd.DataFrame | None, str]:
    """The walkway contact and insole force columns of one recording, or a reason."""
    if not path.exists():
        return None, "no file"
    header = set(pd.read_csv(path, nrows=0).columns)
    if not set(FORCE_COLUMNS.values()) <= header:
        return None, "no insole data"
    if not set(CONTACT_COLUMNS.values()) <= header:
        return None, "no walkway data"
    return pd.read_csv(path, usecols=COLUMNS), ""


def check_participant(
    data: Path, participant: str, body_mass_kg: float | None = None
) -> tuple[pd.DataFrame, list[str]]:
    """Matched footfalls of one participant's three tasks, and notes on what was missing."""
    frames, notes = [], []
    for task in TASKS:
        df, why = read_task(task_path(data, participant, task))
        if df is None:
            notes.append(f"{task}: {why}")
            continue
        m = compare_task(df, threshold_candidates(df, body_mass_kg))
        if len(m):
            m.insert(0, "task", task)
            frames.append(m)
    if not frames:
        return pd.DataFrame(), notes
    out = pd.concat(frames, ignore_index=True)
    out.insert(0, "participant", participant)
    return out, notes


def summary_rows(footfalls: pd.DataFrame, by: str | None) -> pd.DataFrame:
    keys = ["threshold"] + ([by] if by else [])
    rows = []
    for key, g in footfalls.groupby(keys, sort=False):
        key = key if isinstance(key, tuple) else (key,)
        row = dict(zip(keys, key))
        row["subgroup"] = by or "all"
        row["n_participants"] = int(g["participant"].nunique())
        row.update(agreement(g))
        rows.append(row)
    return pd.DataFrame(rows)


def recommend(overall: pd.DataFrame) -> str:
    """Highest share of footfalls matched one to one with stance within 30 ms
    (``agree_pct``), then the smallest median absolute stance difference.

    One-to-one detection alone keeps rising with the threshold while every stance
    gets shorter, so it would pick the most biased threshold; agree_pct weighs
    both. Classification results play no part (Midterm Research Plan, Section IV).
    """
    ranked = overall.sort_values(
        ["agree_pct", "stance_median_abs_diff_s"], ascending=[False, True]
    )
    return str(ranked["threshold"].iloc[0])


def body_mass(participants: pd.DataFrame) -> pd.Series:
    """Weight in kg per participant if the sheets give it; empty otherwise."""
    if "weight_kg" in participants:
        return participants.set_index("participant")["weight_kg"]
    return pd.Series(dtype=float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "raw" / "weargait_pd"))
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()
    data, out = Path(args.data), Path(args.out)
    people = load_participants(data)
    people = people[meets_age_rule(people["age"])].reset_index(drop=True)
    mass = body_mass(people)
    frames, notes = [], []
    for p in people.itertuples(index=False):
        m, why = check_participant(data, p.participant, mass.get(p.participant))
        notes += [f"{p.participant} ({p.group}) {w}" for w in why]
        if len(m):
            frames.append(m.assign(group=p.group, site=p.site))
    if not frames:
        raise SystemExit("no recording with both walkway and insole data was found")
    ff = pd.concat(frames, ignore_index=True)

    table = pd.concat(
        [summary_rows(ff, None), summary_rows(ff, "group"), summary_rows(ff, "site")],
        ignore_index=True,
    )
    overall = table[table["subgroup"] == "all"]
    best = recommend(overall)
    per_person = (
        ff.groupby(["participant", "group", "site", "threshold"], sort=False)
        .apply(lambda g: pd.Series(agreement(g)), include_groups=False)
        .reset_index()
    )
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "weargait_threshold_check.csv", index=False)
    per_person.to_csv(out / "weargait_threshold_participants.csv", index=False)

    lines = [
        "Insole contact threshold against the WearGait-PD walkway "
        "(scripts/check_weargait_threshold.py, gaitpdb.walkway)",
        f"Participants aged {MIN_AGE_YEARS} or over with walkway and insole data in at "
        f"least one of {', '.join(TASKS)}: {ff['participant'].nunique()} "
        f"({ff.drop_duplicates('participant')['group'].value_counts().to_dict()}).",
        "Durations are insole minus walkway, in seconds: median difference, median "
        "absolute difference, and Bland-Altman limits (mean +/- 1.96 SD). One to one: "
        "share of the walkway's complete footfalls matched by exactly one insole contact "
        "that overlaps no other footfall.",
        "",
    ]
    for r in overall.itertuples(index=False):
        lines.append(
            f"  {r.threshold}: within 30 ms {r.agree_pct:.1f}%, one to one "
            f"{r.one_to_one_pct:.1f}% of {r.n_footfalls} "
            f"footfalls (unmatched {r.unmatched_pct:.1f}%); stance "
            f"{r.stance_median_diff_s:+.3f} (abs {r.stance_median_abs_diff_s:.3f}; limits "
            f"{r.stance_loa_low_s:+.3f} to {r.stance_loa_high_s:+.3f}); stride "
            f"{r.stride_median_diff_s:+.3f} (n = {r.n_stride}); swing "
            f"{r.swing_median_diff_s:+.3f} (abs {r.swing_median_abs_diff_s:.3f})"
        )
    lines += [
        "",
        f"Recommended threshold (most footfalls matched one to one with stance within 30 ms of the walkway; walkway agreement only, no classification results): {best}",
        "",
    ]
    for sub in ("group", "site"):
        lines.append(
            f"By {sub}, one to one (%) and median absolute stance difference (s):"
        )
        part = table[table["subgroup"] == sub]
        for t in overall["threshold"]:
            cells = [
                f"{getattr(r, sub)} {r.one_to_one_pct:.0f}% / {r.stance_median_abs_diff_s:.3f}"
                for r in part[part["threshold"] == t].itertuples(index=False)
            ]
            lines.append(f"  {t}: " + "; ".join(cells))
        lines.append("")
    worst = per_person[per_person["threshold"] == "20 N"].nsmallest(
        WORST_SHOWN, "one_to_one_pct"
    )
    lines.append("Lowest one-to-one share at 20 N (participant, group, site):")
    for r in worst.itertuples(index=False):
        alt = per_person[
            (per_person["participant"] == r.participant)
            & (per_person["threshold"] == best)
        ]["one_to_one_pct"]
        at_best = (
            f"{alt.iloc[0]:.0f}%" if len(alt) and np.isfinite(alt.iloc[0]) else "n/a"
        )
        lines.append(
            f"  {r.participant} ({r.group}, {r.site}): {r.one_to_one_pct:.0f}% of "
            f"{r.n_footfalls}; at {best}: {at_best}"
        )
    if notes:
        lines += ["", "Recordings not used:"] + [f"  {n}" for n in notes]
    text = "\n".join(lines) + "\n"
    (out / "weargait_threshold_check.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
