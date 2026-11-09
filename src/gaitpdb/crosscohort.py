"""Evaluation across the two datasets (DECISIONS.md D-007), shared by every model.

``gaitpdb.evaluation`` judges a model inside gaitpdb. D-007 adds a second
dataset, WearGait-PD, and three ways of using it, all here so the logistic
regression, the SVM and the random forest are judged identically:

* ``run_pooled``: the two datasets combined in repeated participant-grouped
  cross-validation, stratified by diagnosis and by dataset, so every fold holds
  both datasets in their overall proportions (``pooled_splits``). Each fold also
  reports the AUC inside each dataset's share of the test participants.
* ``cross_cohort``: a model fitted once on every gaitpdb participant (any
  tuning stays inside gaitpdb) and applied once to every WearGait-PD
  participant, with no further tuning. The plan's research gap rests on this
  test; the pooled analysis above is its main analysis (DECISIONS.md D-007).
* ``dataset_of_origin``: can a model tell which dataset a participant comes
  from, using the same inputs? If it can, the pooled result may partly reflect
  the source rather than the disease.

The screening measures the Midterm Research Plan names are here too:
sensitivity at a fixed specificity (90%), read off the ROC curve
(``sensitivity_at_specificity``) or with the threshold carried over from the
training dataset (``threshold_at_specificity``), and the predictive values at a
chosen prevalence by Bayes' theorem (``predictive_values``).

``stride_matched_tables`` supports a sensitivity analysis. Under D-011 the two
datasets keep different numbers of clean strides per participant (WearGait-PD's
walkway passes are short), and the variability and asymmetry features shift
with the number of strides they are computed from. Each yielded copy of the
gaitpdb clean-stride table keeps, for every participant, only as many clean
strides per foot as a randomly drawn WearGait-PD participant has; computing the
features from those copies shows how much of a cross-cohort difference stride
count alone would produce.

A feature table here has one row per participant with ``participant``,
``dataset`` ("gaitpdb" or "weargait"), ``study`` (the gaitpdb sub-study or the
WearGait-PD site), ``y`` (1 = PD) and the model's input columns.
"""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve
from sklearn.model_selection import StratifiedGroupKFold

from .evaluation import (
    N_REPEATS,
    N_SPLITS,
    SEED,
    Factory,
    bootstrap_auc,
    cv_predictions,
    fold_fingerprint,
    fold_metrics,
    rank_auc,
)

TRAIN_DATASET = "gaitpdb"
TEST_DATASET = "weargait"
DATASETS = (TRAIN_DATASET, TEST_DATASET)
TARGET_SPECIFICITY = 0.90
"""The operating point the plan emphasises for screening: sensitivity at 90% specificity."""


def _check(df: pd.DataFrame) -> None:
    missing = {"participant", "dataset", "y"} - set(df.columns)
    if missing:
        raise ValueError(f"feature table lacks {sorted(missing)}")
    unknown = set(df["dataset"]) - set(DATASETS)
    if unknown:
        raise ValueError(f"unknown dataset labels {sorted(unknown)}")
    if df.duplicated(["dataset", "participant"]).any():
        raise ValueError("more than one row per participant")


def _groups(df: pd.DataFrame) -> np.ndarray:
    return (df["dataset"] + ":" + df["participant"].astype(str)).to_numpy()


def pooled_splits(
    df: pd.DataFrame,
    n_splits: int = N_SPLITS,
    n_repeats: int = N_REPEATS,
    seed: int = SEED,
) -> Iterator[tuple[int, int, np.ndarray, np.ndarray]]:
    """Yield (repeat, fold, train_idx, test_idx) over both datasets combined.

    Stratified by diagnosis within dataset (four strata), grouped by participant,
    shuffled with seeds ``seed`` to ``seed + n_repeats - 1``.
    """
    _check(df)
    strata = df["y"].to_numpy() + 2 * (df["dataset"] == TEST_DATASET).to_numpy()
    groups = _groups(df)
    for r in range(n_repeats):
        splitter = StratifiedGroupKFold(
            n_splits=n_splits, shuffle=True, random_state=seed + r
        )
        for k, (tr, te) in enumerate(splitter.split(df, strata, groups=groups)):
            yield r, k, tr, te


def _auc_or_nan(y: np.ndarray, p: np.ndarray) -> float:
    return rank_auc(y, p) if 0 < y.sum() < len(y) else np.nan


def run_pooled(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    n_splits: int = N_SPLITS,
    n_repeats: int = N_REPEATS,
    seed: int = SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train and test a model under the pooled scheme.

    Returns (folds, predictions) in the shape of ``evaluation.run_scheme``, with
    ``scheme`` = "pooled"; each fold row adds ``auc_gaitpdb`` and
    ``auc_weargait``, the AUC inside each dataset's test participants, and the
    prediction rows add ``dataset``.
    """
    X = df[columns].to_numpy(dtype=float)
    y = df["y"].to_numpy()
    ds = df["dataset"].to_numpy()
    fold_rows, predictions = [], []
    for r, k, tr, te in pooled_splits(df, n_splits, n_repeats, seed):
        model = factory()
        model.fit(X[tr], y[tr])
        p = model.predict_proba(X[te])[:, 1]
        row = {"scheme": "pooled", "repeat": f"{r}", "fold": f"{k}"}
        row.update(fold_metrics(y[te], p))
        for name in DATASETS:
            m = ds[te] == name
            row[f"auc_{name}"] = _auc_or_nan(y[te][m], p[m])
        row["n_train"] = int(len(tr))
        row["test_ids"] = fold_fingerprint(_groups(df)[te])
        fold_rows.append(row)
        predictions.append(
            pd.DataFrame(
                {
                    "repeat": f"{r}",
                    "fold": f"{k}",
                    "participant": df["participant"].iloc[te].to_numpy(),
                    "dataset": ds[te],
                    "study": df["study"].iloc[te].to_numpy(),
                    "y": y[te],
                    "p": p,
                }
            )
        )
    return pd.DataFrame(fold_rows), pd.concat(predictions, ignore_index=True)


def threshold_at_specificity(
    y_true: np.ndarray, p: np.ndarray, target: float = TARGET_SPECIFICITY
) -> float:
    """Threshold of the point ``sensitivity_at_specificity`` reads off the ROC curve.

    A participant is called PD when p >= threshold. The point is the last one
    with specificity >= ``target`` on the curve as ``roc_curve`` returns it by
    default (``drop_intermediate=True``, which keeps only the points where the
    curve turns). With no score tied between the groups, its sensitivity is the
    highest available at that specificity, and the threshold is the highest one
    that reaches that sensitivity: the corner of the curve, not the lowest
    threshold with specificity >= ``target``. Its specificity can therefore be
    above ``target`` (``tests/test_crosscohort.py`` has an example). The
    cross-cohort analysis used this rule as it is, and it was kept after the
    WearGait-PD results were known rather than changed afterwards.
    """
    return _roc_point(y_true, p, target)[2]


def sensitivity_at_specificity(
    y_true: np.ndarray, p: np.ndarray, target: float = TARGET_SPECIFICITY
) -> tuple[float, float, float]:
    """(sensitivity, achieved specificity, threshold) at specificity >= ``target``.

    Read off the ROC curve of these predictions (see ``threshold_at_specificity``
    for which point: the achieved specificity can be above ``target``), so it
    describes this test set at its own best threshold; ``cross_cohort`` also reports the threshold
    carried over from training, which is what a deployed tool would use.
    """
    return _roc_point(y_true, p, target)


def _roc_point(
    y_true: np.ndarray, p: np.ndarray, target: float
) -> tuple[float, float, float]:
    y = np.asarray(y_true)
    if not 0 < y.sum() < len(y):
        raise ValueError("need both groups to read a point off the ROC curve")
    fpr, tpr, thr = roc_curve(y, np.asarray(p, dtype=float))
    ok = np.flatnonzero(fpr <= 1.0 - target + 1e-12)
    i = ok[-1]  # fpr rises along the curve: the last admissible point
    return float(tpr[i]), float(1.0 - fpr[i]), float(thr[i])


def bootstrap_sensitivity_at_specificity(
    y_true: np.ndarray,
    p: np.ndarray,
    target: float = TARGET_SPECIFICITY,
    n_boot: int = 2000,
    seed: int = SEED,
) -> tuple[float, float, float]:
    """ROC-read sensitivity at ``target`` specificity with a percentile bootstrap
    interval over participants (resamples holding one group only are skipped)."""
    y = np.asarray(y_true)
    p = np.asarray(p, dtype=float)
    point = sensitivity_at_specificity(y, p, target)[0]
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        if 0 < y[idx].sum() < len(idx):
            vals.append(_roc_point(y[idx], p[idx], target)[0])
    return point, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def predictive_values(
    sensitivity: float, specificity: float, prevalence: float
) -> tuple[float, float]:
    """(PPV, NPV) at ``prevalence``, by Bayes' theorem (Midterm Research Plan, Eq. 1-2).

    Sensitivity and specificity do not depend on prevalence; the predictive
    values do, so they are recalculated at the prevalence of the intended
    population rather than taken from a sample that is about half PD.
    """
    if not 0.0 <= prevalence <= 1.0:
        raise ValueError("prevalence must be between 0 and 1")
    tp = sensitivity * prevalence
    fp = (1.0 - specificity) * (1.0 - prevalence)
    tn = specificity * (1.0 - prevalence)
    fn = (1.0 - sensitivity) * prevalence
    ppv = tp / (tp + fp) if tp + fp > 0 else np.nan
    npv = tn / (tn + fn) if tn + fn > 0 else np.nan
    return float(ppv), float(npv)


def cross_cohort(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    target_specificity: float = TARGET_SPECIFICITY,
    n_splits: int = N_SPLITS,
    seed: int = SEED,
    n_boot: int = 2000,
) -> dict:
    """Fit on every gaitpdb participant, apply once to every WearGait-PD participant.

    Returns a dict with ``predictions`` (one row per WearGait-PD participant:
    participant, study, y, p), ``auc`` with its 95% participant-bootstrap
    interval (``auc_low``, ``auc_high``), the ROC-read ``sensitivity_at_spec``
    (with the achieved ``specificity_roc``), and the transferred operating
    point: ``threshold`` is the lowest threshold reaching ``target_specificity``
    among gaitpdb's out-of-fold predictions (one repeat of the shared
    cross-validation, so the threshold never comes from a model that saw the
    participant), and ``sensitivity_transferred`` and
    ``specificity_transferred`` are what that threshold gives in WearGait-PD.
    """
    _check(df)
    train = df[df["dataset"] == TRAIN_DATASET].reset_index(drop=True)
    test = df[df["dataset"] == TEST_DATASET].reset_index(drop=True)
    if train.empty or test.empty:
        raise ValueError("need both datasets")
    model = factory()
    model.fit(train[columns].to_numpy(dtype=float), train["y"].to_numpy())
    p = model.predict_proba(test[columns].to_numpy(dtype=float))[:, 1]
    y = test["y"].to_numpy()

    oof = cv_predictions(factory, train, columns, n_splits, seed)
    threshold = threshold_at_specificity(
        oof["y"].to_numpy(), oof["p"].to_numpy(), target_specificity
    )
    called = p >= threshold
    auc, lo, hi = bootstrap_auc(y, p, n_boot=n_boot, seed=seed)
    sens_roc, spec_roc, _ = sensitivity_at_specificity(y, p, target_specificity)
    return {
        "predictions": pd.DataFrame(
            {
                "participant": test["participant"],
                "study": test["study"],
                "y": y,
                "p": p,
            }
        ),
        "auc": auc,
        "auc_low": lo,
        "auc_high": hi,
        "sensitivity_at_spec": sens_roc,
        "specificity_roc": spec_roc,
        "threshold": threshold,
        "sensitivity_transferred": float(called[y == 1].mean()),
        "specificity_transferred": float((~called[y == 0]).mean()),
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "n_test_pd": int(y.sum()),
    }


def dataset_of_origin(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    n_splits: int = N_SPLITS,
    n_repeats: int = N_REPEATS,
    seed: int = SEED,
) -> pd.DataFrame:
    """Cross-validated check of whether the inputs identify the dataset.

    The label is 1 for WearGait-PD, 0 for gaitpdb; folds are the pooled ones
    (``pooled_splits``), so diagnosis is balanced across folds as well. Returns
    one row of metrics per fold with ``scheme`` = "origin" (``evaluation.summarise``
    accepts it); an AUC near 0.5 means the inputs carry little information about
    the source, an AUC near 1 that the datasets are separable.
    """
    X = df[columns].to_numpy(dtype=float)
    origin = (df["dataset"] == TEST_DATASET).astype(int).to_numpy()
    rows = []
    for r, k, tr, te in pooled_splits(df, n_splits, n_repeats, seed):
        model = factory()
        model.fit(X[tr], origin[tr])
        p = model.predict_proba(X[te])[:, 1]
        row = {"scheme": "origin", "repeat": f"{r}", "fold": f"{k}"}
        row.update(fold_metrics(origin[te], p))
        row["n_train"] = int(len(tr))
        rows.append(row)
    return pd.DataFrame(rows)


def stride_matched_tables(
    strides: pd.DataFrame,
    counts: np.ndarray,
    n_draws: int,
    seed: int = SEED,
    runs: int = 4,
) -> Iterator[pd.DataFrame]:
    """Yield ``n_draws`` copies of a clean-stride table cut to WearGait-PD's stride counts.

    ``strides`` holds the clean strides to keep from (one row per stride, with
    ``participant`` and ``foot``, in time order within each participant and
    foot). ``counts`` is an array of shape (m, 2): the clean strides on the left
    and right foot of each of the m WearGait-PD participants included under
    D-011. In each copy, every participant gets the counts of one WearGait-PD
    participant drawn at random, and keeps that many strides per foot, taken as
    ``runs`` runs of consecutive strides from evenly spaced stretches of the
    walk (WearGait-PD's strides come from separate walkway passes). A foot with
    fewer strides than drawn keeps them all. Draw d uses the generator seeded
    ``seed + d``, so each copy can be reproduced on its own.
    """
    counts = np.asarray(counts, dtype=int)
    if counts.ndim != 2 or counts.shape[1] != 2 or len(counts) == 0:
        raise ValueError("counts must be an (m, 2) array of left and right counts")
    groups = strides.groupby(["participant", "foot"], sort=True).indices
    participants = sorted({p for p, _ in groups})
    for d in range(n_draws):
        rng = np.random.default_rng(seed + d)
        keep = []
        for p in participants:
            n_left, n_right = counts[rng.integers(len(counts))]
            for foot, n in (("L", n_left), ("R", n_right)):
                idx = groups.get((p, foot))
                if idx is None:
                    continue
                keep.append(idx[_runs(len(idx), int(n), runs, rng)])
        yield strides.iloc[np.sort(np.concatenate(keep))].reset_index(drop=True)


def _runs(m: int, n: int, runs: int, rng: np.random.Generator) -> np.ndarray:
    """Positions of ``n`` of ``m`` strides as runs from ``runs`` even stretches."""
    if n >= m:
        return np.arange(m)
    k = max(1, min(runs, n))
    stretches = np.array_split(np.arange(m), k)
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    out = []
    for stretch, size in zip(stretches, sizes):
        start = int(rng.integers(0, len(stretch) - size + 1))
        out.extend(stretch[start : start + size])
    return np.array(out, dtype=int)
