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

## T-022 · Model comparison and cross-dataset analyses (final results on the run branch, reproduced from a clean checkout)
_Updated 2026-11-06 12:50 by Claude (cloud session) for Jamie · branches `jamie/T-022-model-comparison` at `c203bb7` (pull request #16 open, no review yet) and `jamie/T-022-cross-cohort-run` at `4eb397d` (merges #15 to #18 and #19)_

- **Now:** final results in the run branch's README: no transfer to WearGait-PD (0.532 and 0.573); D-007's combined analysis 0.628 and 0.666, its gain from age and sex a recruitment effect; within gaitpdb 0.831 at 20 N against 0.789 at D-012 (not tested). Exploratory: the models' PD score rises with age among WearGait-PD's controls (ρ 0.641 and 0.556), and 49 of the 56 age-matched pairs cross sites. A rerun of `085c0cf` from a clean checkout reproduced every output `run_all.py` writes byte for byte, except the commit line in the two `features_summary.txt` files. The README had said a rerun changes only the PDFs' creation dates and that `run_all.py` makes every committed output; it now says what reproduces, on which setup, and that the exploration outputs and the download record are made elsewhere (`2a9381b`), and that a rerun without WearGait-PD changes no committed file (`7297312`). New for the paper (6 November): Figure 5, the main results from unseen participants to an unseen cohort (`scripts/make_figure5.py`, values in `results/figure5_values.csv`); a table of the participants in both datasets (`scripts/make_cohort_table.py`); and a table of the cross-cohort test and its checks (`scripts/make_table_crosscohort.py`, run last in `run_all.py` because it reads the 20 N results). `check_weargait_signal.py` now prints the 49 age-matched pairs that join two sites, which the README had computed by hand (`4eb397d`).
- **Validated:** 125 tests (13 new for the three paper outputs and their place in `run_all.py`); each new output byte-identical when rerun; all 311 PhysioNet files against `SHA256SUMS.txt`; the full clean rerun with both datasets (85 minutes; Linux, Python 3.13, NumPy 2.5.3, pandas 3.0.5, SciPy 1.18.1, scikit-learn 1.9.1, Matplotlib 3.11.2); the PhysioNet-only clean rerun of `085c0cf` (28 minutes: every PhysioNet step ran, the WearGait-PD steps were skipped, and no committed file changed). **Not verified:** a full clean rerun since the three paper outputs were added (the last was `085c0cf`); other operating systems and library versions; a second member reproducing the numbers.
- **Next:** (1) once #15 to #18 and T-017 are on `main`, merge `main` into the run branch, rerun `run_all.py` from a clean checkout, check that only the two commit lines change (and update the README's "last checked" commit), and open its pull request; (2) a teammate reproduces the main numbers on their own machine (`python scripts/run_all.py`, then `git status`; without the WearGait-PD files nothing should change) and reports any difference, even in a last digit; (3) the SVM when T-020 lands.
- **Blocked / needs a decision:** reviews of #15 to #18; T-017 on `main` (Anna's pull request).
- **For teammates:** @anna @yassien: the results for Friday are in the run branch's README: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-022-cross-cohort-run/README.md#results. @anna: your five `scripts/explore_*.py`, rerun from a clean copy of your branch (`7d3e807`), give every number exactly as committed (all 9 text and CSV files); the 13 figures show the same content but differ in pixels, because they were drawn with Matplotlib 3.11.2 against your 3.9.4. `run_all.py` does not run these scripts (the README now says so), and four of them (turn timing, stride counts, WearGait-PD tasks, missing data) are not yet described in the README or in `report/T-017_stride_rule_exploration.md`.
- **Not pushed:** nothing.

## T-023 · Discussion (draft 2 on its branch, for the group's comments)
_Updated 2026-11-06 12:50 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `858f8d9`_

- **Now:** `report/final/discussion.md`, draft 2 (about 2,100 words, slightly above the brief's 1.5 to 2 pages): the answer, prior work, five explanations for the failed transfer weighed against the evidence, what the study shows and does not, screening meaning, six limitations, next step (WearGait-PD's FreeWalk task, its controls' motor scores, turns). `report/final/sources.md`: S21 (Kroneberg et al. 2019) and further checks of S7, S9, S11 and S13. Since draft 2 (`858f8d9`): S9 checked against the published article, and the length of a SelfPace pass (about 8 m, our estimate) is no longer cited to it.
- **Validated:** an independent review of draft 1 by a separate agent (29 findings; those taken in are listed at the end of the draft); every number checked by script against the run branch's outputs; S21 against its repository record and full text; S9's details against the preprint and the published article (PubMed Central PMC13009270). **Not verified:** the group has not read the draft.
- **Next:** the group's comments; cut to two pages now that the Results draft (T-032) carries the bout statistics and the cross-cohort checks; cite Table I (`results/cohort_table.md`) instead of the midterm's Table 1, and use its WearGait-PD Hoehn and Yahr stage (modified, median 2, range 1 to 4, 5 missing) where Section C cites S9's 2.15 ± 0.61; add the SVM when T-020 lands; then paste into the shared Word file and open the pull request.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (finished: pull request #15 waits for a review; the test itself ran in T-022)
_Updated 2026-11-02 21:56 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `e6ee563`; pull request #15 open (checks green), no review yet_

- **Now:** data downloaded and checked; walkway threshold check (D-012) and site table done; D-012 applied to T-017's cleaning in #19, which Anna merged into her branch on 2 November; the final models ran on WearGait-PD in T-022. New on #15 (`e6ee563`, also in the run branch): `data/raw/README.md` no longer says participants turn about 5 ft beyond the walkway in SelfPace, and marks the 8 m per pass as our estimate (the published article gives the 5 ft for the start only).
- **Validated:** 10 walkway tests; #19's 3 tests, and with `--fixed-threshold 20` it reproduced Anna's 20 N summary exactly; the WearGait-PD task descriptions in `data/raw/README.md` against the published article. **Not verified:** no teammate has reviewed #15.
- **Next:** Anna or Yassien reviews #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15), then merge (README conflicts with #16 and #17: merge `main` into whichever goes second), mark done, delete the branch.
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @anna: with #19 merged, the next step is your T-017 pull request to `main`; #17's final feature tables and the run branch wait on it. The earlier first-pass notes still stand (the missed-heel-strike check is gaitpdb-only; freezing and stagger are in `ClinicalEvent`, so the "Walk" filter keeps them).
- **Not pushed:** nothing.

## T-032 · Results section of the final paper (draft 1 on its branch; an independent review is running)
_Updated 2026-11-06 12:50 by Claude (cloud session) for Jamie · branch `jamie/T-032-results-section` at `2eca4ae`_

- **Now:** `report/final/results.md`, draft 1 (about 1,250 words, possibly a little over the brief's two pages with the tables and figures): the participants and how the datasets differ before any label is used (Table I, Fig. 4); the AUC from unseen participants to an unseen cohort with its comparisons (Fig. 5); the checks of the cross-cohort result (Table II); which features carry the separation in gaitpdb; the exploratory checks written after the test. The figure and two tables it uses are made by code on the T-022 run branch.
- **Validated:** a script matched 223 of the 225 numbers in the prose to the output files (verbatim or by rounding); the other two are ratios in `results/feature_checks.txt` written as percentages, which the draft's closing table explains. **Not verified:** the independent review of the draft (running); the group has not read it; the Methods it must agree with are not written.
- **Next:** take in the review; the group's comments; trim Sections C and E if the page budget needs it; add the SVM when T-020 lands; paste into the shared Word file and open the pull request (after the run branch's).
- **Blocked / needs a decision:** who writes Methods (not on the board); the Results assume the evaluation and inclusion described in the README.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-032-results-section/report/final/results.md
- **Not pushed:** nothing.
