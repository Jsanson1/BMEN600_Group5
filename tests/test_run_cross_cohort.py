"""The cross-dataset analysis script (scripts/run_cross_cohort.py, T-022)."""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gaitpdb.crosscohort import predictive_values
from gaitpdb.evaluation import COVARIATES, LOG_TRANSFORMED, MODEL_FEATURES

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_cross_cohort.py"
spec = importlib.util.spec_from_file_location("run_cross_cohort", SCRIPT)
rcc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rcc)

STUB = """
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def make_factory(columns):
    def factory():
        return make_pipeline(StandardScaler(), LogisticRegression())

    return factory
"""


def test_input_sets_derive_from_the_main_features():
    feats = ["stride_time_mean_s", "stride_time_cv_pct", "swing_time_asymmetry_pct"]
    sets = rcc.input_sets(feats)
    assert sets["gait"] == feats
    assert sets["gait + covariates"] == feats + COVARIATES
    assert sets["gait without variability"] == [
        "stride_time_mean_s",
        "swing_time_asymmetry_pct",
    ]
    assert sets["gait, robust variability"][1] == "stride_time_madcv_pct"


def test_standardising_within_dataset_centres_each_dataset_and_logs_first():
    logged = LOG_TRANSFORMED[0]
    df = pd.DataFrame(
        {
            "dataset": ["gaitpdb"] * 4 + ["weargait"] * 4,
            "x": [1.0, 2.0, 3.0, 4.0, 10.0, 20.0, 30.0, 40.0],
            logged: [0.0, 1.0, 3.0, 7.0, 0.0, 1.0, 3.0, 7.0],
        }
    )
    out, names = rcc.standardise_within_dataset(df, ["x", logged])
    assert all(n not in LOG_TRANSFORMED for n in names)
    for _, g in out.groupby("dataset"):
        assert g[names].mean().abs().max() < 1e-12
        assert np.allclose(g[names].std(ddof=1), 1.0)
    z = out.loc[out["dataset"] == "gaitpdb", names[1]].to_numpy()
    lg = np.log1p([0.0, 1.0, 3.0, 7.0])
    assert np.allclose(z, (lg - lg.mean()) / lg.std(ddof=1))


def test_age_matching_pairs_same_sex_within_the_caliper_without_reuse():
    test = pd.DataFrame(
        {
            "participant": ["P1", "P2", "P3", "C1", "C2", "C3", "C4"],
            "y": [1, 1, 1, 0, 0, 0, 0],
            "Age": [60, 62, 70, 61, 63, 71, 80],
            "sex": ["M", "M", "F", "M", "M", "M", "F"],
        }
    )
    keep = rcc.age_matched(test, caliper=3)
    assert keep == ["P1", "C1", "P2", "C2"]  # P3 has no woman within 3 years


def test_operating_point_uses_the_given_threshold():
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.3, 0.6, 0.4, 0.7, 0.8, 0.9])
    r = rcc.operating_point(y, p, threshold=0.5)
    assert (r["sensitivity_transferred"], r["specificity_transferred"]) == (0.75, 0.75)
    ppv, npv = predictive_values(0.75, 0.75, rcc.SCREENING_PREVALENCE)
    assert (r["ppv_at_prevalence"], r["npv_at_prevalence"]) == pytest.approx((ppv, npv))
    assert r["auc"] == pytest.approx(15 / 16)
    assert (r["n"], r["n_pd"]) == (8, 4)


def strides_of(participant, foot, n, rng, task=None, every=None):
    """``n`` strides; with ``every``, every ``every``-th stride is a removed turn."""
    s = 1.0 + 0.02 * rng.standard_normal(n)
    hs = np.r_[0.0, np.cumsum(s)[:-1]]
    clean = np.ones(n, bool) if every is None else (np.arange(n) % every != 0)
    d = pd.DataFrame(
        {
            "participant": participant,
            "foot": foot,
            "hs_s": hs,
            "next_hs_s": hs + s,
            "stride_s": s,
            "swing_s": 0.38 * s,
            "stance_s": 0.62 * s,
            "swing_pct": 38.0,
            "clean": clean,
            "included": True,
        }
    )
    if task is not None:
        d["task"] = task
    return d


def test_bouts_per_foot_counts_runs_between_turns():
    rng = np.random.default_rng(0)
    parts = [
        strides_of("NLS001", f, 12, rng, task=t, every=4)
        for f in ("L", "R")
        for t in ("SelfPace", "SelfPace_mat")
    ]
    # strides 0, 4 and 8 of each task are turns: bouts 1-3, 5-7, 9-11 -> 3 per task
    assert rcc.bouts_per_foot(pd.concat(parts, ignore_index=True)) == 6


def synthetic_study(tmp_path, seed=1):
    rng = np.random.default_rng(seed)
    feats = list(
        dict.fromkeys(MODEL_FEATURES + rcc.input_sets()["gait, robust variability"])
    )
    tables, strides = [], {}
    for ds, n, studies in (
        ("gaitpdb", 60, ["Ga", "Ju", "Si"]),
        ("weargait", 40, ["WPD", "WHC", "NLS", "HC"]),
    ):
        y = np.r_[np.zeros(n // 2, int), np.ones(n // 2, int)]
        t = pd.DataFrame(rng.gamma(4.0, 0.5, size=(n, len(feats))), columns=feats)
        t[feats[1]] += y  # a signal in one feature
        t.insert(0, "participant", [f"{ds[:2]}{i:03d}" for i in range(n)])
        t.insert(1, "dataset", ds)
        t.insert(2, "study", [studies[i % len(studies)] for i in range(n)])
        t.insert(3, "group", np.where(y == 1, "PD", "Control"))
        t.insert(4, "Age", rng.integers(55, 80, n))
        t.insert(5, "sex", rng.choice(["M", "F"], n))
        t["n_strides_left"], t["n_strides_right"] = 20, 22
        t.to_csv(tmp_path / f"features_{ds}.csv", index=False)
        tables.append(t)
        parts = []
        for p in t["participant"]:
            for f in ("L", "R"):
                if ds == "gaitpdb":
                    parts.append(strides_of(p, f, 60, rng))
                else:
                    parts += [
                        strides_of(p, f, 12, rng, task=k, every=4)
                        for k in ("SelfPace", "SelfPace_mat")
                    ]
        strides[ds] = pd.concat(parts, ignore_index=True)
        strides[ds].to_csv(tmp_path / f"clean_strides_{ds}.csv", index=False)
    (tmp_path / "run_logreg.py").write_text(STUB)


def test_main_runs_every_analysis_and_labels_a_shuffled_run(tmp_path, monkeypatch):
    synthetic_study(tmp_path)
    monkeypatch.setattr(rcc, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(rcc, "REPEATS", 2)
    monkeypatch.setattr(rcc, "N_STRIDE_DRAWS", 3)
    argv = [
        "run_cross_cohort.py",
        "--results",
        str(tmp_path),
        "--interim",
        str(tmp_path),
    ]
    monkeypatch.setattr("sys.argv", argv + ["--models", "logreg", "svm"])
    rcc.main()
    table = pd.read_csv(tmp_path / "crosscohort_results.csv")
    gait = table[(table["model"] == "logreg") & (table["inputs"] == "gait")]
    assert set(gait["analysis"]) == {
        "cross-cohort",
        "cross-cohort, VA Puget Sound only",
        "cross-cohort, age-matched",
        "pooled",
        "pooled, gaitpdb test participants",
        "pooled, WearGait-PD test participants",
        "dataset of origin",
        "stride-matched reference",
    }
    assert set(table["inputs"]) == {
        *rcc.input_sets(),
        "gait, standardised within dataset",
    }
    va = gait[gait["analysis"] == "cross-cohort, VA Puget Sound only"].iloc[0]
    assert va["n"] == 20  # WPD and WHC are half of the synthetic WearGait-PD sites
    summary = (tmp_path / "crosscohort_summary.txt").read_text()
    assert "svm: run_svm.py not found, skipped" in summary
    preds = pd.read_csv(tmp_path / "crosscohort_predictions.csv")
    assert len(preds[(preds["inputs"] == "gait")]) == 40
    monkeypatch.setattr("sys.argv", argv + ["--models", "logreg", "--shuffle-labels"])
    rcc.main()
    assert "SHUFFLED" in (tmp_path / "crosscohort_shuffled_summary.txt").read_text()
    assert (tmp_path / "crosscohort_results.csv").exists()
