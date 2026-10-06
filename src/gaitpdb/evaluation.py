"""The evaluation every model in this project shares.

The point of the project is that a classifier is judged the way a screening
tool would be used: on people it has never seen, and on recording protocols it
has never seen. This module fixes that evaluation once so the three models
(logistic regression, support vector machine, random forest) are compared on
exactly the same participants, splits, features and metrics.

* ``MODEL_FEATURES`` are the gait features a model may use, one row per
  participant (the usual walk). ``COVARIATES`` are age and sex, which the
  groups differ on. Study is never a feature, because the cross-protocol
  evaluation holds a study out.
* ``repeated_grouped_cv`` yields stratified k-fold splits of participants,
  repeated with different shuffles; a participant is never in both halves.
* ``leave_one_study_out`` trains on two of the Ga, Ju and Si sub-studies and
  tests on the third.
* ``evaluate`` runs a model factory through either scheme and returns one row
  of metrics per fold; ``summarise`` turns those rows into point estimates
  with 95% intervals.

A "model factory" is a function with no arguments returning an unfitted
scikit-learn estimator (usually a Pipeline with its own scaling and tuning),
so every fold trains a fresh model and any hyper-parameter search happens
inside the training participants only.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

MODEL_FEATURES = [
    "stride_time_mean_s",
    "stride_time_cv_pct",
    "swing_time_cv_pct",
    "swing_pct_mean",
    "stride_time_asymmetry_pct",
    "swing_time_asymmetry_pct",
]
"""Six timing features. Cadence, mean swing time and mean stance time are left out
because they are functions of the others (cadence is 60 / stride time; swing and
stance sum to the stride), which would add nothing but collinearity."""

COVARIATES = ["Age", "sex_male"]
STUDIES = ("Ga", "Ju", "Si")
POSITIVE = "PD"
THRESHOLD = 0.5
Factory = Callable[[], BaseEstimator]


def load_feature_table(path: str) -> pd.DataFrame:
    """Read results/features_usual_walk.csv (one usual-walk record per participant).

    Adds ``sex_male`` (1 = male) and ``y`` (1 = PD) and drops participants with a
    missing feature or covariate, reporting how many.
    """
    df = pd.read_csv(path)
    df["sex_male"] = (df["sex"] == "M").astype(int)
    df["y"] = (df["group"] == POSITIVE).astype(int)
    needed = MODEL_FEATURES + COVARIATES
    complete = df.dropna(subset=needed)
    dropped = len(df) - len(complete)
    if dropped:
        print(
            f"note: {dropped} participants dropped for a missing feature or covariate"
        )
    return complete.reset_index(drop=True)


def repeated_grouped_cv(
    df: pd.DataFrame, n_splits: int = 5, n_repeats: int = 20, seed: int = 0
) -> Iterator[tuple[int, int, np.ndarray, np.ndarray]]:
    """Yield (repeat, fold, train_idx, test_idx), stratified by group, grouped by participant."""
    for r in range(n_repeats):
        splitter = StratifiedGroupKFold(
            n_splits=n_splits, shuffle=True, random_state=seed + r
        )
        for k, (tr, te) in enumerate(
            splitter.split(df, df["y"], groups=df["participant"])
        ):
            yield r, k, tr, te


def leave_one_study_out(
    df: pd.DataFrame,
) -> Iterator[tuple[str, np.ndarray, np.ndarray]]:
    """Yield (held-out study, train_idx, test_idx) for each of Ga, Ju and Si."""
    for study in STUDIES:
        te = np.flatnonzero(df["study"] == study)
        tr = np.flatnonzero(df["study"] != study)
        yield study, tr, te


def fold_metrics(y_true: np.ndarray, p: np.ndarray) -> dict:
    """AUC, balanced accuracy, sensitivity and specificity at THRESHOLD."""
    pred = (p >= THRESHOLD).astype(int)
    pos, neg = y_true == 1, y_true == 0
    return {
        "auc": roc_auc_score(y_true, p),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
        "sensitivity": float(pred[pos].mean()) if pos.any() else np.nan,
        "specificity": float(1 - pred[neg].mean()) if neg.any() else np.nan,
        "n_test": int(len(y_true)),
        "n_test_pd": int(pos.sum()),
    }


def evaluate(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    scheme: str = "cv",
    n_splits: int = 5,
    n_repeats: int = 20,
    seed: int = 0,
) -> pd.DataFrame:
    """Train and test a model under one scheme; one row of metrics per fold.

    ``scheme`` is "cv" (repeated participant-grouped cross-validation) or "loso"
    (leave-one-study-out). ``columns`` are the input columns of ``df`` the model
    sees, in order.
    """
    X = df[columns].to_numpy(dtype=float)
    y = df["y"].to_numpy()
    rows = []
    if scheme == "cv":
        splits = (
            (f"{r}", f"{k}", tr, te)
            for r, k, tr, te in repeated_grouped_cv(df, n_splits, n_repeats, seed)
        )
    elif scheme == "loso":
        splits = (("loso", study, tr, te) for study, tr, te in leave_one_study_out(df))
    else:
        raise ValueError(f"unknown scheme {scheme!r}")
    for repeat, fold, tr, te in splits:
        model = factory()
        model.fit(X[tr], y[tr])
        p = model.predict_proba(X[te])[:, 1]
        row = {"scheme": scheme, "repeat": repeat, "fold": fold}
        row.update(fold_metrics(y[te], p))
        rows.append(row)
    return pd.DataFrame(rows)


def summarise(folds: pd.DataFrame) -> pd.DataFrame:
    """Point estimate and 95% interval for each metric.

    For repeated cross-validation the unit is the repeat: each metric is first
    averaged over the folds of a repeat, then the mean and the 2.5th and 97.5th
    percentiles over repeats are reported, so the interval reflects how much
    the answer depends on how participants were split. For leave-one-study-out
    there is one fold per study and no interval; use ``bootstrap_auc`` for one.
    """
    metrics = ["auc", "balanced_accuracy", "sensitivity", "specificity"]
    if folds["scheme"].iloc[0] == "loso":
        out = folds.set_index("fold")[metrics + ["n_test", "n_test_pd"]]
        return out
    per_repeat = folds.groupby("repeat")[metrics].mean()
    out = pd.DataFrame(
        {
            "mean": per_repeat.mean(),
            "ci_low": per_repeat.quantile(0.025),
            "ci_high": per_repeat.quantile(0.975),
            "sd_over_repeats": per_repeat.std(ddof=1),
        }
    )
    out["n_repeats"] = len(per_repeat)
    return out


def bootstrap_auc(
    y_true: np.ndarray, p: np.ndarray, n_boot: int = 2000, seed: int = 0
) -> tuple[float, float, float]:
    """AUC with a percentile bootstrap interval over the test participants."""
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    p = np.asarray(p)
    point = roc_auc_score(y_true, p)
    vals = []
    n = len(y_true)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if y_true[idx].min() == y_true[idx].max():
            continue
        vals.append(roc_auc_score(y_true[idx], p[idx]))
    return point, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def loso_predictions(
    factory: Factory, df: pd.DataFrame, columns: list[str]
) -> pd.DataFrame:
    """Out-of-study predicted probabilities for every participant (for bootstrap intervals)."""
    X = df[columns].to_numpy(dtype=float)
    y = df["y"].to_numpy()
    p = np.full(len(df), np.nan)
    for _, tr, te in leave_one_study_out(df):
        model = factory()
        model.fit(X[tr], y[tr])
        p[te] = model.predict_proba(X[te])[:, 1]
    return pd.DataFrame(
        {"participant": df["participant"], "study": df["study"], "y": y, "p": p}
    )
