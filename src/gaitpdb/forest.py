"""Random forest with its settings chosen by out-of-bag log-loss (task T-019).

The plan tunes every model's settings inside the training participants of each
outer fold (Midterm Research Plan, Section IV). A random forest needs no further
split for that: each tree is grown on a bootstrap sample of the training
participants, so every participant is left out of about a third of the trees,
and the average prediction of those trees is an honest out-of-bag (OOB)
prediction for that participant (Breiman, 2001). ``OOBTunedForest`` grows one
forest per setting of the grid, scores each by the log-loss of its OOB
predictions, and keeps the best. That costs one forest per setting, about five
times less than a grid search with an inner 5-fold split, which matters because
the shared evaluation fits the model on more than a hundred outer folds per
analysis.

The grid follows the plan: the depth of the trees (``MAX_DEPTHS``) and the
number of inputs tried at each split, spaced relative to the number of inputs
(``max_features_grid``). The number of trees is not tuned but fixed at a large
value (``N_TREES``): for log-loss and the Brier score, adding trees does not make
a forest worse in expectation, and the advice is to use as many as computing
allows (Probst and Boulesteix, 2018). Log-loss rather than AUC is the criterion,
as for the logistic regression, because AUC ignores how well the probabilities
are scaled.

Trees split on thresholds, so they need neither standardisation nor the log
transform the logistic regression applies to swing-time asymmetry.

L. Breiman, "Random forests," Mach. Learn., vol. 45, no. 1, pp. 5-32, 2001.
P. Probst and A.-L. Boulesteix, "To tune or not to tune the number of trees in
random forest," J. Mach. Learn. Res., vol. 18, no. 181, pp. 1-18, 2018.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss

N_TREES = 300
MAX_DEPTHS = (2, 3, 5, None)
"""Shallow to fully grown trees; ``None`` grows each tree until its leaves are pure."""


def max_features_grid(n_inputs: int) -> list[int]:
    """Inputs tried at each split: 1, the rounded square root of the number of
    inputs (scikit-learn's default for classification) and all of them (bagged
    trees), without repeats."""
    if n_inputs < 1:
        raise ValueError("a forest needs at least one input")
    return sorted({1, max(1, int(round(np.sqrt(n_inputs)))), n_inputs})


class OOBTunedForest(ClassifierMixin, BaseEstimator):
    """A random forest whose depth and features per split are chosen by OOB log-loss.

    After ``fit``: ``best_params_`` (the chosen setting), ``best_estimator_`` (the
    forest with that setting, fitted on all the training rows), ``oob_log_loss_``,
    ``search_`` (one row per setting with its OOB log-loss), ``classes_`` and
    ``feature_importances_`` (impurity-based, of the chosen forest). Ties go to the
    setting listed first, which is the one with fewer inputs per split and then
    shallower trees. One row must be one participant, so that a participant's OOB
    prediction never comes from trees that saw them. ``n_jobs`` parallelises the
    fitting only: predictions add up the trees' votes in one thread, in a fixed
    order, so they are identical from run to run (in parallel, the order of the
    additions, and with it the last digit of a probability, changes between runs).
    """

    def __init__(
        self,
        max_depths=MAX_DEPTHS,
        n_estimators: int = N_TREES,
        random_state: int = 0,
        n_jobs: int | None = None,
    ):
        self.max_depths = max_depths
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.n_jobs = n_jobs

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        if set(np.unique(y)) != {0, 1}:
            raise ValueError("OOBTunedForest needs both classes, coded 0 and 1")
        rows, best = [], None
        for m in max_features_grid(X.shape[1]):
            for d in self.max_depths:
                forest = RandomForestClassifier(
                    n_estimators=self.n_estimators,
                    max_features=m,
                    max_depth=d,
                    oob_score=True,
                    random_state=self.random_state,
                    n_jobs=self.n_jobs,
                )
                with warnings.catch_warnings():
                    # warns only when a row is in every bootstrap sample (handled below)
                    warnings.simplefilter("ignore", UserWarning)
                    forest.fit(X, y)
                p = forest.oob_decision_function_[:, 1]
                p = np.where(np.isfinite(p), p, y.mean())  # a row never out of bag
                loss = log_loss(y, np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1])
                rows.append({"max_features": m, "max_depth": d, "oob_log_loss": loss})
                if best is None or loss < best[0]:
                    best = (loss, {"max_features": m, "max_depth": d}, forest)
        self.oob_log_loss_, self.best_params_, self.best_estimator_ = best
        self.best_estimator_.set_params(n_jobs=None)  # predict in one thread
        self.search_ = pd.DataFrame(rows)
        self.classes_ = self.best_estimator_.classes_
        self.feature_importances_ = self.best_estimator_.feature_importances_
        return self

    def predict_proba(self, X):
        return self.best_estimator_.predict_proba(np.asarray(X, dtype=float))

    def predict(self, X):
        return self.best_estimator_.predict(np.asarray(X, dtype=float))
