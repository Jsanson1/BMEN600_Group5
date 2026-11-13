"""Exploration for T-017: who meets the minimum clean strides per foot (DECISIONS.md D-011).

Exploratory, not part of the analysis pipeline: nothing in src/ is changed. Counts
are per foot, after cleaning; a participant is included if both feet reach the
dataset's minimum N (D-011: 40 for gaitpdb, 10 for WearGait-PD). N is an
inclusion minimum: included participants keep all their clean strides.

gaitpdb (analysed usual walks): the timing-based turn removal of
scripts/explore_turn_timing.py (D-008), then the first and last stride of each
foot are trimmed.

WearGait-PD (analysed participants): SelfPace, SelfPace_mat and SelfPace_matTURN
pooled, cleaned by task_strides() in scripts/explore_weargait_tasks.py with no
extra stride removed either side of a labelled turn (D-011): strides from each
insole's total force with gaitpdb's 20 N threshold [provisional: not yet
validated for these insoles, task T-025]; a stride is kept only if every sample
is labelled "Walk", it does not touch a "Turn" label, has no missing samples,
lasts 0.5-2.5 s with a swing phase of 10-70%, and is not the first or last
stride of the foot in that recording.

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
from explore_turn_timing import analyse  # noqa: E402
from explore_weargait_tasks import TASKS, task_strides  # noqa: E402

from gaitpdb import find_data_dir, meets_age_rule  # noqa: E402
from gaitpdb.weargait import load_participants  # noqa: E402

N = {"gaitpdb": 40, "WearGait-PD": 10}  # minimum clean strides per foot (D-011)
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
        n = {"L": 0, "R": 0}
        used = []
        for task in TASKS:
            st = task_strides(p.participant, task, margin=0)
            if st is None:
                continue
            used.append(task)
            for foot in n:
                n[foot] += int(st[(st["foot"] == foot) & st["clean"]].shape[0])
        if not used:
            rows.append({**row, "note": "no insole data in any of the three tasks"})
            continue
        rows.append({**row, "n_L": n["L"], "n_R": n["R"], "tasks": len(used)})
    return pd.DataFrame(rows)


def main() -> None:
    d = pd.concat([gaitpdb_counts(), weargait_counts()], ignore_index=True)
    d["n_min_foot"] = d[["n_L", "n_R"]].min(axis=1)
    d["N"] = d["dataset"].map(N)
    d["included"] = d["n_min_foot"] >= d["N"]
    d.to_csv(OUT_CSV, index=False)

    say("T-017 who meets D-011 (scripts/explore_stride_counts.py)")
    say(
        f"Minimum clean strides per foot: {N}. Exploratory; WearGait-PD stride "
        "timing provisional (20 N on insoles)."
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
    t["included"] = c.groupby(["dataset", "group"])["included"].sum().astype(int)
    say(t[["count", "min", "10%", "50%", "max", "included"]].round(0).to_string())
    say()
    for ds, g in c.groupby("dataset", sort=False):
        all_ds = d[d["dataset"] == ds]
        say(
            f"{ds} (N = {N[ds]}): included {int(g['included'].sum())} of {len(g)} "
            f"countable ({len(all_ds)} analysed participants)"
        )
        for x in g[~g["included"]].sort_values("n_min_foot").itertuples(index=False):
            say(
                f"  excluded {x.participant} ({x.group}, {x.study}): {int(x.n_min_foot)}"
            )
    say()

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
        ax.axvline(N[ds], color="tab:red", ls="--", label=f"N = {N[ds]} (D-011)")
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
