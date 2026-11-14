"""The cross-cohort table of scripts/make_table_crosscohort.py, from synthetic files."""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_table_crosscohort.py"
spec = importlib.util.spec_from_file_location("make_table_crosscohort", SCRIPT)
tab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tab)


def write(folder: Path, families=("logreg", "rf"), n_rf=None) -> None:
    (folder / "fixed_20N").mkdir(exist_ok=True)
    for sub, n in (("", 30), ("fixed_20N", 28)):
        rows = []
        for _, where, analysis, inputs in tab.ROWS:
            if where != sub:
                continue
            for i, fam in enumerate(families):
                size = n_rf if (fam == "rf" and n_rf) else n
                rows.append(
                    {
                        "analysis": analysis,
                        "model": fam,
                        "inputs": inputs,
                        "n": size,
                        "n_pd": size // 2,
                        "auc": 0.5 + 0.01 * i,
                        "auc_low": 0.4,
                        "auc_high": 0.6,
                    }
                )
        pd.DataFrame(rows).to_csv(folder / sub / "crosscohort_results.csv", index=False)


def test_one_row_per_version_with_its_participants_and_every_model(tmp_path):
    write(tmp_path)
    t = tab.build(tmp_path)
    assert list(t["Version of the test"]) == [label for label, *_ in tab.ROWS]
    assert list(t.columns) == [
        "Version of the test",
        "WearGait-PD participants (PD)",
        "Logistic regression",
        "Random forest",
    ]
    by_row = t.set_index("Version of the test")
    assert (
        by_row.loc["Main test: five gait features", "WearGait-PD participants (PD)"]
        == "30 (15)"
    )
    assert (
        by_row.loc["Contact threshold fixed at 20 N", "WearGait-PD participants (PD)"]
        == "28 (14)"
    )
    assert by_row.loc["Age and sex added", "Random forest"] == "0.51 (0.40 to 0.60)"


def test_models_tested_on_different_participants_stop_the_table(tmp_path):
    write(tmp_path, n_rf=29)
    with pytest.raises(SystemExit, match="different participants"):
        tab.build(tmp_path)


def test_a_missing_row_stops_with_its_name(tmp_path):
    write(tmp_path)
    path = tmp_path / "crosscohort_results.csv"
    r = pd.read_csv(path)
    r = r[~((r["inputs"] == "gait + covariates") & (r["model"] == "rf"))]
    r.to_csv(path, index=False)
    with pytest.raises(SystemExit, match="gait \\+ covariates"):
        tab.build(tmp_path)
