"""WearGait-PD participant sheets: reading their two header rows, and the age rule."""

import pytest

from gaitpdb.weargait import SHEETS, load_participants, participant_flow

PD_HEADER = (
    "-,-,-,-,-,Part III\nSubject ID,Release version,Age (years),Gender,Sex,Race\n"
)
CONTROL_HEADER = "\ufeff,,,,,Part III\nSubject ID,Release version,Age,Gender,Sex,Race\n"


def write_sheets(folder, pd_rows, control_rows):
    (folder / SHEETS["PD"][0]).write_text(PD_HEADER + pd_rows, encoding="utf-8")
    (folder / SHEETS["Control"][0]).write_text(
        CONTROL_HEADER + control_rows, encoding="utf-8"
    )


def test_two_header_rows_bom_and_age_rule(tmp_path):
    write_sheets(
        tmp_path,
        "NLS158,Release 1.2,45,Male,Male,White\n"
        "NLS182,Release 1.2,50,-,Female,White\n"
        "WPD001,Release 1.0,67,-,Male,White\n",
        "WHC003,Release 1.0,49,-,Female,White\n"
        "HC001,Release 1.0,74,Female,Female,White\n"
        "HC002,Release 1.0,,-,Male,White\n"
        ",,,,,\n",
    )
    p = load_participants(tmp_path)
    assert list(p["participant"]) == [
        "NLS158",
        "NLS182",
        "WPD001",
        "WHC003",
        "HC001",
        "HC002",
    ]
    assert list(p["group"]) == ["PD"] * 3 + ["Control"] * 3
    assert list(p["site"]) == ["NLS", "NLS", "WPD", "WHC", "HC", "HC"]
    assert p["age"].iloc[:5].tolist() == [45, 50, 67, 49, 74]
    assert p["age"].isna().tolist() == [False] * 5 + [True]

    flow = participant_flow(tmp_path)
    assert flow[0] == "Participants in the two sheets: 6 (3 PD, 3 control)."
    assert flow[1] == (
        "Under 50 or age missing, left out (DECISIONS.md D-006): HC002 (Control, age "
        "missing), WHC003 (Control, 49 y), NLS158 (PD, 45 y)."
    )
    assert flow[2] == "Analysed: 3 (2 PD, 1 control)."


def test_repeated_id_and_missing_sheet(tmp_path):
    write_sheets(
        tmp_path,
        "NLS001,Release 1.0,60,-,Male,White\n",
        "NLS001,Release 1.0,70,-,Female,White\n",
    )
    with pytest.raises(ValueError, match="NLS001"):
        load_participants(tmp_path)
    (tmp_path / SHEETS["PD"][0]).unlink()
    with pytest.raises(FileNotFoundError):
        load_participants(tmp_path)
