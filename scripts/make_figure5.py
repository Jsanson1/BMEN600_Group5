"""Figure 5: how well the gait-feature models separate PD from controls as the
test moves further from the data they were fitted on.

One row per evaluation, from unseen participants to an unseen cohort: within
gaitpdb's protocols (participant-grouped cross-validation) and across them
(each sub-study held out), both datasets combined (DECISIONS.md D-007's main
analysis, overall and within each dataset's participants), and fitted on
gaitpdb and tested once on WearGait-PD (all participants, the one site with
both groups, and the pairs matched on sex and age). Each model fitted on the
five gait features (D-013) is drawn with its AUC and 95% interval; swing-time
asymmetry alone, the reference of results/model_comparison.txt, is drawn where
it was evaluated.

Reads results/model_comparison.csv (scripts/compare_models.py),
results/crosscohort_results.csv (scripts/run_cross_cohort.py) and the two feature
tables (for the participant counts); writes figures/figure5_generalisation.png
and .pdf, and results/figure5_values.csv with every value drawn.

    python scripts/make_figure5.py [--results results] [--figures figures]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["text.hinting"] = "default"
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

FAMILIES = ("logreg", "svm", "rf")  # drawn in this order, when present
FAMILY_LABEL = {
    "logreg": "Logistic regression",
    "svm": "Support vector machine",
    "rf": "Random forest",
}
MARKER = {"logreg": "o", "svm": "^", "rf": "s"}
REFERENCE = "single: swing_time_asymmetry_pct"
REFERENCE_LABEL = "Swing-time asymmetry alone"
INK, MUTED, GRID = "#1f1f1f", "#6e6e6e", "#d9d9d9"

LEVELS = [
    ("Unseen participants", "within gaitpdb's protocols"),
    ("Unseen protocol", "a gaitpdb sub-study held out"),
    ("Both datasets combined", "the plan's main analysis"),
    ("Unseen cohort", "fitted on gaitpdb, tested on WearGait-PD"),
]
"""Section title and subtitle of each level, top to bottom."""

CROSS_ROWS = [  # (level, row label template, analysis in crosscohort_results.csv)
    (2, "All {n_all}", "pooled"),
    (2, "gaitpdb's {n_g}", "pooled, gaitpdb test participants"),
    (2, "WearGait-PD's {n_w}", "pooled, WearGait-PD test participants"),
    (3, "All {n}", "cross-cohort"),
    (3, "VA Puget Sound only, {n}", "cross-cohort, VA Puget Sound only"),
    (3, "Age-matched pairs, {n}", "cross-cohort, age-matched"),
]


def values(results: Path) -> pd.DataFrame:
    """Every value the figure draws: one row per evaluation and model, with the
    level, the row label, the number of test participants, the AUC and its 95%
    interval."""
    comparison = pd.read_csv(results / "model_comparison.csv").set_index("model")
    cross = pd.read_csv(results / "crosscohort_results.csv")
    n_g = len(pd.read_csv(results / "features_gaitpdb.csv"))
    n_w = len(pd.read_csv(results / "features_weargait.csv"))
    families = [f for f in FAMILIES if f"{f}: gait only" in comparison.index]
    rows = []
    for name in [*(f"{f}: gait only" for f in families), REFERENCE]:
        if name not in comparison.index:
            continue
        r = comparison.loc[name]
        model = name.split(":", 1)[0] if name != REFERENCE else "reference"
        for level, label, col in (
            (0, f"All {n_g}", "auc_within"),
            (1, f"All {n_g}", "auc_across"),
        ):
            rows.append(
                {
                    "level": level,
                    "row": label,
                    "model": model,
                    "n": n_g,
                    "auc": r[col],
                    "auc_low": r[f"{col}_low"],
                    "auc_high": r[f"{col}_high"],
                }
            )
    gait = cross[cross["inputs"] == "gait"]
    for level, template, analysis in CROSS_ROWS:
        for fam in families:
            hit = gait[(gait["analysis"] == analysis) & (gait["model"] == fam)]
            if len(hit) != 1:
                raise SystemExit(
                    f"expected one '{analysis}' row for {fam} with gait inputs in "
                    f"{results / 'crosscohort_results.csv'}, found {len(hit)}"
                )
            r = hit.iloc[0]
            n = n_g + n_w if level == 2 and analysis == "pooled" else r["n"]
            if analysis.endswith("gaitpdb test participants"):
                n = n_g
            elif analysis.endswith("WearGait-PD test participants"):
                n = n_w
            rows.append(
                {
                    "level": level,
                    "row": template.format(n=int(n), n_all=n_g + n_w, n_g=n_g, n_w=n_w),
                    "model": fam,
                    "n": int(n),
                    "auc": r["auc"],
                    "auc_low": r["auc_low"],
                    "auc_high": r["auc_high"],
                }
            )
    return pd.DataFrame(rows)


def layout(v: pd.DataFrame) -> tuple[dict[tuple[int, str], float], dict[int, float]]:
    """y position of each (level, row) and of each level's title, top to bottom."""
    y, rows, titles = 0.0, {}, {}
    for level in range(len(LEVELS)):
        titles[level] = y
        y -= 1.0
        for row in dict.fromkeys(v.loc[v["level"] == level, "row"]):
            rows[(level, row)] = y
            y -= 1.0
        y -= 0.35
    return rows, titles


def figure(v: pd.DataFrame, png: Path, pdf: Path) -> None:
    rows, titles = layout(v)
    models = [m for m in (*FAMILIES, "reference") if m in set(v["model"])]
    k = len(models)
    offsets = {m: 0.26 * (k - 1) / 2 - 0.26 * i for i, m in enumerate(models)}
    height = 0.215 * (len(rows) + len(titles) + 0.35 * len(titles)) + 0.8
    fig, ax = plt.subplots(figsize=(3.5, height))
    ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=1)
    for m in models:
        d = v[v["model"] == m]
        ys = [rows[(lv, r)] + offsets[m] for lv, r in zip(d["level"], d["row"])]
        ref = m == "reference"
        ax.hlines(ys, d["auc_low"], d["auc_high"], color=MUTED if ref else INK, lw=1.0)
        ax.plot(
            d["auc"],
            ys,
            "D" if ref else MARKER[m],
            ms=3.4 if ref else 3.8,
            mfc="white" if ref else INK,
            mec=MUTED if ref else INK,
            mew=0.9,
            ls="none",
            zorder=3,
            label=REFERENCE_LABEL if ref else FAMILY_LABEL[m],
        )
    for level, (title, subtitle) in enumerate(LEVELS):
        ax.text(
            -0.03,
            titles[level],
            title,
            transform=ax.get_yaxis_transform(),
            ha="right",
            va="center",
            fontsize=6.6,
            weight="bold",
            color=INK,
        )
        ax.text(
            0.32,
            titles[level],
            subtitle,
            ha="left",
            va="center",
            fontsize=6.2,
            style="italic",
            color=MUTED,
        )
        if level:
            ax.axhline(titles[level] + 0.68, color=GRID, lw=0.8, zorder=1)
    ax.set_yticks(list(rows.values()))
    ax.set_yticklabels([r for _, r in rows], fontsize=6.5, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0.3, 1.0)
    ax.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    ax.tick_params(axis="x", labelsize=6.5, length=2.5, color=MUTED)
    ax.grid(axis="x", color=GRID, lw=0.5, zorder=0)
    ax.set_ylim(min(rows.values()) - 0.7, max(titles.values()) + 0.6)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.spines["bottom"].set_linewidth(0.6)
    ax.set_xlabel("AUC (95% interval); dashed line: chance", fontsize=6.8, color=INK)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=len(handles),
        fontsize=6.2,
        frameon=False,
        handletextpad=0.25,
        columnspacing=0.6,
    )
    fig.subplots_adjust(
        left=0.43, right=0.97, top=1 - 0.08 / height, bottom=0.62 / height
    )
    fig.savefig(png, dpi=300)
    fig.savefig(pdf, metadata={"CreationDate": None})
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--results", default="results")
    ap.add_argument("--figures", default="figures")
    args = ap.parse_args()
    results, figures = Path(args.results), Path(args.figures)
    figures.mkdir(parents=True, exist_ok=True)
    v = values(results)
    v.to_csv(results / "figure5_values.csv", index=False, float_format="%.6f")
    figure(
        v,
        figures / "figure5_generalisation.png",
        figures / "figure5_generalisation.pdf",
    )
    shown = v.assign(auc=v["auc"].round(3))[["level", "row", "model", "n", "auc"]]
    print(shown.to_string(index=False))


if __name__ == "__main__":
    main()
