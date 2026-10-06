"""The statistics the model comparison relies on, and the files each model writes."""

import numpy as np
import pandas as pd
import pytest
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from gaitpdb.evaluation import (
    MODEL_FEATURES,
    corrected_interval,
    corrected_ttest,
    evaluate_model,
    fold_fingerprint,
    log_transform,
    paired_bootstrap_auc,
    rank_auc,
    summarise,
    write_model_outputs,
)


def small_table(n: int = 90, seed: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(rng.normal(size=(n, len(MODEL_FEATURES))), columns=MODEL_FEATURES)
    df["study"] = np.repeat(["Ga", "Ju", "Si"], n // 3)
    df["participant"] = [f"P{i:03d}" for i in range(n)]
    df["y"] = rng.integers(0, 2, n)
    df[MODEL_FEATURES[0]] += 1.5 * df["y"]
    return df


def factory():
    return make_pipeline(StandardScaler(), LogisticRegression())


def test_corrected_interval_matches_the_formula():
    v = np.array([0.70, 0.80, 0.75, 0.85, 0.65, 0.78, 0.72, 0.81, 0.69, 0.77])
    mean, lo, hi = corrected_interval(v, n_train=80, n_test=20)
    se = np.sqrt((1 / 10 + 20 / 80) * v.var(ddof=1))
    half = stats.t.ppf(0.975, 9) * se
    assert mean == pytest.approx(v.mean())
    assert (lo, hi) == pytest.approx((v.mean() - half, v.mean() + half))
    # wider than the naive interval by exactly sqrt((1/J + n_test/n_train) / (1/J))
    naive = stats.t.ppf(0.975, 9) * v.std(ddof=1) / np.sqrt(10)
    assert half / naive == pytest.approx(np.sqrt(3.5))


def test_corrected_ttest_sign_symmetry_and_edge_cases():
    d = np.random.default_rng(0).normal(0.05, 0.03, 100)
    up, down = corrected_ttest(d, 132, 33), corrected_ttest(-d, 132, 33)
    assert up["t"] > 0 and down["t"] == pytest.approx(-up["t"])
    assert up["p"] == pytest.approx(down["p"])
    assert up["ci_low"] < up["mean_difference"] < up["ci_high"]
    assert up["df"] == 99
    same = corrected_ttest(np.zeros(100), 132, 33)
    assert same["t"] == 0 and same["p"] == 1
    constant = corrected_ttest(np.full(100, 0.25), 132, 33)  # exact in binary
    assert constant["t"] == np.inf and constant["p"] == 0


def test_rank_auc_equals_sklearn_with_and_without_ties():
    rng = np.random.default_rng(4)
    for i in range(200):
        y = rng.integers(0, 2, 60)
        if y.min() == y.max():
            continue
        p = rng.normal(size=60)
        if i % 2:
            p = np.round(p, 1)
        assert rank_auc(y, p) == pytest.approx(roc_auc_score(y, p), abs=1e-12)


def test_paired_bootstrap_auc():
    rng = np.random.default_rng(5)
    y = rng.integers(0, 2, 120)
    good = y + rng.normal(0, 0.5, 120)
    noise = rng.normal(0, 1, 120)
    d, lo, hi = paired_bootstrap_auc(y, good, good, n_boot=200)
    assert (d, lo, hi) == (0.0, 0.0, 0.0)
    d, lo, hi = paired_bootstrap_auc(y, good, noise, n_boot=200)
    assert lo > 0 and d == pytest.approx(
        roc_auc_score(y, good) - roc_auc_score(y, noise)
    )


def test_fold_fingerprint_depends_on_the_set_only():
    assert fold_fingerprint(["P2", "P1"]) == fold_fingerprint(["P1", "P2"])
    assert fold_fingerprint(["P1", "P2"]) != fold_fingerprint(["P1", "P3"])


def test_evaluate_model_tables_and_files(tmp_path):
    df = small_table()
    result = evaluate_model(factory, df, MODEL_FEATURES, "test: gait only", n_repeats=2)
    folds = result["folds"]
    assert len(folds) == 10 and set(folds["model"]) == {"test: gait only"}
    assert (folds["n_train"] + folds["n_test"] == len(df)).all()
    assert folds.groupby("repeat")["test_ids"].nunique().eq(5).all()
    for kind in ("cv_predictions", "loso_predictions"):
        table = result[kind]
        assert list(table["participant"]) == list(df["participant"])
        assert (table["y"].to_numpy() == df["y"].to_numpy()).all()
        assert table["p"].between(0, 1).all()
    assert (result["cv_predictions"]["n_repeats"] == 2).all()
    s = summarise(folds)
    assert {"ci_low", "ci_high", "repeat_low", "repeat_high"} <= set(s.columns)
    assert (s["ci_low"] >= 0).all() and (s["ci_high"] <= 1).all()
    paths = write_model_outputs([result], tmp_path, "test")
    assert [p.name for p in paths] == [
        "test_folds.csv",
        "test_cv_predictions.csv",
        "test_loso_predictions.csv",
    ]
    again = pd.read_csv(paths[0])
    assert len(again) == 10 and "test_ids" in again.columns


def test_log_transform_touches_only_the_listed_input():
    cols = ["stride_time_cv_pct", "swing_time_asymmetry_pct"]
    X = np.array([[2.0, 3.0], [4.0, 0.0]])
    out = log_transform(cols).fit_transform(X)
    assert out[:, 0] == pytest.approx(X[:, 0])
    assert out[:, 1] == pytest.approx(np.log1p(X[:, 1]))
    assert X[0, 1] == 3.0  # the input array is not modified in place
