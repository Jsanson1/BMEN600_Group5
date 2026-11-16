"""The values scripts/make_figure5.py draws, from small synthetic result files."""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_figure5.py"
spec = importlib.util.spec_from_file_location("make_figure5", SCRIPT)
fig5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fig5)

ANALYSES = [a for _, _, a in fig5.CROSS_ROWS]


def write_results(folder: Path, families=("logreg", "rf"), drop=None) -> None:
    rows = []
    for i, name in enumerate([*(f"{f}: gait only" for f in families), fig5.REFERENCE]):
        rows.append(
            {
                "model": name,
                "auc_within": 0.8 - 0.01 * i,
                "auc_within_low": 0.7,
                "auc_within_high": 0.9,
                "auc_across": 0.7 - 0.01 * i,
                "auc_across_low": 0.6,
                "auc_across_high": 0.8,
            }
        )
    pd.DataFrame(rows).to_csv(folder / "model_comparison.csv", index=False)
    cross = []
    for fam in families:
        for analysis in ANALYSES:
            if (fam, analysis) == drop:
                continue
            for inputs in ("gait", "gait + covariates"):
                cross.append(
                    {
                        "analysis": analysis,
                        "model": fam,
                        "inputs": inputs,
                        "n": {
                            "cross-cohort": 20,
                            "cross-cohort, VA Puget Sound only": 8,
                            "cross-cohort, age-matched": 10,
                        }.get(analysis, float("nan")),
                        "auc": 0.55 if inputs == "gait" else 0.99,
                        "auc_low": 0.45,
                        "auc_high": 0.65,
                    }
                )
    pd.DataFrame(cross).to_csv(folder / "crosscohort_results.csv", index=False)
    pd.DataFrame({"participant": range(12)}).to_csv(
        folder / "features_gaitpdb.csv", index=False
    )
    pd.DataFrame({"participant": range(20)}).to_csv(
        folder / "features_weargait.csv", index=False
    )


def test_one_row_per_evaluation_and_model_with_the_right_counts(tmp_path):
    write_results(tmp_path)
    v = fig5.values(tmp_path)
    # two models at six cross-dataset rows, plus two models and the reference at
    # the two gaitpdb rows
    assert len(v) == 2 * len(fig5.CROSS_ROWS) + 3 * 2
    assert set(v["model"]) == {"logreg", "rf", "reference"}
    assert (v.loc[v["level"] < 2, "n"] == 12).all()
    pooled = v[(v["level"] == 2)].groupby("row")["n"].first()
    assert pooled.to_dict() == {
        "All 32": 32,
        "gaitpdb's 12": 12,
        "WearGait-PD's 20": 20,
    }
    # only the gait-feature models are drawn, never the covariate sets
    assert (v.loc[v["level"] >= 2, "auc"] == 0.55).all()
    assert (v.loc[v["model"] == "reference", "level"] < 2).all()


def test_an_svm_is_drawn_when_its_results_exist(tmp_path):
    write_results(tmp_path, families=("logreg", "svm", "rf"))
    v = fig5.values(tmp_path)
    assert list(dict.fromkeys(v.loc[v["level"] == 3, "model"])) == [
        "logreg",
        "svm",
        "rf",
    ]


def test_a_missing_cross_dataset_result_stops_with_its_name(tmp_path):
    write_results(tmp_path, drop=("rf", "cross-cohort, age-matched"))
    with pytest.raises(SystemExit, match="cross-cohort, age-matched"):
        fig5.values(tmp_path)


def test_levels_are_laid_out_top_to_bottom_in_order(tmp_path):
    write_results(tmp_path)
    rows, titles = fig5.layout(fig5.values(tmp_path))
    assert list(titles) == [0, 1, 2, 3]
    ys = [titles[0], rows[(0, "All 12")], titles[1], rows[(1, "All 12")], titles[2]]
    assert ys == sorted(ys, reverse=True)
    assert len(rows) == 2 + 6


def test_the_figure_is_written(tmp_path):
    write_results(tmp_path)
    v = fig5.values(tmp_path)
    fig5.figure(v, tmp_path / "f.png", tmp_path / "f.pdf")
    assert (tmp_path / "f.png").stat().st_size > 0
    assert (tmp_path / "f.pdf").stat().st_size > 0
