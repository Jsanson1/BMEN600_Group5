"""Exploration for T-017: find turns from the walking path and walking speed, and remove them.

Exploratory, not part of the analysis pipeline: nothing in src/ is changed. Each
sub-study walked a corridor of known length (Ga and Ju 25 m, Si 35 m, from the
sub-studies' papers [UNVERIFIED: references not yet in report/midterm/sources.md]),
so a walker turns about every path / speed seconds. For each analysed usual walk:

1. expected turn interval = path / Speed_01 (Speed_01 from demographics.txt);
2. the walk's own rhythm: Lomb-Scargle peak of the stride series of both feet,
   searched within 0.7-1.5 x the expected interval (walks with fewer than 2.5
   expected turns use the expected interval directly);
3. turn centres: the most disturbed strides (stride / that foot's median, either
   foot), at least 0.6 intervals apart, at most one per interval of walking, and
   at least MIN_RATIO x the median;
4. every stride of both feet that overlaps a fixed window of +/- WINDOW_S around a
   turn centre is removed, plus one stride either side.

Complete Ju walks are exactly 100 m (four lengths of the corridor), so they have
three turns: the one check here with a known answer.

    python scripts/explore_turn_timing.py [--data data/raw/gaitpdb]

Writes figures/explore_stride_rules/08_*.png, 09_*.png and
results/explore_turn_timing.{txt,csv}.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.signal import lombscargle  # noqa: E402
from scipy.stats import mannwhitneyu  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from explore_stride_rules import pick_pair, removal_table  # noqa: E402

from gaitpdb import find_data_dir, load_record  # noqa: E402
from gaitpdb.events import STRIDE_LIMITS_S, stride_table  # noqa: E402

FIG_DIR = ROOT / "figures" / "explore_stride_rules"
OUT_TXT = ROOT / "results" / "explore_turn_timing.txt"
OUT_CSV = ROOT / "results" / "explore_turn_timing.csv"

PATH_M = {"Ga": 25.0, "Ju": 25.0, "Si": 35.0}  # [UNVERIFIED] corridor lengths
SEARCH = (0.7, 1.5)  # rhythm search, x the expected interval
MIN_TURNS_FOR_RHYTHM = 2.5
MIN_SEPARATION = 0.6  # x the interval, between two turn centres
MIN_RATIO = 1.10  # a turn's most disturbed stride is >= 10% longer than the median
WINDOW_S = 2.0  # fixed window, +/- s around a turn centre
PAD = 1  # strides removed either side of the window, each foot
AGREE_RATIO = 1.05  # the other foot counts as disturbed at >= 5% above its median
SWING_PCT = (10, 70)  # the team's swing rule; with STRIDE_LIMITS_S, applied as well
MISSED_HS_RATIO = (1.75, 2.25)  # x the median, one foot only: a missed heel strike

lines: list[str] = []


def say(text: str = "") -> None:
    print(text)
    lines.append(text)


def foot_strides(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    out = {}
    for foot in ("L", "R"):
        st = stride_table(df[f"{foot}_total"].to_numpy()).reset_index(drop=True)
        st["ratio"] = st["stride_s"] / st["stride_s"].median()
        out[foot] = st
    return out


def rhythm(feet: dict[str, pd.DataFrame], expected: float) -> float:
    """Lomb-Scargle peak of both feet's stride series within SEARCH x expected."""
    t, y = [], []
    for st in feet.values():
        s = st["stride_s"].to_numpy()
        s = np.minimum(s, np.median(s) + 1.0)  # one long turn must not dominate
        t.append(st["hs_s"].to_numpy())
        y.append(s - s.mean())
    periods = np.linspace(SEARCH[0] * expected, SEARCH[1] * expected, 400)
    power = lombscargle(np.concatenate(t), np.concatenate(y), 2 * np.pi / periods)
    return float(periods[power.argmax()])


def find_turns(feet: dict[str, pd.DataFrame], interval: float, span: float):
    """Turn centres (s): most disturbed strides, separated, at most span / interval."""
    cand = pd.concat(
        [
            st.assign(foot=f, mid=(st["hs_s"] + st["next_hs_s"]) / 2)
            for f, st in feet.items()
        ]
    ).sort_values("ratio", ascending=False)
    max_turns = int(np.floor(span / interval))
    centres, agree = [], []
    for row in cand.itertuples(index=False):
        if len(centres) >= max_turns or row.ratio < MIN_RATIO:
            break
        if any(abs(row.mid - c) < MIN_SEPARATION * interval for c in centres):
            continue
        centres.append(row.mid)
        other = feet["R" if row.foot == "L" else "L"]
        near = other[
            (other["next_hs_s"] > row.mid - WINDOW_S)
            & (other["hs_s"] < row.mid + WINDOW_S)
        ]
        agree.append(bool((near["ratio"] >= AGREE_RATIO).any()))
    order = np.argsort(centres)
    return [centres[i] for i in order], [agree[i] for i in order]


def removed_mask(st: pd.DataFrame, centres: list[float]) -> np.ndarray:
    hit = np.zeros(len(st), bool)
    for c in centres:
        hit |= (st["next_hs_s"] > c - WINDOW_S).to_numpy() & (
            st["hs_s"] < c + WINDOW_S
        ).to_numpy()
    out = hit.copy()
    for k in range(1, PAD + 1):
        out[k:] |= hit[:-k]
        out[:-k] |= hit[k:]
    return out


def missed_heel_strikes(feet: dict[str, pd.DataFrame], foot: str) -> np.ndarray:
    """Strides of `foot` near twice its median while the other foot is undisturbed.

    Two strides merged into one (a heel strike the force threshold missed) affect
    one foot only; a turn affects both, so this cannot remove a turn.
    """
    st, other = feet[foot], feet["R" if foot == "L" else "L"]
    out = np.zeros(len(st), bool)
    lo, hi = MISSED_HS_RATIO
    for i in np.flatnonzero(st["ratio"].between(lo, hi).to_numpy()):
        a, b = st["hs_s"].iloc[i], st["next_hs_s"].iloc[i]
        near = other[(other["next_hs_s"] > a) & (other["hs_s"] < b)]
        out[i] = len(near) > 0 and bool((near["ratio"] < AGREE_RATIO).all())
    return out


def cv(s: np.ndarray) -> float:
    return float(100 * s.std(ddof=1) / s.mean()) if len(s) > 2 else np.nan


def analyse(data: Path, r) -> tuple[dict, dict]:
    df = load_record(data / f"{r.record}.txt")
    feet = foot_strides(df)
    span = max(st["next_hs_s"].iloc[-1] for st in feet.values()) - min(
        st["hs_s"].iloc[0] for st in feet.values()
    )
    expected = PATH_M[r.study] / r.Speed_01
    n_expected = span / expected
    interval = (
        rhythm(feet, expected) if n_expected >= MIN_TURNS_FOR_RHYTHM else expected
    )
    centres, agree = find_turns(feet, interval, span)
    row = dict(
        record=r.record,
        study=r.study,
        group=r.group,
        speed=r.Speed_01,
        walk_s=span,
        expected_s=expected,
        interval_s=interval,
        used_rhythm=n_expected >= MIN_TURNS_FOR_RHYTHM,
        turns_possible=int(np.floor(span / interval)),
        turns_found=len(centres),
        turns_both_feet=int(sum(agree)),
    )
    masks = {}
    lo, hi = STRIDE_LIMITS_S
    for f, st in feet.items():
        turn = removed_mask(st, centres)
        limits = ~(
            st["stride_s"].between(lo, hi) & st["swing_pct"].between(*SWING_PCT)
        ).to_numpy()
        missed = missed_heel_strikes(feet, f)
        m = turn | limits | missed
        masks[f] = m
        s = st["stride_s"].to_numpy()
        row[f"turn_pct_{f}"] = 100 * turn.mean()
        row[f"limits_only_pct_{f}"] = 100 * (limits & ~turn).mean()
        row[f"missed_hs_{f}"] = int((missed & ~turn & ~limits).sum())
        row[f"removed_pct_{f}"] = 100 * m.mean()
        row[f"n_kept_{f}"] = int((~m).sum())
        row[f"cv_kept_{f}"] = cv(s[~m])
        row[f"cv_team_rules_{f}"] = cv(s[st["kept"].to_numpy()])
        row[f"n_team_rules_{f}"] = int(st["kept"].sum())
    for key in ("turn_pct", "limits_only_pct", "removed_pct"):
        row[key] = (row[f"{key}_L"] + row[f"{key}_R"]) / 2
    row["n_kept"] = row["n_kept_L"] + row["n_kept_R"]
    row["n_team_rules"] = row["n_team_rules_L"] + row["n_team_rules_R"]
    row["cv_after_turns"] = np.nanmean([row["cv_kept_L"], row["cv_kept_R"]])
    row["cv_team_rules"] = np.nanmean([row["cv_team_rules_L"], row["cv_team_rules_R"]])
    return row, dict(feet=feet, centres=centres, masks=masks)


def fig_examples(examples: dict[str, dict]) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(18, 7))
    for ax, (label, ex) in zip(axes.T.ravel(), examples.items()):
        for c in ex["centres"]:
            ax.axvspan(c - WINDOW_S, c + WINDOW_S, color="tab:green", alpha=0.2, lw=0)
        for f, st in ex["feet"].items():
            m, col = ex["masks"][f], {"L": "tab:blue", "R": "tab:orange"}[f]
            mk = {"L": "o", "R": "s"}[f]
            s = np.clip(st["stride_s"].to_numpy(), None, 2.6)
            ax.plot(st["hs_s"], s, mk + "-", ms=3, lw=0.6, color=col, label=f)
            ax.plot(
                st["hs_s"][m],
                s[m],
                "x",
                ms=7,
                mew=1.8,
                color="tab:red",
                label="removed" if f == "L" else None,
            )
        ax.set(
            title=f"{label}: {len(ex['centres'])} turns found (green = +/-{WINDOW_S:g} s)",
            xlabel="time of heel strike (s)",
            ylabel="stride (s), capped at 2.6",
        )
        ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "08_turn_timing_examples.png", dpi=100)
    plt.close(fig)


def fig_summary(d: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
    ax = axes[0]
    labels, data = [], []
    for study in ("Ga", "Ju", "Si"):
        for group in ("Control", "PD"):
            labels.append(f"{study}\n{group}")
            data.append(d[(d.study == study) & (d.group == group)]["removed_pct"])
    ax.boxplot(data, tick_labels=labels)
    ax.set(
        ylabel="% of strides removed (mean of feet)",
        title="Turn removal by sub-study and group",
    )
    ax = axes[1]
    for group, mk, col in (("Control", "o", "tab:blue"), ("PD", "^", "tab:orange")):
        g = d[d.group == group]
        ax.plot(
            g["cv_team_rules"],
            g["cv_after_turns"],
            mk,
            color=col,
            alpha=0.7,
            label=group,
        )
    lim = [0, max(d["cv_team_rules"].max(), d["cv_after_turns"].max()) * 1.05]
    ax.plot(lim, lim, "k-", lw=0.8)
    ax.set(
        xlabel="stride-time CV, current team rules (%)",
        ylabel="stride-time CV, turns removed (%)",
        title="Variability before and after turn removal",
        xlim=lim,
        ylim=lim,
    )
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "09_turn_timing_summary.png", dpi=100)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(ROOT / "data" / "raw" / "gaitpdb"))
    data = find_data_dir(ap.parse_args().data)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    f = removal_table()
    say(
        "T-017 turn timing (scripts/explore_turn_timing.py); exploratory, src/ unchanged"
    )
    say(
        f"Paths {PATH_M} m [UNVERIFIED]; rhythm search {SEARCH} x expected; turn stride "
        f">= {MIN_RATIO} x median; window +/- {WINDOW_S} s; plus {PAD} stride each side"
    )
    say()
    missing = f[~(f["Speed_01"] > 0)]
    if len(missing):
        say(f"No usable Speed_01, skipped: {', '.join(missing['record'])}")
    rows, examples = [], {}
    pairs = {s: pick_pair(f, s) for s in ("Ga", "Ju", "Si")}
    wanted = {rec: f"{g} {rec}" for p in pairs.values() for g, rec in p.items()}
    for r in f[f["Speed_01"] > 0].itertuples(index=False):
        row, ex = analyse(data, r)
        rows.append(row)
        if r.record in wanted:
            examples[wanted[r.record]] = ex
    d = pd.DataFrame(rows)
    d.to_csv(OUT_CSV, index=False)

    say(f"1. Walks analysed: {len(d)}")
    g = d.groupby(["study", "group"])
    t = g.agg(
        n=("record", "size"),
        turns_found=("turns_found", "median"),
        turns_possible=("turns_possible", "median"),
        both_feet=("turns_both_feet", "sum"),
        all_turns=("turns_found", "sum"),
        removed_pct=("removed_pct", "median"),
        cv_team=("cv_team_rules", "median"),
        cv_turns_removed=("cv_after_turns", "median"),
    )
    t["both_feet_pct"] = (100 * t["both_feet"] / t["all_turns"]).round(0)
    say(t.drop(columns=["both_feet", "all_turns"]).round(2).to_string())
    say(
        "  (medians per walk; both_feet_pct = share of turns where the other foot is also disturbed)"
    )
    say()
    pd_, co = (
        d.loc[d.group == "PD", "removed_pct"],
        d.loc[d.group == "Control", "removed_pct"],
    )
    say(
        f"2. % strides removed, PD vs control: median {pd_.median():.1f} vs {co.median():.1f}, "
        f"Mann-Whitney p = {mannwhitneyu(pd_, co).pvalue:.3f}"
    )
    say(
        f"   Walks with no turn found: {int((d.turns_found == 0).sum())} "
        f"(PD {int(((d.turns_found == 0) & (d.group == 'PD')).sum())}, "
        f"control {int(((d.turns_found == 0) & (d.group == 'Control')).sum())})"
    )
    say()
    ju = d[d.study == "Ju"].copy()
    complete = ju[ju["walk_s"] >= 0.9 * 100 / ju["speed"]]
    say(
        f"3. Known answer: complete Ju walks (>= 90% of 100 m / Speed_01): {len(complete)} of {len(ju)}"
    )
    counts = complete.groupby(["group", "turns_found"]).size().unstack(fill_value=0)
    say(counts.to_string())
    say(
        f"   Exactly 3 turns found: {int((complete.turns_found == 3).sum())} of {len(complete)}"
    )
    say()
    say("4. Removal split: turns vs the fixed limits (median % of strides per walk)")
    say(
        d.groupby(["study", "group"])[["turn_pct", "limits_only_pct", "removed_pct"]]
        .median()
        .round(1)
        .to_string()
    )
    d["missed_hs"] = d["missed_hs_L"] + d["missed_hs_R"]
    say(
        f"   Missed heel strikes (one foot ~2x, other foot undisturbed) removed beyond "
        f"turns and limits: {int(d['missed_hs'].sum())} strides in "
        f"{int((d['missed_hs'] > 0).sum())} walks"
    )
    rise = d[d["cv_after_turns"] > d["cv_team_rules"] + 1]
    say(f"   Walks whose CV rises by > 1 point vs the team rules: {len(rise)}")
    for x in rise.itertuples(index=False):
        say(f"     {x.record}: {x.cv_team_rules:.2f} -> {x.cv_after_turns:.2f}")
    say()
    say("5. Could length alone identify PD? AUC = P(a PD walk has the higher value)")
    for col, what in [
        ("walk_s", "walking time (s)"),
        ("n_team_rules", "strides kept, team rules"),
        ("n_kept", "strides kept, turns + limits"),
        ("removed_pct", "% strides removed, turns + limits"),
    ]:
        a, b = d.loc[d.group == "PD", col], d.loc[d.group == "Control", col]
        u = mannwhitneyu(a, b)
        auc = u.statistic / (len(a) * len(b))
        say(
            f"   {what}: median PD {a.median():.1f} vs control {b.median():.1f}; "
            f"AUC {auc:.2f}, p = {u.pvalue:.3g}"
        )
    say()
    say("6. The six example walks")
    for label in examples:
        x = d[d.record == label.split()[-1]].iloc[0]
        say(
            f"   {label}: expected {x.expected_s:.1f} s, used {x.interval_s:.1f} s "
            f"({'rhythm' if x.used_rhythm else 'expected'}), turns {x.turns_found} of "
            f"{x.turns_possible} possible ({x.turns_both_feet} on both feet), removed "
            f"{x.removed_pct:.0f}%, CV {x.cv_team_rules:.2f} -> {x.cv_after_turns:.2f}"
        )

    fig_examples(examples)
    fig_summary(d)
    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"wrote {OUT_TXT.relative_to(ROOT)}, {OUT_CSV.relative_to(ROOT)}, figures 08-09"
    )


if __name__ == "__main__":
    main()
