"""The shared evaluation: participants never straddle a split; schemes are deterministic."""

import numpy as np
import pandas as pd
import pytest

from gaitpdb.evaluation import (
    COVARIATES,
    MODEL_FEATURES,
    evaluate,
    fold_metrics,
    leave_one_study_out,
    repeated_grouped_cv,
    summarise,
)


def fake_table(n: int = 90, seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(rng.normal(size=(n, len(MODEL_FEATURES))), columns=MODEL_FEATURES)
    df["Age"] = rng.integers(50, 85, n)
    df["sex_male"] = rng.integers(0, 2, n)
    df["study"] = np.repeat(["Ga", "Ju", "Si"], n // 3)
    df["participant"] = [f"P{i:03d}" for i in range(n)]
    df["y"] = rng.integers(0, 2, n)
    # make the first feature informative so AUC is clearly above chance
    df[MODEL_FEATURES[0]] += 2.0 * df["y"]
    return df


def test_grouped_cv_keeps_participants_apart_and_is_deterministic():
    df = fake_table()
    splits = list(repeated_grouped_cv(df, n_splits=5, n_repeats=2, seed=0))
    assert len(splits) == 10
    for _, _, tr, te in splits:
        assert not set(df["participant"].iloc[tr]) & set(df["participant"].iloc[te])
        assert len(tr) + len(te) == len(df)
    again = list(repeated_grouped_cv(df, n_splits=5, n_repeats=2, seed=0))
    assert all(np.array_equal(a[3], b[3]) for a, b in zip(splits, again))


def test_leave_one_study_out_holds_out_each_study():
    df = fake_table()
    for study, tr, te in leave_one_study_out(df):
        assert set(df["study"].iloc[te]) == {study}
        assert study not in set(df["study"].iloc[tr])


def test_evaluate_and_summarise_shapes():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    def factory():
        return make_pipeline(StandardScaler(), LogisticRegression())

    df = fake_table()
    folds = evaluate(factory, df, MODEL_FEATURES + COVARIATES, "cv", 5, 3, 0)
    assert len(folds) == 15
    s = summarise(folds)
    assert {"auc", "brier", "balanced_accuracy"} <= set(s.index)
    assert s.loc["auc", "mean"] > 0.7
    assert s.loc["auc", "ci_low"] <= s.loc["auc", "mean"] <= s.loc["auc", "ci_high"]
    loso = evaluate(factory, df, MODEL_FEATURES, "loso")
    assert list(loso["fold"]) == ["Ga", "Ju", "Si"]


def test_fold_metrics_perfect_and_chance():
    y = np.array([0, 0, 1, 1])
    perfect = fold_metrics(y, np.array([0.1, 0.2, 0.8, 0.9]))
    assert (
        perfect["auc"] == 1.0
        and perfect["sensitivity"] == 1.0
        and perfect["specificity"] == 1.0
    )
    assert perfect["brier"] == pytest.approx(np.mean([0.01, 0.04, 0.04, 0.01]))
