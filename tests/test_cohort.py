"""The age rule (DECISIONS.md D-006): who is analysed, and that every loader applies it."""

import numpy as np
import pandas as pd

from gaitpdb.cohort import MIN_AGE_YEARS, cohort_flow, cohort_manifest, meets_age_rule
from gaitpdb.evaluation import COVARIATES, MODEL_FEATURES, load_feature_table

HEADER = (
    "ID\tStudy\tGroup\tSubjnum\tGender\tAge\tHeight\tWeight\tHoehnYahr\tUPDRS\tUPDRSM"
    "\tTUAG\tSpeed_01\tSpeed_02\tSpeed_03\tSpeed_04\tSpeed_05\tSpeed_06\tSpeed_07\tSpeed_10"
)


def demographics_row(pid: str, study: str, group: int, age: int) -> str:
    return "\t".join(
        [pid, study, str(group), "1", "1", str(age), "1.70", "70"]
        + ["NaN"] * 4
        + ["1.1"]
        + ["NaN"] * 7
    )


def test_age_rule_boundary_and_missing_age():
    assert MIN_AGE_YEARS == 50
    got = meets_age_rule(pd.Series([49, 50, 51, np.nan, "61"]))
    assert list(got) == [False, True, True, False, True]


def test_load_feature_table_leaves_out_under_50s(tmp_path):
    rng = np.random.default_rng(0)
    n = 6
    df = pd.DataFrame(rng.normal(size=(n, len(MODEL_FEATURES))), columns=MODEL_FEATURES)
    df["participant"] = [f"GaPt{i:02d}" for i in range(n)]
    df["study"] = "Ga"
    df["group"] = ["PD", "Control"] * 3
    df["sex"] = "M"
    df["Age"] = [45, 50, 70, 49, 80, 66]
    path = tmp_path / "features.csv"
    df.to_csv(path, index=False)
    table = load_feature_table(str(path))
    assert list(table["Age"]) == [50, 70, 80, 66]
    assert set(COVARIATES) <= set(table.columns)


def test_cohort_manifest_and_flow(tmp_path):
    rows = [
        demographics_row("GaPt01", "Ga", 1, 60),
        demographics_row("GaCo01", "Ga", 2, 45),  # too young
        demographics_row("Juc010", "Ju", 2, 62),  # typo in the real file, no recording
    ]
    (tmp_path / "demographics.txt").write_text(
        HEADER + "\r\n" + "\r\n".join(rows) + "\r\n", encoding="utf-8"
    )
    line = "\t".join(["0.0000"] + ["1"] * 18) + "\n"
    for name in ("GaPt01_01", "GaPt01_10", "GaCo01_01"):
        (tmp_path / f"{name}.txt").write_text(line * 3, encoding="utf-8")

    m = cohort_manifest(tmp_path)
    assert sorted(m["record"]) == ["GaPt01_01", "GaPt01_10"]
    assert set(m["Age"]) == {60}

    flow = "\n".join(cohort_flow(tmp_path))
    assert "Participants in demographics.txt: 3 (1 PD, 2 control)" in flow
    assert "Without a record file: JuCo10" in flow
    assert "GaCo01 (Control, 45 y)" in flow
    assert (
        "Analysed: 1 (1 PD, 0 control), with 2 recordings, of which 1 usual walks"
        in flow
    )
