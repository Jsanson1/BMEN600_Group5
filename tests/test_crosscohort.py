"""The cross-dataset evaluation (D-007): splits, operating points, no leakage."""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from gaitpdb.crosscohort import (
    TARGET_SPECIFICITY,
    bootstrap_sensitivity_at_specificity,
    cross_cohort,
    dataset_of_origin,
    pooled_splits,
    predictive_values,
    run_pooled,
    sensitivity_at_specificity,
    stride_matched_tables,
    threshold_at_specificity,
)
from gaitpdb.evaluation import summarise

COLS = ["f1", "f2", "f3"]


def two_datasets(n_a=80, n_b=60, shift_b=0.0, signal=2.0, seed=0) -> pd.DataFrame:
    """Two synthetic datasets; f1 carries the diagnosis, f2 can carry a dataset shift."""
    rng = np.random.default_rng(seed)
    parts = []
    for name, n, prefix, shift in (
        ("gaitpdb", n_a, "G", 0.0),
        ("weargait", n_b, "W", shift_b),
    ):
        d = pd.DataFrame(rng.normal(size=(n, len(COLS))), columns=COLS)
        d["y"] = rng.permutation(np.r_[np.ones(n // 2), np.zeros(n - n // 2)]).astype(
            int
        )
        d["f1"] += signal * d["y"]
        d["f2"] += shift
        d["dataset"] = name
        d["participant"] = [f"{prefix}{i:03d}" for i in range(n)]
        d["study"] = np.where(np.arange(n) % 2 == 0, f"{prefix}s1", f"{prefix}s2")
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def factory():
    return make_pipeline(StandardScaler(), LogisticRegression())


class RecordingModel:
    """A model that remembers which rows it was fitted on (by their f3 value)."""

    fitted_on: list[np.ndarray] = []

    def __init__(self):
        self.inner = factory()

    def fit(self, X, y):
        RecordingModel.fitted_on.append(X[:, 2].copy())
        self.inner.fit(X, y)
        return self

    def predict_proba(self, X):
        return self.inner.predict_proba(X)


def test_pooled_splits_group_stratify_and_cover():
    df = two_datasets()
    seen = {}
    for r, k, tr, te in pooled_splits(df, n_splits=5, n_repeats=2, seed=0):
        assert not set(df["participant"].iloc[tr]) & set(df["participant"].iloc[te])
        assert set(df["dataset"].iloc[te]) == {"gaitpdb", "weargait"}
        share = (df["dataset"].iloc[te] == "weargait").mean()
        assert abs(share - 60 / 140) < 0.1
        for i in te:
            seen[(r, i)] = seen.get((r, i), 0) + 1
    assert len(seen) == 2 * len(df) and set(seen.values()) == {1}


def test_pooled_splits_reject_duplicates_and_unknown_labels():
    df = two_datasets()
    with pytest.raises(ValueError, match="more than one row"):
        list(pooled_splits(pd.concat([df, df.iloc[:1]])))
    bad = df.copy()
    bad.loc[0, "dataset"] = "other"
    with pytest.raises(ValueError, match="unknown dataset"):
        list(pooled_splits(bad))


def test_run_pooled_reports_per_dataset_auc():
    df = two_datasets()
    folds, pred = run_pooled(factory, df, COLS, n_splits=5, n_repeats=2)
    assert len(folds) == 10 and set(folds["scheme"]) == {"pooled"}
    assert folds["auc_gaitpdb"].between(0, 1).all()
    assert folds["auc_weargait"].between(0, 1).all()
    assert folds["auc"].mean() > 0.75
    assert len(pred) == 2 * len(df) and set(pred["dataset"]) == {"gaitpdb", "weargait"}
    assert summarise(folds).loc["auc", "mean"] == pytest.approx(folds["auc"].mean())


def test_roc_point_on_a_known_example():
    y = np.array([0] * 10 + [1] * 10)
    p = np.r_[np.linspace(0.0, 0.45, 10), np.linspace(0.3, 0.9, 10)]
    sens, spec, thr = sensitivity_at_specificity(y, p, 0.9)
    called = p >= thr
    assert spec >= 0.9 and (~called[y == 0]).mean() == pytest.approx(spec)
    assert called[y == 1].mean() == pytest.approx(sens)
    # here the curve rises right after the point, so no lower threshold keeps the target
    lower = np.sort(np.unique(p))
    lower = lower[lower < thr]
    for t in lower:
        assert (p[y == 0] < t).mean() < 0.9
    assert threshold_at_specificity(y, p, 0.9) == thr


def test_roc_point_is_the_corner_not_the_lowest_admissible_threshold():
    # Pull request #16 review: 10 PD scored 0.95 to 0.86, 20 controls at 0.80,
    # 0.79 and then 0.5 or below. Thresholds 0.86, 0.80 and 0.79 all give
    # sensitivity 1 at specificity >= 0.9; the rule returns the corner (0.86,
    # specificity 1.00), not the lowest of them (0.79, specificity 0.90).
    pd_scores = np.round(np.linspace(0.95, 0.86, 10), 2)
    controls = np.r_[0.80, 0.79, np.linspace(0.5, 0.05, 18)]
    y = np.r_[np.ones(10), np.zeros(20)].astype(int)
    p = np.r_[pd_scores, controls]
    sens, spec, thr = sensitivity_at_specificity(y, p, 0.9)
    assert thr == pytest.approx(0.86)
    assert sens == 1.0 and spec == 1.0
    assert threshold_at_specificity(y, p, 0.9) == thr
    assert ((p[y == 0] < 0.79).mean(), (p[y == 1] >= 0.79).mean()) == (0.9, 1.0)


def test_roc_point_needs_both_groups():
    with pytest.raises(ValueError):
        sensitivity_at_specificity(np.ones(5), np.linspace(0, 1, 5))


def test_predictive_values_bayes():
    ppv, npv = predictive_values(0.8, 0.9, 0.01)
    assert ppv == pytest.approx(0.008 / (0.008 + 0.099))
    assert npv == pytest.approx(0.891 / (0.891 + 0.002))
    ppv, npv = predictive_values(0.8, 0.9, 0.5)
    assert ppv == pytest.approx(0.8 / 0.9)
    with pytest.raises(ValueError):
        predictive_values(0.8, 0.9, 1.5)


def test_cross_cohort_never_fits_on_the_test_dataset():
    df = two_datasets(seed=3)
    df["f3"] = np.arange(len(df), dtype=float)  # a row marker the model records
    RecordingModel.fitted_on = []
    out = cross_cohort(RecordingModel, df, COLS, n_boot=200)
    test_rows = set(df.loc[df["dataset"] == "weargait", "f3"])
    for rows in RecordingModel.fitted_on:
        assert not set(rows) & test_rows
    assert out["n_train"] == 80 and out["n_test"] == 60 and out["n_test_pd"] == 30
    assert len(out["predictions"]) == 60
    assert out["auc_low"] <= out["auc"] <= out["auc_high"]
    assert out["auc"] > 0.8  # same distribution in both datasets
    assert out["specificity_roc"] >= TARGET_SPECIFICITY


def test_cross_cohort_transferred_threshold_feels_a_shift():
    # a shift in the informative feature moves every WearGait-PD score up:
    # the ROC-read sensitivity is unchanged, the transferred threshold is not
    base = cross_cohort(factory, two_datasets(seed=5), COLS, n_boot=200)
    shifted_df = two_datasets(seed=5)
    shifted_df.loc[shifted_df["dataset"] == "weargait", "f1"] += 1.5
    shifted = cross_cohort(factory, shifted_df, COLS, n_boot=200)
    assert shifted["auc"] == pytest.approx(base["auc"])
    assert shifted["specificity_transferred"] < base["specificity_transferred"]


def test_dataset_of_origin_detects_a_shift_and_not_its_absence():
    none = summarise(dataset_of_origin(factory, two_datasets(seed=1), COLS, 5, 2))
    shift = summarise(
        dataset_of_origin(factory, two_datasets(shift_b=2.0, seed=1), COLS, 5, 2)
    )
    assert none.loc["auc", "mean"] < 0.65
    assert shift.loc["auc", "mean"] > 0.9


def stride_table(n_participants=3, n_left=50, n_right=40) -> pd.DataFrame:
    rows = []
    for p in range(n_participants):
        for foot, n in (("L", n_left), ("R", n_right)):
            for i in range(n):
                rows.append({"participant": f"P{p}", "foot": foot, "order": i})
    return pd.DataFrame(rows)


def test_stride_matched_tables_respect_counts_and_runs():
    strides = stride_table()
    counts = np.array([[12, 9], [8, 8]])
    tables = list(stride_matched_tables(strides, counts, n_draws=5, seed=0, runs=4))
    assert len(tables) == 5
    for t in tables:
        n = t.groupby(["participant", "foot"]).size().unstack()
        assert set(n.index) == {"P0", "P1", "P2"}
        for p in n.index:
            assert (n.loc[p, "L"], n.loc[p, "R"]) in {(12, 9), (8, 8)}
        for _, g in t.groupby(["participant", "foot"]):
            order = g["order"].to_numpy()
            assert (np.diff(order) > 0).all()  # time order kept
            assert (np.diff(order) > 1).sum() <= 3  # at most four runs


def test_stride_matched_tables_keep_all_when_counts_exceed_and_reproduce():
    strides = stride_table(n_left=5, n_right=5)
    t = next(stride_matched_tables(strides, np.array([[30, 30]]), n_draws=1))
    assert len(t) == len(strides)
    a = list(stride_matched_tables(stride_table(), np.array([[10, 7], [6, 6]]), 3, 7))
    b = list(stride_matched_tables(stride_table(), np.array([[10, 7], [6, 6]]), 3, 7))
    for x, y in zip(a, b):
        pd.testing.assert_frame_equal(x, y)
    with pytest.raises(ValueError):
        next(stride_matched_tables(strides, np.array([10, 7]), 1))


def test_bootstrap_sensitivity_interval_brackets_the_point():
    rng = np.random.default_rng(2)
    y = np.r_[np.zeros(60), np.ones(60)].astype(int)
    p = rng.normal(size=120) + 1.5 * y
    point, lo, hi = bootstrap_sensitivity_at_specificity(y, p, 0.9, n_boot=300, seed=0)
    assert point == sensitivity_at_specificity(y, p, 0.9)[0]
    assert 0 <= lo <= point <= hi <= 1 and hi - lo > 0.05
