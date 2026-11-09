"""Participant feature tables of both datasets, from the clean strides (task T-018).

Reads the per-stride tables that scripts/make_clean_strides.py (task T-017)
writes to data/interim/ and keeps the clean strides of the included participants
(DECISIONS.md D-011). Each participant's features come from all of their clean
strides of both feet, through gaitpdb.features.stride_features; in WearGait-PD
the strides of its three straight-walking tasks are pooled (D-011). Age and sex
come from each dataset's participant table: demographics.txt for gaitpdb, the
two participant sheets for WearGait-PD.

Writes, in results/:
  features_gaitpdb.csv     one row per included gaitpdb participant
  features_weargait.csv    one row per included WearGait-PD participant
  feature_dictionary.md    every column of the two tables, with unit and definition
  features_summary.txt     participants and clean strides per dataset; which
                           version of the clean strides the features come from
                           (commit and contact threshold, from T-017's provenance
                           file); each feature's median over all participants.

scripts/check_features.py compares the two tables without diagnosis labels.

Nothing in the summary splits WearGait-PD by diagnosis. That dataset is the
cross-cohort test set, and the features and the threshold are fixed before any
group comparison on it is looked at (Midterm Research Plan, Section IV).

Without a dataset's clean-stride table, that dataset is skipped with a note.

    python scripts/make_features.py [--data data/raw/gaitpdb]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb.features import (  # noqa: E402
    STRIDE_FEATURE_COLUMNS,
    feature_dictionary_markdown,
    participant_features,
)
from gaitpdb.io import find_data_dir, load_demographics  # noqa: E402
from gaitpdb.weargait import load_participants  # noqa: E402

DATASETS = ("gaitpdb", "weargait")
ID_COLUMNS = {
    "gaitpdb": ["participant", "dataset", "study", "group", "Age", "sex"],
    "weargait": ["participant", "dataset", "study", "group", "Age", "sex", "n_tasks"],
}
SEX_CODES = {"Male": "M", "Female": "F", "M": "M", "F": "F"}
SUMMARY_FEATURES = [c for c in STRIDE_FEATURE_COLUMNS if not c.startswith("n_")]

lines: list[str] = []


def say(text: str = "") -> None:
    print(text)
    lines.append(text)


def gaitpdb_table(strides: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    """Features plus study, group, age and sex for the included gaitpdb participants."""
    feats = participant_features(strides)
    info = strides.groupby("participant")[["study", "group"]].first()
    demo = load_demographics(data_dir).set_index("ID")[["Age", "sex"]]
    out = feats.join(info, on="participant").join(demo, on="participant")
    out.insert(1, "dataset", "gaitpdb")
    return out[ID_COLUMNS["gaitpdb"] + STRIDE_FEATURE_COLUMNS]


def weargait_table(strides: pd.DataFrame, data_dir: Path) -> pd.DataFrame:
    """Features plus site, group, age, sex and number of tasks for WearGait-PD."""
    feats = participant_features(strides)
    info = strides.groupby("participant")[["site", "group"]].first()
    used = strides[strides["clean"].astype(bool) & strides["included"].astype(bool)]
    n_tasks = used.groupby("participant")["task"].nunique().rename("n_tasks")
    people = load_participants(data_dir).set_index("participant")
    sheet = pd.DataFrame(
        {
            "Age": people["age"],
            "sex": people["sex"].map(SEX_CODES),
            "sheet_group": people["group"],
        }
    )
    out = (
        feats.join(info, on="participant")
        .join(n_tasks, on="participant")
        .join(sheet, on="participant")
    )
    mismatch = out[out["group"] != out["sheet_group"]]
    if len(mismatch):
        raise ValueError(
            "group in the clean-stride table differs from the participant sheets for "
            f"{sorted(mismatch['participant'])}"
        )
    out = out.rename(columns={"site": "study"})
    out.insert(1, "dataset", "weargait")
    return out[ID_COLUMNS["weargait"] + STRIDE_FEATURE_COLUMNS]


def shown(path: Path) -> str:
    """``path`` relative to the repository when it is inside it, else in full."""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def provenance_lines(path: Path) -> list[str]:
    """Commit and contact-threshold parameters of the clean strides, from T-017."""
    if not path.exists():
        return [f"No provenance file at {shown(path)}."]
    prov = json.loads(path.read_text(encoding="utf-8"))
    params = prov.get("parameters", {})
    keys = [k for k in params if "THRESHOLD" in k or "FORCE" in k or "SHARE" in k]
    out = [
        f"Clean strides from {prov.get('script', '?')} at commit "
        f"{str(prov.get('commit', '?'))[:7]}"
        + (" with uncommitted changes" if prov.get("uncommitted_changes") else ""),
    ]
    out += [f"  {k} = {params[k]}" for k in sorted(keys)]
    return out


def describe(name: str, table: pd.DataFrame) -> None:
    groups = table["group"].value_counts().to_dict()
    say(f"{name}: {len(table)} included participants {groups}")
    counts = table[["n_strides_left", "n_strides_right"]]
    weaker = counts.min(axis=1)
    say(
        f"  clean strides per foot: median {counts.stack().median():.0f}; weaker foot "
        f"median {weaker.median():.0f} (range {weaker.min():.0f} to {weaker.max():.0f})"
    )
    say("  feature, median (interquartile range), all participants together:")
    for c in SUMMARY_FEATURES:
        q = table[c].quantile([0.25, 0.5, 0.75])
        say(f"    {c}: {q[0.5]:.3g} ({q[0.25]:.3g} to {q[0.75]:.3g})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--interim", default=str(ROOT / "data" / "interim"))
    ap.add_argument("--data", default=str(ROOT / "data" / "raw" / "gaitpdb"))
    ap.add_argument(
        "--weargait-data", default=str(ROOT / "data" / "raw" / "weargait_pd")
    )
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()
    interim, out = Path(args.interim), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    say("Participant features from the clean strides (scripts/make_features.py,")
    say("definitions in gaitpdb.features; column meanings in feature_dictionary.md)")
    say()
    for x in provenance_lines(interim / "clean_strides_provenance.json"):
        say(x)
    say()

    tables = {}
    for ds in DATASETS:
        path = interim / f"clean_strides_{ds}.csv"
        if not path.exists():
            say(f"{ds} skipped: {shown(path)} not found (run make_clean_strides.py)")
            say()
            continue
        strides = pd.read_csv(path, low_memory=False)
        if ds == "gaitpdb":
            table = gaitpdb_table(strides, find_data_dir(args.data))
        else:
            table = weargait_table(strides, Path(args.weargait_data))
        table.to_csv(out / f"features_{ds}.csv", index=False)
        tables[ds] = table
        describe(ds, table)
        missing = table[table[["Age", "sex"]].isna().any(axis=1)]["participant"]
        if len(missing):
            say(f"  age or sex missing: {', '.join(sorted(missing))}")
        if ds == "weargait":
            tasks = table["n_tasks"].value_counts().sort_index().to_dict()
            say(f"  tasks contributing clean strides (count: participants): {tasks}")
        say()

    columns = list(dict.fromkeys(ID_COLUMNS["weargait"] + STRIDE_FEATURE_COLUMNS))
    (out / "feature_dictionary.md").write_text(
        "# Feature dictionary\n\n"
        "Columns of `results/features_gaitpdb.csv` and `results/features_weargait.csv` "
        "(`n_tasks` is in the WearGait-PD table only), written by "
        "`scripts/make_features.py` from `gaitpdb.features.FEATURE_DICTIONARY`. "
        "One row per participant who meets the minimum of clean strides per foot "
        "(DECISIONS.md D-011).\n\n" + feature_dictionary_markdown(columns),
        encoding="utf-8",
    )
    (out / "features_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
