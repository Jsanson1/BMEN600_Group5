"""Record names, record loading and the ragged demographics file."""

import numpy as np
import pytest

from gaitpdb.io import load_demographics, load_record, parse_record_name


def test_parse_record_name():
    rn = parse_record_name("JuPt03_06.txt")
    assert (rn.study, rn.group, rn.subject_number, rn.walk) == ("Ju", "Pt", 3, 6)
    assert rn.participant == "JuPt03" and rn.record == "JuPt03_06"
    with pytest.raises(ValueError):
        parse_record_name("demographics.txt")


def test_load_record_checks_columns_and_rate(tmp_path):
    t = np.arange(0, 2.0, 0.01)
    good = np.column_stack([t] + [np.ones_like(t)] * 18)
    p = tmp_path / "GaCo01_01.txt"
    np.savetxt(p, good, fmt="%.4f", delimiter="\t")
    df = load_record(p)
    assert df.shape == (200, 19) and list(df.columns[:2]) == ["time_s", "L1"]
    bad = good[:, :10]
    np.savetxt(p, bad, fmt="%.4f", delimiter="\t")
    with pytest.raises(ValueError):
        load_record(p)
    gap = good.copy()
    gap[100:, 0] += 0.5  # a half-second gap in the time column
    np.savetxt(p, gap, fmt="%.4f", delimiter="\t")
    with pytest.raises(ValueError):
        load_record(p)


def test_load_demographics_handles_the_real_file_layout(tmp_path):
    header = "ID\tStudy\tGroup\tSubjnum\tGender\tAge\tHeight\tWeight\tHoehnYahr\tUPDRS\tUPDRSM\tTUAG\tSpeed_01\tSpeed_02\tSpeed_03\tSpeed_04\tSpeed_05\tSpeed_06\tSpeed_07\tSpeed_10"
    rows = [
        "GaPt03\tGa\t1\t3\t2\t82\t1.45\t50\t3.0\t20\t10\t36.34\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\t0.778\t\t\t\t\t\t",
        "JuPt01\tJu\t1\t1\t1\t77\t183\t85\t2\t15\t11\t15.50\t1.013\t1.049\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN",
        "Juc010\tJu\t2\t10\t2\t62\t167\t78\tNaN\t0\t0\t8.82\t1.375\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\t",
        "SiCo30\tSi\t2\t30\t1\t63\t1.74\t82\tNaN\tNaN\tNaN\t8.68\t1.420\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\tNaN\t\t\t\t\t\t\t\t\t\t",
    ]
    text = (
        header
        + "\t\t\t\t\t\t\r\n"
        + "\r\n".join(rows)
        + "\r\n"
        + ("\t" * 29 + "\r\n") * 3
    )
    (tmp_path / "demographics.txt").write_text(text, encoding="utf-8")
    d = load_demographics(tmp_path)
    assert len(d) == 4
    assert list(d["ID"]) == ["GaPt03", "JuPt01", "JuCo10", "SiCo30"]  # Juc010 corrected
    assert d.loc[d["ID"] == "JuPt01", "Height"].iloc[0] == pytest.approx(
        1.83
    )  # cm to m
    assert d.loc[d["ID"] == "GaPt03", "Height"].iloc[0] == pytest.approx(1.45)
    assert list(d["group"]) == ["PD", "PD", "Control", "Control"]
    assert list(d["sex"]) == ["F", "M", "F", "M"]
    assert np.isnan(d.loc[d["ID"] == "SiCo30", "UPDRS"].iloc[0])
    assert d["Age"].dtype.kind in "if"
