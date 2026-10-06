"""Baselines for the model comparison (T-022), on the same splits as the three models.

* chance: always predicts the share of PD among the training participants. Its
  AUC is 0.5 by construction; its Brier score is the one a useful model must
  beat.
* one feature at a time: a logistic regression on a single timing feature
  (swing-time asymmetry as log(1 + x), as in the main models), without a
  penalty. The direction of the effect is learned on the training participants
  only, so the AUC on the test participants is that of the feature itself on
  people the fit has not seen. This shows which features carry the separation,
  and how much the multivariable models add to the best of them.

Reads results/features_usual_walk.csv (made by scripts/make_figure1.py) and
writes results/baselines_summary.txt and results/baselines_folds.csv,
results/baselines_cv_predictions.csv and results/baselines_loso_predictions.csv
(the files scripts/compare_models.py reads).

    python scripts/run_baselines.py [--features results/features_usual_walk.csv]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb.evaluation import (  # noqa: E402
    MODEL_FEATURES,
    N_REPEATS,
    N_SPLITS,
    bootstrap_auc,
    evaluate_model,
    load_feature_table,
    log_transform,
    summarise,
    write_model_outputs,
)


def chance_factory():
    return DummyClassifier(strategy="prior")


def single_feature_factory(feature: str):
    def factory():
        return Pipeline(
            [
                ("log", log_transform([feature])),
                ("scale", StandardScaler()),
                ("logreg", LogisticRegression(C=np.inf, max_iter=5000)),
            ]
        )

    return factory


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default="results/features_usual_walk.csv")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    out = Path(args.out)
    if not Path(args.features).exists():
        raise SystemExit(
            f"{args.features} not found: run scripts/make_figure1.py first"
        )
    df = load_feature_table(args.features)

    models = [("baseline: chance", chance_factory, MODEL_FEATURES)]
    for feature in MODEL_FEATURES:
        models.append(
            (f"single: {feature}", single_feature_factory(feature), [feature])
        )

    outputs = []
    lines = [
        f"Baselines on {len(df)} participants ({int(df['y'].sum())} PD, "
        f"{int((1 - df['y']).sum())} controls), one usual-walk recording each, under the "
        f"same splits as the models ({N_SPLITS}-fold participant-grouped cross-validation "
        f"repeated {N_REPEATS} times; leave-one-study-out).",
        "Cross-validation: mean over the test folds with the corrected 95% interval "
        "(Nadeau and Bengio 2003). Leave-one-study-out: all out-of-study predictions "
        "pooled, 95% participant-bootstrap interval.",
        "",
        f"{'model':<40} {'AUC within protocol':<24} {'AUC across protocols':<24} Brier",
    ]
    for name, factory, cols in models:
        result = evaluate_model(factory, df, cols, name)
        outputs.append(result)
        s = summarise(result["folds"])
        loso = result["loso_predictions"]
        point, lo, hi = bootstrap_auc(loso["y"], loso["p"])
        within = f"{s.loc['auc', 'mean']:.3f} ({s.loc['auc', 'ci_low']:.3f}-{s.loc['auc', 'ci_high']:.3f})"
        across = f"{point:.3f} ({lo:.3f}-{hi:.3f})"
        lines.append(
            f"{name:<40} {within:<24} {across:<24} {s.loc['brier', 'mean']:.3f}"
        )
    write_model_outputs(outputs, out, "baselines")
    text = "\n".join(lines) + "\n"
    (out / "baselines_summary.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
