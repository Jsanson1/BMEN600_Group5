"""Reading the PhysioNet "Gait in Parkinson's Disease" database (gaitpdb v1.0.0).

Data layout, from the database's format.txt:

* one text file per walk, named ``<Study><Group><Subject>_<Walk>.txt``, e.g.
  ``GaPt03_01.txt``: study Ga/Ju/Si, group Co (control) or Pt (patient),
  two-digit subject number, two-digit walk number (01 = usual walk;
  10 = dual-task walk in the Ga study; 02..07 = the other conditions of
  each study);
* 19 tab-separated columns: time (s), 8 left-foot sensors (N), 8 right-foot
  sensors (N), left total (N), right total (N); sampled at 100 Hz;
* ``demographics.txt``: one row per participant with group, sex, age,
  height, weight, Hoehn and Yahr stage, UPDRS, timed up-and-go and the
  walking speed of each walk.

Nothing here touches the network: the files must already be in
``data/raw/gaitpdb`` (see data/raw/README.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

SAMPLE_RATE_HZ = 100.0
COLUMNS = (
    ["time_s"]
    + [f"L{i}" for i in range(1, 9)]
    + [f"R{i}" for i in range(1, 9)]
    + ["L_total", "R_total"]
)
STUDY_NAMES = {
    "Ga": "Ga (dual task)",
    "Ju": "Ju (auditory cueing)",
    "Si": "Si (treadmill study)",
}
GROUP_NAMES = {"Co": "Control", "Pt": "PD"}

_RECORD_RE = re.compile(r"^(Ga|Ju|Si)(Co|Pt)(\d{2})_(\d{2})\.txt$")


@dataclass(frozen=True)
class RecordName:
    study: str
    group: str
    subject_number: int
    walk: int

    @property
    def participant(self) -> str:
        """Participant ID as used in demographics.txt, e.g. ``GaPt03``."""
        return f"{self.study}{self.group}{self.subject_number:02d}"

    @property
    def record(self) -> str:
        return f"{self.participant}_{self.walk:02d}"


def parse_record_name(filename: str | Path) -> RecordName:
    """Split ``GaPt03_01.txt`` into its parts. Raises ValueError for other names."""
    name = Path(filename).name
    m = _RECORD_RE.match(name)
    if not m:
        raise ValueError(f"not a gaitpdb record name: {name}")
    study, group, subj, walk = m.groups()
    return RecordName(study, group, int(subj), int(walk))


def find_data_dir(root: str | Path) -> Path:
    """Return the folder that holds the record files.

    Accepts either the folder itself or ``data/raw/gaitpdb``, inside which the
    PhysioNet ZIP unpacks to ``gait-in-parkinsons-disease-1.0.0/``.
    """
    root = Path(root)
    for candidate in (root, root / "gait-in-parkinsons-disease-1.0.0"):
        if candidate.is_dir() and any(candidate.glob("*Co??_??.txt")):
            return candidate
    raise FileNotFoundError(
        f"no gaitpdb record files under {root}; unpack the PhysioNet ZIP there "
        "(see data/raw/README.md)"
    )


def list_records(data_dir: str | Path) -> list[Path]:
    """All record files, sorted by name."""
    data_dir = Path(data_dir)
    return sorted(p for p in data_dir.glob("*.txt") if _RECORD_RE.match(p.name))


def load_record(path: str | Path) -> pd.DataFrame:
    """Load one walk as a DataFrame with the 19 named columns.

    The time column is checked against the stated 100 Hz: a record whose
    sampling intervals are not all 0.01 s raises, because every timing
    feature downstream assumes that rate.
    """
    arr = np.loadtxt(path)
    if arr.ndim != 2 or arr.shape[1] != 19:
        raise ValueError(f"{Path(path).name}: expected 19 columns, got {arr.shape}")
    dt = np.diff(arr[:, 0])
    # Timestamps are printed with four decimals, so an interval sometimes reads
    # 0.0099 instead of 0.0100; anything further from 0.01 s is a real gap.
    if not np.allclose(dt, 1.0 / SAMPLE_RATE_HZ, atol=2e-4):
        raise ValueError(f"{Path(path).name}: time column is not uniformly 100 Hz")
    return pd.DataFrame(arr, columns=COLUMNS)


def load_demographics(data_dir: str | Path) -> pd.DataFrame:
    """Read demographics.txt with its known quirks corrected.

    * ``Juc010`` is a typo for ``JuCo10`` (a control with no recording).
    * Heights in the Ju study are in centimetres; Ga and Si are in metres.
      They are all returned in metres.
    * Group is coded 1 = PD, 2 = control; a ``group`` column with ``PD`` /
      ``Control`` is added. Gender is coded 1 = male, 2 = female; a ``sex``
      column with ``M`` / ``F`` is added.
    """
    path = Path(data_dir) / "demographics.txt"
    df = pd.read_csv(path, sep="\t", na_values=["NaN"])
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df["ID"] = df["ID"].str.strip().replace({"Juc010": "JuCo10"})
    df["Height"] = pd.to_numeric(df["Height"], errors="coerce")
    tall = df["Height"] > 3  # centimetres
    df.loc[tall, "Height"] = df.loc[tall, "Height"] / 100.0
    df["group"] = df["Group"].map({1: "PD", 2: "Control"})
    df["sex"] = df["Gender"].map({1: "M", 2: "F"})
    return df


def build_manifest(data_dir: str | Path) -> pd.DataFrame:
    """One row per record file: participant, study, group, walk, duration."""
    rows = []
    for p in list_records(data_dir):
        rn = parse_record_name(p)
        n_lines = sum(1 for _ in open(p, "rb"))
        rows.append(
            {
                "record": rn.record,
                "participant": rn.participant,
                "study": rn.study,
                "group": GROUP_NAMES[rn.group],
                "walk": rn.walk,
                "n_samples": n_lines,
                "duration_s": n_lines / SAMPLE_RATE_HZ,
                "path": str(p),
            }
        )
    return pd.DataFrame(rows)
