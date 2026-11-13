"""The insole-versus-walkway check (T-025) on synthetic signals with known events."""

import numpy as np
import pandas as pd
import pytest
from conftest import synthetic_force

from gaitpdb.io import SAMPLE_RATE_HZ
from gaitpdb.walkway import (
    CONTACT_COLUMNS,
    agreement,
    compare_task,
    force_level,
    insole_contacts,
    match_footfalls,
    threshold_candidates,
    walkway_footfalls,
)

STRIDE, SWING, N = 1.1, 0.4, 20


def contact_from_force(force: np.ndarray, lag: int, window: tuple[float, float]):
    """Walkway contact from the plateau of a synthetic force: 1 during stance,
    ``lag`` samples earlier than the insole (the insole lags the walkway), and 0
    for footfalls not wholly inside the walkway's time window (partial footfalls
    read 0, as in the dataset)."""
    on = force > 1.0
    edges = np.diff(np.r_[0, on.astype(int), 0])
    contact = np.zeros(len(force))
    lo, hi = (int(w * SAMPLE_RATE_HZ) for w in window)
    for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
        a2, b2 = a - lag, b - lag
        if a2 >= lo and b2 <= hi:
            contact[a2:b2] = 1
    return contact


def synthetic_task(swing_offset_n: float = 0.0, lag: int = 3) -> pd.DataFrame:
    left = synthetic_force(N, STRIDE, SWING)
    right = synthetic_force(N, STRIDE, SWING, phase_s=STRIDE / 2)
    n = min(len(left), len(right))
    left, right = left[:n] + swing_offset_n, right[:n] + swing_offset_n
    window = (3.0, 15.0)  # the walkway covers part of the walk
    task = pd.DataFrame(
        {
            "LTotalForce": left,
            "RTotalForce": right,
            CONTACT_COLUMNS["L"]: contact_from_force(
                left - swing_offset_n, lag, window
            ),
            CONTACT_COLUMNS["R"]: contact_from_force(
                right - swing_offset_n, lag, window
            ),
        }
    )
    return task


def test_walkway_footfalls_drop_incomplete_runs_and_last_frame():
    c = np.r_[np.nan, np.nan, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, np.nan]
    ff = walkway_footfalls(c)
    # the run at the first frame with data is incomplete; the last run ends at the
    # final frame with data, which is dropped (the _mat tasks' erroneous frame)
    assert list(zip(ff["on"], ff["off"])) == [(6, 9)]
    assert ff["stance_s"].iloc[0] == pytest.approx(0.03)
    assert walkway_footfalls(np.full(10, np.nan)).empty


def test_insole_contacts_flag_gaps():
    f = synthetic_force(5, STRIDE, SWING, phase_s=0.5)
    f[200:203] = np.nan  # 30 ms inside the second stance (1.6 to 2.3 s)
    c = insole_contacts(f, 20.0)
    # shorter than the 0.1 s minimum phase, so the gap is merged into the
    # stance (the gaitpdb rule) and that one contact is flagged
    assert len(c) == 5
    assert list(c["touches_gap"]) == [False, True, False, False, False]
    assert c["hs"].iloc[1] < 200 < c["to"].iloc[1]
    g = synthetic_force(5, STRIDE, SWING, phase_s=0.5)
    g[180:195] = np.nan  # 0.15 s wholly inside that stance splits it in two
    c = insole_contacts(g, 20.0)
    assert len(c) == 6 and list(c["touches_gap"]) == [False, True, True] + [False] * 3


def test_perfect_agreement_with_a_constant_lag():
    task = synthetic_task(lag=3)
    m = compare_task(task, {"20 N": 20.0})
    a = agreement(m)
    assert a["n_footfalls"] > 15 and a["one_to_one_pct"] == 100.0
    assert abs(a["stance_median_diff_s"]) <= 0.01  # durations ignore the lag
    assert a["stride_median_abs_diff_s"] == pytest.approx(0.0, abs=1e-9)
    assert abs(a["swing_median_diff_s"]) <= 0.01
    assert a["n_stride"] > 10


def test_raised_swing_baseline_merges_footfalls_at_20_n_only():
    # like NLS056: the insole never unloads below 20 N in swing
    task = synthetic_task(swing_offset_n=30.0)
    th = threshold_candidates(task)
    m = compare_task(task, {"20 N": 20.0, "5% of force level": th["5% of force level"]})
    at20 = agreement(m[m["threshold"] == "20 N"])
    rel = agreement(m[m["threshold"] == "5% of force level"])
    assert at20["one_to_one_pct"] == 0.0
    assert rel["one_to_one_pct"] == 100.0


def test_missed_contact_is_unmatched():
    task = synthetic_task()
    f = task["LTotalForce"].to_numpy().copy()
    c = task[CONTACT_COLUMNS["L"]].to_numpy()
    walk = walkway_footfalls(c)
    a, b = walk["on"].iloc[2], walk["off"].iloc[2]
    f[a - 10 : b + 10] = 0.0  # the insole sees nothing for this footfall
    m = match_footfalls(walk, insole_contacts(f, 20.0))
    assert not m["matched"].iloc[2] and m["matched"].drop(index=2).all()
    assert agreement(m)["unmatched_pct"] == pytest.approx(100 / len(walk))


def test_threshold_candidates_and_force_level():
    task = synthetic_task()
    th = threshold_candidates(task, body_mass_kg=70.0)
    assert th["20 N"] == 20.0
    assert th["2.5% of body weight"] == pytest.approx(0.025 * 70 * 9.81)
    assert th["5% of force level"] == pytest.approx(0.05 * force_level(task))
    assert "2.5% of body weight" not in threshold_candidates(task, None)
    assert force_level(task) == pytest.approx(800.0, rel=0.01)


def test_agreement_limits_on_known_differences():
    m = pd.DataFrame(
        {
            "matched": [True] * 4,
            "one_to_one": [True] * 4,
            "d_stance_s": [0.01, 0.03, -0.01, 0.01],
            "d_stride_s": [np.nan] * 4,
            "d_swing_s": [np.nan] * 4,
        }
    )
    a = agreement(m)
    d = np.array([0.01, 0.03, -0.01, 0.01])
    assert a["stance_median_diff_s"] == pytest.approx(0.01)
    assert a["stance_loa_low_s"] == pytest.approx(d.mean() - 1.96 * d.std(ddof=1))
    assert a["n_stride"] == 0 and np.isnan(a["stride_median_diff_s"])
    assert a["agree_pct"] == 100.0  # every difference is within 30 ms, 0.03 included
    m.loc[1, "d_stance_s"] = 0.05
    assert agreement(m)["agree_pct"] == 75.0


def test_pairwise_merged_contacts_are_not_one_to_one():
    # every other swing stays above 20 N, so two footfalls share one insole
    # contact: neither may count as matched one to one, though each overlaps it
    task = synthetic_task()
    f = task["LTotalForce"].to_numpy().copy()
    t = np.arange(len(f)) / SAMPLE_RATE_HZ
    for k in range(1, N, 2):
        swing = (t >= k * STRIDE + (STRIDE - SWING)) & (t < (k + 1) * STRIDE)
        f[swing] += 30.0
    walk = walkway_footfalls(task[CONTACT_COLUMNS["L"]].to_numpy())
    m = match_footfalls(walk, insole_contacts(f, 20.0))
    assert m["matched"].all()
    assert agreement(m)["one_to_one_pct"] < 20.0


def load_threshold_script():
    import importlib.util
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[1] / "scripts" / "check_weargait_threshold.py"
    )
    spec = importlib.util.spec_from_file_location("check_weargait_threshold", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_threshold_script_on_synthetic_files(tmp_path):
    script = load_threshold_script()
    (tmp_path / "csv").mkdir()
    synthetic_task().to_csv(tmp_path / "csv" / "P001_SelfPace.csv", index=False)
    synthetic_task(swing_offset_n=30.0).to_csv(
        tmp_path / "csv" / "P001_SelfPace_mat.csv", index=False
    )
    synthetic_task().drop(columns=["LTotalForce", "RTotalForce"]).to_csv(
        tmp_path / "csv" / "P001_SelfPace_matTURN.csv", index=False
    )
    ff, notes = script.check_participant(tmp_path, "P001", body_mass_kg=70.0)
    assert [n for n in notes if not n.endswith(script.NO_LABELS)] == [
        "SelfPace_matTURN: no insole data"
    ]
    assert set(ff["task"]) == {"SelfPace", "SelfPace_mat"}
    overall = script.summary_rows(ff, None)
    assert {
        "10 N",
        "20 N",
        "50 N",
        "2.5% of body weight",
        "5% of body weight",
        "2.5% of force level",
        "5% of force level",
    } <= set(overall["threshold"])
    assert len(overall) == 14
    by_task = script.summary_rows(ff, "task").set_index(["threshold", "task"])
    assert by_task.loc[("20 N", "SelfPace"), "one_to_one_pct"] == 100.0
    assert by_task.loc[("20 N", "SelfPace_mat"), "one_to_one_pct"] == 0.0
    # 20 N fails on the raised-baseline recording; the recommendation avoids it
    assert script.recommend(overall) != "20 N"
    _, why = script.check_participant(tmp_path, "P002")
    assert why == [f"{t}: no file" for t in script.TASKS]


def test_threshold_script_says_when_a_file_has_no_labels(tmp_path):
    # Review of #15 (Yassien): without GeneralEvent every footfall is counted,
    # so the script must say so rather than fall back silently.
    script = load_threshold_script()
    (tmp_path / "csv").mkdir()
    synthetic_task().to_csv(tmp_path / "csv" / "P001_SelfPace.csv", index=False)
    _, notes = script.check_participant(tmp_path, "P001")
    assert any(
        n.startswith("SelfPace:") and n.endswith(script.NO_LABELS) for n in notes
    )


def test_threshold_script_reads_the_labels_and_keeps_straight_walking(tmp_path):
    # The script must load GeneralEvent, or compare_task's walk-only filter
    # never applies and turn footfalls on the walkway are counted too.
    script = load_threshold_script()
    (tmp_path / "csv").mkdir()
    task = synthetic_task()
    walk = walkway_footfalls(task[CONTACT_COLUMNS["L"]].to_numpy())
    labels = np.full(len(task), "Walk", dtype=object)
    a, b = walk["on"].iloc[3], walk["off"].iloc[3]
    labels[a:b] = "Turn"
    task["GeneralEvent"] = labels
    task.to_csv(tmp_path / "csv" / "P001_SelfPace.csv", index=False)
    ff, _ = script.check_participant(tmp_path, "P001")
    left = ff[(ff["foot"] == "L") & (ff["threshold"] == "20 N")]
    assert len(left) == len(walk) - 1 and a not in set(left["on"])


def test_walk_only_keeps_walk_footfalls_but_matches_against_all():
    task = synthetic_task()
    walk = walkway_footfalls(task[CONTACT_COLUMNS["L"]].to_numpy())
    labels = np.full(len(task), "Walk", dtype=object)
    a, b = walk["on"].iloc[3], walk["off"].iloc[3]
    labels[a:b] = "Turn"  # one left footfall falls in a turn
    task["GeneralEvent"] = labels
    every = compare_task(task, {"20 N": 20.0}, walk_only=False)
    walk_rows = compare_task(task, {"20 N": 20.0})
    left = walk_rows[walk_rows["foot"] == "L"]
    assert len(left) == len(walk) - 1 and a not in set(left["on"])
    assert len(every[every["foot"] == "L"]) == len(walk)


def test_stride_and_swing_stop_before_a_turn_footfall():
    # Review of #15: a kept "Walk" footfall followed by a turn footfall of the
    # same foot gets no stride or swing difference, since that stride ends in
    # the turn; the footfalls around it keep theirs.
    task = synthetic_task()
    walk = walkway_footfalls(task[CONTACT_COLUMNS["L"]].to_numpy())
    labels = np.full(len(task), "Walk", dtype=object)
    a, b = walk["on"].iloc[3], walk["off"].iloc[3]
    labels[a:b] = "Turn"
    task["GeneralEvent"] = labels
    left = compare_task(task, {"20 N": 20.0})
    left = left[left["foot"] == "L"].set_index("on")
    before = walk["on"].iloc[2]
    assert np.isnan(left.loc[before, "d_stride_s"])
    assert np.isnan(left.loc[before, "d_swing_s"])
    assert np.isfinite(left.loc[walk["on"].iloc[1], "d_stride_s"])
    assert np.isfinite(left.loc[walk["on"].iloc[4], "d_stride_s"])
    every = compare_task(task, {"20 N": 20.0}, walk_only=False)
    every = every[every["foot"] == "L"].set_index("on")
    assert np.isfinite(every.loc[before, "d_stride_s"])
