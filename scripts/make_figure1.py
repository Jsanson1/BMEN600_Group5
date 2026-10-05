"""Figure 1: detected gait events on one recording, then stride-time
variability and swing-time asymmetry by group across all usual-walk recordings.

Also writes results/features_usual_walk.csv (one row per usual-walk record),
results/features_usual_walk_by_group.csv (median per group, AUC and
Mann-Whitney p for every feature) and results/figure1_summary.txt with the
numbers quoted in the text.

    python scripts/make_figure1.py [--data data/raw/gaitpdb] [--example GaPt03_01]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import (  # noqa: E402
    FEATURE_COLUMNS,
    build_manifest,
    find_data_dir,
    load_demographics,
    load_record,
    parse_record_name,
    record_features,
    stride_table,
)

COLORS = {"Control": "#3b6ea5", "PD": "#c8552d"}


def panel_trace(
    ax, df: pd.DataFrame, record: str, t0: float = 20.0, t1: float = 28.0
) -> None:
    sel = (df["time_s"] >= t0) & (df["time_s"] <= t1)
    t = df.loc[sel, "time_s"]
    for foot, col, color in (
        ("left", "L_total", "#3b6ea5"),
        ("right", "R_total", "#c8552d"),
    ):
        ax.plot(t, df.loc[sel, col], color=color, lw=1.0, label=f"{foot} foot")
        st = stride_table(df[col].to_numpy())
        hs = st.loc[st["kept"], "hs_s"]
        to = st.loc[st["kept"], "to_s"]
        hs = hs[(hs >= t0) & (hs <= t1)]
        to = to[(to >= t0) & (to <= t1)]
        ax.plot(
            hs,
            np.full(len(hs), -40.0 if foot == "left" else -80.0),
            "^",
            color=color,
            ms=5,
        )
        ax.plot(
            to,
            np.full(len(to), -40.0 if foot == "left" else -80.0),
            "v",
            color=color,
            mfc="white",
            ms=5,
        )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Vertical force (N)")
    ax.set_title(
        f"A. Total force per foot, record {record}; ▲ heel strike, ▽ toe off",
        loc="left",
        fontsize=10,
    )
    ax.legend(loc="upper center", ncol=2, frameon=False, fontsize=8)
    ax.set_ylim(-110, 1450)


def panel_strip(ax, feats: pd.DataFrame, column: str, ylabel: str, title: str) -> dict:
    """One jittered point per participant, with the group median as a bar."""
    out = {}
    positions = {"Control": 0, "PD": 1}
    for group, x in positions.items():
        y = feats.loc[feats["group"] == group, column].dropna()
        out[group] = y
        jitter = (np.random.default_rng(0).random(len(y)) - 0.5) * 0.25
        ax.plot(x + jitter, y, "o", color=COLORS[group], alpha=0.55, ms=4)
        ax.hlines(y.median(), x - 0.2, x + 0.2, color="black", lw=2)
    ax.set_xticks(
        [0, 1], [f"Control (n={len(out['Control'])})", f"PD (n={len(out['PD'])})"]
    )
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=10)
    return out


def compare_groups(feats: pd.DataFrame) -> pd.DataFrame:
    """Median per group, AUC (from the Mann-Whitney U) and two-sided p, per feature.

    AUC is the probability that a randomly chosen PD participant has the higher
    value; values below 0.5 mean the feature is lower in PD.
    """
    rows = []
    for col in FEATURE_COLUMNS:
        if col.startswith("n_strides"):
            continue
        pd_ = feats.loc[feats["group"] == "PD", col].dropna()
        co = feats.loc[feats["group"] == "Control", col].dropna()
        u = stats.mannwhitneyu(pd_, co, alternative="two-sided")
        rows.append(
            {
                "feature": col,
                "control_median": co.median(),
                "pd_median": pd_.median(),
                "auc_pd_higher": u.statistic / (len(pd_) * len(co)),
                "p_mann_whitney": u.pvalue,
                "n_control": len(co),
                "n_pd": len(pd_),
            }
        )
    return pd.DataFrame(rows).sort_values("p_mann_whitney").reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    ap.add_argument("--example", default="GaPt03_01")
    ap.add_argument("--out", default="results")
    ap.add_argument("--fig", default="figures")
    args = ap.parse_args()

    data_dir = find_data_dir(args.data)
    out, fig_dir = Path(args.out), Path(args.fig)
    out.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(data_dir)
    usual = manifest[manifest["walk"] == 1].copy()
    demo_path = data_dir / "demographics.txt"
    if demo_path.exists():
        demo = load_demographics(data_dir)[["ID", "Age", "sex", "HoehnYahr", "UPDRSM"]]
    else:
        print("warning: demographics.txt not found; no age, sex or severity columns")
        demo = pd.DataFrame(columns=["ID", "Age", "sex", "HoehnYahr", "UPDRSM"])

    rows = []
    for _, r in usual.iterrows():
        df = load_record(r["path"])
        ft = record_features(df)
        ft.update(
            record=r["record"],
            participant=r["participant"],
            study=r["study"],
            group=r["group"],
        )
        rows.append(ft)
    feats = (
        pd.DataFrame(rows)
        .merge(demo, left_on="participant", right_on="ID", how="left")
        .drop(columns="ID")
    )
    feats.to_csv(out / "features_usual_walk.csv", index=False)
    by_group = compare_groups(feats)
    by_group.to_csv(out / "features_usual_walk_by_group.csv", index=False)

    ex_path = data_dir / f"{args.example}.txt"
    if not ex_path.exists():
        ex_path = Path(usual.iloc[0]["path"])
    ex = load_record(ex_path)

    fig, axes = plt.subplots(
        1, 3, figsize=(13.5, 3.8), gridspec_kw={"width_ratios": [1.7, 1, 1]}
    )
    panel_trace(axes[0], ex, parse_record_name(ex_path).record)
    cv = panel_strip(
        axes[1],
        feats,
        "stride_time_cv_pct",
        "Stride-time variability, CV (%)",
        "B. Usual walk, one point per participant",
    )
    asym = panel_strip(
        axes[2],
        feats,
        "swing_time_asymmetry_pct",
        "Swing-time asymmetry, left vs right (%)",
        "C. Usual walk; bar = median",
    )
    fig.tight_layout()
    fig.savefig(fig_dir / "figure1_events_and_variability.png", dpi=200)
    fig.savefig(fig_dir / "figure1_events_and_variability.pdf")

    def row(col: str) -> pd.Series:
        return by_group.set_index("feature").loc[col]

    cv_row, asym_row = row("stride_time_cv_pct"), row("swing_time_asymmetry_pct")
    co, pd_ = cv["Control"], cv["PD"]
    aco, apd = asym["Control"], asym["PD"]
    lines = [
        f"Usual-walk records: {len(feats)} ({(feats['group'] == 'PD').sum()} PD, {(feats['group'] == 'Control').sum()} control)",
        f"Records with fewer than 3 kept strides on a foot (features NaN): {int(feats['stride_time_cv_pct'].isna().sum())}",
        f"Strides removed as outliers, total: {int(feats['n_strides_removed'].sum())} of {int((feats['n_strides_left'] + feats['n_strides_right'] + feats['n_strides_removed']).sum())}",
        f"Stride-time CV, median (IQR): control {co.median():.2f} ({co.quantile(0.25):.2f}–{co.quantile(0.75):.2f}) %, PD {pd_.median():.2f} ({pd_.quantile(0.25):.2f}–{pd_.quantile(0.75):.2f}) %; AUC {cv_row['auc_pd_higher']:.2f}, Mann-Whitney p = {cv_row['p_mann_whitney']:.2g}",
        f"Swing-time asymmetry, median (IQR): control {aco.median():.2f} ({aco.quantile(0.25):.2f}–{aco.quantile(0.75):.2f}) %, PD {apd.median():.2f} ({apd.quantile(0.25):.2f}–{apd.quantile(0.75):.2f}) %; AUC {asym_row['auc_pd_higher']:.2f}, Mann-Whitney p = {asym_row['p_mann_whitney']:.2g}",
        f"Stride time, mean (SD): control {feats.loc[feats.group == 'Control', 'stride_time_mean_s'].mean():.3f} ({feats.loc[feats.group == 'Control', 'stride_time_mean_s'].std():.3f}) s, PD {feats.loc[feats.group == 'PD', 'stride_time_mean_s'].mean():.3f} ({feats.loc[feats.group == 'PD', 'stride_time_mean_s'].std():.3f}) s",
        f"Swing %, mean (SD): control {feats.loc[feats.group == 'Control', 'swing_pct_mean'].mean():.1f} ({feats.loc[feats.group == 'Control', 'swing_pct_mean'].std():.1f}), PD {feats.loc[feats.group == 'PD', 'swing_pct_mean'].mean():.1f} ({feats.loc[feats.group == 'PD', 'swing_pct_mean'].std():.1f})",
        f"Example record in panel A: {parse_record_name(ex_path).record}",
        "",
        "All features, usual walk, one row per participant (AUC > 0.5 means higher in PD):",
        by_group.to_string(index=False, float_format=lambda v: f"{v:.3g}"),
    ]
    (out / "figure1_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
