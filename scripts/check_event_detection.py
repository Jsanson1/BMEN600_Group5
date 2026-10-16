"""Robustness checks on the gait-event detection, quoted in the Preliminary Results.

For the usual walk of every analysed participant (aged 50 or over,
gaitpdb.cohort, DECISIONS.md D-006), the features are recomputed with contact thresholds
of 10, 20 (default) and 50 N, each with and without the relative stride rule
(strides outside 0.7 to 1.3 times the record's median stride are dropped). For
each setting the script reports, per group, the median stride-time CV and
swing-time asymmetry, the AUC and Mann-Whitney p of the group comparison, and
the median absolute change of each feature relative to the default setting.

Two kinds of relative threshold follow, with the stride rule on, because the
fixed threshold has to be compared with them on WearGait-PD's different insoles
(Methods): a share of the participant's body weight (2.5% and 5%; weight from
demographics.txt, so participants without a recorded weight are left out of these
rows, and the default is repeated on the same participants for comparison), and a
share of the recording's own force level (2.5% and 5% of the mean over the two feet
of the 95th percentile of each foot's total force). Last, the script reports what
20 N is as a share of body weight, and the 95th percentile of each foot's force as a
multiple of body weight, across the participants with a recorded weight.

Writes results/event_detection_checks.csv (one row per setting) and
results/event_detection_checks.txt (the same, readable).

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
    MIN_AGE_YEARS,
    cohort_manifest,
    find_data_dir,
    load_demographics,
    load_record,
    record_features,
)
from gaitpdb.events import STRIDE_RATIO_LIMITS  # noqa: E402

THRESHOLDS_N = (10.0, DEFAULT_THRESHOLD_N, 50.0)
BODY_WEIGHT_SHARES = (0.025, 0.05)
FORCE_LEVEL_SHARES = (0.025, 0.05)
FORCE_LEVEL_PERCENTILE = 95
G = 9.81  # m/s^2, to turn kg into N
COMPARED = ("stride_time_mean_s", "stride_time_cv_pct", "swing_time_asymmetry_pct")
DEFAULT = ("fixed", DEFAULT_THRESHOLD_N, True)


def auc_and_p(feats: pd.DataFrame, col: str) -> tuple[float, float]:
    """AUC = P(PD value > control value), from the Mann-Whitney U, and its p."""
    pd_ = feats.loc[feats["group"] == "PD", col].dropna()
    co = feats.loc[feats["group"] == "Control", col].dropna()
    u = stats.mannwhitneyu(pd_, co, alternative="two-sided")
    return u.statistic / (len(pd_) * len(co)), u.pvalue


def label(kind: str, value: float) -> str:
    if kind == "fixed":
        return f"{value:g} N"
    if kind == "body weight":
        return f"{100 * value:g}% of body weight"
    if kind == "force level":
        return f"{100 * value:g}% of the recording's force level"
    return f"{value:g} N, participants with a recorded weight only"


def force_level(df: pd.DataFrame) -> float:
    """Mean over the two feet of the 95th percentile of each foot's total force (N)."""
    return float(
        np.mean(
            [
                np.percentile(df[c], FORCE_LEVEL_PERCENTILE)
                for c in ("L_total", "R_total")
            ]
        )
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir = find_data_dir(args.data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifest = cohort_manifest(data_dir)
    usual = manifest[manifest["walk"] == 1]
    weight_kg = load_demographics(data_dir).set_index("ID")["Weight"]

    # (kind, value, relative stride rule on)
    settings = [("fixed", t, rule) for t in THRESHOLDS_N for rule in (False, True)]
    settings += [("body weight", s, True) for s in BODY_WEIGHT_SHARES]
    settings += [("weighed", DEFAULT_THRESHOLD_N, True)]
    settings += [("force level", s, True) for s in FORCE_LEVEL_SHARES]
    frames: dict[tuple[str, float, bool], list[dict]] = {s: [] for s in settings}
    share_of_weight, level_over_weight = [], []
    for _, r in usual.iterrows():
        df = load_record(r["path"])
        w = weight_kg.get(r["participant"], np.nan)
        level = force_level(df)
        if pd.notna(w):
            share_of_weight.append(100 * DEFAULT_THRESHOLD_N / (w * G))
            level_over_weight.append(level / (w * G))
        for kind, value, rule in settings:
            if kind in ("body weight", "weighed") and pd.isna(w):
                continue
            t = {
                "fixed": value,
                "weighed": value,
                "body weight": value * (w * G) if pd.notna(w) else np.nan,
                "force level": value * level,
            }[kind]
            ft = record_features(
                df, threshold_n=t, ratio_limits=STRIDE_RATIO_LIMITS if rule else None
            )
            ft.update(record=r["record"], group=r["group"], threshold_used_n=t)
            frames[(kind, value, rule)].append(ft)
    tables = {s: pd.DataFrame(rows).set_index("record") for s, rows in frames.items()}
    base = tables[DEFAULT]

    rows = []
    for (kind, value, rule), f in tables.items():
        row = {
            "kind": kind,
            "threshold": label(kind, value),
            "threshold_n": value if kind in ("fixed", "weighed") else np.nan,
            "threshold_used_n_median": f["threshold_used_n"].median(),
            "threshold_used_n_min": f["threshold_used_n"].min(),
            "threshold_used_n_max": f["threshold_used_n"].max(),
            "relative_stride_rule": rule,
            "records": len(f),
            "strides_removed": int(f["n_strides_removed"].sum()),
        }
        common = f.index.intersection(base.index)
        for col in COMPARED:
            auc, p = auc_and_p(f.reset_index(), col)
            row[f"{col}: control median"] = f.loc[f["group"] == "Control", col].median()
            row[f"{col}: PD median"] = f.loc[f["group"] == "PD", col].median()
            row[f"{col}: AUC"] = auc
            row[f"{col}: p"] = p
            row[f"{col}: median |change| vs default"] = (
                (f.loc[common, col] - base.loc[common, col]).abs().median()
            )
        rows.append(row)
    table = pd.DataFrame(rows)
    table.to_csv(out / "event_detection_checks.csv", index=False)

    lines = [
        f"Usual-walk records of the analysed participants (aged {MIN_AGE_YEARS} or over, "
        f"DECISIONS.md D-006): {len(base)}. Default setting: {DEFAULT_THRESHOLD_N:g} N with "
        f"the relative stride rule ({STRIDE_RATIO_LIMITS[0]:g} to {STRIDE_RATIO_LIMITS[1]:g} x "
        "the record median). AUC = probability that a PD participant has the higher value; "
        "p from a two-sided Mann-Whitney test; |change| is per record, against the default.",
        "",
    ]
    for _, row in table.iterrows():
        head = (
            f"{row['threshold']}, relative rule {'on ' if row['relative_stride_rule'] else 'off'}: "
            f"{row['strides_removed']} strides removed"
        )
        if row["kind"] == "weighed":
            head += f" ({row['records']} records)"
        elif row["kind"] != "fixed":
            head += (
                f" ({row['records']} records; threshold median {row['threshold_used_n_median']:.0f} N, "
                f"range {row['threshold_used_n_min']:.0f} to {row['threshold_used_n_max']:.0f} N)"
            )
        lines.append(head)
        for col in COMPARED:
            lines.append(
                f"    {col}: control {row[f'{col}: control median']:.3g}, "
                f"PD {row[f'{col}: PD median']:.3g}, AUC {row[f'{col}: AUC']:.2f}, "
                f"p {row[f'{col}: p']:.2g}, median |change| {row[f'{col}: median |change| vs default']:.3g}"
            )
    sw, lw = np.array(share_of_weight), np.array(level_over_weight)
    lines += [
        "",
        f"Participants with a recorded weight: {len(sw)} of {len(base)}.",
        f"{DEFAULT_THRESHOLD_N:g} N as a share of body weight: median {np.median(sw):.1f}%, "
        f"range {sw.min():.1f} to {sw.max():.1f}%.",
        f"Force level ({FORCE_LEVEL_PERCENTILE}th percentile of each foot's total force, mean "
        f"of the two feet) as a multiple of body weight: median {np.median(lw):.2f}, "
        f"interquartile range {np.percentile(lw, 25):.2f} to {np.percentile(lw, 75):.2f}, "
        f"range {lw.min():.2f} to {lw.max():.2f}.",
    ]
    text = "\n".join(lines) + "\n"
    (out / "event_detection_checks.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
