"""Data-quality report on the PhysioNet gaitpdb records, for Section 3 of the midterm.

What it checks, record by record and for the demographics file:

* inventory: recordings per study, group and walk number, and which walk
  numbers the database documents (format.txt defines 01 and 10 only);
* recording lengths, and recordings shorter than 60 s;
* force signals: samples with both feet unloaded (pauses or gaps), the longest
  such run, negative sensor values, sensors that never register force, whether
  the per-foot total equals the sum of its eight sensors, and the peak force
  relative to body weight where weight is known;
* strides: how many strides the default rules keep and remove per record;
* demographics: missing values by column and group, participants without a
  recording, and the mean ages against the PhysioNet description;
* balance: participants and recordings per group and study, recordings per
  participant (the leakage risk for any split by recording).

Writes results/data_quality.txt (the report) and results/data_quality_records.csv
(one row per recording).

    python scripts/check_data_quality.py [--data data/raw/gaitpdb]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import (  # noqa: E402
    DEFAULT_THRESHOLD_N,
    build_manifest,
    find_data_dir,
    load_demographics,
    load_record,
    stride_table,
)

DOCUMENTED_WALKS = {1: "usual walk", 10: "dual task (serial-7 subtraction), Ga study"}
SHORT_RECORD_S = 60.0
PHYSIONET_PAGE_MEAN_AGE = {
    "PD": 66.3,
    "Control": 66.3,
}  # as stated on the PhysioNet page
G = 9.81


def longest_run(mask: np.ndarray) -> int:
    best = cur = 0
    for m in mask:
        cur = cur + 1 if m else 0
        best = max(best, cur)
    return best


def record_checks(path: str) -> dict:
    df = load_record(path)
    left = df["L_total"].to_numpy()
    right = df["R_total"].to_numpy()
    sensors = df.iloc[:, 1:17].to_numpy()
    both_off = (left <= DEFAULT_THRESHOLD_N) & (right <= DEFAULT_THRESHOLD_N)
    out = {
        "duration_s": float(df["time_s"].iloc[-1] - df["time_s"].iloc[0]),
        "both_feet_unloaded_pct": 100.0 * float(both_off.mean()),
        "longest_unloaded_s": longest_run(both_off) / 100.0,
        "negative_samples": int((sensors < 0).sum()),
        "silent_sensors": int((sensors.max(axis=0) <= 0).sum()),
        "total_minus_sum_max_n": float(
            max(
                np.abs(df.iloc[:, 1:9].sum(axis=1) - left).max(),
                np.abs(df.iloc[:, 9:17].sum(axis=1) - right).max(),
            )
        ),
        "peak_force_n": float(max(left.max(), right.max())),
    }
    kept = removed = 0
    for col in ("L_total", "R_total"):
        st = stride_table(df[col].to_numpy())
        kept += int(st["kept"].sum()) if not st.empty else 0
        removed += int((~st["kept"]).sum()) if not st.empty else 0
    out["strides_kept"] = kept
    out["strides_removed"] = removed
    out["strides_removed_pct"] = 100.0 * removed / max(kept + removed, 1)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir = find_data_dir(args.data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(data_dir)
    demo = load_demographics(data_dir)
    checks = pd.DataFrame([record_checks(p) for p in manifest["path"]])
    rec = pd.concat(
        [manifest.drop(columns=["path", "n_samples", "duration_s"]), checks], axis=1
    )
    rec = rec.merge(
        demo[["ID", "Weight"]], left_on="participant", right_on="ID", how="left"
    )
    rec = rec.drop(columns="ID")
    rec["peak_force_per_body_weight"] = rec["peak_force_n"] / (rec["Weight"] * G)
    rec.to_csv(out / "data_quality_records.csv", index=False)

    L = []
    L.append(
        f"Data-quality report on {len(rec)} recordings from {rec['participant'].nunique()} "
        f"participants (scripts/check_data_quality.py)."
    )
    L.append("")
    L.append("1. Inventory: recordings by study, group and walk number")
    inv = rec.pivot_table(
        index=["study", "group"],
        columns="walk",
        values="record",
        aggfunc="count",
        fill_value=0,
    )
    L.append(inv.to_string())
    undocumented = sorted(set(rec["walk"]) - set(DOCUMENTED_WALKS))
    n_undoc = int(rec["walk"].isin(undocumented).sum())
    L.append(
        f"format.txt documents walk 01 ({DOCUMENTED_WALKS[1]}) and walk 10 "
        f"({DOCUMENTED_WALKS[10]}) only. Walk numbers {undocumented} ({n_undoc} recordings: "
        f"{int(((rec.study == 'Ga') & rec.walk.isin(undocumented)).sum())} in Ga, "
        f"{int(((rec.study == 'Ju') & rec.walk.isin(undocumented)).sum())} in Ju) have no "
        "documented condition; the Ju ones belong to the cueing protocol of its source paper and "
        "the Ga walk 02 is unexplained. The preliminary results use walk 01 only."
    )
    L.append("")
    L.append("2. Recording length (s) by study")
    L.append(
        rec.groupby("study")["duration_s"]
        .describe()[["count", "min", "50%", "max"]]
        .round(1)
        .to_string()
    )
    short = rec[rec["duration_s"] < SHORT_RECORD_S]
    L.append(
        f"Recordings shorter than {SHORT_RECORD_S:g} s: {len(short)} "
        f"({', '.join(f'{r.record} {r.duration_s:.0f} s' for r in short.itertuples()) or 'none'})."
    )
    L.append("")
    L.append("3. Force signals")
    L.append(
        f"Both feet unloaded (both totals at or below {DEFAULT_THRESHOLD_N:g} N, i.e. a pause or a gap): "
        f"median {rec['both_feet_unloaded_pct'].median():.2f}% of samples, maximum "
        f"{rec['both_feet_unloaded_pct'].max():.2f}% ({rec.loc[rec['both_feet_unloaded_pct'].idxmax(), 'record']}); "
        f"longest such run {rec['longest_unloaded_s'].max():.2f} s. Recordings with a run over 2 s: "
        f"{int((rec['longest_unloaded_s'] > 2).sum())}."
    )
    L.append(
        f"Negative sensor values: {int(rec['negative_samples'].sum())} samples in "
        f"{int((rec['negative_samples'] > 0).sum())} recordings. Sensors that never register force: "
        f"{int((rec['silent_sensors'] > 0).sum())} recordings. Largest difference between a per-foot "
        f"total and the sum of its eight sensors: {rec['total_minus_sum_max_n'].max():.3f} N."
    )
    pf = rec.dropna(subset=["peak_force_per_body_weight"])
    L.append(
        f"Peak force per body weight (weight known for {pf['participant'].nunique()} participants): "
        f"median {pf['peak_force_per_body_weight'].median():.2f}, range "
        f"{pf['peak_force_per_body_weight'].min():.2f} to {pf['peak_force_per_body_weight'].max():.2f}; "
        f"outside 0.8 to 2.0: {int(((pf['peak_force_per_body_weight'] < 0.8) | (pf['peak_force_per_body_weight'] > 2.0)).sum())} "
        f"recordings ({', '.join(pf.loc[(pf['peak_force_per_body_weight'] < 0.8) | (pf['peak_force_per_body_weight'] > 2.0), 'record']) or 'none'})."
    )
    L.append("")
    L.append(
        "4. Strides under the default rules (20 N, 0.5 to 2.5 s, swing 10 to 70%, 0.7 to 1.3 x median)"
    )
    L.append(
        f"Kept per recording: median {rec['strides_kept'].median():.0f} (min {rec['strides_kept'].min()}, "
        f"max {rec['strides_kept'].max()}); removed: median {rec['strides_removed_pct'].median():.1f}% of strides, "
        f"maximum {rec['strides_removed_pct'].max():.1f}% ({rec.loc[rec['strides_removed_pct'].idxmax(), 'record']}). "
        f"Recordings with fewer than 20 kept strides: {int((rec['strides_kept'] < 20).sum())} "
        f"({', '.join(rec.loc[rec['strides_kept'] < 20, 'record']) or 'none'})."
    )
    worst = rec.sort_values("strides_removed_pct", ascending=False).head(5)
    L.append(
        "Most strides removed: "
        + "; ".join(
            f"{r.record} {r.strides_removed_pct:.1f}% ({r.strides_removed} of {r.strides_kept + r.strides_removed})"
            for r in worst.itertuples()
        )
        + "."
    )
    L.append("")
    L.append("5. Demographics")
    cols = ["Height", "Weight", "HoehnYahr", "UPDRS", "UPDRSM", "TUAG", "Speed_01"]
    miss = demo[cols].isna().groupby(demo["group"]).sum()
    miss["participants"] = demo.groupby("group").size()
    L.append("Missing values by group (count of participants):")
    L.append(miss.to_string())
    no_rec = sorted(set(demo["ID"]) - set(rec["participant"]))
    L.append(
        f"Participants in demographics.txt without a recording: {no_rec or 'none'}."
    )
    ages = (
        demo.groupby("group")["Age"]
        .agg(["count", "mean", "std", "min", "max"])
        .round(1)
    )
    L.append(
        "Age by group from demographics.txt (PhysioNet page: 66.3 y for both groups):"
    )
    L.append(ages.to_string())
    for g in ("PD", "Control"):
        L.append(
            f"  {g}: file mean {ages.loc[g, 'mean']:.1f} y vs page {PHYSIONET_PAGE_MEAN_AGE[g]:.1f} y"
            + (
                ""
                if abs(ages.loc[g, "mean"] - PHYSIONET_PAGE_MEAN_AGE[g]) < 0.1
                else "  <-- differs"
            )
        )
    sex = demo.groupby("group")["sex"].value_counts().unstack(fill_value=0)
    L.append(
        "Sex by group: "
        + "; ".join(
            f"{g}: {sex.loc[g, 'M']} men, {sex.loc[g, 'F']} women"
            for g in ("PD", "Control")
        )
        + "."
    )
    L.append("")
    L.append("6. Balance and leakage")
    per = rec.groupby(["study", "group"])["participant"].nunique().unstack()
    L.append("Participants with recordings by study and group:")
    L.append(per.to_string())
    rpp = rec.groupby("participant").size()
    L.append(
        f"Recordings per participant: {int((rpp == 1).sum())} participants have 1, "
        f"{int((rpp == 2).sum())} have 2, {int((rpp == 3).sum())} have 3, {int((rpp > 3).sum())} have more (max {rpp.max()}). "
        f"{int((rpp > 1).sum())} of {len(rpp)} participants contribute more than one recording, so any split by "
        "recording puts the same person on both sides."
    )
    text = "\n".join(L) + "\n"
    (out / "data_quality.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
