"""WearGait-PD participants before and after the age rule, from its two participant sheets.

Reads the PD and CONTROLS "Demographic+Clinical - datasetV1.csv" sheets in
data/raw/weargait_pd (download steps in data/raw/README.md) and writes
results/weargait_participants.txt: the participants in each group, who is under
50, who is analysed, and their age and sex by group. The midterm plan's
"185 to 181" comes from this file. If the sheets are not there (they need a
Synapse account), the script says so and leaves the committed output alone.

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
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
