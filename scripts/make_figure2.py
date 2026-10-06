"""Figure 2: the three levels of evaluation, drawn from the actual participant counts.

A schematic for the methods section: how participants are split within a
protocol (repeated participant-grouped cross-validation), across protocols
(leave-one-study-out) and across cohorts (external test). The counts come from
demographics.txt and the record files, so the figure cannot drift from the data.

    python scripts/make_figure2.py [--data data/raw/gaitpdb]
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
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import build_manifest, find_data_dir  # noqa: E402
from gaitpdb.evaluation import MODEL_FEATURES  # noqa: E402

COLORS = {"Control": "#3b6ea5", "PD": "#c8552d"}
STUDY_LABEL = {
    "Ga": "Ga (dual task)",
    "Ju": "Ju (cueing)",
    "Si": "Si (treadmill study)",
}
WEARGAIT = {"PD": 100, "Control": 85}  # sources.md S9


def counts(data_dir: Path) -> dict[str, dict[str, int]]:
    m = build_manifest(data_dir)
    usual = m[m["walk"] == 1]
    out = {}
    for study in ("Ga", "Ju", "Si"):
        sub = usual[usual["study"] == study]
        out[study] = {
            g: int(sub[sub["group"] == g]["participant"].nunique())
            for g in ("PD", "Control")
        }
    return out


def bar(ax, x, y, w, h, n_pd, n_co, label, lw=0.8):
    """A horizontal bar split into PD (left) and control (right) parts, labelled."""
    total = n_pd + n_co
    ax.add_patch(Rectangle((x, y), w * n_pd / total, h, color=COLORS["PD"], lw=0))
    ax.add_patch(
        Rectangle(
            (x + w * n_pd / total, y),
            w * n_co / total,
            h,
            color=COLORS["Control"],
            lw=0,
        )
    )
    ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=lw, ec="black"))
    ax.text(
        x + w / 2,
        y + h / 2,
        f"{label}: {n_pd} PD, {n_co} control",
        ha="center",
        va="center",
        fontsize=7,
        color="white",
    )


def heldout(ax, x, y, w, h, text):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=1.2, ec="black", hatch="///"))
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=7,
        bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"),
    )


def caption(ax, y, text):
    ax.text(0, y, text, fontsize=6.5, va="top", color="#222222")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    ap.add_argument("--fig", default="figures")
    args = ap.parse_args()
    c = counts(find_data_dir(args.data))
    n_pd = sum(v["PD"] for v in c.values())
    n_co = sum(v["Control"] for v in c.values())

    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Row 0: the data and the model
    ax.text(
        0, 98, "Participants with a usual walk", fontsize=8, weight="bold", va="center"
    )
    bar(ax, 0, 90.5, 58, 5.5, n_pd, n_co, "PhysioNet, three sub-studies")
    ax.add_patch(
        FancyBboxPatch(
            (63, 88.5),
            37,
            9.5,
            boxstyle="round,pad=0.4",
            fc="#f2f2f2",
            ec="black",
            lw=0.8,
        )
    )
    ax.text(
        81.5,
        93.25,
        f"{len(MODEL_FEATURES)} timing features per participant\n(+ age and sex as covariates)\n"
        "logistic regression, SVM, random forest;\ntuning inside the training fold only",
        ha="center",
        va="center",
        fontsize=6.5,
    )

    # Row A: repeated grouped CV
    ax.text(
        0,
        81,
        "A. Within protocol: 5-fold cross-validation grouped by participant, repeated 20 times",
        fontsize=8,
        weight="bold",
        va="center",
    )
    y = 72
    for k in range(5):
        x = k * 16.5
        if k == 4:
            heldout(ax, x, y, 15.5, 5.5, "test fold")
        else:
            ax.add_patch(Rectangle((x, y), 15.5, 5.5, fc="#dddddd", ec="black", lw=0.8))
            ax.text(x + 7.75, y + 2.75, "train", ha="center", va="center", fontsize=7)
    caption(
        ax,
        70,
        "Each fold holds about a fifth of the participants, stratified by group; a participant's "
        "recordings are never split between train and test. Reshuffled 20 times;\n"
        "the mean AUC over repeats is reported with its 2.5th to 97.5th percentile.",
    )

    # Row B: leave-one-study-out
    ax.text(
        0,
        59,
        "B. Across protocols: leave one sub-study out",
        fontsize=8,
        weight="bold",
        va="center",
    )
    studies = ("Ga", "Ju", "Si")
    for i, held in enumerate(studies):
        ry = 51 - i * 6.5
        for j, st in enumerate(studies):
            x = j * 27.5
            n = c[st]
            if st == held:
                heldout(
                    ax,
                    x,
                    ry,
                    26,
                    5.5,
                    f"test: {STUDY_LABEL[st]}, {n['PD'] + n['Control']}",
                )
            else:
                bar(ax, x, ry, 26, 5.5, n["PD"], n["Control"], st)
    caption(
        ax,
        36,
        "Train on two sub-studies, test on the third. The protocols, recording lengths and ages "
        "differ between sub-studies, so this is the primary comparison;\n"
        "the interval is a bootstrap over the held-out participants.",
    )

    # Row C: external test
    ax.text(
        0,
        25,
        "C. Across cohorts: external test",
        fontsize=8,
        weight="bold",
        va="center",
    )
    bar(ax, 0, 16.5, 40, 5.5, n_pd, n_co, "train: all PhysioNet")
    heldout(
        ax,
        43,
        16.5,
        37.5,
        5.5,
        f"test: WearGait-PD, {WEARGAIT['PD']} PD, {WEARGAIT['Control']} control",
    )
    caption(
        ax,
        14.5,
        "A different research group and hardware; the same stride and swing timings from its "
        "pressure insoles or walkway. Run once, after the models are frozen.",
    )

    # legend
    ax.add_patch(Rectangle((0, 1), 2.5, 3, color=COLORS["PD"]))
    ax.text(3.5, 2.5, "PD", fontsize=7, va="center")
    ax.add_patch(Rectangle((9, 1), 2.5, 3, color=COLORS["Control"]))
    ax.text(12.5, 2.5, "control", fontsize=7, va="center")
    ax.add_patch(Rectangle((21, 1), 2.5, 3, fill=False, ec="black", hatch="///"))
    ax.text(24.5, 2.5, "held out for testing", fontsize=7, va="center")

    fig_dir = Path(args.fig)
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(fig_dir / "figure2_evaluation_design.png", dpi=200)
    fig.savefig(fig_dir / "figure2_evaluation_design.pdf")
    print("counts used:", c, "| totals", n_pd, "PD,", n_co, "control")


if __name__ == "__main__":
    main()
