"""WearGait-PD participants before and after the age rule, from its two participant sheets.

Reads the PD and CONTROLS "Demographic+Clinical - datasetV1.csv" sheets in
data/raw/weargait_pd (download steps in data/raw/README.md) and writes
results/weargait_participants.txt: the participants in each group, who is under
50, who is analysed, and their age and sex by group. The midterm plan's
"185 to 181" comes from this file. If the sheets are not there (they need a
Synapse account), the script says so and leaves the committed output alone.

With the task files in data/raw/weargait_pd/csv it also counts, per task, the
participants with a file and with insole data (the missing-data counts of
T-025). With the cleaned strides of scripts/make_clean_strides.py in
data/interim/clean_strides_weargait.csv (T-017), it tabulates who enters the
stride analyses (DECISIONS.md D-011) by recording site and group, with the
reason anyone is left out, because two of the three sites recorded only one
group (Midterm Research Plan, Section III).

    python scripts/check_weargait_participants.py [--data data/raw/weargait_pd]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import meets_age_rule  # noqa: E402
from gaitpdb.weargait import SHEETS, load_participants, participant_flow  # noqa: E402

RECORDED_MD5 = {  # the versions recorded in data/raw/README.md
    "PD": "0a1d1e8931f61c39d318837bc70f232f",
    "Control": "a8cda6bee6c414bc1c6cfb0ab7c69962",
}
OUT = Path("results/weargait_participants.txt")
TASKS = ("SelfPace", "SelfPace_mat", "SelfPace_matTURN")
INSTITUTION = {
    "NLS": "Johns Hopkins Outpatient Center",
    "HC": "Johns Hopkins Bayview",
    "WPD": "VA Puget Sound, Seattle",
    "WHC": "VA Puget Sound, Seattle",
}
"""Site from the participant ID prefix (dataset wiki, "Data description")."""
CLEAN = Path("data/interim/clean_strides_weargait.csv")


def task_availability(data: Path, people: pd.DataFrame) -> list[str]:
    """Per task: participants with a file, and with the insole force columns."""
    folder = data / "csv"
    if not folder.is_dir():
        return [f"Task files not found in {folder}: availability not counted."]
    lines = [
        f"Task files of the {len(people)} analysed participants (insole = LTotalForce and RTotalForce present):"
    ]
    for task in TASKS:
        have = insole = 0
        for pid in people["participant"]:
            f = folder / f"{pid}_{task}.csv"
            if f.exists():
                have += 1
                cols = set(pd.read_csv(f, nrows=0).columns)
                insole += {"LTotalForce", "RTotalForce"} <= cols
        lines.append(f"  {task}: file {have}, insole data {insole}")
    return lines


def stride_inclusion(people: pd.DataFrame) -> list[str]:
    """Who enters the stride analyses (D-011), by institution and group."""
    if not CLEAN.exists():
        return [
            f"{CLEAN} not found (run scripts/make_clean_strides.py): stride inclusion not tabulated."
        ]
    clean = pd.read_csv(CLEAN, usecols=["participant", "included"])
    included = clean.groupby("participant")["included"].first()
    d = people.copy()
    d["institution"] = d["site"].map(INSTITUTION)
    d["status"] = "no insole data in any task"
    d.loc[d["participant"].isin(included.index), "status"] = "too few clean strides"
    d.loc[d["participant"].isin(included[included].index), "status"] = "analysed"
    lines = [
        "Stride analyses (D-011: at least 10 clean strides per foot, three tasks pooled), by site and group:"
    ]
    table = d.pivot_table(
        index=["institution", "group"],
        columns="status",
        values="participant",
        aggfunc="count",
        fill_value=0,
    )
    for (inst, group), row in table.iterrows():
        parts = ", ".join(f"{k} {int(v)}" for k, v in row.items() if v)
        lines.append(f"  {inst}, {group}: {parts}")
    for status in ("no insole data in any task", "too few clean strides"):
        ids = sorted(d.loc[d["status"] == status, "participant"])
        lines.append(f"  {status}: {', '.join(ids) or 'none'}")
    analysed = d[d["status"] == "analysed"]
    one_group = [
        inst for inst, g in analysed.groupby("institution")["group"] if g.nunique() == 1
    ]
    lines.append(
        "  Sites with only one group among the analysed: "
        + (
            ", ".join(
                f"{i} ({analysed[analysed.institution == i].group.iloc[0]} only)"
                for i in one_group
            )
            or "none"
        )
    )
    devices = analysed["assistive_device"].replace("", "not recorded").value_counts()
    lines.append(
        "  Assistive device during testing, analysed: "
        + ", ".join(f"{k} {v}" for k, v in devices.items())
    )
    return lines


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def summary(d: pd.DataFrame) -> str:
    women = int((d["sex"] == "Female").sum())
    men = int((d["sex"] == "Male").sum())
    other = len(d) - women - men
    sex = f"{women} women, {men} men" + (f", {other} other or missing" if other else "")
    return f"{len(d)}, age {d['age'].mean():.1f} ± {d['age'].std(ddof=1):.1f} y, {sex}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data/raw/weargait_pd")
    args = ap.parse_args()
    data = Path(args.data)
    missing = [name for name, _ in SHEETS.values() if not (data / name).exists()]
    if missing:
        print(
            f"WearGait-PD participant sheets not found in {data}: {', '.join(missing)}"
        )
        print(f"{OUT} is left as it is; see data/raw/README.md for the download steps.")
        return

    participants = load_participants(data)
    analysed = participants[meets_age_rule(participants["age"])]
    lines = [
        "WearGait-PD participants (Synapse syn52540892, folder 'Version 1 (Cross-sectional)')",
        "",
    ]
    for group, (name, _) in SHEETS.items():
        digest = md5(data / name)
        note = (
            "the version recorded in data/raw/README.md"
            if digest == RECORDED_MD5[group]
            else "NOT the version recorded in data/raw/README.md"
        )
        lines.append(f"{name}: MD5 {digest} ({note})")
    lines += ["", *participant_flow(data), ""]
    for label, d in [("All participants", participants), ("Analysed", analysed)]:
        lines.append(f"{label}:")
        for group in SHEETS:
            lines.append(f"  {group}: {summary(d[d['group'] == group])}")
    sites = analysed.groupby(["group", "site"]).size()
    lines += [
        "",
        "Analysed, by site (ID prefix): "
        + "; ".join(f"{g} {s} {n}" for (g, s), n in sites.items()),
        "Release version of the sheet rows, all participants: "
        + ", ".join(
            f"{r} {n}"
            for r, n in participants["release"].value_counts().sort_index().items()
        ),
    ]
    lines += ["", *task_availability(data, analysed), "", *stride_inclusion(analysed)]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
