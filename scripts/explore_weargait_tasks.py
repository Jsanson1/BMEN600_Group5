"""Exploration for T-017: can WearGait-PD's three straight-walking tasks be pooled?

Exploratory, not part of the analysis pipeline: nothing in src/ is changed. The
tasks are SelfPace, SelfPace_mat and SelfPace_matTURN (separate recordings).
Pooling them gives more strides per participant, but only if the insoles behave
the same across recordings. Two sensor-level checks for drift, per stride:

* swing baseline: the median insole force while the foot is in the air (should be
  near 0 N; strides are found where force drops below 20 N, so a drift above
  20 N shows up as merged strides instead, i.e. as long median strides);
* peak force in stance (a change in sensor gain moves the peaks).

Strides per foot come from the insole total force with gaitpdb's 20 N threshold
[provisional: not yet validated for these insoles, task T-025]. A stride is clean
if every sample is labelled "Walk", it does not touch a "Turn" label or a stride
that does (one stride either side), it has no missing samples, lasts 0.5-2.5 s
with a swing phase of 10-70%, and is not the first or last stride of the foot.

    python scripts/explore_weargait_tasks.py

Writes results/explore_weargait_tasks.{txt,csv} and
figures/explore_stride_rules/11_weargait_task_drift.png.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import wilcoxon  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gaitpdb import meets_age_rule  # noqa: E402
from gaitpdb.events import STRIDE_LIMITS_S, stride_table  # noqa: E402
from gaitpdb.weargait import load_participants  # noqa: E402

TASKS = ["SelfPace", "SelfPace_mat", "SelfPace_matTURN"]
WG_DIR = ROOT / "data" / "raw" / "weargait_pd"
OUT_TXT = ROOT / "results" / "explore_weargait_tasks.txt"
OUT_CSV = ROOT / "results" / "explore_weargait_tasks.csv"
FIG = ROOT / "figures" / "explore_stride_rules" / "11_weargait_task_drift.png"
FS = 100  # Hz, all WearGait-PD streams
SWING_PCT = (10, 70)
CONTROL_EXAMPLE = "WHC015"
NS = (20, 30)

lines: list[str] = []
# Swing windows that are entirely missing data give an all-NaN median; expected.
warnings.filterwarnings("ignore", message="All-NaN slice encountered")


def say(text: str = "") -> None:
    print(text)
    lines.append(text)


def task_strides(pid: str, task: str, margin: int = 1) -> pd.DataFrame | None:
    """Strides of both feet in one task, with cleaning flags and sensor checks."""
    path = WG_DIR / "csv" / f"{pid}_{task}.csv"
    if not path.exists():
        return None
    cols = pd.read_csv(path, nrows=0).columns
    if not {"LTotalForce", "RTotalForce"} <= set(cols):
        return None
    df = pd.read_csv(
        path, usecols=["GeneralEvent", "LTotalForce", "RTotalForce"], low_memory=False
    )
    label = df["GeneralEvent"].astype(str).to_numpy()
    lo, hi = STRIDE_LIMITS_S
    out = []
    for foot in ("L", "R"):
        force = df[f"{foot}TotalForce"].to_numpy(float)
        missing = np.isnan(force)
        st = stride_table(np.nan_to_num(force, nan=0.0), ratio_limits=None)
        if st.empty:
            continue
        a = np.round(st["hs_s"].to_numpy() * FS).astype(int)
        t = np.round(st["to_s"].to_numpy() * FS).astype(int)
        b = np.round(st["next_hs_s"].to_numpy() * FS).astype(int)
        walk = np.array([(label[i:j] == "Walk").all() for i, j in zip(a, b)])
        turn = np.array([(label[i:j] == "Turn").any() for i, j in zip(a, b)])
        gap = np.array([missing[i:j].any() for i, j in zip(a, b)])
        near = turn.copy()
        for k in range(1, margin + 1):
            near[k:] |= turn[:-k]
            near[:-k] |= turn[k:]
        plausible = (
            st["stride_s"].between(lo, hi) & st["swing_pct"].between(*SWING_PCT)
        ).to_numpy()
        clean = walk & ~near & ~gap & plausible
        clean[0] = clean[-1] = False
        st = st.assign(
            foot=foot,
            task=task,
            clean=clean,
            swing_baseline=[np.nanmedian(force[i:j]) for i, j in zip(t, b)],
            peak=[np.nanmax(force[i:j]) if j > i else np.nan for i, j in zip(a, t)],
        )
        out.append(st)
    return pd.concat(out, ignore_index=True) if out else None


def participant_summary(p) -> tuple[dict, dict[str, pd.DataFrame]]:
    row = dict(participant=p.participant, group=p.group, site=p.site)
    per_task = {}
    for task in TASKS:
        st = task_strides(p.participant, task)
        st0 = task_strides(p.participant, task, margin=0)
        if st is None:
            row[f"{task}_ok"] = False
            continue
        per_task[task] = st
        row[f"{task}_ok"] = True
        row[f"{task}_median_stride"] = st["stride_s"].median()
        row[f"{task}_swing_baseline"] = st["swing_baseline"].median()
        row[f"{task}_peak"] = st["peak"].median()
        for foot in ("L", "R"):
            row[f"{task}_n_{foot}"] = int(st[(st.foot == foot) & st.clean].shape[0])
            row[f"{task}_n0_{foot}"] = int(st0[(st0.foot == foot) & st0.clean].shape[0])
    return row, per_task


def cv(s) -> float:
    s = np.asarray(s, float)
    return float(100 * s.std(ddof=1) / s.mean()) if len(s) > 2 else np.nan


def pick_pd(d: pd.DataFrame) -> str:
    ok = d[(d.group == "PD") & d[[f"{t}_ok" for t in TASKS]].all(axis=1)]
    ok = ok[
        ok[[f"{t}_median_stride" for t in TASKS]].apply(
            lambda r: r.between(0.8, 1.8).all(), axis=1
        )
    ]
    i = (ok["pooled_weaker"] - ok["pooled_weaker"].median()).abs().to_numpy().argmin()
    return ok["participant"].iloc[i]


def fig_drift(examples: dict[str, dict[str, pd.DataFrame]]) -> None:
    fig, axes = plt.subplots(
        3, len(examples), figsize=(8 * len(examples), 9), squeeze=False
    )
    colors = {"L": "tab:blue", "R": "tab:orange"}
    for col, (label, per_task) in enumerate(examples.items()):
        x0, ticks = 0, []
        for task in TASKS:
            if task not in per_task:
                continue
            st = per_task[task].sort_values("hs_s")
            n_ax = 0
            for foot in ("L", "R"):
                s = st[st.foot == foot].reset_index(drop=True)
                x = x0 + np.arange(len(s))
                c = colors[foot]
                axes[0, col].plot(
                    x[s.clean],
                    s.stride_s[s.clean],
                    "o",
                    ms=4,
                    color=c,
                    label=f"{foot} clean" if task == TASKS[0] else None,
                )
                axes[0, col].plot(
                    x[~s.clean],
                    np.clip(s.stride_s[~s.clean], None, 3),
                    "x",
                    ms=5,
                    color=c,
                    alpha=0.5,
                    label=f"{foot} removed" if task == TASKS[0] else None,
                )
                axes[1, col].plot(
                    x,
                    s.swing_baseline,
                    "o-",
                    ms=3,
                    lw=0.6,
                    color=c,
                    label=foot if task == TASKS[0] else None,
                )
                axes[2, col].plot(
                    x,
                    s.peak,
                    "o-",
                    ms=3,
                    lw=0.6,
                    color=c,
                    label=foot if task == TASKS[0] else None,
                )
                n_ax = max(n_ax, len(s))
            clean = st[st.clean]
            cv_l = cv(clean[clean.foot == "L"].stride_s)
            cv_r = cv(clean[clean.foot == "R"].stride_s)
            for ax in axes[:, col]:
                ax.axvline(x0 - 1.5, color="grey", lw=0.8)
            axes[0, col].text(
                x0 + 1,
                2.85,
                f"CV L {cv_l:.1f}%, R {cv_r:.1f}%\n"
                f"clean L {int((clean.foot == 'L').sum())}, "
                f"R {int((clean.foot == 'R').sum())}",
                fontsize=8,
                va="top",
            )
            ticks.append((x0 + n_ax / 2, task))
            x0 += n_ax + 3
        for ax, ylabel in zip(
            axes[:, col],
            ["stride (s), capped at 3", "swing baseline (N)", "peak stance force (N)"],
        ):
            ax.set_xticks([t for t, _ in ticks], [n for _, n in ticks])
            ax.set_ylabel(ylabel)
            ax.legend(fontsize=7, loc="upper right")
        axes[0, col].set(
            title=f"{label}: three tasks in sequence (separate recordings)",
            ylim=(0.4, 3.0),
        )
        axes[1, col].axhline(0, color="grey", lw=0.6)
    fig.tight_layout()
    fig.savefig(FIG, dpi=100)
    plt.close(fig)


def main() -> None:
    people = load_participants(WG_DIR)
    people = people[meets_age_rule(people["age"])]
    rows, store = [], {}
    for p in people.itertuples(index=False):
        row, per_task = participant_summary(p)
        rows.append(row)
        store[p.participant] = per_task
    d = pd.DataFrame(rows)
    for v, suffix in (("", "n"), ("0", "n0")):
        for foot in ("L", "R"):
            d[f"pooled{v}_{foot}"] = sum(
                d.get(f"{t}_{suffix}_{foot}", 0).fillna(0) for t in TASKS
            )
        d[f"pooled{v}_weaker"] = d[[f"pooled{v}_L", f"pooled{v}_R"]].min(axis=1)
        d[f"pooled{v}_both_feet"] = d[f"pooled{v}_L"] + d[f"pooled{v}_R"]
    d["selfpace_weaker"] = d[["SelfPace_n_L", "SelfPace_n_R"]].min(axis=1)
    all_tasks = d[[f"{t}_ok" for t in TASKS]].fillna(False).all(axis=1)
    d.to_csv(OUT_CSV, index=False)

    say(
        "T-017 WearGait-PD straight-walking tasks pooled (scripts/explore_weargait_tasks.py)"
    )
    say(
        "Exploratory; insole stride timing provisional (20 N). Per-foot counts of clean strides."
    )
    say()
    say(
        f"Participants aged >= 50: {len(d)}; with insole data in all three tasks: {int(all_tasks.sum())}"
    )
    say()
    say(
        "1. Participants reaching N clean strides (counts / participants with insole data)"
    )
    variants = [
        ("SelfPace only, weaker foot", "selfpace_weaker"),
        ("3 tasks pooled, weaker foot", "pooled_weaker"),
        ("3 tasks pooled, no +/-1 turn margin, weaker foot", "pooled0_weaker"),
        ("3 tasks pooled, both feet together", "pooled_both_feet"),
    ]
    has = d.dropna(subset=["selfpace_weaker"])
    for name, col in variants:
        parts = []
        for g in ("Control", "PD"):
            x = has[has.group == g][col]
            parts.append(
                f"{g}: median {x.median():.0f}, "
                + ", ".join(f">= {n}: {int((x >= n).sum())}/{len(x)}" for n in NS)
            )
        say(f"   {name}: " + " | ".join(parts))
    say()
    say(
        "2. Drift across tasks, every participant with all three tasks (median of per-participant values)"
    )
    a = d[all_tasks]
    for q, unit in (("swing_baseline", "N"), ("peak", "N"), ("median_stride", "s")):
        base = a[f"SelfPace_{q}"]
        say(f"   {q}: SelfPace {base.median():.2f} {unit}")
        for t in TASKS[1:]:
            diff = a[f"{t}_{q}"] - base
            p = wilcoxon(diff.dropna()).pvalue if diff.notna().sum() > 10 else np.nan
            say(
                f"      {t}: {a[f'{t}_{q}'].median():.2f} {unit}; change vs SelfPace median "
                f"{diff.median():+.2f} (IQR {diff.quantile(0.25):+.2f} to {diff.quantile(0.75):+.2f}), "
                f"Wilcoxon p = {p:.3g}"
            )
    say()

    pd_pick = pick_pd(d)
    examples = {}
    for pid in (CONTROL_EXAMPLE, pd_pick):
        g = d.loc[d.participant == pid, "group"].iloc[0]
        examples[f"{g} {pid}"] = store[pid]
        x = d[d.participant == pid].iloc[0]
        say(
            f"3. Example {g} {pid}: clean strides per task (L/R) "
            + "; ".join(
                f"{t} {int(x.get(f'{t}_n_L', 0) or 0)}/{int(x.get(f'{t}_n_R', 0) or 0)}"
                for t in TASKS
            )
            + f"; pooled weaker foot {int(x.pooled_weaker)}"
        )
    say(
        "   (PD example chosen by rule: all three tasks, median stride 0.8-1.8 s in each, "
        "pooled count closest to the PD median)"
    )
    fig_drift(examples)
    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
