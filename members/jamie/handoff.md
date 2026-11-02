# Handoff: Jamie Sanson (`jamie`)

<!--
CURRENT STATE ONLY. Edited only by Jamie's agents, and only on main (CLAUDE.md sections 3 and 7).
History goes in log.md, next to this file.

One section per task Jamie is working on. At every stopping point, rewrite the section
for your task. Delete it only once the task is done (merged). Do not touch other sections:
another of Jamie's sessions may own them. Keep each section to about 15 lines.
When there are no active tasks, the file ends with the line: _No active tasks._

Section format (keep the bold labels so the others can scan for them; Calgary time):

## T-007 · Short task title
_Updated 2026-10-02 15:40 by Claude Code for Jamie · branch `jamie/T-007-short-slug` at `abc1234`_

- **Now:** where the work stands, in one to three lines.
- **Validated:** what was actually run or checked. **Not verified:** what is still assumed.
- **Next:** the exact next action, specific enough for someone to start cold (for a finished task: the pull request link or who opens it, who reviews, then merge, mark done, delete the branch).
- **Blocked / needs a decision:** none, or what and from whom.
- **For teammates:** none, or a note such as "@jamie: the loader now returns one row per stride".
- **Not pushed:** nothing. (Anything listed here exists on one machine only.)
-->

## T-018 · Feature extraction (code done, pull request #17; feature tables wait for the input decision and for T-017 with D-012)
_Updated 2026-11-02 16:50 by Claude (cloud session) for Jamie · branch `jamie/T-018-feature-extraction` at `c6f7e8b`; pull request #17 open_

- **Now:** handed over by Yassien in person on 2 November. `gaitpdb.features.stride_features` and `participant_features` compute each participant's features from their clean strides (same definitions as the midterm, plus the robust MAD variability); `scripts/make_features.py` writes `results/features_{gaitpdb,weargait}.csv`, `feature_dictionary.md` and `features_summary.txt`; `scripts/check_features.py` compares the datasets without WearGait-PD's diagnosis labels (`results/feature_checks.txt`) and draws Figure 4 (the feature shift; stride time by position in a straight bout); a preview from the exploratory tables went to Jamie for Friday's discussion.
- **Validated:** 16 tests (15 mutations, all caught); 48 tests in all; `results/features_usual_walk.csv` unchanged by the refactor. Exploratory runs on T-017's tables at `2fe20b2` (20 N, and D-012 patched in on our side): WearGait-PD's CVs are about twice gaitpdb's, 62% of its clean strides open or close a straight bout (first stride 6.7% longer), dropping one stride per bout end brings its stride CV to 2.83% but leaves 91 of 169 below N = 10; stride-time asymmetry is 11 times higher in WearGait-PD and has AUC 0.52 in gaitpdb. **Not verified:** anything from T-017 with D-012 in its own code.
- **Next:** (1) group decision on the model inputs (proposal sent 2 November: drop stride-time asymmetry; add a model without the variability features and a within-dataset standardisation check; MAD as an extra check); once Jamie relays it, record D-013 and change `evaluation.MODEL_FEATURES` in this pull request. (2) After T-017 is on `main` with D-012: merge `main`, run `make_clean_strides.py`, `make_features.py`, `check_features.py`, commit the tables. (3) Review by Yassien, then merge.
- **Blocked / needs a decision:** the input decision (group); T-017 applying D-012 and merging (Anna).
- **For teammates:** @yassien: a first look at #17 please (feature definitions and the dictionary). @anna: `make_features.py` reads your clean-stride tables as they are; D-012 needs `_foot_tables` to use 5% of the recording's force level (the mean over the two feet of each foot's 95th percentile of total force, samples without data ignored) in place of `DEFAULT_THRESHOLD_N`.
- **Not pushed:** nothing.

## T-019 · Random forest (done on the midterm features; pull request #18; rerun on the final features with T-022)
_Updated 2026-11-02 16:35 by Claude (cloud session) for Jamie · branch `jamie/T-019-random-forest` at `5db11b7`; pull request #18 open_

- **Now:** `gaitpdb.forest.OOBTunedForest` (300 trees; depth and inputs per split chosen by out-of-bag log-loss; Breiman 2001, Probst and Boulesteix 2018, both checked) and `scripts/run_random_forest.py`. On `results/features_usual_walk.csv` (the logistic regression's six features): gait only AUC 0.785 (0.704 to 0.865) within protocol, 0.766 across protocols; with age and sex 0.780 and 0.770. Swing fraction and swing-time asymmetry carry it (AUC drop 0.125 and 0.101 when shuffled); variability adds nothing measurable; stride-time asymmetry nothing. `compare_models.py` and Figure 3 include it; the ten existing models' numbers are unchanged (only Holm p values move, 4 to 8 pairs).
- **Validated:** 6 tests, 4 mutations caught; 38 tests pass; 300 and 1000 trees give the same out-of-bag log-loss (0.566). **Not verified:** the final features (not yet built).
- **Next:** review by Yassien; merge. #16 and #18 both regenerate `results/model_comparison.*` and Figure 3: whichever merges second needs `main` merged in and `compare_models.py` rerun (done once on `jamie/T-022-cross-cohort-run`, `6936bde`). The final run happens in T-022.
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @anna (T-020): the SVM joins the comparison and the cross-dataset script the same way: a `scripts/run_svm.py` with `make_factory(columns)` and outputs written by `evaluation.write_model_outputs(..., "svm")`.
- **Not pushed:** nothing.

## T-022 · Model comparison and cross-dataset analyses (module in #16; run script ready on its own branch, waits for the input decision)
_Updated 2026-11-02 16:35 by Claude (cloud session) for Jamie · branches `jamie/T-022-model-comparison` at `c203bb7` (pull request #16 open) and `jamie/T-022-cross-cohort-run` at `6936bde` (merges #16, #17 and #18)_

- **Now:** `src/gaitpdb/crosscohort.py` and the screening metrics in `compare_models.py` (#16). `scripts/run_cross_cohort.py` (`bd4c61f`): for every model present and four input sets, the cross-cohort test (AUC, sensitivity at 90% specificity on WearGait-PD's ROC and with gaitpdb's threshold carried over, PPV and NPV at 1%), its VA Puget Sound and age-matched subsets; for the main inputs also pooled cross-validation, within-dataset standardisation, dataset of origin and the stride-matched reference. Committed before any run on WearGait-PD's labels.
- **Validated:** 6 tests for the run script (6 mutations caught); 72 tests pass on the run branch. Dry run with WearGait-PD's labels permuted (`--shuffle-labels`, exploratory tables): runs end to end, 3 min 55 s for the logistic regression. Label-free from it: dataset of origin AUC 0.97 with the six features (0.94 without stride-time asymmetry, 0.85 without the variability features); stride-matched reference within gaitpdb 0.781 to 0.757 (13 runs per foot). **Not verified:** any result with the real labels (deliberately not run).
- **Next:** after the input decision (D-013), T-017 with D-012, and merges of #16 to #18: merge `main` into the run branch, run `make_clean_strides.py`, `make_features.py`, the three model scripts, `compare_models.py` and `run_cross_cohort.py` (the forest takes about 45 min there), open its pull request; then the comparison tables and figures for the paper.
- **Blocked / needs a decision:** the input decision; T-017 (Anna); the SVM (T-020, Anna).
- **For teammates:** none beyond the T-019 note.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (threshold decided, D-012; pull request #15 waits for a review)
_Updated 2026-11-02 16:35 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `a0402fc`; pull request #15 open (checks green)_

- **Now:** data downloaded and checked; walkway threshold check and site-by-diagnosis table done. Threshold decided: D-012, 5% of each recording's force level in both datasets, 20 N kept as a sensitivity analysis (proposed by Jamie, agreed by Anna on 2 November; the procedure the plan set out).
- **Validated:** as before (10 walkway tests; the check's numbers are quoted in D-012 from `results/weargait_threshold_check.txt`). **Not verified:** the cross-cohort result (not computed).
- **Next:** review of #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15) by Anna or Yassien, then merge (README conflicts with #16 and #17: merge `main` into whichever goes second). T-017 applies D-012 (Anna, or Jamie with her OK).
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @anna (T-017 review, first pass, unchanged): missed-heel-strike check is gaitpdb-only; freezing and stagger are in `ClinicalEvent`, so the "Walk" filter keeps them; D-012 needs the per-recording threshold in `_foot_tables` (one line).
- **Not pushed:** nothing.
