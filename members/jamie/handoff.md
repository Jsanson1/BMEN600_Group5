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
_Updated 2026-11-02 15:15 by Claude (cloud session) for Jamie · branch `jamie/T-022-model-comparison` at `c203bb7`; pull request #16 open (checks green)_

- **Now:** `src/gaitpdb/crosscohort.py` (D-007): pooled cross-validation stratified by diagnosis and dataset, with each dataset's AUC per fold; the cross-cohort test (fit once on gaitpdb, applied once to WearGait-PD; the 90%-specificity threshold carried over from gaitpdb's out-of-fold predictions); the dataset-of-origin check; sensitivity at 90% specificity with participant-bootstrap intervals; PPV and NPV at 1% prevalence; `stride_matched_tables` for the stride-count sensitivity analysis (D-011). `scripts/compare_models.py` now reports sensitivity at 90% specificity and the predictive values (logistic regression on gait features: 0.52, 95% CI 0.30 to 0.69, within protocol; PPV 0.058 at 1%).
- **Validated:** 12 unit tests, each checked to fail when its behaviour is broken; full suite passes; the compare_models rerun adds the new columns and leaves every existing number identical. **Not verified:** nothing has run on WearGait-PD yet (no features).
- **Next:** review of pull request #16 (https://github.com/Jsanson1/BMEN600_Group5/pull/16) by Anna or Yassien, then merge (it and #15 edit the same README row: bring the second up to date with `main` before merging). Once T-018 writes feature tables for both datasets: `scripts/run_cross_cohort.py` (pooled, cross-cohort, VA Puget Sound only, dataset of origin, stride-matched reference) for the logistic regression, then the RF and SVM through the same functions.
- **Blocked / needs a decision:** features for both datasets (T-018); whether stride-time asymmetry stays in the feature set (raised with the group on 2 November, see the log).
- **For teammates:** @anna @yassien: the RF and SVM join the cross-dataset comparison through the same model factory you pass to `evaluate_model`; nothing else is needed.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (data downloaded; threshold check and site table done; threshold decision pending)
_Updated 2026-11-02 15:15 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `a0402fc`; pull request #15 open (checks green)_

- **Now:** the three self-paced tasks of all 185 participants are downloaded (553 files, Synapse versions and MD5s in `results/weargait_files_downloaded.csv`; sheets match the README's MD5s). `scripts/check_weargait_threshold.py` ran on 170 participants (19,200 straight-walking footfalls on the walkway): stride time agrees exactly at every threshold; 5% of each recording's force level (and 30 N) matches the most footfalls one to one with stance within 30 ms (46.8% against 39.9% at 20 N; stance limits of agreement -0.15 to +0.11 s against -0.21 to +0.26 s), so it is the recommended threshold (`results/weargait_threshold_check.txt`). `scripts/check_weargait_participants.py` now gives task availability and the site-by-diagnosis table: Johns Hopkins Bayview contributes controls only, the Johns Hopkins Outpatient Center PD only; only VA Puget Sound has both groups (29 controls, 27 PD).
- **Validated:** 10 walkway tests and 43 in all pass; Anna's `make_clean_strides.py` reproduces her committed summaries exactly for both datasets from these files. Local experiment (not committed): at 5% of force level gaitpdb keeps the same 155 participants and WearGait-PD includes 169 instead of 164 (HC109, NLS056, NLS172, NLS185 and WPD011 rescued; 4 of them PD). **Not verified:** the cross-cohort result itself (deliberately not computed before the threshold and features are fixed).
- **Next:** review of pull request #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15) by Anna or Yassien, then merge; group decision on the contact threshold for both datasets (raised in the group chat on 2 November; the plan: the best-agreeing threshold, with 20 N reported as a check); then record it in DECISIONS.md, and T-017 changes the threshold in `clean_data` (Anna's code).
- **Blocked / needs a decision:** the threshold (group, Friday 6 November at the latest).
- **For teammates:** @anna (T-017 review, first pass): 49 tests and ruff pass and `make_clean_strides.py` reproduces your committed summaries exactly, gaitpdb and WearGait-PD. (1) The missed-heel-strike check runs on gaitpdb only, but WearGait-PD's insoles are where 20 N is known to fail; a partly merged stride (1.75 to 2.25 times the median) passes the 0.5 to 2.5 s limits and stays clean. (2) The dataset wiki shows freezing and stagger are labelled in `ClinicalEvent`, not `GeneralEvent`, so the "Walk" filter keeps them in both datasets alike. (3) If the group picks 5% of the force level, `clean_data` needs a per-recording threshold (one line where `stride_table` is called). The WearGait-PD files are on Jamie's side now too, so either of us can run the WearGait-PD part. @yassien (T-018): feature note in the group chat (stride-time asymmetry, MAD variability).
- **Not pushed:** nothing.
