"""Gait-event detection and stride rules on synthetic signals with known timing."""

import numpy as np
import pytest
from conftest import synthetic_force

from gaitpdb.events import DEFAULT_THRESHOLD_N, contact_events, stride_table
from gaitpdb.features import FEATURE_COLUMNS, record_features


def test_events_recover_known_strides():
    f = synthetic_force(n_strides=20, stride_s=1.1, swing_s=0.4)
    st = stride_table(f)
    assert len(st) == 19  # 20 heel strikes give 19 complete strides
    assert st["kept"].all()
    assert np.allclose(st["stride_s"], 1.1, atol=0.011)
    assert np.allclose(
        st["swing_s"], 0.4, atol=0.021
    )  # 20 ms ramps straddle the threshold
    assert np.allclose(st["swing_pct"], 100 * 0.4 / 1.1, atol=2.0)


def test_threshold_glitch_is_ignored():
    f = synthetic_force(n_strides=10, stride_s=1.0, swing_s=0.4)
    hs, to = contact_events(f)
    # a 3-sample blip above threshold in the middle of a swing phase must not create events
    swing_start = int(round((1.0 - 0.4) * 100)) + 5  # inside the first swing
    g = f.copy()
    g[swing_start : swing_start + 3] = DEFAULT_THRESHOLD_N + 50
    hs2, to2 = contact_events(g)
    assert len(hs2) == len(hs) and len(to2) == len(to)


def test_relative_rule_drops_a_doubled_stride():
    # two steps merged into one stride (the foot never unloads between them)
    f = synthetic_force(n_strides=12, stride_s=1.0, swing_s=0.4)
    a = int(round(5.0 * 100))  # fill the swing phase of stride 4 with force
    b = int(round(5.4 * 100))
    f[a - 45 : b + 5] = 800.0
    st = stride_table(f)
    assert (~st["kept"]).sum() == 1
    assert st.loc[~st["kept"], "stride_s"].iloc[0] == pytest.approx(2.0, abs=0.02)
    # without the relative rule the doubled stride passes the absolute limits
    st_no_rule = stride_table(f, ratio_limits=None)
    assert st_no_rule["kept"].all()


def test_record_features_have_all_columns_and_sane_values(record):
    ft = record_features(record)
    assert set(FEATURE_COLUMNS) <= set(ft)
    assert ft["n_strides_removed"] == 0
    assert ft["stride_time_mean_s"] == pytest.approx(1.1, abs=0.02)
    assert ft["stride_time_cv_pct"] < 1.5
    assert ft["swing_time_asymmetry_pct"] < 1.0  # both feet identical by construction
    assert ft["cadence_strides_per_min"] == pytest.approx(60 / 1.1, rel=0.1)


def test_too_few_strides_gives_nan_features():
    f = synthetic_force(n_strides=2, stride_s=1.0, swing_s=0.4)
    import pandas as pd

    from gaitpdb.io import COLUMNS

    n = len(f)
    df = pd.DataFrame(
        {c: f if c in ("L_total", "R_total") else f / 8 for c in COLUMNS[1:]}
    )
    df.insert(0, "time_s", np.arange(n) / 100.0)
    ft = record_features(df)
    assert np.isnan(ft["stride_time_mean_s"])
