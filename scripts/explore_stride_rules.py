"""Exploration for T-017: what the current stride rules remove, and filters on the stride series.

Exploratory, not part of the analysis pipeline: nothing in src/ is changed and no
model uses these outputs. It looks at the usual walk (walk 01) of the analysed
gaitpdb participants (aged 50 or over, DECISIONS.md D-006) and asks

* what the stride rules in gaitpdb.events remove, and whether they remove more
  from PD participants than from controls;
* how the stride-duration series of a PD participant and a control differ:
  raw force, stride durations, stride-to-stride differences, power spectra;
* whether a Butterworth band-pass (to find turns) or high-pass (to keep the
  step-to-step variability and drop turns and slow drift) separates the two;
* whether the Si recordings match the overground or the treadmill condition of
  the Si study, by walking speed.

For each sub-study the example pair is the PD participant and the control whose
share of removed strides is closest to their group's median, so the examples
are typical and anyone re-running this gets the same people.

    python scripts/explore_stride_rules.py [--data data/raw/gaitpdb]

Writes figures/explore_stride_rules/*.png and results/explore_stride_rules.txt.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.signal import butter, filtfilt, freqz, periodogram  # noqa: E402
from scipy.stats import mannwhitneyu  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb import find_data_dir, load_record  # noqa: E402
from gaitpdb.events import (  # noqa: E402
    STRIDE_LIMITS_S,
    STRIDE_RATIO_LIMITS,
    contact_events,
    stride_table,
)

FIG_DIR = ROOT / "figures" / "explore_stride_rules"
OUT_TXT = ROOT / "results" / "explore_stride_rules.txt"
FEATURES = ROOT / "results" / "features_usual_walk.csv"

BAND = (0.03, 0.18)  # band-pass, cycles per stride, read off the spectra
HIGH_CUTOFF = 0.18  # high-pass, cycles per stride
ORDER = 2
DOUBLE_STRIDE = (1.75, 2.25)  # x the median: candidate missed heel strike
FOOT_COLOR = {"L": "tab:blue", "R": "tab:orange"}
FOOT_MARKER = {"L": "o", "R": "s"}

# Si study (Frenkel-Toledo et al., Mov Disord 2005), values as typed from the
# paper by Anna on 2026-10-23. [UNVERIFIED]: the reference is not yet checked
# into report/midterm/sources.md. Mean (SD) per condition.
SI_PAPER = {
    "PD": {"n": 36, "unassisted": 1.12, "walker": 1.05, "treadmill": 1.05},
    "Control": {"n": 30, "unassisted": 1.24, "walker": 1.21, "treadmill": 1.21},
}
SI_PAPER_CV = {
    "PD": {"unassisted": 2.24, "walker": 2.40, "treadmill": 1.76},
    "Control": {"unassisted": 1.94, "walker": 1.87, "treadmill": 1.64},
}

lines: list[str] = []


def say(text: str = "") -> None:
    print(text)
    lines.append(text)


def removal_table() -> pd.DataFrame:
    """Share of strides removed per analysed usual-walk recording."""
    f = pd.read_csv(FEATURES)
    f = f[f["meets_age_rule"]].copy()
    kept = f["n_strides_left"] + f["n_strides_right"]
    f["removed_pct"] = 100 * f["n_strides_removed"] / (kept + f["n_strides_removed"])
    return f


def pick_pair(f: pd.DataFrame, study: str) -> dict[str, str]:
    """Control and PD record of `study` closest to their group's median removal."""
    out = {}
    for group in ("Control", "PD"):
        d = f[(f["study"] == study) & (f["group"] == group)]
        i = (d["removed_pct"] - d["removed_pct"].median()).abs().to_numpy().argmin()
        out[group] = d["record"].iloc[i]
    return out


def strides(df: pd.DataFrame, foot: str) -> pd.DataFrame:
    return stride_table(df[f"{foot}_total"].to_numpy()).reset_index(drop=True)


def artefacts(s: np.ndarray) -> np.ndarray:
    """Strides outside the hard limits, or close to twice the median."""
    med = np.median(s)
    lo, hi = STRIDE_LIMITS_S
    r = s / med
    return (s < lo) | (s > hi) | ((r > DOUBLE_STRIDE[0]) & (r < DOUBLE_STRIDE[1]))


def detection_copy(s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Artefacts replaced by the median of the rest, so the filters do not ring."""
    bad = artefacts(s)
    return np.where(bad, np.median(s[~bad]), s), bad


def band_pass(s: np.ndarray) -> np.ndarray:
    det, _ = detection_copy(s)
    b, a = butter(ORDER, BAND, btype="bandpass", fs=1.0)
    return filtfilt(b, a, det - det.mean())


def high_pass(s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """High-passed series with artefacts and their neighbours set to NaN."""
    det, bad = detection_copy(s)
    b, a = butter(ORDER, HIGH_CUTOFF, btype="highpass", fs=1.0)
    hp = filtfilt(b, a, det - det.mean())
    mask = bad | np.r_[bad[1:], False] | np.r_[False, bad[:-1]]
    return np.where(mask, np.nan, hp), bad


def section_removal(f: pd.DataFrame) -> None:
    say("1. Strides removed by the current rules (analysed usual walks)")
    say(
        f"Rules: {STRIDE_LIMITS_S[0]}-{STRIDE_LIMITS_S[1]} s, swing 10-70% of the "
        f"stride, {STRIDE_RATIO_LIMITS[0]}-{STRIDE_RATIO_LIMITS[1]} x the foot's "
        "median stride in the record (gaitpdb.events)."
    )
    t = f.groupby(["study", "group"])["removed_pct"].describe()
    say(t[["count", "50%", "75%", "max"]].round(1).to_string())
    pd_, co = (f.loc[f["group"] == g, "removed_pct"] for g in ("PD", "Control"))
    p = mannwhitneyu(pd_, co).pvalue
    say(
        f"All studies, median % removed: PD {pd_.median():.2f}, control "
        f"{co.median():.2f}; Mann-Whitney p = {p:.3f}"
    )
    say()


def fig_force(data: Path, pair: dict[str, str]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 3.6), sharey=False)
    for ax, (group, rec) in zip(axes, pair.items()):
        df = load_record(data / f"{rec}.txt")
        t = df["time_s"].to_numpy()
        win = (t >= 30) & (t < 40)
        for foot in ("L", "R"):
            force = df[f"{foot}_total"].to_numpy()
            c = FOOT_COLOR[foot]
            ax.plot(t[win], force[win], color=c, label=f"{foot} total force")
            hs, to = contact_events(force)
            hs = [i for i in hs if 30 <= t[i] < 40]
            to = [i for i in to if 30 <= t[i] < 40]
            ax.plot(t[hs], force[hs], "v", color=c)
            ax.plot(t[to], force[to], "^", color=c)
        ax.axhline(20, color="grey", ls="--", lw=0.8, label="20 N threshold")
        ax.set(
            title=f"{group} {rec}: vertical force, 30-40 s (v heel strike, ^ toe-off)",
            xlabel="time (s)",
            ylabel="force (N)",
        )
        ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_force_pd_vs_control.png", dpi=110)
    plt.close(fig)


def section_sensors(data: Path, rec: str) -> None:
    """One left stance phase of `rec`, sensor by sensor, to show nothing smooths it."""
    df = load_record(data / f"{rec}.txt")
    st = strides(df, "L")
    row = st.iloc[len(st) // 4]
    seg = df[(df["time_s"] >= row["hs_s"]) & (df["time_s"] <= row["to_s"])]
    cols = ["time_s"] + [f"L{i}" for i in range(1, 9)] + ["L_total"]
    say(f"2. Raw left-foot sensors of {rec}, one stance phase (every 5th sample, N)")
    say("Sensors L1 heel ... L8 toes (positions in the PhysioNet format.txt).")
    say(seg[cols].iloc[::5].round(2).to_string(index=False))
    say()


def fig_strides(data: Path, pair: dict[str, str]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 3.6))
    for ax, (group, rec) in zip(axes, pair.items()):
        df = load_record(data / f"{rec}.txt")
        for foot in ("L", "R"):
            st = strides(df, foot)
            m, c = FOOT_MARKER[foot], FOOT_COLOR[foot]
            ok, gone = st[st["kept"]], st[~st["kept"]]
            ax.plot(ok["hs_s"], ok["stride_s"], m, ms=3, color=c, label=f"{foot} kept")
            ax.plot(
                gone["hs_s"],
                gone["stride_s"],
                m,
                ms=8,
                color="tab:red",
                mec="white",
                label=f"{foot} removed",
            )
        ax.set(
            title=f"{group} {rec}: every stride, whole walk",
            xlabel="time of heel strike (s)",
            ylabel="stride duration (s)",
        )
        ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_stride_durations_kept_removed.png", dpi=110)
    plt.close(fig)


def fig_deltas(data: Path, pair: dict[str, str]) -> None:
    cap = 0.6
    fig, axes = plt.subplots(1, 2, figsize=(14, 3.6))
    say("3. Stride-to-stride differences (consecutive strides only), RMS in s")
    for ax, (group, rec) in zip(axes, pair.items()):
        df = load_record(data / f"{rec}.txt")
        for foot in ("L", "R"):
            st = strides(df, foot)
            cons = np.r_[
                False,
                st["hs_s"].iloc[1:].to_numpy() == st["next_hs_s"].iloc[:-1].to_numpy(),
            ]
            d = st["stride_s"].diff().to_numpy()
            x, y = st["hs_s"].to_numpy()[cons], d[cons]
            ax.plot(
                x,
                np.clip(y, -cap, cap),
                FOOT_MARKER[foot] + "-",
                ms=3,
                lw=0.7,
                color=FOOT_COLOR[foot],
                label=f"{foot} (clipped at +/-{cap} s)",
            )
            say(
                f"  {group} {rec} {foot}: {len(y)} differences, "
                f"RMS {np.sqrt(np.mean(y**2)):.3f}"
            )
        ax.axhline(0, color="grey", lw=0.8)
        ax.set(
            title=f"{group} {rec}: change from the previous stride",
            xlabel="time of heel strike (s)",
            ylabel="change (s)",
            ylim=(-cap - 0.05, cap + 0.05),
        )
        ax.legend(fontsize=7, loc="upper right")
    say()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_stride_to_stride_differences.png", dpi=110)
    plt.close(fig)


def fig_spectra(data: Path, pair: dict[str, str]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 3.6), sharey=True)
    say("4. Power spectra of the stride series (artefacts set to the median first)")
    for ax, (group, rec) in zip(axes, pair.items()):
        df = load_record(data / f"{rec}.txt")
        for foot in ("L", "R"):
            det, _ = detection_copy(strides(df, foot)["stride_s"].to_numpy())
            fr, p = periodogram(det - det.mean(), fs=1.0)
            ax.plot(
                fr[1:],
                p[1:],
                FOOT_MARKER[foot] + "-",
                ms=3,
                lw=1,
                color=FOOT_COLOR[foot],
                label=foot,
            )
            top = fr[1:][np.argsort(p[1:])[::-1][:3]]
            say(
                f"  {group} {rec} {foot}: strongest peaks at "
                + ", ".join(f"{x:.3f} (every {1 / x:.1f} strides)" for x in top)
            )
        ax.axvspan(0.15, 0.2, color="grey", alpha=0.15)
        ax.set(
            title=f"{group} {rec}: power spectrum of stride duration",
            xlabel="frequency (cycles per stride)",
            ylabel="power",
        )
        ax.legend(fontsize=7, loc="upper right")
    say()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_power_spectra.png", dpi=110)
    plt.close(fig)


def fig_response() -> None:
    freqs = np.array([0.03, 0.06, 0.12, 0.15, 0.18, 0.2, 0.25, 0.3, 0.4, 0.5])
    say(f"5. Filter gain after filtfilt (|H|^2), order {ORDER}")
    fig, ax = plt.subplots(figsize=(7, 3.4))
    grid = np.linspace(0.005, 0.5, 400)
    for name, ba in [
        (
            f"band-pass {BAND[0]}-{BAND[1]}",
            butter(ORDER, BAND, btype="bandpass", fs=1.0),
        ),
        (
            f"high-pass {HIGH_CUTOFF}",
            butter(ORDER, HIGH_CUTOFF, btype="highpass", fs=1.0),
        ),
    ]:
        _, h = freqz(*ba, worN=grid, fs=1.0)
        ax.plot(grid, np.abs(h) ** 2, label=name)
        _, hp = freqz(*ba, worN=freqs, fs=1.0)
        say(
            f"  {name}: "
            + "  ".join(f"{f:.2f}:{abs(v) ** 2:.2f}" for f, v in zip(freqs, hp))
        )
    ax.set(
        xlabel="frequency (cycles per stride)",
        ylabel="gain (share of power passed)",
        title="Frequency response of the two filters",
    )
    ax.legend(fontsize=8)
    say()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "05_filter_response.png", dpi=110)
    plt.close(fig)


def fig_bandpass(data: Path, pair: dict[str, str]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 6.5), sharex="col")
    for col, (group, rec) in enumerate(pair.items()):
        df = load_record(data / f"{rec}.txt")
        for foot in ("L", "R"):
            st = strides(df, foot)
            s = st["stride_s"].to_numpy()
            m, c = FOOT_MARKER[foot], FOOT_COLOR[foot]
            axes[0, col].plot(st["hs_s"], s, m + "-", ms=3, lw=0.6, color=c, label=foot)
            axes[1, col].plot(
                st["hs_s"], band_pass(s), "-", lw=1.5, color=c, label=foot
            )
        axes[0, col].set(title=f"{group} {rec}: raw stride durations", ylabel="s")
        axes[1, col].set(
            title=f"band-passed {BAND[0]}-{BAND[1]} cycles/stride",
            xlabel="time of heel strike (s)",
            ylabel="deviation (s)",
        )
        axes[1, col].axhline(0, color="grey", lw=0.8)
        for ax in axes[:, col]:
            ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "06_band_pass.png", dpi=110)
    plt.close(fig)


def fig_highpass(data: Path, study: str, pair: dict[str, str], cv: pd.Series) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14, 6.5), sharex="col")
    say(f"  {study}: stride-time CV, current rules vs high-pass (% of mean stride)")
    for col, (group, rec) in enumerate(pair.items()):
        df = load_record(data / f"{rec}.txt")
        for foot in ("L", "R"):
            st = strides(df, foot)
            s = st["stride_s"].to_numpy()
            hp, bad = high_pass(s)
            m, c = FOOT_MARKER[foot], FOOT_COLOR[foot]
            axes[0, col].plot(st["hs_s"], s, m + "-", ms=3, lw=0.6, color=c, label=foot)
            axes[0, col].plot(
                st["hs_s"][bad],
                s[bad],
                "X",
                ms=10,
                color="black",
                label=f"{foot} artefact (rule)",
            )
            axes[1, col].plot(
                st["hs_s"], hp, m + "-", ms=3, lw=0.8, color=c, label=foot
            )
            kept = s[st["kept"].to_numpy()]
            say(
                f"    {group} {rec} {foot}: artefacts {int(bad.sum())}; current CV "
                f"{100 * kept.std(ddof=1) / kept.mean():.2f}; high-pass "
                f"{100 * np.nanstd(hp, ddof=1) / s[~bad].mean():.2f}"
            )
        say(f"    {group} {rec}: team feature stride_time_cv_pct = {cv[rec]:.2f}")
        axes[0, col].set(
            title=f"{group} {rec}: raw stride durations (X = artefact rule)", ylabel="s"
        )
        axes[1, col].set(
            title=f"high-passed above {HIGH_CUTOFF} cycles/stride",
            xlabel="time of heel strike (s)",
            ylabel="deviation (s)",
            ylim=(-0.3, 0.3),
        )
        axes[1, col].axhline(0, color="grey", lw=0.8)
        for ax in axes[:, col]:
            ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"07_high_pass_{study}.png", dpi=110)
    plt.close(fig)


def section_si() -> None:
    f = pd.read_csv(FEATURES)  # every usual walk, before the age rule
    si = f[f["study"] == "Si"]
    say("7. Si walk 01 vs the Si study's conditions (all Si recordings, no age rule)")
    say("Paper values [UNVERIFIED reference], typed from the paper.")
    for group in ("PD", "Control"):
        d = si[si["group"] == group]
        p = SI_PAPER[group]
        say(
            f"  {group}: ours n = {len(d)}, speed {d['Speed_01'].mean():.2f} "
            f"(SD {d['Speed_01'].std():.2f}) m/s, stride CV "
            f"{d['stride_time_cv_pct'].mean():.2f}% | paper n = {p['n']}, speed "
            f"unassisted {p['unassisted']}, walker {p['walker']}, treadmill "
            f"{p['treadmill']} m/s; CV unassisted {SI_PAPER_CV[group]['unassisted']}%"
        )
    say()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(ROOT / "data" / "raw" / "gaitpdb"))
    data = find_data_dir(ap.parse_args().data)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    say("T-017 exploration of the stride rules (scripts/explore_stride_rules.py)")
    say("Exploratory: six participants for the figures; nothing in src/ changed.")
    say()
    f = removal_table()
    section_removal(f)
    pairs = {s: pick_pair(f, s) for s in ("Ga", "Ju", "Si")}
    say("Example pairs (closest to their group's median removal, per sub-study):")
    for s, p in pairs.items():
        say(f"  {s}: control {p['Control']}, PD {p['PD']}")
    say()

    ga = pairs["Ga"]
    fig_force(data, ga)
    section_sensors(data, ga["PD"])
    fig_strides(data, ga)
    fig_deltas(data, ga)
    fig_spectra(data, ga)
    fig_response()
    fig_bandpass(data, ga)
    cv = f.set_index("record")["stride_time_cv_pct"]
    say("6. High-pass on the stride series, by sub-study")
    for study, pair in pairs.items():
        fig_highpass(data, study, pair, cv)
    say()
    section_si()

    OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_TXT.relative_to(ROOT)} and {FIG_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
