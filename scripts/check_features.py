"""Checks of the two feature tables that never use WearGait-PD's diagnosis labels (T-018).

The cross-cohort test applies a model trained on gaitpdb to WearGait-PD. Before
any group comparison on WearGait-PD is looked at, this script compares the two
datasets without WearGait-PD's diagnosis labels (only section 5 splits gaitpdb
by diagnosis), so the choice of model inputs can be fixed on how the features
behave as measurements (Midterm Research Plan, Section IV). It reads the feature
tables of scripts/make_features.py and the clean strides of
scripts/make_clean_strides.py (task T-017) and reports:

1. Dataset shift: each feature's median and interquartile range in each
   dataset, all participants together, and the ratio of the medians.
2. Pooling WearGait-PD's three tasks (DECISIONS.md D-011): whether it adds
   variability, as the CV over the pooled strides divided by the CV around each
   task's own mean.
3. Straight bouts: a bout is a run of consecutive clean strides of one foot,
   ended by a turn or another removed stride. For each dataset, the share of
   clean strides that open or close a bout, how much longer those strides are
   than the participant's median stride, and the variability left when one
   stride is dropped at each end of every bout, with how many participants would
   then fall below D-011's minimum. WearGait-PD's walkway passes are a few metres
   long, so this is where its protocol differs most from gaitpdb's corridors.
4. Stride-time asymmetry and stride count, in gaitpdb: the asymmetry computed
   from n randomly chosen clean strides per foot, for several n. In a long
   continuous walk each foot's strides span the same time, so the asymmetry of
   their means is near zero; with few strides it measures sampling noise.
5. Each feature's AUC for PD against controls in gaitpdb, the training dataset
   (already analysed for the midterm). WearGait-PD is not split by group.

Writes results/feature_checks.txt and Figure 4 (figures/figure4_feature_checks.png
and .pdf): A, each feature's median and interquartile range in both datasets,
relative to gaitpdb's median; B, stride time by position in a straight bout.

    python scripts/check_features.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["text.hinting"] = "default"
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb.features import STRIDE_FEATURE_COLUMNS, stride_features  # noqa: E402

FEATURES = [c for c in STRIDE_FEATURE_COLUMNS if not c.startswith("n_")]
BOUT_KEYS = {
    "gaitpdb": ["participant", "foot"],
    "weargait": ["participant", "task", "foot"],
}
MIN_STRIDES = {"gaitpdb": 40, "weargait": 10}  # D-011
ASYMMETRY_COUNTS = (10, 20, 30, 40)
N_DRAWS = 20
SEED = 0
INK, MUTED, GRID = "#1f1f1f", "#6e6e6e", "#d9d9d9"
COLORS = {"gaitpdb": "#6250d6", "weargait": "#1baf7a"}
"""Violet and aqua: distinct from Figure 1's group colours, checked for colour-vision
deficiency (the dataviz validator: deutan Delta E 27); marker shape repeats the
identity, and the aqua's low contrast is relieved by the legend."""
MARKERS = {"gaitpdb": "o", "weargait": "s"}
NAMES = {"gaitpdb": "gaitpdb (PhysioNet)", "weargait": "WearGait-PD"}
FIGURE_FEATURES = {
    "stride_time_mean_s": "Mean stride time",
    "swing_pct_mean": "Swing fraction of the stride",
    "stride_time_cv_pct": "Stride-time variability (CV)",
    "stride_time_madcv_pct": "Stride-time variability (robust)",
    "swing_time_cv_pct": "Swing-time variability (CV)",
    "swing_time_madcv_pct": "Swing-time variability (robust)",
    "swing_time_asymmetry_pct": "Swing-time asymmetry",
    "stride_time_asymmetry_pct": "Stride-time asymmetry",
}

lines: list[str] = []


def say(text: str = "") -> None:
    print(text)
    lines.append(text)


def used(strides: pd.DataFrame) -> pd.DataFrame:
    """Clean strides of included participants, the ones the features use."""
    return strides[strides["clean"].astype(bool) & strides["included"].astype(bool)]


def dataset_shift(tables: dict[str, pd.DataFrame], columns: list[str]) -> pd.DataFrame:
    """Median and quartiles of each column in each dataset, and the ratio of medians
    (WearGait-PD over gaitpdb)."""
    rows = []
    for c in columns:
        row = {"feature": c}
        for ds, t in tables.items():
            q = t[c].quantile([0.25, 0.5, 0.75])
            row.update(
                {f"{ds}_q1": q[0.25], f"{ds}_median": q[0.5], f"{ds}_q3": q[0.75]}
            )
        row["ratio"] = row["weargait_median"] / row["gaitpdb_median"]
        rows.append(row)
    return pd.DataFrame(rows)


def pooled_vs_within_cv(strides: pd.DataFrame, column: str) -> pd.Series:
    """Per participant with clean strides in two or more tasks: the CV of ``column``
    over the pooled strides (the feature) divided by the CV computed around each
    task's own mean (the pooled within-task SD over the pooled mean), each per foot
    and averaged over the feet. A ratio near 1 means the tasks' means barely differ,
    so pooling them adds no variability of its own."""
    ratios = {}
    for p, g in used(strides).groupby("participant"):
        if g["task"].nunique() < 2:
            continue
        per_foot = []
        for _, f in g.groupby("foot"):
            x = f[column].to_numpy(dtype=float)
            dev = x - f.groupby("task")[column].transform("mean").to_numpy()
            dof = len(x) - f["task"].nunique()
            if len(x) < 3 or dof < 2:
                continue
            within = np.sqrt(np.sum(dev**2) / dof)
            per_foot.append(x.std(ddof=1) / within if within > 0 else np.nan)
        if per_foot:
            ratios[p] = float(np.nanmean(per_foot))
    return pd.Series(ratios, name=f"{column}_pooled_over_within_cv", dtype=float)


def bout_positions(strides: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """The clean strides of included participants, each with its bout.

    Strides are taken in time order within ``keys`` (participant and foot, plus
    task for WearGait-PD). A bout starts at a clean stride whose predecessor is
    removed, missing (its next heel strike is not this stride's heel strike) or
    absent. Adds ``bout`` (numbered within ``keys``), ``k0`` and ``k1`` (strides
    before and after this one in its bout) and ``bout_len``.
    """
    d = strides[strides["included"].astype(bool)].sort_values([*keys, "hs_s"])
    out = []
    for _, g in d.groupby(keys, sort=False):
        clean = g["clean"].to_numpy(bool)
        hs, next_hs = g["hs_s"].to_numpy(float), g["next_hs_s"].to_numpy(float)
        follows = np.r_[False, np.isclose(hs[1:], next_hs[:-1])]
        starts = clean & ~(np.r_[False, clean[:-1]] & follows)
        g = g.assign(bout=np.cumsum(starts))[clean].copy()
        g["k0"] = g.groupby("bout").cumcount()
        g["k1"] = g.iloc[::-1].groupby("bout").cumcount().iloc[::-1]
        g["bout_len"] = g.groupby("bout")["bout"].transform("size")
        out.append(g)
    return pd.concat(out, ignore_index=True) if out else d.iloc[0:0]


def position_ratios(bouts: pd.DataFrame, min_len: int = 5) -> pd.DataFrame:
    """Stride time over the participant's median stride (of that foot), by position
    in bouts of at least ``min_len`` strides: mean, SD and count."""
    b = bouts[bouts["bout_len"] >= min_len].copy()
    median = bouts.groupby(["participant", "foot"])["stride_s"].median()
    b["ratio"] = (
        b["stride_s"] / median.loc[list(zip(b["participant"], b["foot"]))].to_numpy()
    )
    where = {
        "first": b["k0"] == 0,
        "second": b["k0"] == 1,
        "middle": (b["k0"] >= 2) & (b["k1"] >= 2),
        "second to last": b["k1"] == 1,
        "last": b["k1"] == 0,
    }
    rows = [
        {
            "position": k,
            "mean": b.loc[m, "ratio"].mean(),
            "sd": b.loc[m, "ratio"].std(),
            "n": int(m.sum()),
        }
        for k, m in where.items()
    ]
    return pd.DataFrame(rows)


def trimmed_cv(bouts: pd.DataFrame, trim: int) -> pd.DataFrame:
    """Per participant, the stride- and swing-time CV after dropping ``trim`` strides
    at each end of every bout, and the clean strides left on the weaker foot."""
    keep = bouts[(bouts["k0"] >= trim) & (bouts["k1"] >= trim)]
    rows = []
    for p in sorted(bouts["participant"].unique()):
        ft = stride_features(keep[keep["participant"] == p])
        rows.append(
            {
                "participant": p,
                "n_weaker_foot": min(ft["n_strides_left"], ft["n_strides_right"]),
                "stride_time_cv_pct": ft["stride_time_cv_pct"],
                "swing_time_cv_pct": ft["swing_time_cv_pct"],
            }
        )
    return pd.DataFrame(rows)


def _asymmetry(left: np.ndarray, right: np.ndarray) -> float:
    a, b = left.mean(), right.mean()
    return float(100.0 * abs(a - b) / ((a + b) / 2))


def asymmetry_at_counts(
    strides: pd.DataFrame,
    counts=ASYMMETRY_COUNTS,
    n_draws: int = N_DRAWS,
    seed: int = SEED,
) -> pd.DataFrame:
    """Median over participants of the stride- and swing-time asymmetry (as in
    gaitpdb.features) computed from ``n`` clean strides per foot drawn at random,
    each foot independently and without replacement, averaged over ``n_draws``
    draws; ``n`` = "all" uses every clean stride. Participants with fewer than
    ``n`` strides on a foot are skipped for that ``n``."""
    rng = np.random.default_rng(seed)
    per = []
    for _, g in used(strides).groupby("participant"):
        feet = [g[g["foot"] == f] for f in ("L", "R")]
        per.append(
            [
                (f["stride_s"].to_numpy(float), f["swing_s"].to_numpy(float))
                for f in feet
            ]
        )
    rows = []
    for n in [*counts, "all"]:
        eligible = [
            p for p in per if n == "all" or min(len(p[0][0]), len(p[1][0])) >= n
        ]
        st, sw = [], []
        for _ in range(1 if n == "all" else n_draws):
            a, b = [], []
            for (l_st, l_sw), (r_st, r_sw) in eligible:
                if n == "all":
                    li, ri = slice(None), slice(None)
                else:
                    li = rng.choice(len(l_st), n, replace=False)
                    ri = rng.choice(len(r_st), n, replace=False)
                a.append(_asymmetry(l_st[li], r_st[ri]))
                b.append(_asymmetry(l_sw[li], r_sw[ri]))
            st.append(np.median(a))
            sw.append(np.median(b))
        rows.append(
            {
                "strides_per_foot": n,
                "participants": len(eligible),
                "stride_time_asymmetry_pct": float(np.mean(st)),
                "swing_time_asymmetry_pct": float(np.mean(sw)),
            }
        )
    return pd.DataFrame(rows)


def single_feature_auc(table: pd.DataFrame, columns: list[str]) -> pd.Series:
    """AUC of each column alone for PD (positive) against controls; above 0.5 means
    higher in PD."""
    y = (table["group"] == "PD").astype(int)
    return pd.Series({c: roc_auc_score(y, table[c]) for c in columns}, name="auc")


def _style(ax) -> None:
    ax.tick_params(labelsize=7, length=2.5, color=MUTED)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
        ax.spines[side].set_linewidth(0.6)


def figure(
    shift: pd.DataFrame,
    positions: dict[str, pd.DataFrame],
    path_png: Path,
    path_pdf: Path,
) -> None:
    """Figure 4: A, each feature in both datasets relative to gaitpdb's median;
    B, stride time by position in a straight bout (mean and 95% interval)."""
    fig, (ax_a, ax_b) = plt.subplots(
        1,
        2,
        figsize=(7.2, 3.4),
        gridspec_kw={"wspace": 0.45, "width_ratios": [1.35, 1]},
    )
    rows = shift.set_index("feature").loc[list(FIGURE_FEATURES)]
    y = np.arange(len(rows))[::-1].astype(float)
    ref = rows["gaitpdb_median"].to_numpy()
    for k, ds in enumerate(("gaitpdb", "weargait")):
        off = 0.14 if k == 0 else -0.14
        lo = rows[f"{ds}_q1"].to_numpy() / ref
        hi = rows[f"{ds}_q3"].to_numpy() / ref
        mid = rows[f"{ds}_median"].to_numpy() / ref
        ax_a.hlines(y + off, lo, hi, color=COLORS[ds], lw=1.2, zorder=2)
        ax_a.plot(
            mid,
            y + off,
            MARKERS[ds],
            color=COLORS[ds],
            ms=5,
            zorder=3,
            mec="white",
            mew=0.6,
            label=NAMES[ds],
        )
    ax_a.axvline(1.0, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=1)
    ax_a.set_xscale("log")
    ax_a.set_xticks([0.25, 0.5, 1, 2, 4, 8, 16])
    ax_a.set_xticklabels(["0.25", "0.5", "1", "2", "4", "8", "16"])
    ax_a.minorticks_off()
    ax_a.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(list(FIGURE_FEATURES.values()), fontsize=7, color=INK)
    ax_a.set_xlabel("Relative to gaitpdb's median (log scale)", fontsize=7.5, color=INK)
    ax_a.set_title(
        "A  Median and interquartile range,\nall participants, no diagnosis labels",
        fontsize=7.5,
        loc="left",
        color=INK,
    )
    _style(ax_a)
    order = ["first", "second", "middle", "second to last", "last"]
    x = np.arange(len(order))
    for k, ds in enumerate(("gaitpdb", "weargait")):
        t = positions[ds].set_index("position").loc[order]
        half = 1.96 * t["sd"] / np.sqrt(t["n"])
        ax_b.errorbar(
            x + (-0.08 if k == 0 else 0.08),
            t["mean"],
            yerr=half,
            color=COLORS[ds],
            marker=MARKERS[ds],
            ms=5,
            mec="white",
            mew=0.6,
            lw=1.2,
            capsize=0,
            label=NAMES[ds],
        )
    ax_b.axhline(1.0, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=1)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(["First", "Second", "Middle", "Second\nto last", "Last"])
    ax_b.set_ylabel("Stride time / participant's median", fontsize=7.5, color=INK)
    ax_b.grid(axis="y", color=GRID, lw=0.5, zorder=0)
    ax_b.set_title(
        "B  Stride time by position in a\nstraight bout of 5 or more strides",
        fontsize=7.5,
        loc="left",
        color=INK,
    )
    _style(ax_b)
    handles, labels = ax_b.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=2,
        frameon=False,
        fontsize=7,
        bbox_to_anchor=(0.5, 0.0),
    )
    fig.subplots_adjust(left=0.27, right=0.985, top=0.86, bottom=0.25)
    path_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path_png, dpi=200)
    fig.savefig(path_pdf, metadata={"CreationDate": None})
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--interim", default=str(ROOT / "data" / "interim"))
    ap.add_argument("--figures", default=str(ROOT / "figures"))
    args = ap.parse_args()
    results, interim = Path(args.results), Path(args.interim)
    figures = Path(args.figures)
    tables, strides = {}, {}
    for ds in ("gaitpdb", "weargait"):
        f, s = results / f"features_{ds}.csv", interim / f"clean_strides_{ds}.csv"
        if f.exists() and s.exists():
            tables[ds] = pd.read_csv(f)
            strides[ds] = pd.read_csv(s, low_memory=False)
    say("Label-free checks of the feature tables (scripts/check_features.py)")
    say("WearGait-PD is never split by diagnosis here; gaitpdb only in section 5.")
    say()
    if set(tables) != {"gaitpdb", "weargait"}:
        say("Skipped: needs results/features_{gaitpdb,weargait}.csv and the clean")
        say(
            "strides of both datasets (scripts/make_clean_strides.py, make_features.py)."
        )
        (results / "feature_checks.txt").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        return

    say("1. Dataset shift: median (interquartile range), all participants together")
    shift = dataset_shift(tables, FEATURES)
    for r in shift.itertuples(index=False):
        say(
            f"  {r.feature}: gaitpdb {r.gaitpdb_median:.3g} ({r.gaitpdb_q1:.3g} to "
            f"{r.gaitpdb_q3:.3g}); WearGait-PD {r.weargait_median:.3g} "
            f"({r.weargait_q1:.3g} to {r.weargait_q3:.3g}); ratio {r.ratio:.2f}"
        )
    say()

    say("2. Pooling WearGait-PD's three tasks: CV over the pooled strides / CV around")
    say("   each task's own mean (1 = pooling adds no variability)")
    for col in ("stride_s", "swing_s"):
        r = pooled_vs_within_cv(strides["weargait"], col)
        say(
            f"  {col}: median {r.median():.3f} (interquartile range {r.quantile(0.25):.3f} "
            f"to {r.quantile(0.75):.3f}), {len(r)} participants with two or more tasks"
        )
    say()

    say("3. Straight bouts (runs of consecutive clean strides of one foot)")
    positions = {}
    for ds, keys in BOUT_KEYS.items():
        b = bout_positions(strides[ds], keys)
        n_bouts = b.groupby([*keys, "bout"]).ngroups
        lengths = b.drop_duplicates([*keys, "bout"])["bout_len"]
        per_foot = (
            b.drop_duplicates([*keys, "bout"]).groupby(["participant", "foot"]).size()
        )
        ends = ((b["k0"] == 0) | (b["k1"] == 0)).mean()
        say(
            f"  {ds}: {len(b)} clean strides in {n_bouts} bouts, bout length median "
            f"{lengths.median():.0f} strides, median {per_foot.median():.0f} bouts per "
            f"participant and foot; {100 * ends:.1f}% of clean strides open or close a bout"
        )
        say("    stride time / participant's median, in bouts of 5 or more strides:")
        positions[ds] = position_ratios(b)
        for r in positions[ds].itertuples(index=False):
            say(f"      {r.position}: mean {r.mean:.3f} (SD {r.sd:.3f}, {r.n} strides)")
        for trim in (0, 1):
            t = trimmed_cv(b, trim)
            below = int((t["n_weaker_foot"] < MIN_STRIDES[ds]).sum())
            label = (
                "all clean strides"
                if trim == 0
                else "one stride dropped at each bout end"
            )
            say(
                f"    {label}: stride-time CV median {t['stride_time_cv_pct'].median():.2f}%, "
                f"swing-time CV median {t['swing_time_cv_pct'].median():.2f}%; weaker foot "
                f"median {t['n_weaker_foot'].median():.0f} strides, {below} of {len(t)} "
                f"below D-011's minimum of {MIN_STRIDES[ds]}"
            )
    say()

    say("4. Asymmetry against stride count in gaitpdb: median over participants of the")
    say(
        f"   asymmetry from n random clean strides per foot ({N_DRAWS} draws, seed {SEED})"
    )
    for r in asymmetry_at_counts(strides["gaitpdb"]).itertuples(index=False):
        say(
            f"  n = {r.strides_per_foot} ({r.participants} participants): stride time "
            f"{r.stride_time_asymmetry_pct:.3f}%, swing time {r.swing_time_asymmetry_pct:.2f}%"
        )
    wg_n = (
        tables["weargait"][["n_strides_left", "n_strides_right"]].min(axis=1).median()
    )
    say(f"  (WearGait-PD weaker foot: median {wg_n:.0f} clean strides)")
    say()

    figure(
        shift,
        positions,
        figures / "figure4_feature_checks.png",
        figures / "figure4_feature_checks.pdf",
    )

    say("5. AUC of each feature alone, PD against controls, gaitpdb only")
    for c, a in single_feature_auc(tables["gaitpdb"], FEATURES).items():
        say(f"  {c}: {a:.3f}")
    (results / "feature_checks.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
