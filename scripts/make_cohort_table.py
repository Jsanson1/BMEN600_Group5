"""Table: the participants of the final analysis in both datasets, by group.

The participants are those of the two final feature tables,
results/features_gaitpdb.csv and results/features_weargait.csv (aged 50 or over,
DECISIONS.md D-006, with enough clean strides on each foot, D-011): the people
every model in this repository is fitted on or tested on. Age, sex, sub-study or
site and clean stride counts come from those tables; Hoehn and Yahr stage from
gaitpdb's demographics.txt and from WearGait-PD's PD sheet ("Modified Hoehn &
Yahr Score"). Writes results/cohort_table.csv and results/cohort_table.md.

    python scripts/make_cohort_table.py [--data data/raw/gaitpdb]
        [--weargait data/raw/weargait_pd] [--results results]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import find_data_dir, load_demographics  # noqa: E402
from gaitpdb.weargait import SHEETS  # noqa: E402

GROUPS = ("PD", "Control")
WEARGAIT_HY = "Modified Hoehn & Yahr Score"
SITE = {  # participant ID prefix -> site (dataset wiki, "Data description")
    "NLS": "JH Outpatient Center",
    "HC": "JH Bayview",
    "WPD": "VA Puget Sound",
    "WHC": "VA Puget Sound",
}
STUDY = {"Ga": "Ga", "Ju": "Ju", "Si": "Si"}  # gaitpdb's sub-study codes


def median_iqr(x: pd.Series, digits: int = 0) -> str:
    x = x.dropna()
    if not len(x):
        return "n/a"
    q1, q2, q3 = x.quantile([0.25, 0.5, 0.75])
    return f"{q2:.{digits}f} ({q1:.{digits}f} to {q3:.{digits}f})"


def median_range(x: pd.Series) -> str:
    x = x.dropna()
    return f"{x.median():g} ({x.min():g} to {x.max():g})" if len(x) else "n/a"


def weargait_hoehn_yahr(folder: Path) -> pd.Series:
    """Modified Hoehn and Yahr stage of WearGait-PD's PD participants, by ID
    (NaN where the sheet has none)."""
    sheet = pd.read_csv(
        folder / SHEETS["PD"][0],
        header=1,
        encoding="utf-8-sig",
        dtype=str,
        keep_default_na=False,
    )
    ids = sheet["Subject ID"].str.strip()
    stage = pd.to_numeric(sheet[WEARGAIT_HY].str.strip(), errors="coerce")
    return pd.Series(stage.to_numpy(), index=ids)[ids.to_numpy() != ""]


def counts_by(labels: pd.Series) -> str:
    """'A 12, B 3' in descending order of count, ties alphabetical."""
    c = labels.value_counts()
    c = c.sort_index().sort_values(ascending=False, kind="stable")
    return ", ".join(f"{k} {v}" for k, v in c.items())


def table_rows(
    features: pd.DataFrame, dataset: str, site: pd.Series, stage: pd.Series
) -> list[dict]:
    """One row per group: the columns of the table for one dataset."""
    rows = []
    for group in GROUPS:
        d = features[features["group"] == group]
        fewer = d[["n_strides_left", "n_strides_right"]].min(axis=1)
        hy = stage.reindex(d["participant"]) if group == "PD" else None
        women = int((d["sex"] == "F").sum())
        rows.append(
            {
                "Dataset": dataset,
                "Group": group,
                "Participants": len(d),
                "Sub-study or site": counts_by(site.loc[d.index]),
                "Age, years": median_iqr(d["Age"]),
                "Women, n (%)": f"{women} ({100 * women / len(d):.0f}%)",
                "Hoehn and Yahr stage": (
                    median_range(hy)
                    + (f", {int(hy.isna().sum())} missing" if hy.isna().any() else "")
                    if hy is not None
                    else ""
                ),
                "Clean strides, foot with fewer": median_iqr(fewer),
            }
        )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data/raw/gaitpdb")
    ap.add_argument("--weargait", default="data/raw/weargait_pd")
    ap.add_argument("--results", default="results")
    args = ap.parse_args()
    results = Path(args.results)

    g = pd.read_csv(results / "features_gaitpdb.csv")
    w = pd.read_csv(results / "features_weargait.csv")
    demo = load_demographics(find_data_dir(args.data)).set_index("ID")
    g_stage = demo["HoehnYahr"]
    w_stage = weargait_hoehn_yahr(Path(args.weargait))
    unknown = sorted(set(w["study"]) - set(SITE))
    if unknown:
        raise SystemExit(f"WearGait-PD sites without a name: {unknown}")

    rows = table_rows(g, "gaitpdb", g["study"].map(STUDY), g_stage) + table_rows(
        w, "WearGait-PD", w["study"].map(SITE), w_stage
    )
    table = pd.DataFrame(rows)
    table.to_csv(results / "cohort_table.csv", index=False)
    caption = (
        "Participants of the final analysis: everyone aged 50 or over (DECISIONS.md "
        "D-006) with at least 40 (gaitpdb) or 10 (WearGait-PD) clean strides on each "
        "foot (D-011), as in results/features_gaitpdb.csv and "
        "results/features_weargait.csv. Age and clean strides are median "
        "(interquartile range); Hoehn and Yahr stage is median (range), modified "
        "Hoehn and Yahr in WearGait-PD. gaitpdb's clean strides come from one usual "
        "walk; WearGait-PD's from its three self-paced tasks pooled. Sub-studies: Ga "
        "dual task, Ju auditory cueing, Si treadmill study (here its overground "
        "walk, D-009); JH, Johns Hopkins. Generated by scripts/make_cohort_table.py."
    )
    with open(results / "cohort_table.md", "w", encoding="utf-8") as f:
        f.write(caption + "\n\n" + table.to_markdown(index=False) + "\n")
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
