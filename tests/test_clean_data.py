"""Stride cleaning (gaitpdb.clean_data) on synthetic walks with known turns and events."""

import numpy as np
import pandas as pd
import pytest

from gaitpdb.clean_data import (
    CORRIDOR_M,
    MIN_STRIDES,
    REASONS,
    TURN_WINDOW_S,
    clean_gaitpdb,
    clean_weargait,
    expected_turn_interval,
    meets_minimum,
)
from gaitpdb.io import SAMPLE_RATE_HZ

FS = int(SAMPLE_RATE_HZ)
SWING = 0.38  # swing fraction of each synthetic stride


def force_from_strides(
    strides: list[float], start_s: float = 0.5, peak: float = 800.0, tail_s: float = 1.0
) -> np.ndarray:
    """One foot's total force: stance plateau then swing at 0 N, stride by stride.

    Each stride starts with a heel strike; the last heel strike closes the last
    stride. Edges are 20 ms ramps, as in conftest.synthetic_force.
    """
    n = int(round((start_s + sum(strides) + tail_s) * FS))
    t = np.arange(n) / FS
    f = np.zeros(n)
    hs = start_s
    for s in list(strides) + [strides[-1]]:  # a final stance closes the last stride
        stance = s * (1 - SWING)
        on = (t >= hs) & (t < hs + stance)
        f[on] = peak
        up = (t >= hs) & (t < hs + 0.02)
        f[up] = peak * (t[up] - hs) / 0.02
        down = (t >= hs + stance - 0.02) & (t < hs + stance)
        f[down] = peak * (hs + stance - t[down]) / 0.02
        hs += s
    return f


def record(left: list[float], right: list[float] | None = None) -> pd.DataFrame:
    """A record with L_total and R_total; the right foot starts half a stride later."""
    right = left if right is None else right
    lf = force_from_strides(left)
    rf = force_from_strides(right, start_s=0.5 + left[0] / 2)
    n = max(len(lf), len(rf))
    pad = lambda x: np.pad(x, (0, n - len(x)))  # noqa: E731
    return pd.DataFrame(
        {"time_s": np.arange(n) / FS, "L_total": pad(lf), "R_total": pad(rf)}
    )


def straight(n: int, stride: float = 1.1) -> list[float]:
    # tiny alternation so the series is not perfectly constant
    return [stride + (0.01 if i % 2 else -0.01) for i in range(n)]


TURN_SHAPE = [0.15, 0.35, 0.6, 0.2]  # extra seconds on the strides of a turn


def walk_with_turns(n_turns: int = 5, every: int = 18, base: float = 1.1):
    """Strides with turns every `every` strides; returns strides and true turn peak times."""
    strides, peaks, t = [], [], 0.5
    for k in range(n_turns + 1):
        for s in straight(every - len(TURN_SHAPE), base):
            strides.append(s)
            t += s
        if k == n_turns:
            break
        for j, extra in enumerate(TURN_SHAPE):
            s = base + extra
            if j == 2:
                peaks.append(t + s / 2)  # the slowest stride's midpoint
            strides.append(s)
            t += s
    return strides, peaks


def turn_period(strides: list[float], every: int = 18) -> float:
    return sum(strides[:every])


def test_straight_walk_loses_only_first_and_last():
    # long expected interval: no turn can be placed in a 60 s walk
    out, info = clean_gaitpdb(record(straight(50)), "Ga", 0.25)
    assert info["turn_centres_s"] == []
    for foot in ("L", "R"):
        f = out[out["foot"] == foot]
        removed = f[~f["clean"]]
        assert list(removed["reason"]) == ["first_last", "first_last"]
        assert removed.index[0] == f.index[0] and removed.index[-1] == f.index[-1]


def test_turns_found_at_known_times_and_removed_on_both_feet():
    strides, peaks = walk_with_turns()
    speed = CORRIDOR_M["Ga"] / turn_period(strides)  # expected interval = true period
    out, info = clean_gaitpdb(record(strides), "Ga", speed)
    assert info["used_rhythm"]
    centres = info["turn_centres_s"]
    assert len(centres) == len(peaks)
    for p in peaks:  # every turn found within one stride of its slowest stride
        assert min(abs(c - p) for c in centres) < 1.6
    for foot in ("L", "R"):
        f = out[out["foot"] == foot]
        mid = (f["hs_s"] + f["next_hs_s"]) / 2
        for p in peaks:  # the slowest stride of each turn is removed as a turn
            nearest = (mid - p).abs().idxmin()
            assert f.loc[nearest, "reason"] == "turn"
        # nothing far from a turn is removed, apart from the first and last stride
        far = mid.apply(lambda m: min(abs(m - c) for c in centres)) > TURN_WINDOW_S + 3
        assert set(f[far & ~f["clean"]]["reason"]) <= {"first_last"}


def test_short_walk_uses_the_expected_interval():
    out, info = clean_gaitpdb(record(straight(30)), "Si", 1.0)
    assert not info["used_rhythm"]
    assert info["interval_s"] == pytest.approx(expected_turn_interval("Si", 1.0))
    assert info["interval_s"] == pytest.approx(35.0)


def test_missing_speed_is_an_error():
    with pytest.raises(ValueError):
        clean_gaitpdb(record(straight(20)), "Ga", float("nan"))


def test_missed_heel_strike_on_one_foot_only():
    left = straight(40)
    left[20] = 2.2  # two strides merged on the left foot only
    out, _ = clean_gaitpdb(record(left, straight(40)), "Ga", 0.25)
    f = out[out["foot"] == "L"].reset_index(drop=True)
    assert f.loc[20, "reason"] == "missed_heel_strike"
    assert (out["reason"] == "missed_heel_strike").sum() == 1


def test_same_event_on_both_feet_is_not_a_missed_heel_strike():
    both = straight(40)
    both[20] = 2.2  # both feet slow down together: a real event, not a sensor miss
    out, _ = clean_gaitpdb(record(both), "Ga", 0.25)
    assert (out["reason"] == "missed_heel_strike").sum() == 0


def test_stop_longer_than_the_limit_is_removed():
    both = straight(40)
    both[20] = 3.0
    out, _ = clean_gaitpdb(record(both), "Ga", 0.25)
    for foot in ("L", "R"):
        f = out[out["foot"] == foot].reset_index(drop=True)
        assert f.loc[20, "reason"] == "limits"


def weargait_task(strides: list[float], turn_s: tuple[float, float]):
    """A WearGait-PD recording: insole forces and a Walk / Turn / Walk annotation."""
    rec = record(strides)
    t = rec["time_s"].to_numpy()
    label = np.where((t >= turn_s[0]) & (t < turn_s[1]), "Turn", "Walk")
    label[t < 0.3] = "Standing"
    return pd.DataFrame(
        {
            "GeneralEvent": label,
            "LTotalForce": rec["L_total"],
            "RTotalForce": rec["R_total"],
        }
    )


def test_weargait_turn_labels_without_margin():
    task = weargait_task(straight(30), (15.0, 17.0))
    out = clean_weargait(task)
    for foot in ("L", "R"):
        f = out[out["foot"] == foot].reset_index(drop=True)
        touches = (f["next_hs_s"] > 15.0) & (f["hs_s"] < 17.0)
        assert (f.loc[touches, "reason"] == "turn").all()
        # the strides just before and after the turn are kept (no margin, D-011)
        first, last = touches.idxmax(), touches[::-1].idxmax()
        assert f.loc[first - 1, "clean"] and f.loc[last + 1, "clean"]


def test_weargait_missing_samples_remove_the_stride():
    task = weargait_task(straight(30), (15.0, 17.0))
    task.loc[600:620, "LTotalForce"] = np.nan  # 6.0-6.2 s, inside a left stance
    out = clean_weargait(task)
    f = out[out["foot"] == "L"]
    hit = (f["next_hs_s"] > 6.0) & (f["hs_s"] < 6.2)
    assert (f.loc[hit, "reason"] == "missing_data").all() and hit.any()


def test_meets_minimum_per_dataset():
    def strides(n_left, n_right):
        return pd.DataFrame({"foot": ["L"] * n_left + ["R"] * n_right, "clean": True})

    for dataset, n in MIN_STRIDES.items():
        assert meets_minimum(strides(n, n), dataset)
        assert not meets_minimum(strides(n, n - 1), dataset)
        assert not meets_minimum(strides(n - 1, n + 5), dataset)


def test_every_removed_stride_has_one_reason():
    strides, _ = walk_with_turns()
    speed = CORRIDOR_M["Ga"] / turn_period(strides)
    out, _ = clean_gaitpdb(record(strides), "Ga", speed)
    assert set(out.loc[~out["clean"], "reason"]) <= set(REASONS)
    assert (out.loc[out["clean"], "reason"] == "").all()
    assert (out.loc[~out["clean"], "reason"] != "").all()


def test_tied_candidates_go_to_the_one_with_both_feet_disturbed():
    # Two left strides with exactly the same ratio; only one turn fits in this walk
    # (expected interval 30 s, about 44 s of walking). Only the later one has the
    # right foot slowed at the same time, so it is the turn.
    left, right = straight(40), straight(40)
    left[10] = left[30] = 1.5
    right[30] = 1.4
    out, info = clean_gaitpdb(record(left, right), "Ga", CORRIDOR_M["Ga"] / 30.0)
    assert len(info["turn_centres_s"]) == 1
    f = out[out["foot"] == "L"].reset_index(drop=True)
    mid = (f["hs_s"] + f["next_hs_s"]) / 2
    assert abs(info["turn_centres_s"][0] - mid[30]) < 0.01
    assert f.loc[30, "reason"] == "turn" and f.loc[10, "reason"] != "turn"
