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
_Updated 2026-11-02 20:15 by Claude (cloud session) for Jamie · branch `jamie/T-019-random-forest` at `131c31b`; pull request #18 open, no review yet_

- **Now:** final run on D-013's five inputs (run branch): AUC 0.75 (0.65 to 0.85) within protocol, 0.70 (0.62 to 0.78) across protocols, 0.573 (0.486 to 0.659) across cohorts. New on #18 (`131c31b`): the fitted forest predicts in one thread. In parallel threads scikit-learn added the trees' votes in a varying order, so the last digit of some probabilities changed between runs (found by a rerun from a clean checkout; once it moved a 20 N AUC by one patient-control pair, 0.477177 to 0.477252).
- **Validated:** 7 tests, the new one failing without the fix in 5 of 5 runs; 39 pass on the branch. **Not verified:** no teammate has reviewed the code.
- **Next:** Yassien reviews #18 (https://github.com/Jsanson1/BMEN600_Group5/pull/18), then merge, mark done, delete the branch. #16 and #18 both regenerate `results/model_comparison.*` and Figure 3: whichever merges second needs `main` merged in and `compare_models.py` rerun (the run branch holds the final versions).
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @anna (T-020): the SVM joins through a `scripts/run_svm.py` with `make_factory(columns)` and outputs written by `evaluation.write_model_outputs(..., "svm")`; `run_cross_cohort.py` and `compare_models.py` pick it up by that file name (`MODEL_FILES` already lists `svm`); add it to `READS_RESULTS` in `scripts/run_all.py`.
- **Not pushed:** nothing.

## T-022 · Model comparison and cross-dataset analyses (final results and reproduction fixes on the run branch; a clean rerun is checking them)
_Updated 2026-11-02 20:15 by Claude (cloud session) for Jamie · branches `jamie/T-022-model-comparison` at `c203bb7` (pull request #16 open, no review yet) and `jamie/T-022-cross-cohort-run` at `085c0cf` (merges #15 to #18 and #19)_

- **Now:** final results in the run branch's README: no transfer to WearGait-PD (0.532 and 0.573); D-007's combined analysis 0.628 and 0.666, its gain from age and sex a recruitment effect; within gaitpdb 0.831 at 20 N against 0.789 at D-012 (not tested). Exploratory: the models' PD score rises with age among WearGait-PD's controls (ρ 0.641 and 0.556), and 49 of the 56 age-matched pairs cross sites. Reruns from clean checkouts found and fixed: `compare_models.py` stopping on any fresh checkout (now reads the model files by name); `run_all.py` with PhysioNet alone overwriting three summaries and crashing (now runs the PhysioNet steps only); the forest's parallel predictions (T-019); a stale Figure 2 (now redrawn for the final design from the feature tables); creation dates in two figures' PDFs.
- **Validated:** 112 tests; all 311 PhysioNet files against `SHA256SUMS.txt`; the PhysioNet-only rerun ran every step; the regeneration changed only the forest's rows (1e-16, one 20 N value 7.5e-5) and no summary. **Not verified:** the full clean rerun of `085c0cf` (running; it should differ only in the commit line of the two `features_summary.txt` files); a second member reproducing the numbers.
- **Next:** (1) when the rerun ends, check it and correct the README's reproduction sentence (it still says "nothing but the PDFs' creation dates"; the expected difference is that commit line); (2) once #15 to #18 and T-017 are on `main`, merge `main` into the run branch and open its pull request; (3) a teammate reproduces the main numbers; (4) the SVM when T-020 lands.
- **Blocked / needs a decision:** reviews of #15 to #18; T-017 on `main` (Anna: merge #19, then her pull request).
- **For teammates:** @anna @yassien: the results for Friday are in the run branch's README: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-022-cross-cohort-run/README.md#results
- **Not pushed:** nothing.

## T-023 · Discussion (draft 2 on its branch, for the group's comments)
_Updated 2026-11-02 20:15 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `21d935a`_

- **Now:** `report/final/discussion.md`, draft 2 (about 2,100 words, slightly above the brief's 1.5 to 2 pages): the answer, prior work, five explanations for the failed transfer weighed against the evidence, what the study shows and does not, screening meaning, six limitations, next step (WearGait-PD's FreeWalk task, its controls' motor scores, turns). `report/final/sources.md`: S21 (Kroneberg et al. 2019) and further checks of S7, S9, S11 and S13.
- **Validated:** an independent review of draft 1 by a separate agent (29 findings; those taken in are listed at the end of the draft); every number checked by script against the run branch's outputs; S21 against its repository record and full text; S9's new details in the article's preprint. **Not verified:** S9's new details against the published article (the page could not be opened from the session); the group has not read the draft.
- **Next:** the group's comments; cut to two pages once the Results section carries the bout statistics; add the SVM when T-020 lands; then paste into the shared Word file and open the pull request.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (finished: pull request #15 waits for a review; the test itself ran in T-022)
_Updated 2026-11-02 18:20 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `a0402fc`; pull request #15 open (checks green), no review yet_

- **Now:** data downloaded and checked; walkway threshold check (D-012) and site table done; D-012 applied to T-017's cleaning in #19 (into Anna's branch, waiting for her merge); the final models ran on WearGait-PD in T-022.
- **Validated:** 10 walkway tests; #19 adds 3 tests, and with `--fixed-threshold 20` it reproduces Anna's committed 20 N summary exactly. **Not verified:** no teammate has reviewed #15 or #19.
- **Next:** Anna or Yassien reviews #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15), then merge (README conflicts with #16 and #17: merge `main` into whichever goes second), mark done, delete the branch.
- **Blocked / needs a decision:** a reviewer; Anna's merge of #19.
- **For teammates:** @anna: #19 (https://github.com/Jsanson1/BMEN600_Group5/pull/19) adds D-012 to your T-017 branch as agreed; please merge it, then open your T-017 pull request to `main`. The earlier first-pass notes still stand (the missed-heel-strike check is gaitpdb-only; freezing and stagger are in `ClinicalEvent`, so the "Walk" filter keeps them).
- **Not pushed:** nothing.
