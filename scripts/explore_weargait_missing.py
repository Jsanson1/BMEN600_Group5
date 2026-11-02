"""Exploration for T-017: where WearGait-PD's insole data is missing.

Exploratory; nothing in src/ is changed. For each analysed participant's
SelfPace, SelfPace_mat and SelfPace_matTURN recording and each insole, the
missing samples (NaN) are split into padding (a run touching the start or end
of the recording; the dataset pads streams to align devices) and dropouts (runs
inside the recording). Also: how much of the "Walk"-labelled time is missing.

    python scripts/explore_weargait_missing.py

Writes results/explore_weargait_missing.{txt,csv}.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaitpdb import meets_age_rule  # noqa: E402
from gaitpdb.weargait import load_participants  # noqa: E402

WG_DIR = ROOT / "data" / "raw" / "weargait_pd"
TASKS = ["SelfPace", "SelfPace_mat", "SelfPace_matTURN"]
FS = 100
OUT_TXT = ROOT / "results" / "explore_weargait_missing.txt"
OUT_CSV = ROOT / "results" / "explore_weargait_missing.csv"


def runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """Start and end (exclusive) of each run of True."""
    d = np.diff(np.r_[0, mask.astype(int), 0])
    return list(zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)))


def main() -> None:
    people = load_participants(WG_DIR)
    people = people[meets_age_rule(people["age"])]
    rows = []
    for p in people.itertuples(index=False):
        for task in TASKS:
            path = WG_DIR / "csv" / f"{p.participant}_{task}.csv"
            if not path.exists():
                continue
            cols = pd.read_csv(path, nrows=0).columns
            if not {"LTotalForce", "RTotalForce"} <= set(cols):
                continue
            df = pd.read_csv(
                path,
                usecols=["GeneralEvent", "LTotalForce", "RTotalForce"],
                low_memory=False,
            )
            walk = (df["GeneralEvent"].astype(str) == "Walk").to_numpy()
            n = len(df)
            for foot in ("L", "R"):
                miss = df[f"{foot}TotalForce"].isna().to_numpy()
                pad = drop = 0
                drop_runs = []
                for a, b in runs(miss):
                    if a == 0 or b == n:
                        pad += b - a
                    else:
                        drop += b - a
                        drop_runs.append((b - a) / FS)
                rows.append(
                    dict(
                        participant=p.participant,
                        group=p.group,
                        site=p.site,
                        task=task,
                        foot=foot,
                        duration_s=n / FS,
                        missing_pct=100 * miss.mean(),
                        padding_pct=100 * pad / n,
                        dropout_pct=100 * drop / n,
                        dropout_runs=len(drop_runs),
                        longest_dropout_s=max(drop_runs, default=0.0),
                        walk_missing_pct=100 * miss[walk].mean()
                        if walk.any()
                        else np.nan,
                        walk_padding_overlap_pct=100
                        * (miss & walk)[: max(1, n)].sum()
                        / max(1, walk.sum()),
                    )
                )
    d = pd.DataFrame(rows)
    d.to_csv(OUT_CSV, index=False)
    lines = [
        "T-017 WearGait-PD missing insole data (scripts/explore_weargait_missing.py)",
        f"Recordings x feet: {len(d)} ({d['participant'].nunique()} participants)",
        "",
        "Median % of samples per recording and foot (IQR in brackets):",
    ]
    for col, what in [
        ("missing_pct", "missing, all"),
        ("padding_pct", "padding (start/end)"),
        ("dropout_pct", "dropouts (inside)"),
        ("walk_missing_pct", "of Walk-labelled time"),
    ]:
        q = d[col].quantile([0.25, 0.5, 0.75])
        lines.append(f"  {what}: {q[0.5]:.1f} ({q[0.25]:.1f}-{q[0.75]:.1f})")
    share = d["padding_pct"].sum() / d["missing_pct"].sum()
    lines.append(f"  share of all missing samples that is padding: {100 * share:.1f}%")
    lines += [
        "",
        f"Recordings with any dropout: {int((d['dropout_runs'] > 0).sum())} of {len(d)}; "
        f"longest dropout {d['longest_dropout_s'].max():.2f} s; "
        f"dropouts over 1 s: {int((d['longest_dropout_s'] > 1).sum())}",
        "",
        "By task (median % missing of Walk-labelled time):",
    ]
    for task, g in d.groupby("task"):
        lines.append(f"  {task}: {g['walk_missing_pct'].median():.1f}")
    per_person = (
        d.groupby(["participant", "group"])["walk_missing_pct"].mean().reset_index()
    )
    a = per_person[per_person.group == "PD"]["walk_missing_pct"].dropna()
    b = per_person[per_person.group == "Control"]["walk_missing_pct"].dropna()
    lines += [
        "",
        f"Walk-labelled time missing, per participant: PD median {a.median():.1f}% vs "
        f"control {b.median():.1f}%, Mann-Whitney p = {mannwhitneyu(a, b).pvalue:.3f}",
    ]
    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
