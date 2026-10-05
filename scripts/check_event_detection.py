"""Two checks on the gait-event detection, quoted in the Preliminary Results.

1. Threshold sensitivity: features recomputed with contact thresholds of 10 and
   50 N instead of the default 20 N, on every usual-walk record.
2. The relative stride rule: stride-time variability (CV) computed from all
   strides that pass the absolute limits (0.5 to 2.5 s, swing 10 to 70%),
   against the CV from the strides that also pass the relative rule (0.7 to
   1.3 times the record's median stride), and whether the group difference
   changes.

Writes results/event_detection_checks.txt.

    python scripts/check_event_detection.py [--data data/raw/gaitpdb]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import (  # noqa: E402
    DEFAULT_THRESHOLD_N,
    build_manifest,
    find_data_dir,
    load_record,
    record_features,
    stride_table,
)
from gaitpdb.events import STRIDE_LIMITS_S, STRIDE_RATIO_LIMITS  # noqa: E402

THRESHOLDS_N = (10.0, DEFAULT_THRESHOLD_N, 50.0)
COMPARED = ("stride_time_mean_s", "stride_time_cv_pct", "swing_time_asymmetry_pct")


def untrimmed_cv(df: pd.DataFrame) -> tuple[float, int, int]:
    """Mean of the two feet's stride-time CV using only the absolute limits.

    Returns (cv_pct, strides the relative rule removes, strides before it).
    """
    lo, hi = STRIDE_LIMITS_S
    cvs, dropped, total = [], 0, 0
    for col in ("L_total", "R_total"):
        st = stride_table(df[col].to_numpy())
        plausible = st["stride_s"].between(lo, hi) & st["swing_pct"].between(10, 70)
        s = st.loc[plausible, "stride_s"].to_numpy()
        if len(s) < 3:
            return np.nan, dropped, total
        dropped += int((plausible & ~st["kept"]).sum())
        total += len(s)
        cvs.append(100.0 * s.std(ddof=1) / s.mean())
    return float(np.mean(cvs)), dropped, total


def auc_and_p(feats: pd.DataFrame, col: str) -> tuple[float, float]:
    pd_ = feats.loc[feats["group"] == "PD", col].dropna()
    co = feats.loc[feats["group"] == "Control", col].dropna()
    u = stats.mannwhitneyu(pd_, co, alternative="two-sided")
    return u.statistic / (len(pd_) * len(co)), u.pvalue


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir = find_data_dir(args.data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(data_dir)
    usual = manifest[manifest["walk"] == 1]
    per_threshold = {t: [] for t in THRESHOLDS_N}
    trimmed = []
    for _, r in usual.iterrows():
        df = load_record(r["path"])
        for t in THRESHOLDS_N:
            ft = record_features(df, threshold_n=t)
            ft.update(record=r["record"], group=r["group"])
            per_threshold[t].append(ft)
        cv, dropped, total = untrimmed_cv(df)
        trimmed.append(
            {
                "record": r["record"],
                "group": r["group"],
                "stride_time_cv_absolute_rules_pct": cv,
                "dropped": dropped,
                "total": total,
            }
        )
    frames = {
        t: pd.DataFrame(rows).set_index("record") for t, rows in per_threshold.items()
    }
    base = frames[DEFAULT_THRESHOLD_N]
    trimmed = pd.DataFrame(trimmed).set_index("record")

    lines = [f"Usual-walk records: {len(base)}", ""]
    lines.append(
        f"1. Contact threshold sensitivity (reference {DEFAULT_THRESHOLD_N:g} N). "
        "Median absolute change per record, and the group comparison at each threshold:"
    )
    for t in THRESHOLDS_N:
        f = frames[t]
        parts = []
        for col in COMPARED:
            diff = (f[col] - base[col]).abs().median()
            auc, p = auc_and_p(f.reset_index(), col)
            parts.append(f"{col}: median |change| {diff:.3g}, AUC {auc:.2f}, p {p:.2g}")
        lines.append(f"  {t:g} N: " + "; ".join(parts))
    lines.append("")
    lines.append(
        f"2. Stride-time CV from strides passing the absolute limits only "
        f"({STRIDE_LIMITS_S[0]:g} to {STRIDE_LIMITS_S[1]:g} s, swing 10 to 70%) "
        f"-> after the relative rule ({STRIDE_RATIO_LIMITS[0]:g} to "
        f"{STRIDE_RATIO_LIMITS[1]:g} x the record median), one value per "
        "participant, mean of the two feet:"
    )
    both = base.join(trimmed, rsuffix="_t")
    for group in ("Control", "PD"):
        g = both[both["group"] == group]
        lines.append(
            f"  {group}: CV median {g['stride_time_cv_absolute_rules_pct'].median():.2f} % -> "
            f"{g['stride_time_cv_pct'].median():.2f} %; strides removed by the relative rule "
            f"{int(g['dropped'].sum())} of {int(g['total'].sum())} "
            f"(mean {g['dropped'].mean():.2f} per record)"
        )
    for col, label in (
        ("stride_time_cv_absolute_rules_pct", "absolute limits only"),
        ("stride_time_cv_pct", "with the relative rule"),
    ):
        auc, p = auc_and_p(both.reset_index(), col)
        lines.append(f"  {label}: AUC {auc:.2f}, Mann-Whitney p {p:.2g}")
    text = "\n".join(lines) + "\n"
    (out / "event_detection_checks.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
