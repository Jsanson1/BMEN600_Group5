"""The post hoc within-dataset check (scripts/check_weargait_signal.py, T-022)."""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_weargait_signal.py"
spec = importlib.util.spec_from_file_location("check_weargait_signal", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def test_single_aucs_point_upwards_when_pd_is_higher():
    t = pd.DataFrame({"y": [0, 0, 1, 1], "up": [1, 2, 3, 4], "down": [4, 3, 2, 1]})
    a = check.single_aucs(t, ["up", "down"])
    assert a["up"] == pytest.approx(1.0) and a["down"] == pytest.approx(0.0)


def test_same_site_treats_the_two_va_prefixes_as_one_site():
    assert check.same_site("WPD", "WHC") and check.same_site("HC", "HC")
    assert not check.same_site("NLS", "HC") and not check.same_site("WPD", "HC")


def test_pair_sites_counts_patient_site_then_control_site():
    t = pd.DataFrame(
        {
            "participant": ["P1", "C1", "P2", "C2", "P3", "C3"],
            "study": ["NLS", "HC", "WPD", "WHC", "NLS", "HC"],
        }
    )
    counts = check.pair_sites(t, ["P1", "C1", "P2", "C2", "P3", "C3"])
    assert counts.to_dict() == {"NLS-HC": 2, "WPD-WHC": 1}
    assert list(counts.index) == ["NLS-HC", "WPD-WHC"]


def test_age_correlations_are_within_each_group():
    t = pd.DataFrame(
        {
            "y": [0, 0, 0, 1, 1, 1],
            "Age": [60, 70, 80, 60, 70, 80],
            "p": [0.1, 0.2, 0.3, 0.9, 0.5, 0.1],
        }
    )
    r = check.age_correlations(t)
    assert r[0][0] == pytest.approx(1.0) and r[1][0] == pytest.approx(-1.0)
    assert r[0][2] == 3 and r[1][2] == 3
