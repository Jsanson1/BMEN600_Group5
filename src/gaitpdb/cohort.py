"""Who is analysed: the group's inclusion rule, kept in one place.

DECISIONS.md D-006: participants under 50 are left out of every analysis, in
both datasets. The plan's intended use is screening people aged 50 and over, so
the models are trained and evaluated on that population. The rule uses the age
recorded in the dataset's demographic table. A participant whose age is missing
cannot be checked and is left out as well (no PhysioNet participant has a
missing age).

Every script that compares groups or fits a model selects its participants
through this module, so the models, tables and figures always describe the same
people. The checks that describe the database itself (``scripts/verify_data.py``
and ``scripts/check_data_quality.py``) still cover every file, and the
data-quality report says whom the rule removes.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .io import build_manifest, load_demographics

MIN_AGE_YEARS = 50
"""Youngest age analysed (DECISIONS.md D-006)."""


def meets_age_rule(age: pd.Series) -> pd.Series:
    """True where the age is known and at least MIN_AGE_YEARS."""
    return pd.to_numeric(age, errors="coerce") >= MIN_AGE_YEARS


def cohort_manifest(data_dir: str | Path) -> pd.DataFrame:
    """``build_manifest`` for the participants who meet the age rule, with their age.

    One row per record file of an analysed participant, all walks; filter on
    ``walk`` for the usual walk.
    """
    manifest = build_manifest(data_dir)
    ages = load_demographics(data_dir)[["ID", "Age"]].rename(
        columns={"ID": "participant"}
    )
    m = manifest.merge(ages, on="participant", how="left")
    return m[meets_age_rule(m["Age"])].reset_index(drop=True)


def cohort_flow(data_dir: str | Path) -> list[str]:
    """How the database narrows to the analysed participants, as lines of text.

    Used in the Table 1 notes and the data-quality report, so the counts quoted
    in the reports are produced here rather than typed in.
    """
    demo = load_demographics(data_dir)
    manifest = build_manifest(data_dir)
    with_rec = demo[demo["ID"].isin(manifest["participant"])]
    no_rec = sorted(set(demo["ID"]) - set(manifest["participant"]))
    young = with_rec[~meets_age_rule(with_rec["Age"])].sort_values("ID")
    kept = with_rec[meets_age_rule(with_rec["Age"])]
    kept_records = manifest[manifest["participant"].isin(kept["ID"])]

    def by_group(d: pd.DataFrame) -> str:
        return (
            f"{len(d)} ({int((d['group'] == 'PD').sum())} PD, "
            f"{int((d['group'] == 'Control').sum())} control)"
        )

    return [
        f"Participants in demographics.txt: {by_group(demo)}.",
        f"Without a record file: {', '.join(no_rec) or 'none'}. "
        f"With at least one recording: {by_group(with_rec)}.",
        f"Under {MIN_AGE_YEARS} or age missing, left out (DECISIONS.md D-006): "
        + (
            ", ".join(
                f"{r.ID} ({r.group}, {r.Age:g} y)"
                for r in young.itertuples(index=False)
            )
            or "none"
        )
        + ".",
        f"Analysed: {by_group(kept)}, with {len(kept_records)} recordings, of which "
        f"{int((kept_records['walk'] == 1).sum())} usual walks.",
        f"Analysed participants with more than one recording: "
        f"{int((kept_records.groupby('participant').size() > 1).sum())}.",
    ]
