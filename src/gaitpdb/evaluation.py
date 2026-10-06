"""The evaluation every model in this project shares.

The point of the project is that a classifier is judged the way a screening
tool would be used: on people it has never seen, and on recording protocols it
has never seen. This module fixes that evaluation once so the three models
(logistic regression, support vector machine, random forest) are compared on
exactly the same participants, splits, features and metrics.

* ``MODEL_FEATURES`` are the gait features a model may use, one row per
  participant (the usual walk). ``COVARIATES`` are age and sex, which the
  groups differ on. Study is never a feature, because the cross-protocol
  evaluation holds a study out. ``LOG_TRANSFORMED`` lists the inputs that
  enter as log(1 + x), applied by the ``log_transform`` pipeline step.
* ``repeated_grouped_cv`` yields stratified k-fold splits of participants,
  repeated with different shuffles; a participant is never in both halves.
  ``N_SPLITS``, ``N_REPEATS`` and ``SEED`` fix the splits for every model.
* ``leave_one_study_out`` trains on two of the Ga, Ju and Si sub-studies and
  tests on the third.
* ``evaluate_model`` runs a model factory through both schemes and returns
  what the model comparison needs: one row of metrics per cross-validation
  fold, each participant's out-of-fold probability averaged over the repeats,
  and each participant's out-of-study probability. ``write_model_outputs``
  saves them as ``<prefix>_folds.csv``, ``<prefix>_cv_predictions.csv`` and
  ``<prefix>_loso_predictions.csv`` in ``results/``, which is where
  ``scripts/compare_models.py`` looks. ``run_scheme`` and ``evaluate`` are the
  lower-level pieces.
* ``summarise`` turns the fold rows into a mean and a 95% interval for each
  metric; ``corrected_interval`` and ``corrected_ttest`` hold the variance
  correction for repeated cross-validation; ``bootstrap_auc`` and
  ``paired_bootstrap_auc`` resample participants.

Uncertainty. The folds of repeated cross-validation share most of their
training participants, so the spread of the fold or repeat results understates
how much the estimate would change with a new sample of participants. The
intervals here therefore use the correction of Nadeau and Bengio (2003): the
variance of a mean over J = k x r folds is (1/J + n_test/n_train) times the
sample variance of the J fold results, with Student's t on J - 1 degrees of
freedom. Bouckaert and Frank (2004) give this form for repeated k-fold
cross-validation and recommend it over the uncorrected test. The spread over
repeats is still reported, as a measure of how much the result moves with the
split alone.

A "model factory" is a function with no arguments returning an unfitted
scikit-learn estimator (usually a Pipeline with its own scaling and tuning),
so every fold trains a fresh model and any hyper-parameter search happens
inside the training participants only.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import BaseEstimator
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import FunctionTransformer

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

LOG_TRANSFORMED = ["swing_time_asymmetry_pct"]
"""Inputs that enter the models as log(1 + x). Swing-time asymmetry is skewed and
bounded at zero, and on the raw value the logistic regression's linearity check
fails (results/logreg_summary.txt); trees are unaffected by the transform."""

COVARIATES = ["Age", "sex_male"]
STUDIES = ("Ga", "Ju", "Si")
POSITIVE = "PD"
THRESHOLD = 0.5
METRICS = ["auc", "brier", "balanced_accuracy", "sensitivity", "specificity"]
N_SPLITS, N_REPEATS, SEED = 5, 20, 0
"""The splits every model uses: 5 folds, 20 repeats, shuffles seeded 0 to 19."""
Factory = Callable[[], BaseEstimator]


def log_transform(columns: list[str]) -> FunctionTransformer:
    """A pipeline step applying log(1 + x) to the LOG_TRANSFORMED inputs among ``columns``.

    ``columns`` are the model's input columns in order, the same list passed to
    ``evaluate_model``; inputs not in LOG_TRANSFORMED pass through unchanged.
    """
    idx = [i for i, c in enumerate(columns) if c in LOG_TRANSFORMED]

    def f(A):
        A = np.array(A, dtype=float, copy=True)
        A[:, idx] = np.log1p(A[:, idx])
        return A

    return FunctionTransformer(f)


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
    if complete["participant"].duplicated().any():
        raise ValueError(
            "more than one row per participant: the inner tuning in the model scripts "
            "uses a plain stratified split and would leak; group it by participant first"
        )
    return complete.reset_index(drop=True)


def repeated_grouped_cv(
    df: pd.DataFrame,
    n_splits: int = N_SPLITS,
    n_repeats: int = N_REPEATS,
    seed: int = SEED,
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
    """AUC, balanced accuracy, sensitivity and specificity at THRESHOLD, Brier score."""
    pred = (p >= THRESHOLD).astype(int)
    pos, neg = y_true == 1, y_true == 0
    return {
        "auc": roc_auc_score(y_true, p),
        "brier": brier_score_loss(y_true, p),
        "balanced_accuracy": balanced_accuracy_score(y_true, pred),
        "sensitivity": float(pred[pos].mean()) if pos.any() else np.nan,
        "specificity": float(1 - pred[neg].mean()) if neg.any() else np.nan,
        "n_test": int(len(y_true)),
        "n_test_pd": int(pos.sum()),
    }


def fold_fingerprint(participants: Iterable) -> str:
    """A short hash of the participant IDs in a test fold.

    Two models can only be compared fold by fold if they were tested on the same
    participants; the comparison script checks these hashes before pairing folds.
    """
    text = "\n".join(sorted(str(p) for p in participants))
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def run_scheme(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    scheme: str = "cv",
    n_splits: int = N_SPLITS,
    n_repeats: int = N_REPEATS,
    seed: int = SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Train and test a model under one scheme.

    Returns (folds, predictions): one row of metrics per test fold, and one row
    per test participant per fold with the predicted probability of PD.
    ``scheme`` is "cv" (repeated participant-grouped cross-validation) or "loso"
    (leave-one-study-out). ``columns`` are the input columns of ``df`` the model
    sees, in order.
    """
    X = df[columns].to_numpy(dtype=float)
    y = df["y"].to_numpy()
    if scheme == "cv":
        splits = (
            (f"{r}", f"{k}", tr, te)
            for r, k, tr, te in repeated_grouped_cv(df, n_splits, n_repeats, seed)
        )
    elif scheme == "loso":
        splits = (("loso", study, tr, te) for study, tr, te in leave_one_study_out(df))
    else:
        raise ValueError(f"unknown scheme {scheme!r}")
    fold_rows, predictions = [], []
    for repeat, fold, tr, te in splits:
        model = factory()
        model.fit(X[tr], y[tr])
        p = model.predict_proba(X[te])[:, 1]
        row = {"scheme": scheme, "repeat": repeat, "fold": fold}
        row.update(fold_metrics(y[te], p))
        row["n_train"] = int(len(tr))
        row["test_ids"] = fold_fingerprint(df["participant"].iloc[te])
        fold_rows.append(row)
        predictions.append(
            pd.DataFrame(
                {
                    "repeat": repeat,
                    "fold": fold,
                    "participant": df["participant"].iloc[te].to_numpy(),
                    "study": df["study"].iloc[te].to_numpy(),
                    "y": y[te],
                    "p": p,
                }
            )
        )
    return pd.DataFrame(fold_rows), pd.concat(predictions, ignore_index=True)


def evaluate(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    scheme: str = "cv",
    n_splits: int = N_SPLITS,
    n_repeats: int = N_REPEATS,
    seed: int = SEED,
) -> pd.DataFrame:
    """One row of metrics per fold under one scheme (``run_scheme`` without the predictions)."""
    return run_scheme(factory, df, columns, scheme, n_splits, n_repeats, seed)[0]


def evaluate_model(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    name: str,
    n_splits: int = N_SPLITS,
    n_repeats: int = N_REPEATS,
    seed: int = SEED,
) -> dict[str, pd.DataFrame]:
    """Everything the model comparison needs for one model, under both schemes.

    ``name`` identifies the model in the comparison as "<family>: <inputs>", for
    example "rf: gait only". Returns three tables, each with a ``model`` column:

    * "folds": one row of metrics per cross-validation fold (k x r rows);
    * "cv_predictions": each participant's out-of-fold probability averaged over
      the r repeats (every repeat predicts every participant exactly once);
    * "loso_predictions": each participant's probability from the model trained
      on the other two sub-studies.

    Both prediction tables are in the row order of ``df``.
    """
    folds, cv_pred = run_scheme(factory, df, columns, "cv", n_splits, n_repeats, seed)
    _, loso_pred = run_scheme(factory, df, columns, "loso")
    order = df["participant"].to_numpy()
    oof = (
        cv_pred.groupby("participant")
        .agg(
            study=("study", "first"),
            y=("y", "first"),
            p=("p", "mean"),
            n_repeats=("p", "size"),
        )
        .loc[order]
        .reset_index()
    )
    loso = (
        loso_pred.set_index("participant").loc[order, ["study", "y", "p"]].reset_index()
    )
    for table in (folds, oof, loso):
        table.insert(0, "model", name)
    return {"folds": folds, "cv_predictions": oof, "loso_predictions": loso}


def write_model_outputs(
    results: list[dict[str, pd.DataFrame]], out_dir: str | Path, prefix: str
) -> list[Path]:
    """Save several ``evaluate_model`` results for the comparison script.

    Writes ``<out_dir>/<prefix>_folds.csv``, ``<prefix>_cv_predictions.csv`` and
    ``<prefix>_loso_predictions.csv`` (one block of rows per model) and returns
    the paths.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for kind in ("folds", "cv_predictions", "loso_predictions"):
        path = out / f"{prefix}_{kind}.csv"
        pd.concat([r[kind] for r in results], ignore_index=True).to_csv(
            path, index=False
        )
        paths.append(path)
    return paths


def corrected_interval(
    values: Iterable[float], n_train: float, n_test: float, level: float = 0.95
) -> tuple[float, float, float]:
    """Mean of J cross-validation fold results with the corrected interval.

    The variance of the mean is (1/J + n_test/n_train) * s^2, where s^2 is the
    sample variance of the J results, and the interval uses Student's t with
    J - 1 degrees of freedom (Nadeau and Bengio 2003; Bouckaert and Frank 2004).
    The usual s^2 / J alone would treat folds that share most of their training
    participants as independent and give an interval that is too narrow.
    """
    v = np.asarray(list(values), dtype=float)
    j = len(v)
    mean = float(v.mean())
    se = float(np.sqrt((1.0 / j + n_test / n_train) * v.var(ddof=1)))
    half = float(stats.t.ppf(0.5 + level / 2, j - 1)) * se
    return mean, mean - half, mean + half


def corrected_ttest(
    differences: Iterable[float], n_train: float, n_test: float
) -> dict[str, float]:
    """Corrected repeated k-fold cross-validation t-test of paired fold differences.

    ``differences`` are model A minus model B, fold by fold, on identical test
    folds. Returns the mean difference with its corrected 95% interval, the t
    statistic, its degrees of freedom and the two-sided p value (Bouckaert and
    Frank 2004, after Nadeau and Bengio 2003).
    """
    d = np.asarray(list(differences), dtype=float)
    j = len(d)
    mean, lo, hi = corrected_interval(d, n_train, n_test)
    se = float(np.sqrt((1.0 / j + n_test / n_train) * d.var(ddof=1)))
    if se == 0.0:
        t = 0.0 if mean == 0.0 else float(np.copysign(np.inf, mean))
    else:
        t = mean / se
    return {
        "mean_difference": mean,
        "ci_low": lo,
        "ci_high": hi,
        "t": t,
        "df": j - 1,
        "p": float(2 * stats.t.sf(abs(t), j - 1)),
    }


def summarise(folds: pd.DataFrame) -> pd.DataFrame:
    """Point estimate and 95% interval for each metric.

    For repeated cross-validation: ``mean`` over all k x r test folds;
    ``ci_low`` and ``ci_high``, the corrected interval of ``corrected_interval``
    (clipped to the metric's range, 0 to 1); ``repeat_low`` and ``repeat_high``,
    the 2.5th and 97.5th percentiles of the r per-repeat means, which show how
    much the answer moves with the split alone; ``sd_over_repeats``. For
    leave-one-study-out there is one fold per study and no interval; use
    ``bootstrap_auc`` on the predictions for one.
    """
    if folds["scheme"].iloc[0] == "loso":
        return folds.set_index("fold")[METRICS + ["n_test", "n_test_pd"]]
    n_train, n_test = folds["n_train"].mean(), folds["n_test"].mean()
    per_repeat = folds.groupby("repeat")[METRICS].mean()
    rows = {}
    for m in METRICS:
        mean, lo, hi = corrected_interval(folds[m], n_train, n_test)
        rows[m] = {
            "mean": mean,
            "ci_low": max(lo, 0.0),
            "ci_high": min(hi, 1.0),
            "repeat_low": per_repeat[m].quantile(0.025),
            "repeat_high": per_repeat[m].quantile(0.975),
            "sd_over_repeats": per_repeat[m].std(ddof=1),
        }
    out = pd.DataFrame.from_dict(rows, orient="index")
    out["n_folds"] = len(folds)
    out["n_repeats"] = len(per_repeat)
    return out


def bootstrap_auc(
    y_true: np.ndarray, p: np.ndarray, n_boot: int = 2000, seed: int = SEED
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


def paired_bootstrap_auc(
    y_true: np.ndarray,
    p_a: np.ndarray,
    p_b: np.ndarray,
    n_boot: int = 2000,
    seed: int = SEED,
) -> tuple[float, float, float]:
    """AUC of A minus AUC of B on the same participants, with a percentile
    bootstrap interval; both are scored on the same resample every time, so the
    interval reflects the difference, not the two AUCs separately."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y_true)
    a = np.asarray(p_a)
    b = np.asarray(p_b)
    point = roc_auc_score(y, a) - roc_auc_score(y, b)
    vals = []
    n = len(y)
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if y[idx].min() == y[idx].max():
            continue
        vals.append(roc_auc_score(y[idx], a[idx]) - roc_auc_score(y[idx], b[idx]))
    return (
        float(point),
        float(np.percentile(vals, 2.5)),
        float(np.percentile(vals, 97.5)),
    )


def cv_predictions(
    factory: Factory,
    df: pd.DataFrame,
    columns: list[str],
    n_splits: int = N_SPLITS,
    seed: int = SEED,
) -> pd.DataFrame:
    """Out-of-fold predicted probabilities for every participant, one repeat of the CV."""
    X = df[columns].to_numpy(dtype=float)
    y = df["y"].to_numpy()
    p = np.full(len(df), np.nan)
    for _, _, tr, te in repeated_grouped_cv(df, n_splits, n_repeats=1, seed=seed):
        model = factory()
        model.fit(X[tr], y[tr])
        p[te] = model.predict_proba(X[te])[:, 1]
    return pd.DataFrame(
        {"participant": df["participant"], "study": df["study"], "y": y, "p": p}
    )


def calibration_table(
    y_true: np.ndarray, p: np.ndarray, n_bins: int = 5
) -> pd.DataFrame:
    """Observed PD fraction against mean predicted probability, in quantile bins."""
    d = pd.DataFrame({"y": np.asarray(y_true), "p": np.asarray(p)})
    d["bin"] = pd.qcut(d["p"], n_bins, labels=False, duplicates="drop")
    out = d.groupby("bin").agg(
        n=("y", "size"), mean_predicted=("p", "mean"), observed_pd=("y", "mean")
    )
    return out.reset_index(drop=True)


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
