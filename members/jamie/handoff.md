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
_Updated 2026-11-06 16:15 by Claude (cloud session) for Jamie · branches `jamie/T-022-model-comparison` at `c203bb7` (pull request #16 open, no review yet) and `jamie/T-022-cross-cohort-run` at `87b45f5` (merges #15 to #18 and #19)_

- **Now:** final results in the run branch's README: no transfer to WearGait-PD (0.532 and 0.573); D-007's combined analysis 0.628 and 0.666, its gain from age and sex a recruitment effect; within gaitpdb 0.831 at 20 N against 0.789 at D-012 (not tested). The paper's Figure 5, cohort table and cross-cohort table are made by `scripts/make_figure5.py`, `make_cohort_table.py` and `make_table_crosscohort.py`, all run by `run_all.py`. A full rerun of `aff8778` from a clean copy (6 November, 91 minutes) reproduced every output `run_all.py` writes byte for byte, these three included, except the commit line in the two `features_summary.txt` files; the README says so (`87b45f5`). Since `aff8778` only `README.md` and `data/raw/README.md` changed (the README no longer says the datasets differ "before any model is fitted", and T-025's label definitions are merged in).
- **Validated:** 125 tests; the full clean rerun above (Linux, Python 3.13, NumPy 2.5.3, pandas 3.0.5, SciPy 1.18.1, scikit-learn 1.9.1, Matplotlib 3.11.2, two cores); the PhysioNet-only clean rerun of `085c0cf` (28 minutes, no committed file changed). **Not verified:** other operating systems and library versions; a second member reproducing the numbers.
- **Next:** (1) once #15 to #18 and T-017 are on `main`, merge `main` into the run branch, rerun `run_all.py` from a clean checkout, check that only the two commit lines change (update the README's "last checked" commit), and open its pull request; (2) a teammate reproduces the main numbers on their own machine (`python scripts/run_all.py`, then `git status`; without the WearGait-PD files nothing should change) and reports any difference, even in a last digit; (3) the SVM when T-020 lands.
- **Blocked / needs a decision:** reviews of #15 to #18; T-017 on `main` (Anna's pull request).
- **For teammates:** @anna @yassien: the results are in the run branch's README: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-022-cross-cohort-run/README.md#results; how to rerun them: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-022-cross-cohort-run/README.md#how-to-run. @anna: your five `scripts/explore_*.py`, rerun from a clean copy of your branch (`7d3e807`), give every number exactly as committed; four of them (turn timing, stride counts, WearGait-PD tasks, missing data) are not yet described in the README or in `report/T-017_stride_rule_exploration.md`.
- **Not pushed:** nothing.

## T-023 · Discussion (draft 3 on its branch, for the group's comments)
_Updated 2026-11-06 16:15 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `6bb30c5`_

- **Now:** `report/final/discussion.md`, draft 3 (about 1,700 words). Since the last handoff: Section C says the datasets differ "in the five features themselves" (not "before any model is fitted") and explains a WearGait-PD bout's slower last stride from the "Walk" label's definition [S20]. `report/final/sources.md` (also cited by the Methods and Results) records three new checks: S9's published article (sites, annotation), S20's Synapse wiki on the labels, and S20's licence page with Synapse's access type (for sharing the derived tables).
- **Validated:** draft 1's independent review; every number in draft 3's prose traced to the outputs (a script listed unmatched ones, each traced by hand); every value-and-interval pair checked jointly; the new sentence's source read. **Not verified:** the group has not read it.
- **Next:** the group's comments; add the SVM when T-020 lands; paste into the shared Word file and open the pull request (with `sources.md`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (finished: pull request #15 waits for a review; the test itself ran in T-022)
_Updated 2026-11-06 16:15 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `64b436b`; pull request #15 open (checks green), no review yet_

- **Now:** data downloaded and checked; walkway threshold check (D-012) and site table done; D-012 applied to T-017's cleaning in #19; the final models ran on WearGait-PD in T-022. `data/raw/README.md` on #15: the SelfPace description fixed (`e6ee563`); "How we use it" describes the final analysis (`274c3a6`); and now what the "Walk" and "Turn" labels cover, from the dataset's Synapse wiki (page "Video annotation"), and that the separate freezing and staggering labels (`ClinicalEvent`) are not used (`76540e6`, `64b436b`). All in #15's description and merged into the run branch.
- **Validated:** 10 walkway tests; #19's 3 tests; the task descriptions against the published article; the label definitions against the Synapse wiki (read 6 November); that the cleaning reads only `GeneralEvent` (`src/gaitpdb/clean_data.py`, `clean_weargait`). A scratch count (not in the repository) found freezing or staggering labels on about 0.5% of the "Walk" samples, in 23 of the 553 task files. **Not verified:** no teammate has reviewed #15; the article's Supplementary Tables S1 to S3 (did not open from the session).
- **Next:** Anna or Yassien reviews #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15), then merge (README conflicts with #16 and #17: merge `main` into whichever goes second), mark done, delete the branch.
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @anna: with #19 merged, the next step is your T-017 pull request to `main`; #17's final feature tables and the run branch wait on it. Strides during a labelled freeze are kept if they pass the stride limits; if the group wants them dropped, that is a change to `clean_weargait` and a rerun.
- **Not pushed:** nothing.

## T-032 · Results section of the final paper (draft 3 on its branch, for the group's comments)
_Updated 2026-11-06 16:15 by Claude (cloud session) for Jamie · branch `jamie/T-032-results-section` at `828d475`_

- **Now:** `report/final/results.md`, draft 3 (about 1,550 words of text, two tables, two figures): the participant flow and feature definitions now live in the Methods; numbers cited at `a4b9b73` (outputs identical to `2190b19` and, by the clean rerun, to `aff8778`). Section A now says the datasets differ "in ways that involve no diagnosis" rather than "before any diagnosis label is used" (the dataset-of-origin folds are stratified by diagnosis).
- **Validated:** draft 1's independent review; every number in draft 2's prose traced to the outputs; a joint check of all 46 value-and-interval triples; draft 3 removes text and changes no number. **Not verified:** the group has not read it.
- **Next:** the group's comments; add the SVM when T-020 lands; paste into the shared Word file and open the pull request (after the run branch's).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-032-results-section/report/final/results.md
- **Not pushed:** nothing.

## T-033 · Dataset and Methods section of the final paper (draft 2 on its branch, for the group's comments)
_Updated 2026-11-06 16:15 by Claude (cloud session) for Jamie · branch `jamie/T-033-methods-section` at `ea67c5f`_

- **Now:** `report/final/methods.md`, draft 2 (about 2,330 words in Sections A to G), after an independent review of draft 1; the list at the end says what changed. Since the last handoff: the "Walk" and "Turn" labels are defined from the dataset's Synapse wiki [S20], replacing the [UNVERIFIED] note, and the cleaning's non-use of the freezing and staggering labels is stated; Section C says what WearGait-PD's licence (CC BY 4.0) and Synapse's open-access type allow for the derived tables. The header gives a page estimate (9 to 10 of the 10 pages, references excluded) and what to cut here first.
- **Validated:** every number against the outputs and code at `a4b9b73`; S9's points in its published article; the label definitions and the licence in S20's Synapse wiki. **Not verified:** the Synapse Pledge's wording (it opens only when signed in); the group has not read it.
- **Next:** Jamie reads the Synapse Pledge while signed in and removes the bracketed note in Section C if nothing in it stops us sharing the derived tables (same note in the statements); the group's comments; the SVM sentence when T-020 lands; the submitted commit and the final rerun in Section G; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** Fig. 1 still shows the midterm's processing (regenerate with the final cleaning, or drop).
- **For teammates:** @anna: you wrote the midterm's Methods (Section IV); this one is yours to take over or revise if you want it (tell Jamie, and the board entry moves to you). @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-033-methods-section/report/final/methods.md
- **Not pushed:** nothing.

## T-034 · End statements of the final paper (draft 2 on its branch, for each member to check their part)
_Updated 2026-11-06 16:15 by Claude (cloud session) for Jamie · branch `jamie/T-034-end-statements` at `a75d4ea`_

- **Now:** `report/final/statements.md`, draft 2, aligned with the Methods draft 2: the AI's role in Jamie's work (designed and ran the analysis, proposed the threshold, the dropped feature and the added checks, which Jamie put to the group), the derived tables in full and shared under WearGait-PD's CC BY 4.0 licence, the dataset versions, and the number check as it was done.
- **Validated:** each statement about a member traced to their own log, the midterm statements or `DECISIONS.md`; the licence wording in S20's Synapse wiki. **Not verified:** no member has confirmed their part; Jamie's own checks of the AI-written work are not stated (his logs say he has not reviewed it); the Synapse Pledge's wording.
- **Next:** each member confirms or edits their part; Jamie confirms the AI description, states how he checked the code and drafts, and reads the Synapse Pledge; fill in the submitted commit; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** the members' confirmations.
- **For teammates:** @anna @yassien: please check what it says about you: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-034-end-statements/report/final/statements.md
- **Not pushed:** nothing.
