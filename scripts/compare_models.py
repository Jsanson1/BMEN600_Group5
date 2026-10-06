"""Compare every model run under the shared evaluation (T-022).

Reads every results/*_folds.csv, *_cv_predictions.csv and *_loso_predictions.csv
written by gaitpdb.evaluation.write_model_outputs (today the logistic regression
and the baselines; the support vector machine and the random forest join as
soon as their scripts write the same files), checks that all models were tested
on identical folds and participants, and writes:

* results/model_comparison.csv, .md and .txt: for each model, the AUC, balanced
  accuracy, sensitivity, specificity and Brier score within protocol (mean over
  the 100 test folds of participant-grouped cross-validation, 95% interval
  corrected for the overlap between training sets), the AUC across protocols
  (each sub-study held out in turn; per study and pooled, participant-bootstrap
  intervals), and the drop from within to across protocols (pooled AUC of the
  out-of-fold predictions, averaged over the 20 repeats, minus pooled AUC of the
  out-of-study predictions; paired bootstrap over participants);
* results/model_comparison_pairs.csv and a section of the .txt: differences in
  AUC between pairs of models, within protocol on identical folds (corrected
  repeated k-fold cross-validation t-test; Holm-adjusted p values over the
  pairs) and across protocols on identical participants (paired bootstrap);
* figures/figure3_model_comparison.png and .pdf.

The pairs are every multivariable model against the reference (by default the
best-known single feature, swing-time asymmetry, so the comparison shows what
combining features adds), every pair of the "gait only" models of different
families, and, within a family, gait features with and without age and sex.

    python scripts/compare_models.py [--results results] [--figures figures]
        [--reference "single: swing_time_asymmetry_pct"]
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["font.family"] = "DejaVu Sans"
matplotlib.rcParams["text.hinting"] = "default"
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb.evaluation import (  # noqa: E402
    METRICS,
    STUDIES,
    bootstrap_auc,
    corrected_ttest,
    paired_bootstrap_auc,
    summarise,
)

NOT_MODELS = ("baseline", "single")  # families that are reference points, not models
FAMILY_ORDER = ["logreg", "svm", "rf"]
FAMILY_LABEL = {"logreg": "Logistic regression", "svm": "SVM", "rf": "Random forest"}
INPUT_LABEL = {
    "gait only": "gait features",
    "gait + covariates": "gait features + age, sex",
    "covariates only": "age and sex only",
}
INPUT_ORDER = ["gait only", "gait + covariates", "covariates only"]
FEATURE_LABEL = {
    "stride_time_mean_s": "Mean stride time",
    "stride_time_cv_pct": "Stride-time variability",
    "swing_time_cv_pct": "Swing-time variability",
    "swing_pct_mean": "Swing fraction of the stride",
    "stride_time_asymmetry_pct": "Stride-time asymmetry",
    "swing_time_asymmetry_pct": "Swing-time asymmetry",
}
STUDY_MARKER = {"Ga": "o", "Ju": "s", "Si": "^"}
STUDY_LABEL = {"Ga": "Ga held out", "Ju": "Ju held out", "Si": "Si held out"}
INK, MUTED, GRID = "#1f1f1f", "#6e6e6e", "#d9d9d9"


def family(model: str) -> str:
    return model.split(":", 1)[0].strip()


def inputs(model: str) -> str:
    return model.split(":", 1)[1].strip() if ":" in model else ""


def label(model: str) -> str:
    fam, inp = family(model), inputs(model)
    if fam == "single":
        return f"{FEATURE_LABEL.get(inp, inp)} alone"
    if fam == "baseline" and inp == "chance":
        return "Chance (share of PD in training)"
    return f"{FAMILY_LABEL.get(fam, fam)}: {INPUT_LABEL.get(inp, inp)}"


def read_all(results: Path, kind: str) -> pd.DataFrame:
    paths = sorted(results.glob(f"*_{kind}.csv"))
    if not paths:
        raise SystemExit(
            f"no results/*_{kind}.csv found: run scripts/run_logreg.py and scripts/run_baselines.py first"
        )
    frames = [pd.read_csv(p) for p in paths]
    seen: dict[str, Path] = {}
    for p, f in zip(paths, frames):
        for m in f["model"].unique():
            if m in seen:
                raise SystemExit(f"model {m!r} appears in both {seen[m]} and {p}")
            seen[m] = p
    return pd.concat(frames, ignore_index=True)


def check_alignment(folds: pd.DataFrame, cvp: pd.DataFrame, loso: pd.DataFrame):
    """Every model must have been tested on the same folds and the same participants."""
    ids = folds.pivot(index=["repeat", "fold"], columns="model", values="test_ids")
    if ids.isna().any().any():
        missing = ids.columns[ids.isna().any()].tolist()
        raise SystemExit(f"these models lack some cross-validation folds: {missing}")
    differing = ids.nunique(axis=1) > 1
    if differing.any():
        raise SystemExit(
            f"{int(differing.sum())} folds have different test participants across models; "
            "every model script must use gaitpdb.evaluation with the default splits"
        )
    for name, table in (("cv_predictions", cvp), ("loso_predictions", loso)):
        reference = None
        for model, t in table.groupby("model", sort=False):
            pairs = list(zip(t["participant"], t["y"]))
            if reference is None:
                reference = pairs
            elif sorted(pairs) != sorted(reference):
                raise SystemExit(
                    f"{name}: {model} was scored on different participants"
                )
    models = list(dict.fromkeys(folds["model"]))
    for model in models:
        for name, table in (("cv_predictions", cvp), ("loso_predictions", loso)):
            if model not in set(table["model"]):
                raise SystemExit(f"{model} has folds but no {name}")
    return models


def wide(table: pd.DataFrame, order: list[str]) -> pd.DataFrame:
    """Participants (in the order of the first model's file) by model, probability of PD."""
    w = table.pivot(index="participant", columns="model", values="p")
    first = table[table["model"] == table["model"].iloc[0]]
    w = w.loc[first["participant"].to_numpy()]
    meta = first.set_index("participant")[["study", "y"]]
    return w[order].join(meta)


def order_table(table: pd.DataFrame) -> pd.DataFrame:
    """Models first (by family, then inputs), then single features from the best
    within-protocol AUC down, then chance."""

    def key(m: str, auc: float):
        fam, inp = family(m), inputs(m)
        if fam not in NOT_MODELS:
            f = FAMILY_ORDER.index(fam) if fam in FAMILY_ORDER else len(FAMILY_ORDER)
            i = INPUT_ORDER.index(inp) if inp in INPUT_ORDER else len(INPUT_ORDER)
            return (0, f, fam, i, inp, 0.0)
        if fam == "single":
            return (1, 0, "", 0, "", -auc)
        return (2, 0, "", 0, inp, 0.0)

    keys = [key(m, a) for m, a in zip(table["model"], table["auc_within"])]
    order = sorted(range(len(table)), key=lambda i: keys[i])
    return table.iloc[order].reset_index(drop=True)


def per_model(models, folds, cvw, losow) -> pd.DataFrame:
    rows = []
    y, study = losow["y"].to_numpy(), losow["study"].to_numpy()
    for m in models:
        s = summarise(folds[folds["model"] == m])
        row = {"model": m, "label": label(m)}
        for metric in METRICS:
            row[f"{metric}_within"] = s.loc[metric, "mean"]
            row[f"{metric}_within_low"] = s.loc[metric, "ci_low"]
            row[f"{metric}_within_high"] = s.loc[metric, "ci_high"]
        row["auc_within_repeat_low"] = s.loc["auc", "repeat_low"]
        row["auc_within_repeat_high"] = s.loc["auc", "repeat_high"]
        point, lo, hi = bootstrap_auc(y, losow[m].to_numpy())
        row.update(auc_across=point, auc_across_low=lo, auc_across_high=hi)
        for st in STUDIES:
            keep = study == st
            point, lo, hi = bootstrap_auc(y[keep], losow[m].to_numpy()[keep])
            row.update({f"auc_{st}": point, f"auc_{st}_low": lo, f"auc_{st}_high": hi})
        d, lo, hi = paired_bootstrap_auc(y, cvw[m].to_numpy(), losow[m].to_numpy())
        row.update(
            auc_within_pooled=roc_auc_score(y, cvw[m].to_numpy()),
            drop=d,
            drop_low=lo,
            drop_high=hi,
        )
        rows.append(row)
    return pd.DataFrame(rows)


def comparison_pairs(models: list[str], reference: str) -> list[tuple[str, str]]:
    pairs = []
    proper = [m for m in models if family(m) not in NOT_MODELS]
    if reference in models:
        pairs += [(m, reference) for m in proper]
    gait_only = [m for m in proper if inputs(m) == "gait only"]
    pairs += list(itertools.combinations(gait_only, 2))
    for fam in dict.fromkeys(family(m) for m in proper):
        a, b = f"{fam}: gait + covariates", f"{fam}: gait only"
        if a in models and b in models:
            pairs.append((a, b))
    return list(dict.fromkeys(pairs))


def holm(p: np.ndarray) -> np.ndarray:
    """Holm step-down adjustment of a set of p values."""
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    adjusted = np.empty_like(p)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(p) - rank) * p[i]))
        adjusted[i] = running
    return adjusted


def pairwise(pairs, folds, losow) -> pd.DataFrame:
    y = losow["y"].to_numpy()
    auc = folds.pivot(index=["repeat", "fold"], columns="model", values="auc")
    n_train = folds["n_train"].mean()
    n_test = folds["n_test"].mean()
    rows = []
    for a, b in pairs:
        t = corrected_ttest(auc[a] - auc[b], n_train, n_test)
        d, lo, hi = paired_bootstrap_auc(y, losow[a].to_numpy(), losow[b].to_numpy())
        rows.append(
            {
                "model_a": a,
                "model_b": b,
                "within_difference": t["mean_difference"],
                "within_low": t["ci_low"],
                "within_high": t["ci_high"],
                "within_t": t["t"],
                "within_df": t["df"],
                "within_p": t["p"],
                "across_difference": d,
                "across_low": lo,
                "across_high": hi,
            }
        )
    out = pd.DataFrame(rows)
    if len(out):
        out["within_p_holm"] = holm(out["within_p"].to_numpy())
    return out


def ci(point: float, lo: float, hi: float, digits: int = 2) -> str:
    return f"{point:.{digits}f} ({lo:.{digits}f} to {hi:.{digits}f})"


def p_text(p: float) -> str:
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def write_text(table, pairs_table, n, n_pd, reference, path: Path) -> str:
    lines = [
        f"Model comparison on the usual walk: {n} participants ({n_pd} PD, {n - n_pd} controls), "
        "one recording each, identical splits for every model (checked fold by fold).",
        "Within protocol: 5-fold participant-grouped cross-validation repeated 20 times; mean "
        "over the 100 test folds, 95% interval corrected for the overlap between training sets "
        "(Nadeau and Bengio 2003). Across protocols: each sub-study held out in turn, the model "
        "trained on the other two; AUC per held-out study and for all out-of-study predictions "
        "pooled, 95% participant-bootstrap intervals (2000 resamples). Drop: pooled AUC of the "
        "out-of-fold predictions (averaged over the 20 repeats) minus pooled out-of-study AUC, "
        "paired bootstrap.",
        "",
        "AUC by model:",
    ]
    for r in table.itertuples():
        lines.append(f"  {r.label}")
        lines.append(
            f"      within protocol {ci(r.auc_within, r.auc_within_low, r.auc_within_high)}; "
            f"across protocols {ci(r.auc_across, r.auc_across_low, r.auc_across_high)} "
            f"(Ga {r.auc_Ga:.2f}, Ju {r.auc_Ju:.2f}, Si {r.auc_Si:.2f}); "
            f"drop {ci(r.drop, r.drop_low, r.drop_high)}"
        )
    chance = table[table["model"] == "baseline: chance"]
    if len(chance):
        c = chance.iloc[0]
        lines.append(
            "  Pooled AUCs mix predictions from different fitted models (one per fold or per "
            "held-out study). The chance model, whose AUC is exactly 0.5 within every fold and "
            "every study, shows how far pooling alone can move them: "
            f"{c['auc_within_pooled']:.2f} for the pooled out-of-fold and {c['auc_across']:.2f} "
            "for the pooled out-of-study predictions."
        )
    lines += [
        "",
        "Threshold metrics within protocol (probability 0.5), and Brier score:",
    ]
    for r in table.itertuples():
        lines.append(
            f"  {r.label}: balanced accuracy {ci(r.balanced_accuracy_within, r.balanced_accuracy_within_low, r.balanced_accuracy_within_high)}, "
            f"sensitivity {r.sensitivity_within:.2f}, specificity {r.specificity_within:.2f}, "
            f"Brier {r.brier_within:.3f}"
        )
    lines += [
        "",
        "Paired differences in AUC (first minus second). Within protocol: corrected repeated "
        "k-fold cross-validation t-test on the 100 paired folds (Bouckaert and Frank 2004), "
        "p values Holm-adjusted over the pairs listed. Across protocols: paired bootstrap of "
        "the pooled out-of-study AUC.",
    ]
    if not len(pairs_table):
        lines.append(f"  none (reference {reference!r} or the models are missing)")
    for r in pairs_table.itertuples():
        lines.append(f"  {label(r.model_a)} vs {label(r.model_b)}")
        lines.append(
            f"      within {r.within_difference:+.3f} ({r.within_low:+.3f} to {r.within_high:+.3f}), "
            f"t({r.within_df}) = {r.within_t:.2f}, p = {p_text(r.within_p)}, Holm p = {p_text(r.within_p_holm)}; "
            f"across {r.across_difference:+.3f} ({r.across_low:+.3f} to {r.across_high:+.3f})"
        )
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


def write_markdown(table: pd.DataFrame, path: Path) -> None:
    md = pd.DataFrame(
        {
            "Model": table["label"],
            "AUC within protocol": [
                ci(a, b, c)
                for a, b, c in zip(
                    table["auc_within"],
                    table["auc_within_low"],
                    table["auc_within_high"],
                )
            ],
            "AUC across protocols (pooled)": [
                ci(a, b, c)
                for a, b, c in zip(
                    table["auc_across"],
                    table["auc_across_low"],
                    table["auc_across_high"],
                )
            ],
            "Ga": table["auc_Ga"].map("{:.2f}".format),
            "Ju": table["auc_Ju"].map("{:.2f}".format),
            "Si": table["auc_Si"].map("{:.2f}".format),
            "Balanced accuracy": table["balanced_accuracy_within"].map("{:.2f}".format),
            "Brier": table["brier_within"].map("{:.3f}".format),
        }
    )
    path.write_text(md.to_markdown(index=False) + "\n", encoding="utf-8")


def figure(table: pd.DataFrame, path_png: Path, path_pdf: Path) -> None:
    n = len(table)
    ypos = np.arange(n)[::-1].astype(float)
    groups = [0 if family(m) not in NOT_MODELS else 1 for m in table["model"]]
    top_in, bottom_in, height = 0.55, 0.72, 0.30 * n + 1.3
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(7.2, height), sharey=True, gridspec_kw={"wspace": 0.10}
    )
    for ax in (ax_a, ax_b):
        ax.axvline(0.5, color=MUTED, lw=0.8, ls=(0, (3, 3)), zorder=1)
        ax.set_xlim(0.3, 1.0)
        ax.set_xticks([0.4, 0.6, 0.8, 1.0])
        ax.set_xticks([0.3, 0.5, 0.7, 0.9], minor=True)
        ax.tick_params(labelsize=7, length=2.5, color=MUTED)
        ax.tick_params(which="minor", length=1.5, color=MUTED)
        ax.grid(axis="x", which="both", color=GRID, lw=0.5, zorder=0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(MUTED)
            ax.spines[side].set_linewidth(0.6)
        ax.set_xlabel("AUC", fontsize=7.5, color=INK)
        for i in range(1, n):
            if groups[i] != groups[i - 1]:
                ax.axhline((ypos[i] + ypos[i - 1]) / 2, color=GRID, lw=0.8, zorder=1)
    ax_a.hlines(
        ypos, table["auc_within_low"], table["auc_within_high"], color=INK, lw=1.2
    )
    ax_a.plot(table["auc_within"], ypos, "o", color=INK, ms=4.5, zorder=3)
    ax_a.set_yticks(ypos)
    ax_a.set_yticklabels(table["label"], fontsize=7, color=INK)
    ax_a.set_title(
        "A  Within protocol: participant-grouped\n5-fold cross-validation, 20 repeats",
        fontsize=7.5,
        loc="left",
        color=INK,
    )
    ax_b.hlines(
        ypos, table["auc_across_low"], table["auc_across_high"], color=INK, lw=1.2
    )
    ax_b.plot(
        table["auc_across"],
        ypos,
        "o",
        color=INK,
        ms=4.5,
        zorder=3,
        label="all held-out predictions pooled",
    )
    for offset, st in zip((0.22, 0.0, -0.22), STUDIES):
        ax_b.plot(
            table[f"auc_{st}"],
            ypos + offset,
            STUDY_MARKER[st],
            ms=3.6,
            mfc="white",
            mec=MUTED,
            mew=0.9,
            ls="none",
            zorder=2,
            label=STUDY_LABEL[st],
        )
    ax_b.set_title(
        "B  Across protocols: train on two\nsub-studies, test on the third",
        fontsize=7.5,
        loc="left",
        color=INK,
    )
    ax_b.tick_params(axis="y", length=0)
    fig.subplots_adjust(
        left=0.33, right=0.985, top=1 - top_in / height, bottom=bottom_in / height
    )
    handles, labels = ax_b.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.66, 0.0),
        ncol=4,
        fontsize=6.5,
        frameon=False,
        handletextpad=0.3,
        columnspacing=1.2,
    )
    fig.savefig(path_png, dpi=200)
    fig.savefig(path_pdf, metadata={"CreationDate": None})
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--figures", default="figures")
    ap.add_argument("--reference", default="single: swing_time_asymmetry_pct")
    args = ap.parse_args()
    results, figures = Path(args.results), Path(args.figures)
    figures.mkdir(parents=True, exist_ok=True)

    folds = read_all(results, "folds")
    cvp = read_all(results, "cv_predictions")
    loso = read_all(results, "loso_predictions")
    models = check_alignment(folds, cvp, loso)
    losow = wide(loso, models)
    cvw = wide(cvp, models).loc[losow.index]
    if not (cvw["y"] == losow["y"]).all():
        raise SystemExit("the two prediction files disagree on participants' groups")

    table = order_table(per_model(models, folds, cvw, losow))
    models = table["model"].tolist()
    table.to_csv(results / "model_comparison.csv", index=False)
    write_markdown(table, results / "model_comparison.md")
    pairs_table = pairwise(comparison_pairs(models, args.reference), folds, losow)
    pairs_table.to_csv(results / "model_comparison_pairs.csv", index=False)
    n, n_pd = len(losow), int(losow["y"].sum())
    text = write_text(
        table, pairs_table, n, n_pd, args.reference, results / "model_comparison.txt"
    )
    figure(
        table,
        figures / "figure3_model_comparison.png",
        figures / "figure3_model_comparison.pdf",
    )
    print(text)


if __name__ == "__main__":
    main()
