"""Support vector machine with its kernel and settings chosen by log-loss (task T-020).

The Midterm Research Plan (Section IV) has the SVM explore a linear and a radial
basis function (RBF) kernel, tuning the cost C for the linear kernel and both C
and the kernel coefficient gamma for the RBF kernel, each between 1e-4 and 1e4
on a logarithmic scale, inside the training participants of each outer fold.
Here the kernel is tuned with them: every linear and every RBF setting is one
candidate (``param_grid``), so a single model per input set enters the
comparison, and the summary reports which kernel each fit chose.

An SVM outputs a signed distance from its boundary, not a probability, and the
Brier score, the calibration check and log-loss need probabilities. They come
from Platt scaling (Platt, 1999): a logistic curve that maps the distance to a
probability, fitted on distances the SVM produced for participants it was not
trained on. ``PlattTunedSVM`` does the tuning and the scaling in one pass. For
each setting it runs an inner stratified 5-fold split of the training
participants (one row per participant, so the inner folds are
participant-grouped too), collects every participant's out-of-fold distance,
fits one Platt curve to them and scores the setting by the log-loss of the
resulting probabilities. The setting with the lowest log-loss is refitted on all
the training participants, and the Platt curve of that setting maps its
distances to probabilities. This is what scikit-learn's
``CalibratedClassifierCV(SVC(), method="sigmoid", ensemble=False)`` does for one
setting; log-loss is the tuning criterion for the same reason as for the
logistic regression and the random forest (AUC ignores how well the
probabilities are scaled).

The Platt curve uses Platt's smoothed targets, (N+ + 1) / (N+ + 2) for PD and
1 / (N- + 2) for controls, which keeps the fit finite when the distances
separate the two groups perfectly (Lin, Lin and Weng, 2007).

Inputs are standardised (an SVM's boundary depends on distances between
participants), and swing-time asymmetry enters as log(1 + x), as in the logistic
regression; the pipeline in ``make_svm`` applies both inside each training set.

J. C. Platt, "Probabilistic outputs for support vector machines and comparisons
to regularized likelihood methods," in Advances in Large Margin Classifiers,
MIT Press, 1999, pp. 61-74.
H.-T. Lin, C.-J. Lin and R. C. Weng, "A note on Platt's probabilistic outputs for
support vector machines," Mach. Learn., vol. 68, no. 3, pp. 267-276, 2007.
"""

from __future__ import annotations

import numpy as np
from joblib import Parallel, delayed
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

C_GRID = tuple(np.logspace(-4, 4, 17))
"""Half-decade steps from 1e-4 to 1e4 (the plan's range; the logistic regression's grid)."""
GAMMA_GRID = tuple(np.logspace(-4, 4, 17))
"""The RBF kernel coefficient over the same range, on standardised inputs."""
N_INNER = 5


def param_grid(
    c_grid=C_GRID, gamma_grid=GAMMA_GRID, kernels=("linear", "rbf")
) -> list[dict]:
    """Every candidate setting: the linear kernel at each C, then the RBF kernel at
    each (C, gamma). Ties in log-loss go to the earlier setting in this order."""
    grid = []
    if "linear" in kernels:
        grid += [{"kernel": "linear", "C": float(c)} for c in c_grid]
    if "rbf" in kernels:
        grid += [
            {"kernel": "rbf", "C": float(c), "gamma": float(g)}
            for c in c_grid
            for g in gamma_grid
        ]
    if not grid:
        raise ValueError("no kernel to tune")
    return grid


def platt_fit(d: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Platt's sigmoid p = 1 / (1 + exp(-(a d + b))) fitted to distances ``d``.

    Each participant enters twice, as PD with weight t and as control with
    weight 1 - t, where t is Platt's smoothed target; this is the log-likelihood
    Platt maximises, solved by an unpenalised logistic regression. Returns (a, b).
    """
    d = np.asarray(d, dtype=float).reshape(-1, 1)
    y = np.asarray(y)
    n_pos, n_neg = int((y == 1).sum()), int((y == 0).sum())
    t = np.where(y == 1, (n_pos + 1) / (n_pos + 2), 1 / (n_neg + 2))
    lr = LogisticRegression(C=np.inf, max_iter=1000)
    lr.fit(
        np.vstack([d, d]),
        np.r_[np.ones(len(d)), np.zeros(len(d))],
        sample_weight=np.r_[t, 1 - t],
    )
    return float(lr.coef_[0, 0]), float(lr.intercept_[0])


def platt_proba(d: np.ndarray, a: float, b: float) -> np.ndarray:
    """Probability of PD from distances ``d`` and a Platt curve (a, b)."""
    return 1.0 / (1.0 + np.exp(-(a * np.asarray(d, dtype=float) + b)))


def _fold_distances(setting, X, y, tr, te):
    return te, SVC(**setting).fit(X[tr], y[tr]).decision_function(X[te])


class PlattTunedSVM(ClassifierMixin, BaseEstimator):
    """An SVM whose kernel, C and gamma are chosen by the log-loss of Platt-scaled
    inner-fold distances, with probabilities from the chosen setting's Platt curve.

    Expects standardised inputs (``make_svm`` puts it after the scaler). After
    ``fit``: ``best_params_``, ``best_estimator_`` (the SVC with that setting fitted
    on all the training rows), ``platt_`` (a, b), ``best_log_loss_`` and
    ``cv_log_loss_`` (one value per setting, in ``param_grid`` order).
    ``n_jobs`` runs the inner fits in threads; results do not depend on it.
    """

    def __init__(
        self,
        c_grid=C_GRID,
        gamma_grid=GAMMA_GRID,
        kernels=("linear", "rbf"),
        n_inner: int = N_INNER,
        random_state: int = 0,
        n_jobs: int | None = -1,
    ):
        self.c_grid = c_grid
        self.gamma_grid = gamma_grid
        self.kernels = kernels
        self.n_inner = n_inner
        self.random_state = random_state
        self.n_jobs = n_jobs

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        if len(self.classes_) != 2:
            raise ValueError("PlattTunedSVM needs both classes in the training set")
        y = (y == self.classes_[1]).astype(int)
        grid = param_grid(self.c_grid, self.gamma_grid, self.kernels)
        folds = list(
            StratifiedKFold(
                self.n_inner, shuffle=True, random_state=self.random_state
            ).split(X, y)
        )
        jobs = Parallel(n_jobs=self.n_jobs, backend="threading")(
            delayed(_fold_distances)(s, X, y, tr, te) for s in grid for tr, te in folds
        )
        losses, curves = [], []
        for i in range(len(grid)):
            d = np.empty(len(y))
            for te, dist in jobs[i * len(folds) : (i + 1) * len(folds)]:
                d[te] = dist
            a, b = platt_fit(d, y)
            p = np.clip(platt_proba(d, a, b), 1e-12, 1 - 1e-12)
            losses.append(log_loss(y, p, labels=[0, 1]))
            curves.append((a, b))
        best = int(np.argmin(losses))
        self.cv_log_loss_ = np.array(losses)
        self.best_params_ = grid[best]
        self.best_log_loss_ = float(losses[best])
        self.platt_ = curves[best]
        self.best_estimator_ = SVC(**grid[best]).fit(X, y)
        self.n_features_in_ = X.shape[1]
        return self

    def decision_function(self, X):
        return self.best_estimator_.decision_function(np.asarray(X, dtype=float))

    def predict_proba(self, X):
        p = platt_proba(self.decision_function(X), *self.platt_)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return self.classes_[(self.predict_proba(X)[:, 1] >= 0.5).astype(int)]


def make_svm(log_step=None, random_state: int = 0, n_jobs: int | None = -1, **kw):
    """Pipeline: optional log step (``gaitpdb.evaluation.log_transform``),
    standardisation, then ``PlattTunedSVM``."""
    steps = [] if log_step is None else [("log", log_step)]
    steps += [
        ("scale", StandardScaler()),
        ("svm", PlattTunedSVM(random_state=random_state, n_jobs=n_jobs, **kw)),
    ]
    return Pipeline(steps)
