"""Shared fixtures: synthetic records with known gait events, no real data needed."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gaitpdb.io import COLUMNS, SAMPLE_RATE_HZ  # noqa: E402


def synthetic_force(
    n_strides: int,
    stride_s: float,
    swing_s: float,
    peak_n: float = 800.0,
    phase_s: float = 0.0,
) -> np.ndarray:
    """One foot's total force: a flat plateau during stance, zero during swing.

    Stride k starts (heel strike) at phase_s + k * stride_s; stance lasts
    stride_s - swing_s. Edges are 20 ms ramps so the signal is not a pure step.
    """
    fs = SAMPLE_RATE_HZ
    n = int(round((phase_s + n_strides * stride_s + 1.0) * fs))
    t = np.arange(n) / fs
    f = np.zeros(n)
    stance_s = stride_s - swing_s
    for k in range(n_strides):
        hs = phase_s + k * stride_s
        on = (t >= hs) & (t < hs + stance_s)
        f[on] = peak_n
        ramp = (t >= hs) & (t < hs + 0.02)
        f[ramp] = peak_n * (t[ramp] - hs) / 0.02
        down = (t >= hs + stance_s - 0.02) & (t < hs + stance_s)
        f[down] = peak_n * (hs + stance_s - t[down]) / 0.02
    return f


def synthetic_record(
    n_strides: int = 30, stride_s: float = 1.1, swing_s: float = 0.4
) -> pd.DataFrame:
    """A record DataFrame with the 19 columns the loader produces."""
    left = synthetic_force(n_strides, stride_s, swing_s)
    right = synthetic_force(n_strides, stride_s, swing_s, phase_s=stride_s / 2)
    n = min(len(left), len(right))
    t = np.arange(n) / SAMPLE_RATE_HZ
    data = {"time_s": t}
    for i in range(1, 9):
        data[f"L{i}"] = left[:n] / 8
        data[f"R{i}"] = right[:n] / 8
    data["L_total"] = left[:n]
    data["R_total"] = right[:n]
    return pd.DataFrame(data)[COLUMNS]


@pytest.fixture
def record() -> pd.DataFrame:
    return synthetic_record()
