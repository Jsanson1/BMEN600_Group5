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
_Updated 2026-11-06 12:50 by Claude (cloud session) for Jamie · branches `jamie/T-022-model-comparison` at `c203bb7` (pull request #16 open, no review yet) and `jamie/T-022-cross-cohort-run` at `a4b9b73` (merges #15 to #18 and #19)_

- **Now:** final results in the run branch's README: no transfer to WearGait-PD (0.532 and 0.573); D-007's combined analysis 0.628 and 0.666, its gain from age and sex a recruitment effect; within gaitpdb 0.831 at 20 N against 0.789 at D-012 (not tested). Exploratory: the models' PD score rises with age among WearGait-PD's controls (ρ 0.641 and 0.556), and 49 of the 56 age-matched pairs cross sites. A rerun of `085c0cf` from a clean checkout reproduced every output `run_all.py` writes byte for byte, except the commit line in the two `features_summary.txt` files. The README had said a rerun changes only the PDFs' creation dates and that `run_all.py` makes every committed output; it now says what reproduces, on which setup, and that the exploration outputs and the download record are made elsewhere (`2a9381b`), and that a rerun without WearGait-PD changes no committed file (`7297312`). New for the paper (6 November): Figure 5, the main results from unseen participants to an unseen cohort (`scripts/make_figure5.py`, values in `results/figure5_values.csv`); a table of the participants in both datasets (`scripts/make_cohort_table.py`); and a table of the cross-cohort test and its checks (`scripts/make_table_crosscohort.py`, run last in `run_all.py` because it reads the 20 N results). `check_weargait_signal.py` now prints the 49 age-matched pairs that join two sites, which the README had computed by hand (`4eb397d`). After the Results review (`2190b19`): Figure 5 prints no decision ID, the cross-cohort table gives two decimals and defines its terms, and `gaitpdb.crosscohort`'s docstring no longer calls the cross-cohort test "the plan's main result" (D-007 makes the pooled analysis the main analysis).
- **Validated:** 125 tests (13 new for the three paper outputs and their place in `run_all.py`); each new output byte-identical when rerun; all 311 PhysioNet files against `SHA256SUMS.txt`; the full clean rerun with both datasets (85 minutes; Linux, Python 3.13, NumPy 2.5.3, pandas 3.0.5, SciPy 1.18.1, scikit-learn 1.9.1, Matplotlib 3.11.2); the PhysioNet-only clean rerun of `085c0cf` (28 minutes: every PhysioNet step ran, the WearGait-PD steps were skipped, and no committed file changed). **Not verified:** a full clean rerun since the three paper outputs were added (the last was `085c0cf`); other operating systems and library versions; a second member reproducing the numbers.
- **Next:** (1) once #15 to #18 and T-017 are on `main`, merge `main` into the run branch, rerun `run_all.py` from a clean checkout, check that only the two commit lines change (and update the README's "last checked" commit), and open its pull request; (2) a teammate reproduces the main numbers on their own machine (`python scripts/run_all.py`, then `git status`; without the WearGait-PD files nothing should change) and reports any difference, even in a last digit; (3) the SVM when T-020 lands.
- **Blocked / needs a decision:** reviews of #15 to #18; T-017 on `main` (Anna's pull request).
- **For teammates:** @anna @yassien: the results for Friday are in the run branch's README: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-022-cross-cohort-run/README.md#results. @anna: your five `scripts/explore_*.py`, rerun from a clean copy of your branch (`7d3e807`), give every number exactly as committed (all 9 text and CSV files); the 13 figures show the same content but differ in pixels, because they were drawn with Matplotlib 3.11.2 against your 3.9.4. `run_all.py` does not run these scripts (the README now says so), and four of them (turn timing, stride counts, WearGait-PD tasks, missing data) are not yet described in the README or in `report/T-017_stride_rule_exploration.md`.
- **Not pushed:** nothing.

## T-023 · Discussion (draft 3 on its branch, for the group's comments)
_Updated 2026-11-06 13:30 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `7a48b2c`_

- **Now:** `report/final/discussion.md`, draft 3 (about 1,670 words, about two pages). `report/final/sources.md` (also on this branch, cited by the Methods and Results too) holds S21 to S24 and, since `7a48b2c`, a row recording the checks of S9's published article behind the Methods: the sites share equipment, software and protocol; the task labels come from frame-by-frame video annotation by two expert reviewers. The label definitions (the article's Supplementary Tables S1 to S3) did not open from the session and are not read.
- **Validated:** draft 1's independent review (taken in by draft 2); a script listed every number in draft 3's prose not found in the outputs, and each was traced by hand (one, S1's 80.6%, is a literature value); every value-and-interval pair checked jointly. **Not verified:** the group has not read it.
- **Next:** the group's comments; add the SVM when T-020 lands; paste into the shared Word file and open the pull request (with `sources.md`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md. Whoever can open the WearGait-PD article's supplement (Sci. Data 13, 440, the .docx under Supplementary information), please read Tables S1 to S3 and say what the "Walk" label covers (our cleaning keeps only "Walk" samples).
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (finished: pull request #15 waits for a review; the test itself ran in T-022)
_Updated 2026-11-06 13:12 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `274c3a6`; pull request #15 open (checks green), no review yet_

- **Now:** data downloaded and checked; walkway threshold check (D-012) and site table done; D-012 applied to T-017's cleaning in #19, which Anna merged into her branch on 2 November; the final models ran on WearGait-PD in T-022. New on #15 (`e6ee563`, also in the run branch): `data/raw/README.md` no longer says participants turn about 5 ft beyond the walkway in SelfPace, and marks the 8 m per pass as our estimate (the published article gives the 5 ft for the start only); since `274c3a6` its "How we use it" section describes the final analysis rather than the October plan. Both are in #15's description and in the run branch.
- **Validated:** 10 walkway tests; #19's 3 tests, and with `--fixed-threshold 20` it reproduced Anna's 20 N summary exactly; the WearGait-PD task descriptions in `data/raw/README.md` against the published article. **Not verified:** no teammate has reviewed #15.
- **Next:** Anna or Yassien reviews #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15), then merge (README conflicts with #16 and #17: merge `main` into whichever goes second), mark done, delete the branch.
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @anna: with #19 merged, the next step is your T-017 pull request to `main`; #17's final feature tables and the run branch wait on it. The earlier first-pass notes still stand (the missed-heel-strike check is gaitpdb-only; freezing and stagger are in `ClinicalEvent`, so the "Walk" filter keeps them).
- **Not pushed:** nothing.

## T-032 · Results section of the final paper (draft 3 on its branch, for the group's comments)
_Updated 2026-11-06 13:30 by Claude (cloud session) for Jamie · branch `jamie/T-032-results-section` at `0ff4b07`_

- **Now:** `report/final/results.md`, draft 3 (about 1,550 words of text, two tables, two figures): the participant flow and the feature definitions now live in the Methods, and Section A and B point to them; numbers cited at `a4b9b73`, whose outputs are identical to `2190b19`'s. Draft 2's word count (1,350) was low and is corrected.
- **Validated:** draft 1's independent review; a script listed every number in draft 2's prose not found in the outputs (two, ratios written as percentages, explained in the draft); a joint check of all 46 value-and-interval triples. Draft 3 removes text and changes no number. **Not verified:** the group has not read it.
- **Next:** the group's comments; add the SVM when T-020 lands; paste into the shared Word file and open the pull request (after the run branch's).
- **Blocked / needs a decision:** none (the Methods draft 2 names the primary result as this draft does).
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-032-results-section/report/final/results.md
- **Not pushed:** nothing.

## T-033 · Dataset and Methods section of the final paper (draft 2 on its branch, for the group's comments)
_Updated 2026-11-06 13:30 by Claude (cloud session) for Jamie · branch `jamie/T-033-methods-section` at `a0cc7d9`_

- **Now:** `report/final/methods.md`, draft 2 (about 2,330 words in Sections A to G), after an independent review of draft 1 by a separate agent. The review was right on every point I checked: the threshold choice was described wrongly (its criterion, the 14 candidates, the tie with 30 N, the changed criterion; and it was chosen on walkway agreement, not before any classification result), 306 recordings come from 165 people not 166, the label-free checks are not label-free in every step, and several settings were missing. All taken in; the list at the end of the draft says what changed. The header gives a page estimate (9 to 10 of the 10 pages, references excluded) and what to cut here first if needed.
- **Validated:** every number in draft 2 against the outputs and code at `a4b9b73` (participant flow, recordings per person, task files, assistive devices, threshold check, model grids, splits, bootstraps, matching, stride-matched reference, 1% prevalence, 125 tests); S9's points in its published article. **Not verified:** the definitions of WearGait-PD's video labels (marked [UNVERIFIED]); the group has not read it.
- **Next:** the group's comments; the SVM sentence when T-020 lands; the submitted commit and the final rerun's result in Section G; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** whether the Synapse terms allow sharing the derived per-participant WearGait-PD tables in `results/`; Fig. 1 still shows the midterm's processing (regenerate with the final cleaning, or drop).
- **For teammates:** @anna: you wrote the midterm's Methods (Section IV); this one is yours to take over or revise if you want it (tell Jamie, and the board entry moves to you). @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-033-methods-section/report/final/methods.md
- **Not pushed:** nothing.

## T-034 · End statements of the final paper (draft 2 on its branch, for each member to check their part)
_Updated 2026-11-06 13:30 by Claude (cloud session) for Jamie · branch `jamie/T-034-end-statements` at `5f75504`_

- **Now:** `report/final/statements.md`, draft 2: aligned with the Methods draft 2. The AI's role in Jamie's work now says it designed and ran the analysis and proposed the threshold, the dropped feature and the added checks, which Jamie put to the group (D-012, D-013); the derived tables are listed in full; the dataset versions are named; the check of the numbers is described as it was done (a script listed unmatched numbers, traced by hand), not as a full automatic match.
- **Validated:** each statement about a member traced to their own log, the midterm statements or `DECISIONS.md`. **Not verified:** no member has confirmed their part; Jamie's own checks of the AI-written work are not stated (his logs say he has not reviewed it).
- **Next:** each member confirms or edits their part; Jamie confirms the AI description and states how he checked the code and drafts; fill in the submitted commit; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** the members' confirmations.
- **For teammates:** @anna @yassien: please check what it says about you: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-034-end-statements/report/final/statements.md
- **Not pushed:** nothing.
