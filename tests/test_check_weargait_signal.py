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
