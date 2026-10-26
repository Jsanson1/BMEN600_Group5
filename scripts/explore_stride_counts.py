"""Exploration for T-017: how many clean strides each participant keeps, in both datasets.

Exploratory, not part of the analysis pipeline: nothing in src/ is changed. The
count is per foot, after cleaning, and each participant is summarised by the
foot with fewer strides (a per-foot feature needs that many). The question is
whether a common number of strides per foot, N (N = 30 proposed), is reachable.

gaitpdb (analysed usual walks): the timing-based turn removal of
scripts/explore_turn_timing.py (DECISIONS.md D-008), then the first and last
stride of each foot are trimmed.

WearGait-PD (analysed participants, SelfPace task): strides from each insole's
total force with gaitpdb's 20 N threshold [provisional: not yet validated for
these insoles, task T-025]; a stride is kept only if every sample is labelled
"Walk" in the video annotation (GeneralEvent); strides touching a "Turn" label
are removed with one stride either side; strides over missing data, outside
0.5-2.5 s or with a swing phase outside 10-70% are removed; the first and last
stride of each foot are trimmed.

    python scripts/explore_stride_counts.py

Writes results/explore_stride_counts.{txt,csv} and
figures/explore_stride_rules/10_stride_counts.png.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from explore_stride_rules import removal_table  # noqa: E402
from explore_turn_timing import SWING_PCT, analyse  # noqa: E402

from gaitpdb import find_data_dir, meets_age_rule  # noqa: E402
from gaitpdb.events import STRIDE_LIMITS_S, stride_table  # noqa: E402
from gaitpdb.weargait import load_participants  # noqa: E402

N = 30  # proposed common number of strides per foot (Jamie, 2026-10-23)
WG_DIR = ROOT / "data" / "raw" / "weargait_pd"
OUT_TXT = ROOT / "results" / "explore_stride_counts.txt"
OUT_CSV = ROOT / "results" / "explore_stride_counts.csv"
FIG = ROOT / "figures" / "explore_stride_rules" / "10_stride_counts.png"

lines: list[str] = []


def say(text: str = "") -> None:
    print(text)
    lines.append(text)


def trim_ends(kept: np.ndarray) -> np.ndarray:
    """Drop the first and last stride of the foot (technical start and stop effects)."""
    out = kept.copy()
    if len(out):
        out[0] = out[-1] = False
    return out


def gaitpdb_counts() -> pd.DataFrame:
    data = find_data_dir(ROOT / "data" / "raw" / "gaitpdb")
    f = removal_table()
    rows = []
    for r in f.itertuples(index=False):
        row = dict(
            dataset="gaitpdb", participant=r.participant, study=r.study, group=r.group
        )
        if not r.Speed_01 > 0:
            rows.append({**row, "note": "no Speed_01: turns cannot be located"})
            continue
        _, ex = analyse(data, r)
        for foot, st in ex["feet"].items():
            row[f"n_{foot}"] = int(trim_ends(~ex["masks"][foot]).sum())
            row[f"n_raw_{foot}"] = len(st)
        rows.append(row)
    return pd.DataFrame(rows)


def weargait_strides(force: np.ndarray, label: np.ndarray) -> tuple[int, int]:
    """(clean strides, all strides) for one foot of one SelfPace recording."""
    missing = np.isnan(force)
    st = stride_table(np.nan_to_num(force, nan=0.0), ratio_limits=None)
    if st.empty:
        return 0, 0
    lo, hi = STRIDE_LIMITS_S
    a = np.round(st["hs_s"].to_numpy() * 100).astype(int)
    b = np.round(st["next_hs_s"].to_numpy() * 100).astype(int)
    all_walk = np.array([(label[i:j] == "Walk").all() for i, j in zip(a, b)])
    turn = np.array([(label[i:j] == "Turn").any() for i, j in zip(a, b)])
    gap = np.array([missing[i:j].any() for i, j in zip(a, b)])
    near_turn = turn.copy()
    near_turn[1:] |= turn[:-1]
    near_turn[:-1] |= turn[1:]
    plausible = st["stride_s"].between(lo, hi) & st["swing_pct"].between(*SWING_PCT)
    kept = all_walk & ~near_turn & ~gap & plausible.to_numpy()
    return int(trim_ends(kept).sum()), len(st)


def weargait_counts() -> pd.DataFrame:
    people = load_participants(WG_DIR)
    people = people[meets_age_rule(people["age"])]
    rows = []
    for p in people.itertuples(index=False):
        row = dict(
            dataset="WearGait-PD",
            participant=p.participant,
            study=p.site,
            group=p.group,
        )
        path = WG_DIR / "csv" / f"{p.participant}_SelfPace.csv"
        if not path.exists():
            rows.append({**row, "note": "no SelfPace file"})
            continue
        cols = pd.read_csv(path, nrows=0).columns
        if not {"LTotalForce", "RTotalForce"} <= set(cols):
            rows.append({**row, "note": "no insole data"})
            continue
        df = pd.read_csv(
            path,
            usecols=["GeneralEvent", "LTotalForce", "RTotalForce"],
            low_memory=False,
        )
        label = df["GeneralEvent"].astype(str).to_numpy()
        for foot in ("L", "R"):
            n, n_raw = weargait_strides(df[f"{foot}TotalForce"].to_numpy(float), label)
            row[f"n_{foot}"], row[f"n_raw_{foot}"] = n, n_raw
        rows.append(row)
    return pd.DataFrame(rows)


def main() -> None:
    d = pd.concat([gaitpdb_counts(), weargait_counts()], ignore_index=True)
    d["n_min_foot"] = d[["n_L", "n_R"]].min(axis=1)
    d.to_csv(OUT_CSV, index=False)

    say(
        "T-017 clean strides per foot, both datasets (scripts/explore_stride_counts.py)"
    )
    say(
        f"Exploratory; WearGait-PD stride timing provisional (20 N on insoles). N = {N}."
    )
    say()
    skipped = d[d["n_min_foot"].isna()]
    say(f"Not countable: {len(skipped)}")
    for x in skipped.itertuples(index=False):
        say(f"  {x.dataset} {x.participant} ({x.group}): {x.note}")
    say()
    c = d.dropna(subset=["n_min_foot"])
    say("Clean strides on the participant's weaker foot")
    t = c.groupby(["dataset", "group"])["n_min_foot"].describe(percentiles=[0.1, 0.5])
    t["below_N"] = c.groupby(["dataset", "group"])["n_min_foot"].apply(
        lambda x: int((x < N).sum())
    )
    say(t[["count", "min", "10%", "50%", "max", "below_N"]].round(0).to_string())
    say()
    lowest = c.nsmallest(1, "n_min_foot").iloc[0]
    say(
        f"Lowest overall: {lowest.participant} ({lowest.dataset}, {lowest.group}), "
        f"{int(lowest.n_min_foot)} strides on the weaker foot"
    )
    for ds, g in c.groupby("dataset"):
        lo = g.nsmallest(1, "n_min_foot").iloc[0]
        say(f"Lowest in {ds}: {lo.participant} ({lo.group}), {int(lo.n_min_foot)}")
    say()
    below = c[c["n_min_foot"] < N].sort_values(["dataset", "n_min_foot"])
    say(f"Below N = {N}: {len(below)} of {len(c)}")
    for x in below.itertuples(index=False):
        say(
            f"  {x.dataset} {x.participant} ({x.group}, {x.study}): {int(x.n_min_foot)}"
        )

    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    for ax, (ds, g) in zip(axes, c.groupby("dataset", sort=False)):
        bins = np.arange(0, g["n_min_foot"].max() + 10, 5)
        for group, col in (("Control", "tab:blue"), ("PD", "tab:orange")):
            ax.hist(
                g[g.group == group]["n_min_foot"],
                bins=bins,
                alpha=0.6,
                color=col,
                label=f"{group} (n={int((g.group == group).sum())})",
            )
        ax.axvline(N, color="tab:red", ls="--", label=f"N = {N}")
        ax.set(
            title=f"{ds}: clean strides on the weaker foot",
            xlabel="strides per foot after cleaning",
            ylabel="participants",
        )
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG, dpi=100)
    plt.close(fig)
    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
