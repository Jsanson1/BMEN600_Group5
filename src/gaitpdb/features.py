"""Per-record spatiotemporal features from the stride tables of both feet.

Every feature except cadence is computed from kept strides only (see
events.stride_table); cadence counts every complete left-foot stride.
Variability is the coefficient of variation, 100 * SD / mean, the measure
used by the studies that produced this database. Asymmetry is
100 * |left - right| / mean(left, right) of the per-foot mean, which is the
"swing asymmetry" used in those studies when applied to swing time.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .events import DEFAULT_THRESHOLD_N, STRIDE_RATIO_LIMITS, stride_table

FEATURE_COLUMNS = [
    "n_strides_left",
    "n_strides_right",
    "n_strides_removed",
    "stride_time_mean_s",
    "stride_time_cv_pct",
    "swing_time_mean_s",
    "swing_time_cv_pct",
    "stance_time_mean_s",
    "swing_pct_mean",
    "cadence_strides_per_min",
    "stride_time_asymmetry_pct",
    "swing_time_asymmetry_pct",
]


def _cv(x: pd.Series) -> float:
    return float(100.0 * x.std(ddof=1) / x.mean()) if len(x) > 2 else np.nan


def _asym(left: float, right: float) -> float:
    return float(100.0 * abs(left - right) / np.mean([left, right]))


def record_features(
    df: pd.DataFrame,
    threshold_n: float = DEFAULT_THRESHOLD_N,
    ratio_limits: tuple[float, float] | None = STRIDE_RATIO_LIMITS,
) -> dict:
    """Spatiotemporal features for one loaded record (output of io.load_record)."""
    left = stride_table(df["L_total"].to_numpy(), threshold_n, ratio_limits)
    right = stride_table(df["R_total"].to_numpy(), threshold_n, ratio_limits)
    kl = left[left["kept"]] if not left.empty else left
    kr = right[right["kept"]] if not right.empty else right
    both = pd.concat([kl, kr], ignore_index=True)
    removed = (
        int((~left["kept"]).sum() + (~right["kept"]).sum()) if not both.empty else 0
    )
    if len(kl) < 3 or len(kr) < 3:
        out = {c: np.nan for c in FEATURE_COLUMNS}
        out.update(
            n_strides_left=len(kl), n_strides_right=len(kr), n_strides_removed=removed
        )
        return out
    duration_min = (df["time_s"].iloc[-1] - df["time_s"].iloc[0]) / 60.0
    return {
        "n_strides_left": int(len(kl)),
        "n_strides_right": int(len(kr)),
        "n_strides_removed": removed,
        "stride_time_mean_s": float(both["stride_s"].mean()),
        "stride_time_cv_pct": float(
            np.mean([_cv(kl["stride_s"]), _cv(kr["stride_s"])])
        ),
        "swing_time_mean_s": float(both["swing_s"].mean()),
        "swing_time_cv_pct": float(np.mean([_cv(kl["swing_s"]), _cv(kr["swing_s"])])),
        "stance_time_mean_s": float(both["stance_s"].mean()),
        "swing_pct_mean": float(both["swing_pct"].mean()),
        "cadence_strides_per_min": float(len(left) / duration_min),
        "stride_time_asymmetry_pct": _asym(
            kl["stride_s"].mean(), kr["stride_s"].mean()
        ),
        "swing_time_asymmetry_pct": _asym(kl["swing_s"].mean(), kr["swing_s"].mean()),
    }
