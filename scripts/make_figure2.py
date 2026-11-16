"""Figure 2: the evaluation design, drawn from the participants the models use.

A schematic for the methods section: within PhysioNet's protocols (repeated
participant-grouped cross-validation), across its protocols (leave one sub-study
out), with the two datasets combined (DECISIONS.md D-007's main analysis) and
across cohorts (fitted on PhysioNet, tested once on WearGait-PD). The counts are
the participants in the final feature tables, results/features_gaitpdb.csv and
results/features_weargait.csv (aged 50 or over, D-006, with enough clean strides
on each foot, D-011), so the figure cannot drift from the analysis.

    python scripts/make_figure2.py [--results results] [--fig figures]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["text.hinting"] = "default"
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gaitpdb import MIN_AGE_YEARS  # noqa: E402
from gaitpdb.evaluation import MODEL_FEATURES  # noqa: E402

COLORS = {"Control": "#3b6ea5", "PD": "#c8552d"}
STUDY_LABEL = {
    "Ga": "Ga (dual task)",
    "Ju": "Ju (cueing)",
    "Si": "Si (treadmill study)",
}
STUDIES = ("Ga", "Ju", "Si")
H = 4.6  # bar height


def counts(results: Path) -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    """PD and control counts per gaitpdb sub-study, and for WearGait-PD."""
    g = pd.read_csv(results / "features_gaitpdb.csv")
    w = pd.read_csv(results / "features_weargait.csv")
    per_study = {
        s: {grp: int(((g["study"] == s) & (g["group"] == grp)).sum()) for grp in COLORS}
        for s in STUDIES
    }
    weargait = {grp: int((w["group"] == grp).sum()) for grp in COLORS}
    return per_study, weargait


def bar(ax, x, y, w, n_pd, n_co, label, lw=0.8):
    """A horizontal bar split into PD (left) and control (right) parts, labelled."""
    total = n_pd + n_co
    ax.add_patch(Rectangle((x, y), w * n_pd / total, H, color=COLORS["PD"], lw=0))
    ax.add_patch(
        Rectangle(
            (x + w * n_pd / total, y),
            w * n_co / total,
            H,
            color=COLORS["Control"],
            lw=0,
        )
    )
    ax.add_patch(Rectangle((x, y), w, H, fill=False, lw=lw, ec="black"))
    ax.text(
        x + w / 2,
        y + H / 2,
        f"{label}: {n_pd} PD, {n_co} control",
        ha="center",
        va="center",
        fontsize=7,
        color="white",
    )


def heldout(ax, x, y, w, text):
    ax.add_patch(Rectangle((x, y), w, H, fill=False, lw=1.2, ec="black", hatch="///"))
    ax.text(
        x + w / 2,
        y + H / 2,
        text,
        ha="center",
        va="center",
        fontsize=7,
        bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"),
    )


def folds(ax, y, label="train"):
    for k in range(5):
        x = k * 16.5
        if k == 4:
            heldout(ax, x, y, 15.5, "test fold")
        else:
            ax.add_patch(Rectangle((x, y), 15.5, H, fc="#dddddd", ec="black", lw=0.8))
            ax.text(x + 7.75, y + H / 2, label, ha="center", va="center", fontsize=7)


def title(ax, y, text):
    ax.text(0, y, text, fontsize=8, weight="bold", va="center")


def caption(ax, y, text):
    ax.text(0, y, text, fontsize=6.5, va="top", color="#222222")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--fig", default=str(ROOT / "figures"))
    args = ap.parse_args()
    c, w = counts(Path(args.results))
    n_pd = sum(v["PD"] for v in c.values())
    n_co = sum(v["Control"] for v in c.values())

    fig, ax = plt.subplots(figsize=(7.2, 6.8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    title(
        ax,
        98.5,
        f"Participants aged {MIN_AGE_YEARS} or over with enough clean strides on each foot",
    )
    bar(ax, 0, 92, 48.5, n_pd, n_co, "PhysioNet, three sub-studies")
    bar(ax, 51.5, 92, 48.5, w["PD"], w["Control"], "WearGait-PD, three sites")
    caption(
        ax,
        90.6,
        f"{len(MODEL_FEATURES)} timing features per participant (+ age and sex as "
        "covariates); logistic regression, SVM and random forest, their settings tuned "
        "inside the\ntraining participants only. A participant's strides are never split "
        "between training and test.",
    )

    title(
        ax,
        82.5,
        "A. Within PhysioNet: 5-fold cross-validation grouped by participant, "
        "repeated 20 times",
    )
    folds(ax, 75.5)
    caption(
        ax,
        74.1,
        "Each fold holds about a fifth of the participants, stratified by group. "
        "Reshuffled 20 times; the mean over the 100 test folds is reported with a 95% "
        "interval\ncorrected for the overlap between training sets.",
    )

    title(ax, 65.5, "B. Across PhysioNet's protocols: leave one sub-study out")
    for i, held in enumerate(STUDIES):
        ry = 58.5 - i * 5.6
        for j, st in enumerate(STUDIES):
            x = j * 27.5
            n = c[st]
            if st == held:
                heldout(
                    ax, x, ry, 26, f"test: {STUDY_LABEL[st]}, {n['PD'] + n['Control']}"
                )
            else:
                bar(ax, x, ry, 26, n["PD"], n["Control"], st)
    caption(
        ax,
        46.0,
        "Train on two sub-studies, test on the third; their protocols, recording lengths "
        "and ages differ. The interval is a bootstrap over the held-out participants.",
    )

    title(
        ax,
        39.5,
        "C. Both datasets combined (main analysis): the same cross-validation over all "
        f"{n_pd + n_co + w['PD'] + w['Control']} participants",
    )
    folds(ax, 32.5)
    caption(
        ax,
        31.1,
        "Folds stratified by diagnosis within each dataset; the AUC is reported over all "
        "test participants and within each dataset's.",
    )

    title(
        ax, 24.5, "D. Across cohorts: fitted on PhysioNet, tested once on WearGait-PD"
    )
    bar(ax, 0, 17.5, 48.5, n_pd, n_co, "train: all PhysioNet")
    heldout(
        ax, 51.5, 17.5, 48.5, f"test: WearGait-PD, {w['PD']} PD, {w['Control']} control"
    )
    caption(
        ax,
        16.1,
        "A different research group, three sites and pressure insoles; the same stride "
        "and swing timings. Run once, after the analysis code and its\ninputs were "
        "committed; also within VA Puget Sound (the one site with both groups) and in "
        "pairs matched on sex and age.",
    )

    ax.add_patch(Rectangle((0, 3.5), 2.5, 3, color=COLORS["PD"]))
    ax.text(3.5, 5, "PD", fontsize=7, va="center")
    ax.add_patch(Rectangle((9, 3.5), 2.5, 3, color=COLORS["Control"]))
    ax.text(12.5, 5, "control", fontsize=7, va="center")
    ax.add_patch(Rectangle((21, 3.5), 2.5, 3, fill=False, ec="black", hatch="///"))
    ax.text(24.5, 5, "held out for testing", fontsize=7, va="center")

    fig_dir = Path(args.fig)
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "figure2_evaluation_design.png", dpi=200)
    fig.savefig(
        fig_dir / "figure2_evaluation_design.pdf", metadata={"CreationDate": None}
    )
    print("counts used:", c, "| WearGait-PD", w)


if __name__ == "__main__":
    main()
