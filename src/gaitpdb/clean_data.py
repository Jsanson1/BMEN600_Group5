"""Clean stride series: remove turns and implausible strides (task T-017).

Both datasets are cleaned into the same shape: one row per stride of both feet,
with the columns of ``events.stride_table`` plus

* ``foot``: "L" or "R";
* ``clean``: True if the stride is kept;
* ``reason``: why a removed stride was removed (empty for clean strides), the
  first that applies of ``missing_data``, ``not_walk``, ``turn``, ``limits``,
  ``missed_heel_strike`` and ``first_last``.

gaitpdb (``clean_gaitpdb``, DECISIONS.md D-008). The walks went up and down a
corridor of known length, so a walker turns about every corridor / speed
seconds (the expected interval). The walk's own rhythm is the Lomb-Scargle peak of both feet's stride series, searched within RHYTHM_SEARCH x the expected interval; walks too short for a rhythm (fewer than MIN_TURNS_FOR_RHYTHM expected turns) use the expected interval. Turn centres are the most disturbed strides (stride / that foot's median, either foot, at least TURN_MIN_RATIO), at least MIN_SEPARATION intervals apart and at most one per interval of walking. Every stride of both feet that overlaps TURN_WINDOW_S around a centre is removed, plus TURN_MARGIN["gaitpdb"] stride either side (D-008). A stride near twice its foot's median while the other foot is undisturbed is a heel strike the force threshold missed (two strides merged on one foot; a turn affects both feet).

WearGait-PD (``clean_weargait``, D-011): one recording of one task with its
video annotation (``GeneralEvent``). A stride is kept only if every sample is
labelled "Walk"; a stride touching a "Turn" label is a turn stride, with no
extra margin (TURN_MARGIN["weargait"], D-011); strides over missing samples are removed. Strides come from the insole total force with gaitpdb's contact
threshold, which is not yet validated for these insoles (task T-025).

In both datasets strides outside STRIDE_LIMITS_S or with a swing phase outside
SWING_PCT are removed, and the first and last stride of each foot in a
recording are trimmed (technical start and stop effects, such as a delayed
sensor start). ``meets_minimum`` applies D-011: at least MIN_STRIDES clean
strides on each foot; included participants keep all their clean strides.

The parameters come from the exploration in scripts/explore_turn_timing.py,
scripts/explore_stride_counts.py and scripts/explore_weargait_tasks.py.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import lombscargle

from .events import DEFAULT_THRESHOLD_N, STRIDE_LIMITS_S, stride_table
from .io import SAMPLE_RATE_HZ

CORRIDOR_M = {"Ga": 25.0, "Ju": 25.0, "Si": 35.0}
"""Corridor length per gaitpdb sub-study, from the sub-studies' papers."""

RHYTHM_SEARCH = (0.7, 1.5)  # x the expected interval
MIN_TURNS_FOR_RHYTHM = 2.5  # fewer expected turns: use the expected interval
MIN_SEPARATION = 0.6  # x the interval, between two turn centres
TURN_MIN_RATIO = 1.10  # a turn's most disturbed stride, x that foot's median
TURN_WINDOW_S = 2.0  # +/- s around a turn centre (fixed window)
TURN_MARGIN = {"gaitpdb": 1, "weargait": 0}  # strides either side (D-008, D-011)
AGREE_RATIO = 1.05  # the other foot is disturbed at >= 5% above its median
MISSED_HS_RATIO = (1.75, 2.25)  # x the median, one foot only
SWING_PCT = (10.0, 70.0)
MIN_STRIDES = {"gaitpdb": 40, "weargait": 10}  # clean strides per foot (D-011)

REASONS = (
    "missing_data",
    "not_walk",
    "turn",
    "limits",
    "missed_heel_strike",
    "first_last",
)


def _foot_tables(left: np.ndarray, right: np.ndarray) -> dict[str, pd.DataFrame]:
    out = {}
    for foot, force in (("L", left), ("R", right)):
        st = stride_table(np.asarray(force, float), DEFAULT_THRESHOLD_N, None)
        st = st.drop(columns="kept").reset_index(drop=True)
        st["foot"] = foot
        st["ratio"] = st["stride_s"] / st["stride_s"].median() if len(st) else []
        out[foot] = st
    return out


def _grow(mask: np.ndarray, k: int) -> np.ndarray:
    out = mask.copy()
    for i in range(1, k + 1):
        out[i:] |= mask[:-i]
        out[:-i] |= mask[i:]
    return out


def _limits(st: pd.DataFrame) -> np.ndarray:
    lo, hi = STRIDE_LIMITS_S
    ok = st["stride_s"].between(lo, hi) & st["swing_pct"].between(*SWING_PCT)
    return ~ok.to_numpy()


def _first_last(n: int) -> np.ndarray:
    out = np.zeros(n, bool)
    if n:
        out[0] = out[-1] = True
    return out


def _with_reasons(st: pd.DataFrame, flags: dict[str, np.ndarray]) -> pd.DataFrame:
    """Add ``clean`` and ``reason`` (the first flag, in REASONS order, that applies)."""
    reason = np.full(len(st), "", dtype=object)
    for name in reversed(REASONS):
        if name in flags:
            reason[flags[name]] = name
    out = st.copy()
    out["clean"] = reason == ""
    out["reason"] = reason
    return out


def expected_turn_interval(study: str, speed_m_s: float) -> float:
    """Seconds between turns: corridor length / walking speed."""
    if not speed_m_s > 0:
        raise ValueError(f"walking speed must be positive, got {speed_m_s!r}")
    return CORRIDOR_M[study] / speed_m_s


def turn_rhythm(feet: dict[str, pd.DataFrame], expected: float) -> float:
    """Lomb-Scargle peak period of both feet's stride series near ``expected``."""
    t, y = [], []
    for st in feet.values():
        s = st["stride_s"].to_numpy()
        s = np.minimum(s, np.median(s) + 1.0)  # one long turn must not dominate
        t.append(st["hs_s"].to_numpy())
        y.append(s - s.mean())
    periods = np.linspace(RHYTHM_SEARCH[0] * expected, RHYTHM_SEARCH[1] * expected, 400)
    power = lombscargle(np.concatenate(t), np.concatenate(y), 2 * np.pi / periods)
    return float(periods[power.argmax()])


def find_turns(
    feet: dict[str, pd.DataFrame], interval: float, span: float
) -> list[float]:
    """Turn centres (s): the most disturbed strides of either foot, kept apart.

    Candidates are ranked by their own ratio to the median. Stride times come in 0.01 s steps, so ratios tie; a tie goes to the candidate whose other foot is more disturbed within TURN_WINDOW_S (a turn involves both feet), then to the earlier stride.
    """
    cand = pd.concat(
        [st.assign(mid=(st["hs_s"] + st["next_hs_s"]) / 2) for st in feet.values()],
        ignore_index=True,
    )
    cand = cand[cand["ratio"] >= TURN_MIN_RATIO].copy()
    other_ratio = []
    for row in cand.itertuples(index=False):
        other = feet["R" if row.foot == "L" else "L"]
        near = other[
            (other["next_hs_s"] > row.mid - TURN_WINDOW_S)
            & (other["hs_s"] < row.mid + TURN_WINDOW_S)
        ]
        other_ratio.append(near["ratio"].max() if len(near) else 0.0)
    cand["other_ratio"] = other_ratio
    cand = cand.sort_values(
        ["ratio", "other_ratio", "hs_s"], ascending=[False, False, True], kind="stable"
    )
    max_turns = int(np.floor(span / interval))
    centres: list[float] = []
    for row in cand.itertuples(index=False):
        if len(centres) >= max_turns or row.ratio < TURN_MIN_RATIO:
            break
        if any(abs(row.mid - c) < MIN_SEPARATION * interval for c in centres):
            continue
        centres.append(float(row.mid))
    return sorted(centres)


def _turn_strides(st: pd.DataFrame, centres: list[float], margin: int) -> np.ndarray:
    hit = np.zeros(len(st), bool)
    for c in centres:
        hit |= (st["next_hs_s"] > c - TURN_WINDOW_S).to_numpy() & (
            st["hs_s"] < c + TURN_WINDOW_S
        ).to_numpy()
    return _grow(hit, margin)


def _missed_heel_strikes(feet: dict[str, pd.DataFrame], foot: str) -> np.ndarray:
    st, other = feet[foot], feet["R" if foot == "L" else "L"]
    out = np.zeros(len(st), bool)
    lo, hi = MISSED_HS_RATIO
    for i in np.flatnonzero(st["ratio"].between(lo, hi).to_numpy()):
        a, b = st["hs_s"].iloc[i], st["next_hs_s"].iloc[i]
        near = other[(other["next_hs_s"] > a) & (other["hs_s"] < b)]
        out[i] = len(near) > 0 and bool((near["ratio"] < AGREE_RATIO).all())
    return out


def clean_gaitpdb(
    record: pd.DataFrame, study: str, speed_m_s: float
) -> tuple[pd.DataFrame, dict]:
    """Clean strides of one gaitpdb walk (output of io.load_record).

    Returns the stride table of both feet (see the module docstring) and a dict with the turn centres (s), the expected and the used turn interval (s) and whether the walk's own rhythm was used. Raises ValueError without a speed.
    """
    expected = expected_turn_interval(study, speed_m_s)
    feet = _foot_tables(record["L_total"].to_numpy(), record["R_total"].to_numpy())
    span = max(st["next_hs_s"].iloc[-1] for st in feet.values()) - min(
        st["hs_s"].iloc[0] for st in feet.values()
    )
    used_rhythm = span / expected >= MIN_TURNS_FOR_RHYTHM
    interval = turn_rhythm(feet, expected) if used_rhythm else expected
    centres = find_turns(feet, interval, span)
    out = []
    for foot, st in feet.items():
        flags = {
            "turn": _turn_strides(st, centres, TURN_MARGIN["gaitpdb"]),
            "limits": _limits(st),
            "missed_heel_strike": _missed_heel_strikes(feet, foot),
            "first_last": _first_last(len(st)),
        }
        out.append(_with_reasons(st, flags))
    info = dict(
        turn_centres_s=centres,
        expected_interval_s=expected,
        interval_s=interval,
        used_rhythm=bool(used_rhythm),
    )
    return pd.concat(out, ignore_index=True).drop(columns="ratio"), info


def clean_weargait(task: pd.DataFrame) -> pd.DataFrame:
    """Clean strides of one WearGait-PD recording (one task, one participant).

    ``task`` needs the columns GeneralEvent, LTotalForce and RTotalForce, at
    SAMPLE_RATE_HZ. Returns the stride table of both feet (module docstring).
    """
    label = task["GeneralEvent"].astype(str).to_numpy()
    forces = {f: task[f"{f}TotalForce"].to_numpy(float) for f in ("L", "R")}
    feet = _foot_tables(
        np.nan_to_num(forces["L"], nan=0.0), np.nan_to_num(forces["R"], nan=0.0)
    )
    out = []
    for foot, st in feet.items():
        missing = np.isnan(forces[foot])
        a = np.round(st["hs_s"].to_numpy() * SAMPLE_RATE_HZ).astype(int)
        b = np.round(st["next_hs_s"].to_numpy() * SAMPLE_RATE_HZ).astype(int)
        spans = list(zip(a, b))
        turn = np.array([(label[i:j] == "Turn").any() for i, j in spans], bool)
        flags = {
            "missing_data": np.array([missing[i:j].any() for i, j in spans], bool),
            "not_walk": np.array([(label[i:j] != "Walk").any() for i, j in spans], bool)
            & ~turn,
            "turn": _grow(turn, TURN_MARGIN["weargait"]),
            "limits": _limits(st),
            "first_last": _first_last(len(st)),
        }
        out.append(_with_reasons(st, flags))
    return pd.concat(out, ignore_index=True).drop(columns="ratio")


def meets_minimum(strides: pd.DataFrame, dataset: str) -> bool:
    """D-011: at least MIN_STRIDES[dataset] clean strides on each foot.

    ``strides`` may stack several recordings of one participant (WearGait-PD's
    three straight-walking tasks).
    """
    n = strides[strides["clean"]].groupby("foot").size()
    return all(n.get(f, 0) >= MIN_STRIDES[dataset] for f in ("L", "R"))
