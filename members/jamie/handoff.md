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

## T-022 · Model comparison and cross-dataset analyses (#16 merged; the run branch is current with main and waits for T-017 and #15)
_Updated 2026-11-09 15:20 by Claude (cloud session) for Jamie · `jamie/T-022-model-comparison` merged as #16 (branch still to delete); `jamie/T-022-cross-cohort-run` at `3fb9bc8`; docs fix #20 merged into `main`_

- **Now:** #16, #17 and #18 are merged into `main` after Yassien's approvals and the fixes he asked for: #16's docstrings now say the 90% specificity rule picks the corner of the ROC curve (the code is unchanged, since the cross-cohort run used it) and his example is a test; #17 escapes the bars in the feature dictionary; #18 got `main` merged in with `compare_models.py` rerun. The run branch has `main` merged in (`3fb9bc8`): results identical except the escaped dictionary, and the README records Yassien's full rerun of `87b45f5` on Windows with both datasets (every reported number reproduced; line endings, last digits in 21 CSVs and PNG bytes differ) and limits "byte for byte" to the Linux setup.
- **Also:** #20 (self-merged docs fix, `89d51bf`) corrects `main`'s README after #17: `run_all.py` does not stop at `make_features.py` without T-017 (the feature steps skip); a clean run of `main` at `a3e1600` took 31 minutes (25 the random forest) and changed no reported number (PDF creation dates; random forest predictions within 3.3e-16).
- **Validated:** 126 tests; checks green on each merged pull request; rerunning `make_features.py` and `compare_models.py` after the merge changes only the dictionary; all 79 numbers in the run branch's README Results section are in its outputs; two full reruns (`aff8778` here on Linux; `87b45f5` by Yassien on Windows). **Not verified:** the run branch's full rerun after `3fb9bc8` (the code changes since `aff8778` are docstrings, a test and the dictionary escape).
- **Next:** (1) T-017 (Anna's pull request) and #15 merged into `main`; (2) merge `main` into the run branch, full rerun from a clean checkout, update the README's "last checked", open its pull request (Yassien or Anna reviews); (3) the SVM when T-020 lands.
- **Blocked / needs a decision:** Anna's T-017 pull request (her branch has not moved since 2 November); a review of #15.
- **For teammates:** @yassien: thanks for the rerun and the reviews; the README now says what your Windows run showed (`3fb9bc8`), so your T-022 handoff section can go. Could you also review #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15)? @anna: the rest of the analysis can only reach `main` after your cleaning code does; please open the pull request from `anna/T-017-preprocessing` when you can.
- **Not pushed:** nothing.

## T-023 · Discussion (draft 3 on its branch, for the group's comments)
_Updated 2026-11-06 16:15 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `6bb30c5`_

- **Now:** `report/final/discussion.md`, draft 3 (about 1,700 words). Since the last handoff: Section C says the datasets differ "in the five features themselves" (not "before any model is fitted") and explains a WearGait-PD bout's slower last stride from the "Walk" label's definition [S20]. `report/final/sources.md` (also cited by the Methods and Results) records three new checks: S9's published article (sites, annotation), S20's Synapse wiki on the labels, and S20's licence page with Synapse's access type (for sharing the derived tables).
- **Validated:** draft 1's independent review; every number in draft 3's prose traced to the outputs (a script listed unmatched ones, each traced by hand); every value-and-interval pair checked jointly; the new sentence's source read. **Not verified:** the group has not read it.
- **Next:** the group's comments; add the SVM when T-020 lands; paste into the shared Word file and open the pull request (with `sources.md`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (finished: pull request #15 is current with main and waits for a review)
_Updated 2026-11-09 15:20 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `0f7cd84`; pull request #15 open (checks green, mergeable), no review yet_

- **Now:** #15 has `main` (with #16 to #18 and #20) merged in. Its `results/weargait_participants.txt` is now what its own code writes without T-017 (the stride-inclusion table says it needs T-017's clean strides); the version committed before had been made from T-017's strides at the old 20 N threshold (6 with too few strides against the final 1) and could not be reproduced from this branch. The final table is on the run branch. Earlier: data downloaded and checked; walkway threshold check (D-012); `data/raw/README.md` with the task descriptions, the label definitions from the Synapse wiki and the final use of the data.
- **Validated:** a clean run of the merge with both datasets (9 November, 34 minutes, exit 0): no other reported number changed (PDF creation dates; random forest predictions within 3.3e-16); 80 tests; checks green. **Not verified:** no teammate has reviewed #15; WearGait-PD's Supplementary Tables S1 to S3.
- **Next:** Yassien (asked on #15) or Anna reviews; Jamie merges; mark done; delete the branch. When the run branch next merges `main`, keep its own `results/weargait_participants.txt` (the final table).
- **Blocked / needs a decision:** a reviewer.
- **For teammates:** @yassien: could you review #15 (https://github.com/Jsanson1/BMEN600_Group5/pull/15)? The comment at the bottom says what changed since it was opened. @anna: strides during a labelled freeze are kept if they pass the stride limits; if the group wants them dropped, that is a change to `clean_weargait` and a rerun.
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
_Updated 2026-11-09 13:15 by Claude (cloud session) for Jamie · branch `jamie/T-033-methods-section` at `246e0c4`_

- **Now:** `report/final/methods.md`, draft 2 (about 2,330 words in Sections A to G), after an independent review of draft 1; the list at the end says what changed. Since the last handoff: the "Walk" and "Turn" labels are defined from the dataset's Synapse wiki [S20], replacing the [UNVERIFIED] note, and the cleaning's non-use of the freezing and staggering labels is stated; Section C says what WearGait-PD's licence (CC BY 4.0) and Synapse's open-access type allow for the derived tables; Section F describes the threshold carried to WearGait-PD as the code sets it (the highest threshold reaching the best sensitivity at a specificity of at least 90%), after Yassien's review of #16. The header gives a page estimate (9 to 10 of the 10 pages, references excluded) and what to cut here first.
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
