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

## T-018 · Feature extraction (finished: pull request #17 waits for a review; the final tables are on the T-022 run branch)
_Updated 2026-11-02 18:20 by Claude (cloud session) for Jamie · branch `jamie/T-018-feature-extraction` at `c6f7e8b`; pull request #17 open, no review yet_

- **Now:** #17 holds the code: participant features from the clean strides, the feature dictionary, the label-free checks and Figure 4. The final tables (T-017's strides with D-012 from #19, D-011 inclusion) were built on `jamie/T-022-cross-cohort-run` (`d0ea809`): 155 gaitpdb and 169 WearGait-PD participants. D-013 is recorded (`f629ab3`); its five inputs were set in `evaluation.MODEL_FEATURES` on the run branch (`4921862`), not in #17.
- **Validated:** 17 tests on #17, each checked to fail when broken; 108 tests on the run branch; the label-free numbers in the run branch's README re-read from `results/feature_checks.txt`. **Not verified:** no teammate has reviewed the code.
- **Next:** Yassien reviews #17 (https://github.com/Jsanson1/BMEN600_Group5/pull/17), then merge, mark done, delete the branch. The tables reach `main` with the run branch's pull request.
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @yassien: a first look at #17 please (the feature definitions and the dictionary).
- **Not pushed:** nothing.

## T-019 · Random forest (finished: pull request #18 waits for a review)
_Updated 2026-11-02 18:20 by Claude (cloud session) for Jamie · branch `jamie/T-019-random-forest` at `5076598`; pull request #18 open, no review yet_

- **Now:** final run on D-013's five inputs (run branch, `1a68375`): AUC 0.75 (0.65 to 0.85) within protocol, 0.70 (0.62 to 0.78) across protocols (`results/model_comparison.txt`); trained on gaitpdb and tested on WearGait-PD 0.573 (0.486 to 0.659) (`results/crosscohort_summary.txt`).
- **Validated:** 6 tests (4 mutations caught); 300 and 1000 trees give the same out-of-bag log-loss on the midterm features. **Not verified:** no teammate has reviewed the code.
- **Next:** Yassien reviews #18 (https://github.com/Jsanson1/BMEN600_Group5/pull/18), then merge, mark done, delete the branch. #16 and #18 both regenerate `results/model_comparison.*` and Figure 3: whichever merges second needs `main` merged in and `compare_models.py` rerun (the run branch already holds the final versions).
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @anna (T-020): the SVM joins through a `scripts/run_svm.py` with `make_factory(columns)` and outputs written by `evaluation.write_model_outputs(..., "svm")`; `run_cross_cohort.py` picks it up by that file name; add it to `READS_RESULTS` in `scripts/run_all.py`.
- **Not pushed:** nothing.

## T-022 · Model comparison and cross-dataset analyses (final results on the run branch; its pull request waits for #15 to #18 and T-017)
_Updated 2026-11-02 18:20 by Claude (cloud session) for Jamie · branches `jamie/T-022-model-comparison` at `c203bb7` (pull request #16 open, no review yet) and `jamie/T-022-cross-cohort-run` at `47ebeca` (merges #15 to #18 and #19)_

- **Now:** the final run is committed on the run branch (16:34 to 17:53). Trained on gaitpdb, the models do not transfer to WearGait-PD: AUC 0.532 (0.449 to 0.621) for the logistic regression and 0.573 (0.486 to 0.659) for the random forest. Not explained by stride count (cost at most 0.008), standardisation (0.535, 0.538) or leaving out variability (0.521, 0.576); the datasets are separable (0.94); age-matched pairs 0.646 and 0.670; the same at 20 N (0.534, 0.540). Post hoc, exploratory (`scripts/check_weargait_signal.py`): inside WearGait-PD the features barely separate the groups (logistic regression 0.595, 0.500 to 0.690). README Results rewritten (`47ebeca`); `run_all.py` now works without WearGait-PD's files (`be68f1c`).
- **Validated:** 108 tests; every README number re-read from its output file; the analysis (`bd4c61f`, 15:50) and inputs (`4921862`, 16:32) were committed before the first run on the real labels (16:34). Reruns from a clean checkout are under way (PhysioNet only, then full), with all 311 PhysioNet files now downloaded and checked against `SHA256SUMS.txt`. **Not verified:** a second member reproducing the numbers (midterm plan, Section VI); the reruns' outcome.
- **Next:** (1) when the reruns finish, confirm or correct the README's reproduction sentence; (2) once #15 to #18 and T-017 are on `main`, merge `main` into the run branch, rerun `compare_models.py` if needed, open its pull request; (3) a teammate reproduces the main numbers; (4) add the SVM when T-020 lands.
- **Blocked / needs a decision:** reviews of #15 to #18; T-017 on `main` (Anna: merge #19 into her branch, then open her pull request).
- **For teammates:** @anna @yassien: the results are in the run branch's README for Friday's discussion: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-022-cross-cohort-run/README.md#results
- **Not pushed:** nothing.

## T-023 · Discussion (outline ready; drafting from the final results)
_Updated 2026-11-02 18:20 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` not created yet_

- **Now:** outline written: the answer to the question; prior work; each alternative explanation for the failed transfer with its evidence (protocol and bout ends, stride count, hardware and threshold, population and site, dataset of origin); screening meaning; limitations; ethics; next step. New reference checked for the bout-end argument: D. Kroneberg et al., Front. Aging Neurosci., vol. 10, art. 435, 2019, doi:10.3389/fnagi.2018.00435.
- **Validated:** the reference's DOI, authors, title, year and venue, and that it reports longer strides after turns (more so in PD) and edge strides inflating variability. **Not verified:** the draft (not written yet).
- **Next:** create the branch, draft `report/final/discussion.md` from the run branch's results, push.
- **Blocked / needs a decision:** none (the SVM result goes in when T-020 lands).
- **For teammates:** none.
- **Not pushed:** the outline (in this session's scratch space; committed with the first draft).

## T-025 · WearGait-PD external test (finished: pull request #15 waits for a review; the test itself ran in T-022)
_Updated 2026-11-02 18:20 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `a0402fc`; pull request #15 open (checks green), no review yet_

- **Now:** data downloaded and checked; walkway threshold check (D-012) and site table done; D-012 applied to T-017's cleaning in #19 (into Anna's branch, waiting for her merge); the final models ran on WearGait-PD in T-022.
- **Validated:** 10 walkway tests; #19 adds 3 tests, and with `--fixed-threshold 20` it reproduces Anna's committed 20 N summary exactly. **Not verified:** no teammate has reviewed #15 or #19.
- **Next:** Anna or Yassien reviews #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15), then merge (README conflicts with #16 and #17: merge `main` into whichever goes second), mark done, delete the branch.
- **Blocked / needs a decision:** a reviewer; Anna's merge of #19.
- **For teammates:** @anna: #19 (https://github.com/Jsanson1/BMEN600_Group5/pull/19) adds D-012 to your T-017 branch as agreed; please merge it, then open your T-017 pull request to `main`. The earlier first-pass notes still stand (the missed-heel-strike check is gaitpdb-only; freezing and stagger are in `ClinicalEvent`, so the "Walk" filter keeps them).
- **Not pushed:** nothing.
