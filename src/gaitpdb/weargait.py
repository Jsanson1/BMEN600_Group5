"""WearGait-PD participants: the two demographic and clinical sheets, and who is analysed.

WearGait-PD (Synapse syn52540892; Anderson et al., Sci. Data, 2026) keeps one
sheet per group in its "Version 1 (Cross-sectional)" folder:

    PD - Demographic+Clinical - datasetV1.csv
    CONTROLS - Demographic+Clinical - datasetV1.csv

Both sheets have two header rows: the first groups the MDS-UPDRS items, the
second holds the column names. The controls sheet starts with a UTF-8 byte-order
mark, and its age column is "Age" where the PD sheet has "Age (years)".

The age rule is the one the PhysioNet analyses use (gaitpdb.cohort,
DECISIONS.md D-006). The sensor files are not read here yet (task T-025).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .cohort import MIN_AGE_YEARS, meets_age_rule

SHEETS = {
    "PD": ("PD - Demographic+Clinical - datasetV1.csv", "Age (years)"),
    "Control": ("CONTROLS - Demographic+Clinical - datasetV1.csv", "Age"),
}
"""Group -> (file name, age column) of the two participant sheets."""


def load_participants(data_dir: str | Path) -> pd.DataFrame:
    """One row per participant: participant, group, age, sex, site, release.

    ``site`` is the letter prefix of the participant ID (NLS, HC, WPD or WHC);
    ``release`` is the sheet's "Release version" column. Rows without an ID are
    skipped. Raises if a sheet is missing or an ID appears more than once.
    """
    data_dir = Path(data_dir)
    frames = []
    for group, (name, age_column) in SHEETS.items():
        path = data_dir / name
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found; the download steps are in data/raw/README.md"
            )
        sheet = pd.read_csv(
            path, header=1, encoding="utf-8-sig", dtype=str, keep_default_na=False
        )
        ids = sheet["Subject ID"].str.strip()
        frame = pd.DataFrame(
            {
                "participant": ids,
                "group": group,
                "age": pd.to_numeric(sheet[age_column].str.strip(), errors="coerce"),
                "sex": sheet["Sex"].str.strip(),
                "site": ids.str.extract(r"^([A-Za-z]+)", expand=False),
                "release": sheet["Release version"].str.strip(),
            }
        )
        frames.append(frame[frame["participant"] != ""])
    participants = pd.concat(frames, ignore_index=True)
    repeated = participants["participant"][participants["participant"].duplicated()]
    if len(repeated):
        raise ValueError(
            f"participant IDs listed more than once: {sorted(set(repeated))}"
        )
    return participants


def participant_flow(data_dir: str | Path) -> list[str]:
    """How the two sheets narrow to the analysed participants, as lines of text."""
    participants = load_participants(data_dir)
    keep = meets_age_rule(participants["age"])
    left_out = participants[~keep].sort_values(["group", "participant"])

    def by_group(d: pd.DataFrame) -> str:
        return (
            f"{len(d)} ({int((d['group'] == 'PD').sum())} PD, "
            f"{int((d['group'] == 'Control').sum())} control)"
        )

    def describe(row) -> str:
        age = "age missing" if pd.isna(row.age) else f"{row.age:g} y"
        return f"{row.participant} ({row.group}, {age})"

    return [
        f"Participants in the two sheets: {by_group(participants)}.",
        f"Under {MIN_AGE_YEARS} or age missing, left out (DECISIONS.md D-006): "
        + (", ".join(describe(r) for r in left_out.itertuples(index=False)) or "none")
        + ".",
        f"Analysed: {by_group(participants[keep])}.",
    ]
