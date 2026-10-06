"""Does our pipeline reproduce the published dual-task effect?

The Ga sub-study recorded a usual walk (walk 01) and a walk while counting
backwards by sevens (walk 10). Its source paper reported that stride-to-stride
variability rose under the dual task in the PD group (sources.md, S4). This
script recomputes our features on both walks for every participant who has
both and compares them within participant (Wilcoxon signed-rank test), per
group. Agreement with the published finding is evidence that the event
detection and features behave; the database holds only a few of the control
dual-task walks, so the control comparison is weak.

Writes results/dual_task_check.txt and results/dual_task_features.csv.

    python scripts/check_dual_task.py [--data data/raw/gaitpdb]
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
    build_manifest,
    find_data_dir,
    load_record,
    record_features,
)

FEATURES = [
    "stride_time_cv_pct",
    "swing_time_cv_pct",
    "swing_time_asymmetry_pct",
    "stride_time_mean_s",
    "cadence_strides_per_min",
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir = find_data_dir(args.data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifest = build_manifest(data_dir)
    ga = manifest[(manifest["study"] == "Ga") & (manifest["walk"].isin([1, 10]))]
    rows = []
    for _, r in ga.iterrows():
        ft = record_features(load_record(r["path"]))
        ft.update(participant=r["participant"], group=r["group"], walk=r["walk"])
        rows.append(ft)
    feats = pd.DataFrame(rows)
    feats.to_csv(out / "dual_task_features.csv", index=False)

    wide = feats.pivot(index=["participant", "group"], columns="walk", values=FEATURES)
    wide = wide.dropna()
    lines = [
        "Dual-task check on the Ga sub-study: usual walk (01) against the serial-7 "
        "counting walk (10), within participant (scripts/check_dual_task.py).",
        "Participants with both walks: "
        + ", ".join(
            f"{g} {int((wide.index.get_level_values('group') == g).sum())}"
            for g in ("PD", "Control")
        )
        + " (the source study had 30 PD and 28 controls; the database holds the rest of the "
        "control dual-task walks only as usual walks).",
        "",
    ]
    for feat in FEATURES:
        for group in ("PD", "Control"):
            sel = wide.index.get_level_values("group") == group
            a = wide.loc[sel, (feat, 1)]
            b = wide.loc[sel, (feat, 10)]
            n = int(sel.sum())
            p = stats.wilcoxon(a, b).pvalue if n >= 6 else np.nan
            lines.append(
                f"{feat}, {group} (n = {n}): median {a.median():.2f} on the usual walk, "
                f"{b.median():.2f} under the dual task, median within-participant change "
                f"{np.median(b.to_numpy() - a.to_numpy()):+.2f}, Wilcoxon p = "
                + (f"{p:.3g}" if np.isfinite(p) else "n/a (too few)")
            )
        lines.append("")
    text = "\n".join(lines) + "\n"
    (out / "dual_task_check.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
