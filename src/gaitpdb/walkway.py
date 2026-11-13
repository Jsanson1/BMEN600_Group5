"""Insole gait events checked against the WearGait-PD walkway (task T-025).

The Midterm Research Plan carries gaitpdb's contact threshold (20 N) over to
WearGait-PD's insoles only after checking it against an independent reference:
the instrumented walkway. This module holds that check; the walkway itself is
never used to find strides in the analysis.

What the dataset provides (Synapse syn52540892, wiki "Data description" and
"Things to know"), at 100 Hz on the walkway's clock:

* ``L Foot Contact``, ``R Foot Contact`` (the CSV files' names; the wiki and the
  MAT files call them LFootContact and RFootContact): 1 while that foot is in contact with the
  walkway (ProtoKinetics Zeno, 16 ft), 0 otherwise. Partial footfalls at the
  walkway's edges are excluded, so they read 0. For the tasks done entirely on
  the walkway (``_mat``), the walkway software writes one erroneous 0 frame at
  the very end of a recording;
* ``LTotalForce``, ``RTotalForce``: total force on each insole, in newtons
  (Moticon OpenGo, 16 sensors). The insoles lag the walkway by a site-specific
  delay that the dataset's authors corrected, plus a small random remainder.

Because of that remainder, the comparison is made on durations rather than on
time stamps: the stance time of each complete walkway footfall against the
stance time of the insole contact that overlaps it, and, where two consecutive
footfalls of the same foot are both on the walkway, the stride and swing times.
A threshold that misses a toe-off merges two footfalls into one insole contact,
and one that misses a heel strike leaves a footfall without one; both show up as
footfalls that are not matched one to one.

* ``walkway_footfalls``: complete contact intervals of one foot on the walkway;
* ``insole_contacts``: contact intervals of one foot from its insole force at a
  threshold, with ``events.contact_events`` (the rule used for gaitpdb);
* ``match_footfalls``: each walkway footfall paired with the insole contact
  that overlaps it most, with the duration differences (insole minus walkway);
* ``agreement``: one row of summary measures for a set of matched footfalls;
* ``threshold_candidates``: the thresholds compared, the same kinds as in
  scripts/check_event_detection.py for gaitpdb (fixed, a share of body weight,
  a share of the recording's own force level).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .events import contact_events
from .io import SAMPLE_RATE_HZ

FIXED_THRESHOLDS_N = (10.0, 20.0, 30.0, 50.0, 75.0, 100.0)
BODY_WEIGHT_SHARES = (0.025, 0.05, 0.075, 0.10)
FORCE_LEVEL_SHARES = (0.025, 0.05, 0.075, 0.10)
"""The midterm's candidates (10, 20, 50 N; 2.5% and 5%) and a few more on either
side, so that the best agreement does not sit at the edge of the grid."""
FORCE_LEVEL_PERCENTILE = 95
G = 9.81  # m/s^2, kg to N
AGREE_WITHIN_S = 0.03  # three samples at 100 Hz
CONTACT_COLUMNS = {"L": "L Foot Contact", "R": "R Foot Contact"}  # as in the CSV files
FORCE_COLUMNS = {"L": "LTotalForce", "R": "RTotalForce"}


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """(start, end) sample indexes of each run of True, end exclusive."""
    edges = np.diff(np.r_[0, mask.astype(np.int8), 0])
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def walkway_footfalls(contact: np.ndarray) -> pd.DataFrame:
    """Complete footfalls of one foot on the walkway.

    ``contact`` is the frame-by-frame 0/1 marker (NaN where the walkway has no
    data, such as the padding at either end). A footfall is a run of 1s; runs
    touching the first or last frame with data are incomplete and dropped,
    which also removes the erroneous last frame of the ``_mat`` tasks. Returns
    one row per footfall: ``on`` and ``off`` (sample indexes, ``off``
    exclusive), ``on_s``, ``off_s`` and ``stance_s``.
    """
    c = np.asarray(contact, dtype=float).copy()
    valid = np.flatnonzero(~np.isnan(c))
    if len(valid) < 3:
        return pd.DataFrame(columns=["on", "off", "on_s", "off_s", "stance_s"])
    c[valid[-1]] = np.nan  # the _mat tasks' erroneous last frame; harmless elsewhere
    first, last = valid[0], valid[-2]
    rows = [
        (a, b)
        for a, b in _runs(np.nan_to_num(c, nan=0.0) > 0.5)
        if a > first and b <= last  # b is exclusive, so b <= last ends before it
    ]
    out = pd.DataFrame(rows, columns=["on", "off"], dtype=int)
    out["on_s"] = out["on"] / SAMPLE_RATE_HZ
    out["off_s"] = out["off"] / SAMPLE_RATE_HZ
    out["stance_s"] = (out["off"] - out["on"]) / SAMPLE_RATE_HZ
    return out


def insole_contacts(force: np.ndarray, threshold_n: float) -> pd.DataFrame:
    """Contact intervals of one foot from its insole total force at ``threshold_n``.

    Uses ``events.contact_events``, the rule applied to gaitpdb (contact while the
    force exceeds the threshold, phases shorter than 0.1 s merged). Samples
    without data (NaN) count as no contact, and contacts touching them are
    flagged ``touches_gap`` so they can be left out of the comparison. Returns
    one row per complete contact: ``hs`` and ``to`` (sample indexes),
    ``touches_gap``.
    """
    f = np.asarray(force, dtype=float)
    missing = np.isnan(f)
    hs, to = contact_events(np.nan_to_num(f, nan=0.0), threshold_n)
    rows = []
    for a in hs:
        later = to[to > a]
        if len(later) == 0:
            break
        b = int(later[0])
        rows.append((int(a), b, bool(missing[max(a - 1, 0) : b + 1].any())))
    return pd.DataFrame(rows, columns=["hs", "to", "touches_gap"])


def match_footfalls(walkway: pd.DataFrame, insole: pd.DataFrame) -> pd.DataFrame:
    """Pair each walkway footfall with the insole contact that overlaps it most.

    Returns ``walkway`` with ``matched`` (an insole contact overlaps it),
    ``one_to_one`` (that contact overlaps no other walkway footfall of this
    foot, this footfall overlaps no other insole contact, and the contact does
    not touch missing insole data), the insole ``hs`` and ``to``, and the
    duration differences in seconds, insole minus walkway: ``d_stance_s`` for
    every one-to-one footfall, and ``d_stride_s`` and ``d_swing_s`` from this
    footfall to the next one of the same foot when both are one to one and
    matched to consecutive insole contacts.
    """
    out = walkway.copy().reset_index(drop=True)
    n = len(out)
    for col in ("hs", "to"):
        out[col] = np.nan
    out["matched"] = False
    out["one_to_one"] = False
    if n == 0 or insole.empty:
        for col in ("d_stance_s", "d_stride_s", "d_swing_s"):
            out[col] = np.nan
        return out
    hs = insole["hs"].to_numpy()
    to = insole["to"].to_numpy()
    on = out["on"].to_numpy()
    off = out["off"].to_numpy()
    overlap = np.clip(
        np.minimum(off[:, None], to[None, :]) - np.maximum(on[:, None], hs[None, :]),
        0,
        None,
    )  # walkway footfall x insole contact, in samples
    best = overlap.argmax(axis=1)
    has = overlap[np.arange(n), best] > 0
    per_contact = (overlap > 0).sum(axis=0)  # walkway footfalls touching each contact
    per_footfall = (overlap > 0).sum(axis=1)  # contacts touching each footfall
    gap = insole["touches_gap"].to_numpy()
    one = has & (per_contact[best] == 1) & (per_footfall == 1) & ~gap[best]
    out["matched"] = has
    out["one_to_one"] = one
    out.loc[has, "hs"] = hs[best[has]]
    out.loc[has, "to"] = to[best[has]]
    stance_insole = (out["to"] - out["hs"]) / SAMPLE_RATE_HZ
    out["d_stance_s"] = np.where(one, stance_insole - out["stance_s"], np.nan)
    d_stride = np.full(n, np.nan)
    d_swing = np.full(n, np.nan)
    for k in range(n - 1):
        if one[k] and one[k + 1] and best[k + 1] == best[k] + 1:
            walk_stride = (on[k + 1] - on[k]) / SAMPLE_RATE_HZ
            walk_swing = (on[k + 1] - off[k]) / SAMPLE_RATE_HZ
            ins_stride = (hs[best[k + 1]] - hs[best[k]]) / SAMPLE_RATE_HZ
            ins_swing = (hs[best[k + 1]] - to[best[k]]) / SAMPLE_RATE_HZ
            d_stride[k] = ins_stride - walk_stride
            d_swing[k] = ins_swing - walk_swing
    out["d_stride_s"] = d_stride
    out["d_swing_s"] = d_swing
    return out


def agreement(matched: pd.DataFrame) -> dict:
    """Summary of matched footfalls: detection, then bias and spread of durations.

    ``one_to_one_pct`` is the share of walkway footfalls the insole contact
    matches one to one; ``agree_pct`` the share matched one to one with a stance
    time within AGREE_WITHIN_S of the walkway's, which rewards finding each
    footfall and timing it well (a high threshold finds more footfalls but
    shortens every stance; a low one times them well but merges more). For each duration (stance, stride, swing): the number of
    pairs, the median difference (insole minus walkway, s), the median absolute
    difference, and the Bland-Altman limits of agreement (mean difference +/-
    1.96 SD).
    """
    n = len(matched)
    close = matched["d_stance_s"].abs() <= AGREE_WITHIN_S + 1e-9
    out = {
        "n_footfalls": int(n),
        "one_to_one_pct": float(100 * matched["one_to_one"].mean()) if n else np.nan,
        "unmatched_pct": float(100 * (~matched["matched"]).mean()) if n else np.nan,
        "agree_pct": float(100 * close.mean()) if n else np.nan,
    }
    for name in ("stance", "stride", "swing"):
        d = matched[f"d_{name}_s"].dropna().to_numpy()
        out[f"n_{name}"] = int(len(d))
        if len(d) >= 2:
            sd = float(d.std(ddof=1))
            out.update(
                {
                    f"{name}_median_diff_s": float(np.median(d)),
                    f"{name}_median_abs_diff_s": float(np.median(np.abs(d))),
                    f"{name}_loa_low_s": float(d.mean() - 1.96 * sd),
                    f"{name}_loa_high_s": float(d.mean() + 1.96 * sd),
                }
            )
        else:
            for k in ("median_diff_s", "median_abs_diff_s", "loa_low_s", "loa_high_s"):
                out[f"{name}_{k}"] = np.nan
    return out


def force_level(task: pd.DataFrame) -> float:
    """Mean over the two feet of the 95th percentile of each foot's total force (N),
    the reference for thresholds relative to a recording (as for gaitpdb)."""
    return float(
        np.mean(
            [
                np.nanpercentile(task[c].to_numpy(dtype=float), FORCE_LEVEL_PERCENTILE)
                for c in FORCE_COLUMNS.values()
            ]
        )
    )


def threshold_candidates(
    task: pd.DataFrame, body_mass_kg: float | None = None
) -> dict[str, float]:
    """Label -> threshold in newtons for one recording.

    Fixed thresholds, shares of the participant's body weight (left out when the
    mass is unknown) and shares of the recording's force level.
    """
    out = {f"{t:g} N": float(t) for t in FIXED_THRESHOLDS_N}
    if body_mass_kg is not None and np.isfinite(body_mass_kg) and body_mass_kg > 0:
        for s in BODY_WEIGHT_SHARES:
            out[f"{100 * s:g}% of body weight"] = float(s * body_mass_kg * G)
    level = force_level(task)
    for s in FORCE_LEVEL_SHARES:
        out[f"{100 * s:g}% of force level"] = float(s * level)
    return out


def compare_task(
    task: pd.DataFrame, thresholds: dict[str, float], walk_only: bool = True
) -> pd.DataFrame:
    """Matched footfalls of both feet of one recording, for every threshold.

    ``task`` needs the walkway contact and insole force columns of both feet.
    With ``walk_only`` and a ``GeneralEvent`` column, only footfalls whose every
    sample is labelled "Walk" are returned, the straight walking the analysis
    uses (turns and standing on the walkway produce shuffling contacts the
    analysis never keeps); matching is still done against all footfalls, so an
    insole contact that also covers a turn footfall is not counted one to one.
    A kept footfall's ``d_stride_s`` and ``d_swing_s`` are set only when the next
    footfall of the same foot is kept too, so they never run into a turn.
    Returns the rows of ``match_footfalls`` with ``foot`` and ``threshold``
    (the label) added.
    """
    labels = (
        task["GeneralEvent"].astype(str).to_numpy()
        if walk_only and "GeneralEvent" in task
        else None
    )
    frames = []
    for foot in ("L", "R"):
        walk = walkway_footfalls(task[CONTACT_COLUMNS[foot]].to_numpy())
        if labels is not None and len(walk):
            keep = np.array(
                [(labels[a:b] == "Walk").all() for a, b in zip(walk["on"], walk["off"])]
            )
        else:
            keep = np.ones(len(walk), bool)
        force = task[FORCE_COLUMNS[foot]].to_numpy(dtype=float)
        next_kept = np.r_[keep[1:], False]
        for label, t in thresholds.items():
            m = match_footfalls(walk, insole_contacts(force, t))
            m.loc[~next_kept, ["d_stride_s", "d_swing_s"]] = np.nan
            m = m[keep]
            m.insert(0, "threshold", label)
            m.insert(0, "foot", foot)
            frames.append(m)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
