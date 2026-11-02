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

## T-022 · Model comparison (cross-dataset evaluation built; waits for both datasets' features, T-018, and the random forest and SVM, T-019 and T-020)
_Updated 2026-11-02 14:05 by Claude (cloud session) for Jamie · branch `jamie/T-022-model-comparison` at `a9b14b7`_

- **Now:** `src/gaitpdb/crosscohort.py` (D-007): pooled cross-validation stratified by diagnosis and dataset, with each dataset's AUC per fold; the cross-cohort test (fit once on gaitpdb, applied once to WearGait-PD; the 90%-specificity threshold carried over from gaitpdb's out-of-fold predictions); the dataset-of-origin check; sensitivity at 90% specificity with participant-bootstrap intervals; PPV and NPV at 1% prevalence; `stride_matched_tables` for the stride-count sensitivity analysis (D-011). `scripts/compare_models.py` now reports sensitivity at 90% specificity and the predictive values (logistic regression on gait features: 0.52, 95% CI 0.30 to 0.69, within protocol; PPV 0.058 at 1%).
- **Validated:** 12 unit tests, each checked to fail when its behaviour is broken; full suite passes; the compare_models rerun adds the new columns and leaves every existing number identical. **Not verified:** nothing has run on WearGait-PD yet (no features).
- **Next:** once T-018 writes feature tables for both datasets, add `scripts/run_cross_cohort.py` (pooled, cross-cohort, Seattle only, dataset of origin, stride-matched reference) for the logistic regression, then the RF and SVM through the same functions; open the pull request (reviewer Anna or Yassien).
- **Blocked / needs a decision:** features for both datasets (T-018); whether stride-time asymmetry stays in the feature set (raised with the group on 2 November, see the log).
- **For teammates:** @anna @yassien: the RF and SVM join the cross-dataset comparison through the same model factory you pass to `evaluate_model`; nothing else is needed.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (walkway threshold check built; sensor files being downloaded)
_Updated 2026-11-02 14:05 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `0a694b9`_

- **Now:** `src/gaitpdb/walkway.py` and `scripts/check_weargait_threshold.py`: the insole contacts at each candidate threshold (10, 20 and 50 N; 2.5% and 5% of the recording's force level; 2.5% and 5% of body weight) matched to the walkway's complete footfalls, with stance, stride and swing differences and limits of agreement, overall, by group and by site; the threshold is recommended on walkway agreement only (Midterm Research Plan, Section IV). Column names, units and the `_mat` tasks' erroneous last frame are from the dataset's Synapse wiki ("Data description", "Things to know"), read on 2 November.
- **Validated:** 9 unit tests on synthetic signals (including the NLS056-type raised swing baseline and pairwise merged contacts), each checked to fail when its behaviour is broken. **Not verified:** anything on real WearGait-PD files; the body-weight thresholds need the weight column of the participant sheets, which `weargait.load_participants` does not read yet.
- **Next:** download the sensor files (SelfPace, SelfPace_mat, SelfPace_matTURN, Version 1) and the participant sheets; run `scripts/check_weargait_threshold.py`; take the recommended threshold to the group; the site-by-diagnosis table with the D-011 inclusion (after T-017 merges); README file map.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna (T-017 review, first pass): 49 tests and ruff pass and `make_clean_strides.py` reproduces your committed gaitpdb summary exactly. (1) The missed-heel-strike check runs on gaitpdb only, but WearGait-PD's insoles are where 20 N is known to fail; a partly merged stride (1.75 to 2.25 times the median) passes the 0.5 to 2.5 s limits and stays clean, so it may be worth applying `_missed_heel_strikes` there too. (2) The dataset wiki shows freezing and stagger are labelled in `ClinicalEvent`, not `GeneralEvent`, so the "Walk" filter keeps them in both datasets alike; worth one line in the docstring. @yassien (T-018): feature note in the group chat of 2 November (stride-time asymmetry, MAD variability).
- **Not pushed:** nothing.
