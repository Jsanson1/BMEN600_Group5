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

## T-022 · Model comparison and cross-dataset analyses (final rerun with the SVM running; then the run branch's pull request)
_Updated 2026-11-13 14:35 by Claude (cloud session) for Jamie · `jamie/T-022-cross-cohort-run` at `79228fa`; `jamie/T-022-model-comparison` merged as #16 (branch still to delete)_

- **Now:** #21 and #15 are merged. The run branch has merged `main` (`450cedc`) and Anna's SVM branch at `7100e65` (`79228fa`; `run_all.py` now runs `run_svm.py` on the final feature table, which the other models read by default; 139 tests). The final rerun of every step, the SVM included, is running from a fresh clone of `79228fa`. It needs about 4 hours on two cores, and one command in this cloud session stops after 2, so it runs `run_all.py`'s own plan in chunks (each command as `run_all.py` builds it), with the cross-cohort step's results kept per model and input set between chunks by a scratch helper that is not in the repository. Every random draw in those analyses starts from a fixed seed inside each call, so the kept values are the ones a single run computes.
- **Validated:** the helper on the logistic regression's cross-cohort test: its outputs are byte-identical to those of `run_cross_cohort.py` run directly, whether computed or read back; stopped at its time limit, it writes nothing. **Not verified:** the rerun itself (running); one uninterrupted `python scripts/run_all.py` with the SVM.
- **Next:** when the rerun ends: check that the logistic regression's and random forest's outputs equal the committed ones (their inputs have not changed) and look at every other changed file; commit the outputs and the README's "last checked"; update the Results, Discussion and Methods drafts (the SVM's numbers, the Holm p values); open the run branch's pull request (reviewer Yassien or Anna), asking Yassien to run `python scripts/run_all.py` once in one go on his PC as the uninterrupted check.
- **Blocked / needs a decision:** the correction note to D-012 (from #15's bug fix): Jamie confirms that the group agreed, then it is appended as D-014: "D-014 · Correction to the evidence of D-012 (no change to the decision). The threshold check behind D-012 counted every walkway footfall, turns and stops included, because its script did not load the video labels (fixed in #15, `24037b8`). On the 12,397 straight-walking footfalls 5% of the force level still ranks first (53.5% within 30 ms against 53.4% at 30 N), with more footfalls matched one to one (87.1% against 85.5%) and narrower stance limits (-0.13 to +0.09 s against -0.21 to +0.23 s). The figures quoted in D-012 are superseded by `results/weargait_threshold_check.txt`."
- **For teammates:** @anna: your SVM (`7100e65`) is in the final rerun; open its pull request when you are ready (reviewer Jamie or Yassien); the run branch already contains it, so either can be merged first. #21 is merged, so T-017 can be marked done. @yassien: thanks for the reruns; once the run branch's pull request is up, one `python scripts/run_all.py` on your PC would be the check that the chunked rerun equals a single run.
- **Not pushed:** nothing.

## T-023 · Discussion (draft 3 on its branch, for the group's comments)
_Updated 2026-11-12 17:40 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `755dc3a`_

- **Now:** `report/final/discussion.md`, draft 3 (about 1,860 words). On 12 November, Anna's two suggestions went in: Section D says how to read the combined analysis's AUC (two feature scales a model can tell apart, 0.94, so its 0.63 and 0.67 describe neither one clinic nor a screening population; the per-dataset AUCs 0.71 and 0.73, 0.58 and 0.62, and the cross-cohort test are the interpretable results), and Section E recommends recording gait the same way across clinics, without the contact rule her wording included (we already used one rule for both). `report/final/sources.md` also holds the S9 and S20 checks.
- **Validated:** the new numbers against `crosscohort_summary.txt` (0.628, 0.666; 0.714, 0.726; 0.583, 0.622; 0.940, 0.941); earlier checks as before. **Not verified:** the group has not read draft 3 as a whole.
- **Next:** the group's comments; the SVM when T-020 lands; trim to fit the page budget if the Introduction needs the room; paste into the Word file and open the pull request (with `sources.md`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna: both suggestions are in (`755dc3a`), the second without the contact rule; check that the wording is still yours in spirit. @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md
- **Not pushed:** nothing.

## T-032 · Results section of the final paper (draft 3 on its branch, for the group's comments)
_Updated 2026-11-12 17:40 by Claude (cloud session) for Jamie · branch `jamie/T-032-results-section` at `05f3d46`_

- **Now:** `report/final/results.md`, draft 3 (about 1,550 words of text, two tables, two figures). The header now notes that the three Holm-adjusted p values in Section B change when the SVM joins the comparisons (Anna's T-020 note: one goes from 0.044 to 0.072 on the midterm table).
- **Validated:** as before (every number traced to the outputs; 46 value-and-interval triples checked jointly). **Not verified:** the group has not read it; the SVM's numbers and the final Holm values.
- **Next:** the group's comments; the SVM and the final Holm values from the run branch's rerun; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-032-results-section/report/final/results.md
- **Not pushed:** nothing.

## T-033 · Dataset and Methods section of the final paper (draft 2 on its branch, for the group's comments)
_Updated 2026-11-12 17:40 by Claude (cloud session) for Jamie · branch `jamie/T-033-methods-section` at `a7f726a`_

- **Now:** `report/final/methods.md`, draft 2 (about 2,350 words). On 12 November: the threshold check's figures corrected to the straight-walking footfalls (see T-025); and, for the page limit, the threshold choice, the gaitpdb turn rule's parameters (now pointed to in the code) and the operating points shortened by about 100 words. A trial layout (below) is described in the header.
- **Page budget:** a trial layout of the drafted sections in the IEEE conference template's page geometry (US Letter, two 3.5-inch columns, 10-point Times; Table I and Figure 4 at full width, Table II and Figures 2 and 5 at one column; placeholders of the brief's lengths for the abstract, 230 words, and Conclusion, 250), converted to PDF with LibreOffice, put the paper at its 10-page limit with an Introduction of only about 1,300 words before these cuts. With the Methods cuts and the short AI-Assisted Work statement proposed in T-034, an Introduction of 1,500 words leaves about half a page on page 10, and 1,700 words fills it. A scratch measurement, not in the repository; Word's layout may differ by about half a page.
- **Validated:** every number in the Methods against the outputs and code (the threshold figures against `results/weargait_threshold_check.txt` at `24037b8`). **Not verified:** the Synapse Pledge's wording; the group has not read it.
- **Next:** Jamie reads the Synapse Pledge while signed in; the group's comments; the SVM sentence when T-020 lands; the submitted commit and the final rerun in Section G; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** Fig. 1 (regenerate with the final cleaning, or drop; dropping it also saves space).
- **For teammates:** @anna @yassien: the Introduction has about 1,500 words (about 1.7 pages) if the group adopts the short AI statement, and about 1,300 if not; the Conclusion about 250. Comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-033-methods-section/report/final/methods.md
- **Not pushed:** nothing.

## T-034 · End statements of the final paper (draft 3 on its branch, for each member to check their part)
_Updated 2026-11-13 14:35 by Claude (cloud session) for Jamie · branch `jamie/T-034-end-statements` at `0775172`_

- **Now:** `report/final/statements.md`: Anna's checked wording for her AI-use paragraph and her contributions (12 November), plus her review of #15; Yassien's reruns (the whole analysis; on 13 November #15's threshold check and the SVM) and his reviews (#15 to #18) in his parts, for him to confirm (`0775172`); the reruns and cross-reviews in the verification paragraph. Jamie's review is now in his words (13 November, `c5f6e0c`): he skimmed all of the code, drafts and figures for errors, with a placeholder for the longer pass he plans before submission. A short AI-Assisted Work version (about 220 words, against about 770) is proposed for the page limit, keeping the long one for the repository.
- **Validated:** each statement about a member traced to their log, the midterm statements, `DECISIONS.md` or the pull requests. **Not verified:** Yassien's confirmation; the group's choice of the short version.
- **Next:** Yassien confirms his parts; the group chooses the short or long AI statement; after his longer pass, Jamie describes it in one clause; fill in the submitted commit and the reviews of the last pull requests; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** the short or long AI statement (group); Yassien's confirmation.
- **For teammates:** @yassien: your parts now include your 13 November reruns and your review of #15; confirm them, and add the Conclusion. All: the short AI-Assisted Work version saves about half a page: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-034-end-statements/report/final/statements.md
- **Not pushed:** nothing.
