"""Label-free feature checks (scripts/check_features.py, task T-018) on known tables."""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gaitpdb.features import stride_features

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_features.py"
spec = importlib.util.spec_from_file_location("check_features", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def foot_series(stride, clean, participant="P1", foot="L", task=None, gap_after=()):
    """Consecutive strides of one foot; a gap (a missing stride) after the given
    positions makes the next stride not follow on from the previous one."""
    s = np.asarray(stride, dtype=float)
    hs = np.r_[0.0, np.cumsum(s)[:-1]]
    for k in gap_after:
        hs[k + 1 :] += 1.0
    d = pd.DataFrame(
        {
            "participant": participant,
            "foot": foot,
            "hs_s": hs,
            "next_hs_s": hs + s,
            "stride_s": s,
            "swing_s": 0.38 * s,
            "stance_s": 0.62 * s,
            "swing_pct": 38.0,
            "clean": clean,
            "included": True,
        }
    )
    if task is not None:
        d["task"] = task
    return d


def test_bouts_break_at_removed_and_missing_strides():
    clean = [True, True, False, True, True, True, True, False, True]
    d = foot_series([1.0] * 9, clean, gap_after=(4,))  # stride 5 does not follow 4
    b = check.bout_positions(d, ["participant", "foot"])
    assert len(b) == 7
    assert b["bout"].tolist() == [1, 1, 2, 2, 3, 3, 4]
    assert b["k0"].tolist() == [0, 1, 0, 1, 0, 1, 0]
    assert b["k1"].tolist() == [1, 0, 1, 0, 1, 0, 0]
    assert b["bout_len"].tolist() == [2, 2, 2, 2, 2, 2, 1]


def bouty_participant(participant, first_last=1.3, n_bouts=6, per_bout=6, seed=0):
    """Bouts of ``per_bout`` strides whose first and last strides are slow."""
    rng = np.random.default_rng(seed)
    parts = []
    for foot in ("L", "R"):
        stride, clean = [], []
        for _ in range(n_bouts):
            s = 1.0 + 0.01 * rng.standard_normal(per_bout)
            s[0] = s[-1] = first_last
            stride += [*s, 1.6]  # a turn stride between bouts
            clean += [True] * per_bout + [False]
        parts.append(foot_series(stride, clean, participant, foot))
    return pd.concat(parts, ignore_index=True)


def test_dropping_bout_ends_removes_their_variability_and_their_strides():
    d = pd.concat([bouty_participant("P1"), bouty_participant("P2", seed=1)])
    b = check.bout_positions(d, ["participant", "foot"])
    full, trimmed = check.trimmed_cv(b, 0), check.trimmed_cv(b, 1)
    assert (full["n_weaker_foot"] == 36).all()
    assert (trimmed["n_weaker_foot"] == 24).all()
    assert (full["stride_time_cv_pct"] > 10).all()
    assert (trimmed["stride_time_cv_pct"] < 2).all()
    pos = check.position_ratios(b).set_index("position")
    assert pos.loc["first", "mean"] == pytest.approx(1.3, abs=0.02)
    assert pos.loc["last", "mean"] == pytest.approx(1.3, abs=0.02)
    assert pos.loc["middle", "mean"] == pytest.approx(1.0, abs=0.02)


def weargait_like(shift):
    """Two participants, three tasks; ``shift`` moves each task's mean stride time."""
    rng = np.random.default_rng(1)
    parts = []
    for p in ("NLS001", "HC001"):
        for k, task in enumerate(("SelfPace", "SelfPace_mat", "SelfPace_matTURN")):
            for foot in ("L", "R"):
                s = 1.0 + shift * k + 0.02 * rng.standard_normal(12)
                parts.append(foot_series(s, [True] * 12, p, foot, task))
    return pd.concat(parts, ignore_index=True)


def test_pooling_check_is_one_when_tasks_agree_and_larger_when_they_differ():
    same = check.pooled_vs_within_cv(weargait_like(0.0), "stride_s")
    apart = check.pooled_vs_within_cv(weargait_like(0.05), "stride_s")
    assert set(same.index) == {"NLS001", "HC001"}
    assert same.between(0.9, 1.15).all()
    assert (apart > 1.5).all()


def test_asymmetry_grows_as_strides_get_fewer_and_matches_the_features_with_all():
    rng = np.random.default_rng(2)
    parts = []
    for p in range(12):
        for foot in ("L", "R"):
            s = 1.0 + 0.03 * rng.standard_normal(80)
            parts.append(foot_series(s, [True] * 80, f"P{p:02d}", foot))
    d = pd.concat(parts, ignore_index=True)
    out = check.asymmetry_at_counts(d, counts=(5, 40), n_draws=10).set_index(
        "strides_per_foot"
    )
    assert (
        out.loc[5, "stride_time_asymmetry_pct"]
        > out.loc[40, "stride_time_asymmetry_pct"]
    )
    assert (
        out.loc[40, "stride_time_asymmetry_pct"]
        > out.loc["all", "stride_time_asymmetry_pct"]
    )
    by_features = np.median(
        [
            stride_features(g)["stride_time_asymmetry_pct"]
            for _, g in d.groupby("participant")
        ]
    )
    assert out.loc["all", "stride_time_asymmetry_pct"] == pytest.approx(by_features)
    assert out.loc["all", "participants"] == 12


def test_dataset_shift_reports_the_ratio_of_medians():
    tables = {
        "gaitpdb": pd.DataFrame({"x": [1.0, 2.0, 3.0]}),
        "weargait": pd.DataFrame({"x": [3.0, 4.0, 5.0]}),
    }
    row = check.dataset_shift(tables, ["x"]).iloc[0]
    assert (row["gaitpdb_median"], row["weargait_median"]) == (2.0, 4.0)
    assert row["ratio"] == pytest.approx(2.0)


def test_main_skips_without_both_datasets(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["check_features.py", "--results", str(tmp_path), "--interim", str(tmp_path)],
    )
    check.lines.clear()
    check.main()
    text = (tmp_path / "feature_checks.txt").read_text()
    assert "Skipped" in text


def test_figure_is_written_from_the_shift_and_position_tables(tmp_path):
    feats = list(check.FIGURE_FEATURES)
    tables = {
        "gaitpdb": pd.DataFrame({c: [1.0, 2.0, 3.0] for c in feats}),
        "weargait": pd.DataFrame({c: [2.0, 4.0, 6.0] for c in feats}),
    }
    shift = check.dataset_shift(tables, feats)
    pos = pd.DataFrame(
        {
            "position": ["first", "second", "middle", "second to last", "last"],
            "mean": [1.06, 1.01, 1.0, 1.01, 1.04],
            "sd": [0.1] * 5,
            "n": [100] * 5,
        }
    )
    png, pdf = tmp_path / "f.png", tmp_path / "f.pdf"
    check.figure(shift, {"gaitpdb": pos, "weargait": pos}, png, pdf)
    assert png.stat().st_size > 10_000 and pdf.stat().st_size > 5_000
