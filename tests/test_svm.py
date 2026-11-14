"""The log-loss-tuned SVM with Platt scaling (task T-020), on synthetic data."""

import numpy as np
import pytest
from sklearn.metrics import log_loss, roc_auc_score

from gaitpdb.evaluation import log_transform
from gaitpdb.svm import (
    C_GRID,
    GAMMA_GRID,
    PlattTunedSVM,
    make_svm,
    param_grid,
    platt_fit,
    platt_proba,
)

SMALL = dict(c_grid=(0.1, 1.0, 10.0), gamma_grid=(0.1, 1.0, 10.0))


def linear_data(n=120, signal=2.0, seed=0, p=4):
    """PD shifted along the first input: a flat boundary separates the groups."""
    rng = np.random.default_rng(seed)
    y = np.r_[np.zeros(n // 2, int), np.ones(n - n // 2, int)]
    X = rng.standard_normal((n, p))
    X[:, 0] += signal * y
    return X, y


def ring_data(n=160, seed=0):
    """PD on a ring around the controls: no flat boundary separates them."""
    rng = np.random.default_rng(seed)
    y = np.r_[np.zeros(n // 2, int), np.ones(n - n // 2, int)]
    r = np.where(y == 1, 2.5, 0.8) + 0.25 * rng.standard_normal(n)
    a = rng.uniform(0, 2 * np.pi, n)
    return np.column_stack([r * np.cos(a), r * np.sin(a)]), y


def test_grid_follows_the_plan():
    grid = param_grid()
    linear = [s for s in grid if s["kernel"] == "linear"]
    rbf = [s for s in grid if s["kernel"] == "rbf"]
    assert len(linear) == 17 and len(rbf) == 17 * 17
    assert min(C_GRID) == pytest.approx(1e-4) and max(C_GRID) == pytest.approx(1e4)
    assert min(GAMMA_GRID) == pytest.approx(1e-4) and max(GAMMA_GRID) == pytest.approx(
        1e4
    )
    assert all("gamma" not in s for s in linear)
    assert param_grid(kernels=("linear",)) == linear
    with pytest.raises(ValueError):
        param_grid(kernels=())


def test_platt_curve_recovers_a_known_sigmoid():
    rng = np.random.default_rng(0)
    d = rng.normal(0, 2, 5000)
    y = (rng.uniform(size=d.size) < platt_proba(d, 1.5, -0.5)).astype(int)
    a, b = platt_fit(d, y)
    assert a == pytest.approx(1.5, abs=0.15) and b == pytest.approx(-0.5, abs=0.15)


def test_platt_curve_stays_finite_when_the_groups_separate_perfectly():
    d = np.r_[np.linspace(-3, -1, 20), np.linspace(1, 3, 20)]
    y = np.r_[np.zeros(20, int), np.ones(20, int)]
    a, b = platt_fit(d, y)
    p = platt_proba(d, a, b)
    assert np.isfinite([a, b]).all() and 0 < a < 3
    # smoothed targets (21/22 for PD, 1/22 for controls here) keep the curve from
    # going vertical: the extremes stay near 0.99, where 0/1 targets give 1 - 1e-9
    assert 0.005 < p.min() < 0.1 and 0.9 < p.max() < 0.995


def test_rbf_wins_when_the_boundary_is_curved():
    X, y = ring_data()
    m = PlattTunedSVM(**SMALL, random_state=0).fit(X, y)
    assert m.best_params_["kernel"] == "rbf"
    Xt, yt = ring_data(seed=1)
    assert roc_auc_score(yt, m.predict_proba(Xt)[:, 1]) > 0.95


def test_keeps_the_setting_with_the_lowest_inner_log_loss():
    X, y = linear_data()
    m = PlattTunedSVM(**SMALL, random_state=0).fit(X, y)
    grid = param_grid(**SMALL)
    assert len(m.cv_log_loss_) == len(grid)
    assert m.best_params_ == grid[int(np.argmin(m.cv_log_loss_))]
    assert m.best_log_loss_ == pytest.approx(m.cv_log_loss_.min())
    # a constant guess at the base rate scores log 2 here; the chosen setting beats it
    assert m.best_log_loss_ < np.log(2) - 0.1


def test_probabilities_are_platt_scaled_distances():
    X, y = linear_data()
    m = PlattTunedSVM(**SMALL, random_state=0).fit(X, y)
    d = m.decision_function(X)
    p = m.predict_proba(X)
    assert p.shape == (len(y), 2) and np.allclose(p.sum(axis=1), 1)
    assert np.allclose(p[:, 1], platt_proba(d, *m.platt_))
    assert m.platt_[0] > 0  # larger distance on the PD side, higher P(PD)
    assert np.array_equal(m.predict(X), (p[:, 1] >= 0.5).astype(int))
    Xt, yt = linear_data(seed=1)
    pt = m.predict_proba(Xt)[:, 1]
    assert roc_auc_score(yt, pt) > 0.8
    assert log_loss(yt, pt) < np.log(2)


def test_labels_other_than_0_and_1():
    X, y = linear_data()
    labels = np.where(y == 1, "PD", "Control")
    m = PlattTunedSVM(**SMALL, random_state=0).fit(X, labels)
    assert list(m.classes_) == ["Control", "PD"]
    assert set(m.predict(X)) <= {"Control", "PD"}
    with pytest.raises(ValueError):
        PlattTunedSVM(**SMALL).fit(X, np.zeros(len(y), int))


def test_same_seed_same_model_whatever_the_threads():
    X, y = linear_data()
    a = PlattTunedSVM(**SMALL, random_state=3, n_jobs=1).fit(X, y)
    b = PlattTunedSVM(**SMALL, random_state=3, n_jobs=-1).fit(X, y)
    assert a.best_params_ == b.best_params_
    assert np.allclose(a.predict_proba(X), b.predict_proba(X))


def test_pipeline_log_transforms_and_standardises_inside_the_training_set():
    X, y = linear_data(p=3)
    X[:, 2] = np.exp(X[:, 2])  # skewed, positive: the log step applies to it
    cols = ["a", "b", "swing_time_asymmetry_pct"]
    m = make_svm(log_transform(cols), random_state=0, **SMALL).fit(X, y)
    assert list(m.named_steps) == ["log", "scale", "svm"]
    Z = m.named_steps["log"].transform(X)
    assert np.allclose(Z[:, 2], np.log1p(X[:, 2]))
    assert np.allclose(Z[:, :2], X[:, :2])
    assert np.allclose(m.named_steps["scale"].mean_, Z.mean(axis=0))
    assert list(make_svm(**SMALL).named_steps) == ["scale", "svm"]
