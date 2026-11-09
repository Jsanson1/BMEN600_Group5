"""Spatiotemporal gait features, per recording and per participant.

Two entry points share one set of definitions:

* ``record_features``: one gaitpdb recording, from its raw force with the
  stride rules of ``events.stride_table``. The midterm's figures and models use
  it (``results/features_usual_walk.csv``, made by scripts/make_figure1.py).
* ``stride_features``: one participant, from their clean strides of both feet
  as ``gaitpdb.clean_data`` marks them (task T-017). In WearGait-PD these are
  the strides of the three straight-walking tasks pooled (DECISIONS.md D-011).
  ``participant_features`` applies it to every included participant of a
  clean-stride table (task T-018); scripts/make_features.py writes the final
  feature tables of both datasets with it.

Definitions. Means are over the strides of both feet together. Variability is
the coefficient of variation, 100 * SD / mean, the measure used by the studies
that produced the PhysioNet database, computed for each foot and averaged over
the two feet. The robust variability is the same ratio with the scaled median
absolute deviation and the median in place of the SD and the mean, so a single
hesitation in a short walk moves it far less; the factor 1.4826 makes it equal
to the SD for normally distributed strides, so the two are on the same scale.
Asymmetry is 100 * |left - right| / mean(left, right) of the per-foot means;
applied to swing time it is the "swing asymmetry" of the studies above. Applied
to stride time it is close to zero in any continuous walk, because each foot's
strides span the same stretch of time, so what is left of it mostly reflects
the start and end of the walk and shrinks as strides accumulate.
``FEATURE_DICTIONARY`` gives every column in words, with its unit.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .events import DEFAULT_THRESHOLD_N, STRIDE_RATIO_LIMITS, stride_table

FEATURE_COLUMNS = [
    "n_strides_left",
    "n_strides_right",
    "n_strides_removed",
    "stride_time_mean_s",
    "stride_time_cv_pct",
    "swing_time_mean_s",
    "swing_time_cv_pct",
    "stance_time_mean_s",
    "swing_pct_mean",
    "cadence_strides_per_min",
    "stride_time_asymmetry_pct",
    "swing_time_asymmetry_pct",
]
"""Columns of ``record_features`` (one recording, the midterm pipeline)."""

STRIDE_FEATURE_COLUMNS = [
    "n_strides_left",
    "n_strides_right",
    "stride_time_mean_s",
    "stride_time_cv_pct",
    "stride_time_madcv_pct",
    "swing_time_mean_s",
    "swing_time_cv_pct",
    "swing_time_madcv_pct",
    "stance_time_mean_s",
    "swing_pct_mean",
    "stride_time_asymmetry_pct",
    "swing_time_asymmetry_pct",
]
"""Columns of ``stride_features`` (one participant, from the clean strides).

Cadence is left out: from clean strides alone it is 60 / mean stride time, so it
would repeat ``stride_time_mean_s``."""

MIN_STRIDES_PER_FOOT = 3
"""Fewest strides on a foot for which a standard deviation means anything; with
fewer, the features are missing. D-011's minimums (40 and 10) are far above it."""

MAD_TO_SD = 1.4826
"""Scales the median absolute deviation to the SD of a normal distribution."""

FEATURE_DICTIONARY: dict[str, tuple[str, str]] = {
    "participant": ("-", "Participant ID as in the dataset."),
    "dataset": ("-", "gaitpdb (PhysioNet) or weargait (WearGait-PD)."),
    "study": (
        "-",
        "gaitpdb sub-study (Ga, Ju or Si) or WearGait-PD site prefix (NLS, HC, "
        "WPD or WHC). Never a model input: the prefixes WPD and WHC encode the "
        "diagnosis, and NLS and HC each recruited one group only.",
    ),
    "group": ("-", "PD or Control, from the dataset's participant table."),
    "Age": ("years", "Age in the dataset's participant table (all 50 or over, D-006)."),
    "sex": ("-", "M or F, from the dataset's participant table."),
    "n_tasks": (
        "count",
        "WearGait-PD only: tasks (SelfPace, SelfPace_mat, SelfPace_matTURN) that "
        "contribute clean strides; their strides are pooled (D-011).",
    ),
    "n_strides_left": ("count", "Clean strides of the left foot used."),
    "n_strides_right": ("count", "Clean strides of the right foot used."),
    "n_strides_removed": (
        "count",
        "Midterm pipeline only: strides removed by the stride rules, both feet.",
    ),
    "stride_time_mean_s": (
        "s",
        "Mean stride time (heel strike to the next heel strike of the same foot), "
        "both feet.",
    ),
    "stride_time_cv_pct": (
        "%",
        "Stride-time variability: coefficient of variation (100 x SD / mean) of "
        "each foot's stride times, averaged over the two feet.",
    ),
    "stride_time_madcv_pct": (
        "%",
        "Robust stride-time variability: 100 x 1.4826 x median absolute deviation "
        "/ median of each foot's stride times, averaged over the two feet.",
    ),
    "swing_time_mean_s": ("s", "Mean swing time (toe off to heel strike), both feet."),
    "swing_time_cv_pct": (
        "%",
        "Swing-time variability: coefficient of variation of each foot's swing "
        "times, averaged over the two feet.",
    ),
    "swing_time_madcv_pct": (
        "%",
        "Robust swing-time variability: as the robust stride-time variability, "
        "for swing times.",
    ),
    "stance_time_mean_s": (
        "s",
        "Mean stance time (heel strike to toe off), both feet.",
    ),
    "swing_pct_mean": ("% of stride", "Mean swing time as a share of its stride."),
    "cadence_strides_per_min": (
        "strides/min",
        "Midterm pipeline only: left-foot strides per minute of recording.",
    ),
    "stride_time_asymmetry_pct": (
        "%",
        "100 x |left - right| / mean(left, right) of the two feet's mean stride "
        "times. Near zero in a continuous walk (each foot's strides span the same "
        "time), so it mostly reflects stride count and the walk's start and end.",
    ),
    "swing_time_asymmetry_pct": (
        "%",
        "Swing asymmetry: 100 x |left - right| / mean(left, right) of the two "
        "feet's mean swing times.",
    ),
}


def _cv(x: pd.Series) -> float:
    return float(100.0 * x.std(ddof=1) / x.mean()) if len(x) > 2 else np.nan


def _madcv(x: pd.Series) -> float:
    if len(x) <= 2:
        return np.nan
    v = np.asarray(x, dtype=float)
    med = np.median(v)
    return float(100.0 * MAD_TO_SD * np.median(np.abs(v - med)) / med)


def _asym(left: float, right: float) -> float:
    return float(100.0 * abs(left - right) / np.mean([left, right]))


def record_features(
    df: pd.DataFrame,
    threshold_n: float = DEFAULT_THRESHOLD_N,
    ratio_limits: tuple[float, float] | None = STRIDE_RATIO_LIMITS,
) -> dict:
    """Spatiotemporal features for one loaded record (output of io.load_record).

    Every feature except cadence is computed from kept strides only (see
    events.stride_table); cadence counts every complete left-foot stride.
    """
    left = stride_table(df["L_total"].to_numpy(), threshold_n, ratio_limits)
    right = stride_table(df["R_total"].to_numpy(), threshold_n, ratio_limits)
    kl = left[left["kept"]] if not left.empty else left
    kr = right[right["kept"]] if not right.empty else right
    both = pd.concat([kl, kr], ignore_index=True)
    removed = (
        int((~left["kept"]).sum() + (~right["kept"]).sum()) if not both.empty else 0
    )
    if len(kl) < 3 or len(kr) < 3:
        out = {c: np.nan for c in FEATURE_COLUMNS}
        out.update(
            n_strides_left=len(kl), n_strides_right=len(kr), n_strides_removed=removed
        )
        return out
    duration_min = (df["time_s"].iloc[-1] - df["time_s"].iloc[0]) / 60.0
    return {
        "n_strides_left": int(len(kl)),
        "n_strides_right": int(len(kr)),
        "n_strides_removed": removed,
        "stride_time_mean_s": float(both["stride_s"].mean()),
        "stride_time_cv_pct": float(
            np.mean([_cv(kl["stride_s"]), _cv(kr["stride_s"])])
        ),
        "swing_time_mean_s": float(both["swing_s"].mean()),
        "swing_time_cv_pct": float(np.mean([_cv(kl["swing_s"]), _cv(kr["swing_s"])])),
        "stance_time_mean_s": float(both["stance_s"].mean()),
        "swing_pct_mean": float(both["swing_pct"].mean()),
        "cadence_strides_per_min": float(len(left) / duration_min),
        "stride_time_asymmetry_pct": _asym(
            kl["stride_s"].mean(), kr["stride_s"].mean()
        ),
        "swing_time_asymmetry_pct": _asym(kl["swing_s"].mean(), kr["swing_s"].mean()),
    }


def stride_features(strides: pd.DataFrame) -> dict:
    """Features of one participant from their clean strides of both feet.

    ``strides`` holds only the strides to use, one row each, with ``foot`` ("L"
    or "R"), ``stride_s``, ``swing_s``, ``stance_s`` and ``swing_pct`` (the columns
    of ``gaitpdb.clean_data``'s tables). Returns the STRIDE_FEATURE_COLUMNS; with
    fewer than MIN_STRIDES_PER_FOOT strides on either foot, only the counts are
    filled in and every feature is missing.
    """
    unknown = set(strides["foot"]) - {"L", "R"}
    if unknown:
        raise ValueError(f"unknown foot labels {sorted(unknown)}")
    kl = strides[strides["foot"] == "L"]
    kr = strides[strides["foot"] == "R"]
    out = {c: np.nan for c in STRIDE_FEATURE_COLUMNS}
    out.update(n_strides_left=int(len(kl)), n_strides_right=int(len(kr)))
    if len(kl) < MIN_STRIDES_PER_FOOT or len(kr) < MIN_STRIDES_PER_FOOT:
        return out
    out.update(
        {
            "stride_time_mean_s": float(strides["stride_s"].mean()),
            "stride_time_cv_pct": float(
                np.mean([_cv(kl["stride_s"]), _cv(kr["stride_s"])])
            ),
            "stride_time_madcv_pct": float(
                np.mean([_madcv(kl["stride_s"]), _madcv(kr["stride_s"])])
            ),
            "swing_time_mean_s": float(strides["swing_s"].mean()),
            "swing_time_cv_pct": float(
                np.mean([_cv(kl["swing_s"]), _cv(kr["swing_s"])])
            ),
            "swing_time_madcv_pct": float(
                np.mean([_madcv(kl["swing_s"]), _madcv(kr["swing_s"])])
            ),
            "stance_time_mean_s": float(strides["stance_s"].mean()),
            "swing_pct_mean": float(strides["swing_pct"].mean()),
            "stride_time_asymmetry_pct": _asym(
                kl["stride_s"].mean(), kr["stride_s"].mean()
            ),
            "swing_time_asymmetry_pct": _asym(
                kl["swing_s"].mean(), kr["swing_s"].mean()
            ),
        }
    )
    return out


def participant_features(strides: pd.DataFrame) -> pd.DataFrame:
    """One row of ``stride_features`` per included participant of a clean-stride table.

    ``strides`` is a table as scripts/make_clean_strides.py writes it: one row per
    stride with ``participant``, ``clean`` (the stride is kept) and ``included``
    (the participant meets D-011's minimum), plus the columns ``stride_features``
    reads. Only clean strides of included participants are used, all of them
    (D-011: the minimum is not a truncation). Returns ``participant`` and the
    STRIDE_FEATURE_COLUMNS, sorted by participant.
    """
    needed = {"participant", "clean", "included", "foot"}
    missing = needed - set(strides.columns)
    if missing:
        raise ValueError(f"clean-stride table lacks {sorted(missing)}")
    use = strides[strides["clean"].astype(bool) & strides["included"].astype(bool)]
    rows = [
        {"participant": p, **stride_features(g)}
        for p, g in use.groupby("participant", sort=True)
    ]
    return pd.DataFrame(rows, columns=["participant", *STRIDE_FEATURE_COLUMNS])


def feature_dictionary_markdown(columns: list[str]) -> str:
    """A Markdown table of FEATURE_DICTIONARY for ``columns``, in that order."""
    unknown = [c for c in columns if c not in FEATURE_DICTIONARY]
    if unknown:
        raise KeyError(f"no dictionary entry for {unknown}")
    lines = ["| Column | Unit | Definition |", "|---|---|---|"]
    for c in columns:
        unit, text = (_cell(x) for x in FEATURE_DICTIONARY[c])
        lines.append(f"| `{c}` | {unit} | {text} |")
    return "\n".join(lines) + "\n"


def _cell(text: str) -> str:
    """Escape ``|`` so a Markdown table cell is not split (e.g. ``|left - right|``)."""
    return text.replace("|", "\\|")
