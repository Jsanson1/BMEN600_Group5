"""Participant features from clean strides (task T-018), on tables with known values."""

import importlib.util
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from conftest import synthetic_record

from gaitpdb.events import stride_table
from gaitpdb.features import (
    FEATURE_COLUMNS,
    FEATURE_DICTIONARY,
    STRIDE_FEATURE_COLUMNS,
    feature_dictionary_markdown,
    participant_features,
    record_features,
    stride_features,
)

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_features.py"
spec = importlib.util.spec_from_file_location("make_features", SCRIPT)
make_features = importlib.util.module_from_spec(spec)
spec.loader.exec_module(make_features)


def strides_of(foot: str, stride: list[float], swing: list[float]) -> pd.DataFrame:
    s = np.asarray(stride, dtype=float)
    w = np.asarray(swing, dtype=float)
    return pd.DataFrame(
        {
            "foot": foot,
            "stride_s": s,
            "swing_s": w,
            "stance_s": s - w,
            "swing_pct": 100 * w / s,
        }
    )


def test_stride_features_match_the_definitions():
    left = strides_of("L", [1.0, 1.1, 0.9, 1.0, 1.2], [0.40, 0.42, 0.38, 0.40, 0.45])
    right = strides_of("R", [1.0, 1.0, 1.1, 0.9], [0.36, 0.37, 0.39, 0.35])
    ft = stride_features(pd.concat([left, right], ignore_index=True))

    def cv(x):
        return 100 * np.std(x, ddof=1) / np.mean(x)

    def madcv(x):
        return 100 * 1.4826 * np.median(np.abs(x - np.median(x))) / np.median(x)

    both = pd.concat([left, right])
    assert ft["n_strides_left"] == 5 and ft["n_strides_right"] == 4
    assert ft["stride_time_mean_s"] == pytest.approx(both["stride_s"].mean())
    assert ft["stride_time_cv_pct"] == pytest.approx(
        (cv(left["stride_s"]) + cv(right["stride_s"])) / 2
    )
    assert ft["stride_time_madcv_pct"] == pytest.approx(
        (madcv(left["stride_s"]) + madcv(right["stride_s"])) / 2
    )
    assert ft["swing_time_cv_pct"] == pytest.approx(
        (cv(left["swing_s"]) + cv(right["swing_s"])) / 2
    )
    assert ft["swing_time_madcv_pct"] == pytest.approx(
        (madcv(left["swing_s"]) + madcv(right["swing_s"])) / 2
    )
    assert ft["stance_time_mean_s"] == pytest.approx(both["stance_s"].mean())
    assert ft["swing_pct_mean"] == pytest.approx(both["swing_pct"].mean())
    l_sw, r_sw = left["swing_s"].mean(), right["swing_s"].mean()
    assert ft["swing_time_asymmetry_pct"] == pytest.approx(
        100 * abs(l_sw - r_sw) / ((l_sw + r_sw) / 2)
    )
    l_st, r_st = left["stride_s"].mean(), right["stride_s"].mean()
    assert ft["stride_time_asymmetry_pct"] == pytest.approx(
        100 * abs(l_st - r_st) / ((l_st + r_st) / 2)
    )
    assert set(ft) == set(STRIDE_FEATURE_COLUMNS)


def test_robust_variability_shrugs_off_one_hesitation_and_matches_cv_in_scale():
    rng = np.random.default_rng(0)
    s = 1.0 + 0.03 * rng.standard_normal(60)
    calm = pd.concat(
        [strides_of("L", s, 0.38 * s), strides_of("R", s[::-1], 0.38 * s[::-1])]
    )
    s2 = s.copy()
    s2[30] = 1.9  # one hesitation on each foot
    shaken = pd.concat(
        [strides_of("L", s2, 0.38 * s2), strides_of("R", s2[::-1], 0.38 * s2[::-1])]
    )
    a, b = stride_features(calm), stride_features(shaken)
    assert b["stride_time_cv_pct"] > 3 * a["stride_time_cv_pct"]
    assert b["stride_time_madcv_pct"] < 1.2 * a["stride_time_madcv_pct"]
    # for normally distributed strides the two measures agree in scale
    big = 1.0 + 0.05 * rng.standard_normal(20000)
    ft = stride_features(
        pd.concat([strides_of("L", big, 0.4 * big), strides_of("R", big, 0.4 * big)])
    )
    assert ft["stride_time_madcv_pct"] == pytest.approx(
        ft["stride_time_cv_pct"], rel=0.03
    )


def test_too_few_strides_on_a_foot_leaves_only_the_counts():
    t = pd.concat(
        [strides_of("L", [1.0] * 5, [0.4] * 5), strides_of("R", [1.0, 1.1], [0.4, 0.4])]
    )
    ft = stride_features(t)
    assert ft["n_strides_left"] == 5 and ft["n_strides_right"] == 2
    others = [c for c in STRIDE_FEATURE_COLUMNS if not c.startswith("n_")]
    assert all(np.isnan(ft[c]) for c in others)


def test_unknown_foot_label_is_an_error():
    t = strides_of("L", [1.0] * 4, [0.4] * 4)
    t.loc[0, "foot"] = "left"
    with pytest.raises(ValueError, match="foot"):
        stride_features(t)


def test_both_entry_points_give_the_same_features_from_the_same_strides():
    rec = synthetic_record(n_strides=40, stride_s=1.05, swing_s=0.41)
    parts = []
    for foot, col in (("L", "L_total"), ("R", "R_total")):
        st = stride_table(rec[col].to_numpy())
        parts.append(st[st["kept"]].assign(foot=foot))
    ft = stride_features(pd.concat(parts, ignore_index=True))
    old = record_features(rec)
    shared = [c for c in STRIDE_FEATURE_COLUMNS if c in FEATURE_COLUMNS]
    assert len(shared) == 10
    for c in shared:
        assert ft[c] == pytest.approx(old[c]), c


def table_of(participant, clean, included, stride, foot):
    return strides_of(foot, stride, [0.4 * x for x in stride]).assign(
        participant=participant, clean=clean, included=included
    )


def test_participant_features_use_only_clean_strides_of_included_participants():
    good = [1.0, 1.02, 0.98, 1.01, 0.99]
    t = pd.concat(
        [
            table_of("A", True, True, good, "L"),
            table_of("A", True, True, good, "R"),
            table_of("A", False, True, [3.0, 0.2, 2.9], "L"),  # removed strides
            table_of("B", True, False, good, "L"),  # B is not included (D-011)
            table_of("B", True, False, good, "R"),
        ],
        ignore_index=True,
    )
    out = participant_features(t)
    assert out["participant"].tolist() == ["A"]
    row = out.iloc[0]
    assert row["n_strides_left"] == 5
    assert row["stride_time_mean_s"] == pytest.approx(np.mean(good))
    assert list(out.columns) == ["participant", *STRIDE_FEATURE_COLUMNS]


def test_participant_features_needs_the_flags():
    t = strides_of("L", [1.0] * 4, [0.4] * 4).assign(participant="A")
    with pytest.raises(ValueError, match="clean"):
        participant_features(t)


def test_every_column_has_a_dictionary_entry():
    columns = list(
        dict.fromkeys(
            make_features.ID_COLUMNS["weargait"]
            + STRIDE_FEATURE_COLUMNS
            + FEATURE_COLUMNS
        )
    )
    md = feature_dictionary_markdown(columns)
    assert md.count("\n") == len(columns) + 2
    for c in columns:
        assert f"`{c}`" in md and FEATURE_DICTIONARY[c][1]
    with pytest.raises(KeyError):
        feature_dictionary_markdown(["no_such_column"])
    # every row has exactly the table's four column bars once escaped bars are set
    # aside, so "|left - right|" in a definition does not split its cell (#17 review)
    asym = feature_dictionary_markdown(["swing_time_asymmetry_pct"]).splitlines()[-1]
    assert "\\|left - right\\|" in asym
    assert len(re.findall(r"(?<!\\)\|", asym)) == 4


def weargait_strides(shift: float) -> pd.DataFrame:
    """Two participants, three tasks; ``shift`` moves each task's mean stride time."""
    rng = np.random.default_rng(1)
    parts = []
    for p, group, site in (("NLS001", "PD", "NLS"), ("HC001", "Control", "HC")):
        for k, task in enumerate(("SelfPace", "SelfPace_mat", "SelfPace_matTURN")):
            for foot in ("L", "R"):
                s = 1.0 + shift * k + 0.02 * rng.standard_normal(12)
                parts.append(
                    strides_of(foot, s, 0.38 * s).assign(
                        participant=p,
                        site=site,
                        group=group,
                        task=task,
                        clean=True,
                        included=True,
                    )
                )
    return pd.concat(parts, ignore_index=True)


def test_weargait_table_adds_sheet_columns_and_checks_the_group(monkeypatch):
    sheets = pd.DataFrame(
        {
            "participant": ["NLS001", "HC001"],
            "group": ["PD", "Control"],
            "age": [67, 72],
            "sex": ["Male", "Female"],
            "site": ["NLS", "HC"],
            "release": ["1", "1"],
        }
    )
    monkeypatch.setattr(make_features, "load_participants", lambda _: sheets)
    out = make_features.weargait_table(weargait_strides(0.0), Path("unused"))
    assert list(out.columns) == (
        make_features.ID_COLUMNS["weargait"] + STRIDE_FEATURE_COLUMNS
    )
    row = out.set_index("participant").loc["HC001"]
    assert (row["dataset"], row["study"], row["group"]) == ("weargait", "HC", "Control")
    assert (row["Age"], row["sex"], row["n_tasks"]) == (72, "F", 3)
    assert row["n_strides_left"] == 36  # three tasks pooled (D-011)
    wrong = sheets.assign(group=["Control", "Control"])
    monkeypatch.setattr(make_features, "load_participants", lambda _: wrong)
    with pytest.raises(ValueError, match="NLS001"):
        make_features.weargait_table(weargait_strides(0.0), Path("unused"))


def test_main_without_clean_strides_skips_both_datasets_and_writes_the_dictionary(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        "sys.argv",
        ["make_features.py", "--interim", str(tmp_path), "--out", str(tmp_path)],
    )
    make_features.lines.clear()
    make_features.main()
    summary = (tmp_path / "features_summary.txt").read_text()
    assert "gaitpdb skipped" in summary and "weargait skipped" in summary
    assert "No provenance file" in summary
    assert (
        "`swing_time_asymmetry_pct`" in (tmp_path / "feature_dictionary.md").read_text()
    )
    assert not list(tmp_path.glob("features_*.csv"))
