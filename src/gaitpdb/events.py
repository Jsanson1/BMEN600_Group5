"""Gait events and stride timing from the per-foot total vertical force.

The database gives, for each foot, the total vertical ground reaction force
at 100 Hz. A foot is on the ground while that force is above a threshold and
in the air (swing) while it is below. From the on/off transitions we get

* heel strike (HS): force rises above the threshold;
* toe off (TO): force falls below the threshold;
* stride time: HS to the next HS of the same foot;
* stance time: HS to the following TO; swing time: TO to the following HS.

The threshold is a documented choice, not a property of the data. We use
20 N by default (about 2% of body weight for a 100 kg person), with a
minimum contact and swing duration of 0.1 s so that single-sample glitches
at the threshold do not create spurious strides.

A stride is kept for the features only if it lasts 0.5 to 2.5 s, its swing
phase is 10 to 70% of the stride, and it is within 0.7 to 1.3 times the median
stride of that foot in that record. The last rule removes the slow strides at
turns and stops, and the occasional double-length stride that appears when the
foot never unloads below the threshold between two steps (a foot drag or a
slide): one such stride in a hundred roughly doubles the stride-time CV.
``stride_table`` flags removed strides rather than dropping them, so the rules
can be audited.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .io import SAMPLE_RATE_HZ

DEFAULT_THRESHOLD_N = 20.0
MIN_PHASE_S = 0.10  # shortest stance or swing we accept as real
STRIDE_LIMITS_S = (0.5, 2.5)  # strides outside this range are turns, stops or errors
STRIDE_RATIO_LIMITS = (0.7, 1.3)  # relative to the foot's median stride in the record


def contact_events(force: np.ndarray, threshold_n: float = DEFAULT_THRESHOLD_N):
    """Return (heel_strike_idx, toe_off_idx) sample indexes for one foot.

    Contact phases shorter than MIN_PHASE_S are merged into the surrounding
    swing, and swing phases shorter than MIN_PHASE_S into the surrounding
    stance, in that order.
    """
    on = np.asarray(force) > threshold_n
    min_len = int(round(MIN_PHASE_S * SAMPLE_RATE_HZ))
    on = _remove_short_runs(on, True, min_len)
    on = _remove_short_runs(on, False, min_len)
    d = np.diff(on.astype(np.int8))
    heel_strikes = np.flatnonzero(d == 1) + 1
    toe_offs = np.flatnonzero(d == -1) + 1
    return heel_strikes, toe_offs


def _remove_short_runs(mask: np.ndarray, value: bool, min_len: int) -> np.ndarray:
    """Flip runs of ``value`` shorter than ``min_len`` samples, except at the edges."""
    mask = mask.copy()
    n = len(mask)
    i = 0
    while i < n:
        if mask[i] == value:
            j = i
            while j < n and mask[j] == value:
                j += 1
            if (j - i) < min_len and i > 0 and j < n:
                mask[i:j] = not value
            i = j
        else:
            i += 1
    return mask


def stride_table(
    force: np.ndarray, threshold_n: float = DEFAULT_THRESHOLD_N
) -> pd.DataFrame:
    """One row per complete stride (HS, TO, next HS) for one foot.

    Columns: hs_s, to_s, next_hs_s, stride_s, stance_s, swing_s, swing_pct,
    and ``kept`` (False for strides outside STRIDE_LIMITS_S, with a swing
    fraction outside 10-70%, or outside STRIDE_RATIO_LIMITS times the median
    of the strides that passed the first two rules; these are turns, pauses
    and detection errors).
    """
    hs, to = contact_events(force, threshold_n)
    rows = []
    for k in range(len(hs) - 1):
        a, b = hs[k], hs[k + 1]
        tos = to[(to > a) & (to < b)]
        if len(tos) != 1:
            continue
        t = tos[0]
        stride = (b - a) / SAMPLE_RATE_HZ
        stance = (t - a) / SAMPLE_RATE_HZ
        swing = (b - t) / SAMPLE_RATE_HZ
        rows.append(
            {
                "hs_s": a / SAMPLE_RATE_HZ,
                "to_s": t / SAMPLE_RATE_HZ,
                "next_hs_s": b / SAMPLE_RATE_HZ,
                "stride_s": stride,
                "stance_s": stance,
                "swing_s": swing,
                "swing_pct": 100.0 * swing / stride,
            }
        )
    df = pd.DataFrame(rows)
    if df.empty:
        df["kept"] = pd.Series(dtype=bool)
        return df
    lo, hi = STRIDE_LIMITS_S
    plausible = df["stride_s"].between(lo, hi) & df["swing_pct"].between(10, 70)
    median = df.loc[plausible, "stride_s"].median()
    r_lo, r_hi = STRIDE_RATIO_LIMITS
    df["kept"] = plausible & df["stride_s"].between(r_lo * median, r_hi * median)
    return df
