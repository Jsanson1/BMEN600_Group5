"""The out-of-bag-tuned random forest (task T-019), on synthetic data."""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import log_loss, roc_auc_score

from gaitpdb.evaluation import MODEL_FEATURES
from gaitpdb.forest import MAX_DEPTHS, OOBTunedForest, max_features_grid

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_random_forest.py"
spec = importlib.util.spec_from_file_location("run_random_forest", SCRIPT)
run_rf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_rf)


def data(n=120, signal=2.0, seed=0, p=6):
    rng = np.random.default_rng(seed)
    y = np.r_[np.zeros(n // 2, int), np.ones(n - n // 2, int)]
    X = rng.standard_normal((n, p))
    X[:, 0] += signal * y
    return X, y


def test_max_features_grid_is_relative_to_the_number_of_inputs():
    assert max_features_grid(1) == [1]
    assert max_features_grid(2) == [1, 2]
    assert max_features_grid(6) == [1, 2, 6]
    assert max_features_grid(8) == [1, 3, 8]
    with pytest.raises(ValueError):
        max_features_grid(0)


def test_search_covers_the_grid_and_keeps_the_lowest_oob_loss():
    X, y = data()
    m = OOBTunedForest(n_estimators=60, random_state=1).fit(X, y)
    assert len(m.search_) == len(max_features_grid(6)) * len(MAX_DEPTHS)
    best = m.search_.loc[m.search_["oob_log_loss"].idxmin()]
    assert m.best_params_["max_features"] == best["max_features"]
    assert m.oob_log_loss_ == pytest.approx(best["oob_log_loss"])
    assert m.best_estimator_.max_features == m.best_params_["max_features"]
    assert list(m.classes_) == [0, 1]
    assert m.feature_importances_.argmax() == 0  # the informative input


def test_forest_generalises_and_is_reproducible():
    X, y = data(n=200, seed=2)
    Xt, yt = data(n=200, seed=3)
    a = OOBTunedForest(n_estimators=60, random_state=4).fit(X, y)
    b = OOBTunedForest(n_estimators=60, random_state=4).fit(X, y)
    p = a.predict_proba(Xt)
    assert p.shape == (200, 2) and np.allclose(p.sum(axis=1), 1)
    assert roc_auc_score(yt, p[:, 1]) > 0.85
    assert np.array_equal(p, b.predict_proba(Xt))
    assert set(a.predict(Xt)) <= {0, 1}


def test_parallel_fit_predicts_in_a_fixed_order():
    X, y = data(n=150, seed=6)
    m = OOBTunedForest(n_estimators=80, random_state=0, n_jobs=2).fit(X, y)
    assert m.best_estimator_.n_jobs is None
    trees = m.best_estimator_.estimators_
    total = np.zeros((len(X), 2))
    for tree in trees:  # the order a single thread adds them in
        total += tree.predict_proba(X)
    assert np.array_equal(m.predict_proba(X), total / len(trees))


def test_out_of_bag_loss_is_honest_on_noise():
    X, y = data(signal=0.0, seed=5)
    m = OOBTunedForest(n_estimators=100, random_state=0).fit(X, y)
    in_sample = log_loss(y, np.clip(m.predict_proba(X)[:, 1], 1e-6, 1 - 1e-6))
    # no signal: the out-of-bag loss stays near chance (log 2 = 0.693), while the
    # same forest scored on the rows it was grown on looks far better than it is
    assert m.oob_log_loss_ > 0.62
    assert in_sample < m.oob_log_loss_ - 0.05


def test_needs_both_classes():
    X, y = data()
    with pytest.raises(ValueError, match="both classes"):
        OOBTunedForest(n_estimators=10).fit(X, np.zeros_like(y))


def test_permutation_importance_finds_the_informative_input(monkeypatch):
    X, y = data(n=150, signal=2.5, seed=6, p=len(MODEL_FEATURES))
    df = pd.DataFrame(X, columns=MODEL_FEATURES)
    df["participant"] = [f"P{i:03d}" for i in range(len(y))]
    df["y"] = y

    def fast():
        return OOBTunedForest(max_depths=(3,), n_estimators=40, random_state=0)

    imp = run_rf.permutation_importances(df, MODEL_FEATURES, fast)
    assert list(imp["input"]) == MODEL_FEATURES
    assert imp["permutation_auc_drop"].idxmax() == 0
    assert imp.loc[0, "permutation_auc_drop"] > 0.1
    assert run_rf.describe_setting({"max_depth": None, "max_features": 2}) == (
        "depth full, 2 per split"
    )
