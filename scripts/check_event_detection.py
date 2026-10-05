"""Robustness checks on the gait-event detection, quoted in the Preliminary Results.

For every usual-walk record, the features are recomputed with contact thresholds
of 10, 20 (default) and 50 N, each with and without the relative stride rule
(strides outside 0.7 to 1.3 times the record's median stride are dropped). For
each setting the script reports, per group, the median stride-time CV and
swing-time asymmetry, the AUC and Mann-Whitney p of the group comparison, and
the median absolute change of each feature relative to the default setting.

Writes results/event_detection_checks.csv (one row per setting) and
results/event_detection_checks.txt (the same, readable).

    python scripts/check_event_detection.py [--data data/raw/gaitpdb]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import (  # noqa: E402
    DEFAULT_THRESHOLD_N,
    build_manifest,
    find_data_dir,
    load_record,
    record_features,
)
from gaitpdb.events import STRIDE_RATIO_LIMITS  # noqa: E402

THRESHOLDS_N = (10.0, DEFAULT_THRESHOLD_N, 50.0)
COMPARED = ("stride_time_mean_s", "stride_time_cv_pct", "swing_time_asymmetry_pct")


def auc_and_p(feats: pd.DataFrame, col: str) -> tuple[float, float]:
    """AUC = P(PD value > control value), from the Mann-Whitney U, and its p."""
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
    settings = [(t, rule) for t in THRESHOLDS_N for rule in (False, True)]
    frames: dict[tuple[float, bool], list[dict]] = {s: [] for s in settings}
    for _, r in usual.iterrows():
        df = load_record(r["path"])
        for t, rule in settings:
            ft = record_features(
                df, threshold_n=t, ratio_limits=STRIDE_RATIO_LIMITS if rule else None
            )
            ft.update(record=r["record"], group=r["group"])
            frames[(t, rule)].append(ft)
    tables = {s: pd.DataFrame(rows).set_index("record") for s, rows in frames.items()}
    base = tables[(DEFAULT_THRESHOLD_N, True)]

    rows = []
    for (t, rule), f in tables.items():
        row = {
            "threshold_n": t,
            "relative_stride_rule": rule,
            "records": len(f),
            "strides_removed": int(f["n_strides_removed"].sum()),
        }
        for col in COMPARED:
            auc, p = auc_and_p(f.reset_index(), col)
            row[f"{col}: control median"] = f.loc[f["group"] == "Control", col].median()
            row[f"{col}: PD median"] = f.loc[f["group"] == "PD", col].median()
            row[f"{col}: AUC"] = auc
            row[f"{col}: p"] = p
            row[f"{col}: median |change| vs default"] = (
                (f[col] - base[col]).abs().median()
            )
        rows.append(row)
    table = pd.DataFrame(rows)
    table.to_csv(out / "event_detection_checks.csv", index=False)

    lines = [
        f"Usual-walk records: {len(base)}. Default setting: {DEFAULT_THRESHOLD_N:g} N with "
        f"the relative stride rule ({STRIDE_RATIO_LIMITS[0]:g} to {STRIDE_RATIO_LIMITS[1]:g} x "
        "the record median). AUC = probability that a PD participant has the higher value; "
        "p from a two-sided Mann-Whitney test; |change| is per record, against the default.",
        "",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"{row['threshold_n']:g} N, relative rule {'on ' if row['relative_stride_rule'] else 'off'}: "
            f"{row['strides_removed']} strides removed"
        )
        for col in COMPARED:
            lines.append(
                f"    {col}: control {row[f'{col}: control median']:.3g}, "
                f"PD {row[f'{col}: PD median']:.3g}, AUC {row[f'{col}: AUC']:.2f}, "
                f"p {row[f'{col}: p']:.2g}, median |change| {row[f'{col}: median |change| vs default']:.3g}"
            )
    text = "\n".join(lines) + "\n"
    (out / "event_detection_checks.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
