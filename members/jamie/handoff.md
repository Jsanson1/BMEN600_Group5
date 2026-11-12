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

## T-022 · Model comparison and cross-dataset analyses (#16 merged; the run branch waits for T-017 (#21), #15 and the SVM)
_Updated 2026-11-12 17:40 by Claude (cloud session) for Jamie · `jamie/T-022-model-comparison` merged as #16 (branch still to delete); `jamie/T-022-cross-cohort-run` at `3fb9bc8`_

- **Now:** waiting on three merges before the final rerun: Anna's cleaning (#21; Jamie's first-pass review posted 12 November recommending approval), #15 (fixed on 12 November, waiting for Yassien), and the SVM (T-020, Anna's branch, not yet a pull request). Then merge `main` into the run branch, keep its own `results/weargait_participants.txt` and threshold-check outputs if they conflict (the final versions), rerun everything from a clean checkout with the SVM, update the README's "last checked", and open the run branch's pull request.
- **Validated:** see the log; #21's cleaning code is byte-identical to the run branch's, and its tables give byte-identical final feature tables. **Not verified:** the run time of the cross-cohort analyses with the SVM: a clean rerun of Anna's `run_svm.py` alone (midterm table) is running here to time it; `run_cross_cohort.py` fits it several hundred more times.
- **Next:** (1) Jamie approves #21 on GitHub if satisfied (Files changed, Review changes, Approve), then Anna merges; (2) after #15 and T-020 are merged, the run branch's merge and final rerun; (3) if the SVM makes the rerun too long, the group chooses between Anna's coarser grid (9 values, about 4 times faster) and running it overnight.
- **Blocked / needs a decision:** the three merges above.
- **For teammates:** @anna: #21 reviewed (first pass, recommending approval; two minor notes); the cross-cohort rerun with your SVM will need its run time, which I am measuring. @yassien: thanks for the reruns and reviews.
- **Not pushed:** nothing.

## T-023 · Discussion (draft 3 on its branch, for the group's comments)
_Updated 2026-11-12 17:40 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `755dc3a`_

- **Now:** `report/final/discussion.md`, draft 3 (about 1,860 words). On 12 November, Anna's two suggestions went in: Section D says how to read the combined analysis's AUC (two feature scales a model can tell apart, 0.94, so its 0.63 and 0.67 describe neither one clinic nor a screening population; the per-dataset AUCs 0.71 and 0.73, 0.58 and 0.62, and the cross-cohort test are the interpretable results), and Section E recommends recording gait the same way across clinics, without the contact rule her wording included (we already used one rule for both). `report/final/sources.md` also holds the S9 and S20 checks.
- **Validated:** the new numbers against `crosscohort_summary.txt` (0.628, 0.666; 0.714, 0.726; 0.583, 0.622; 0.940, 0.941); earlier checks as before. **Not verified:** the group has not read draft 3 as a whole.
- **Next:** the group's comments; the SVM when T-020 lands; trim to fit the page budget if the Introduction needs the room; paste into the Word file and open the pull request (with `sources.md`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna: both suggestions are in (`755dc3a`), the second without the contact rule; check that the wording is still yours in spirit. @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (pull request #15: Anna's review answered, a bug found and fixed; waits for Yassien's review)
_Updated 2026-11-12 17:40 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `24037b8`; pull request #15 open (checks green), approved by Anna before the fix_

- **Now:** Anna approved #15 on 12 November with four points; all are done in `24037b8`. Fixing the fourth found a real bug: `check_weargait_threshold.py` never loaded `GeneralEvent`, so the threshold check counted every walkway footfall (19,200), turns and stops included, not only straight walking as documented. On the 12,397 straight-walking footfalls D-012's choice holds: 5% of force level 53.5% within 30 ms against 30 N 53.4% (7 footfalls apart), one to one 87.1% against 85.5%, stance limits -0.128 to +0.092 s against -0.210 to +0.229 s. The report now states the margin, says the limits pool footfalls (median 106 per participant), and stops stride and swing differences before a turn footfall. Methods draft corrected (`d7577be`).
- **Validated:** two new tests, each failing without its fix; 82 tests; the threshold check rerun on the full data (3 minutes); checks green. **Not verified:** a second reviewer of the fix (asked of Yassien on #15).
- **Next:** Yassien reviews `24037b8`; Jamie merges; mark done; delete the branch. The group decides whether to append a correction note to D-012 (proposed wording below); D-012's text says "19,200 straight-walking footfalls", 46.8% and 83.4% against 79.7%, which were all walkway footfalls.
- **Blocked / needs a decision:** Yassien's review; the D-012 correction note.
- **For teammates:** @yassien: please look at `24037b8` on #15 in particular (`read_task` and `results/weargait_threshold_check.txt`). @anna: thanks; your fourth point led to the bug. Proposed `DECISIONS.md` entry, if the group agrees: "D-0xx · Correction to the evidence of D-012 (no change to the decision). The threshold check behind D-012 counted every walkway footfall, turns and stops included, because its script did not load the video labels (fixed in #15, `24037b8`). On the 12,397 straight-walking footfalls 5% of the force level still ranks first (53.5% within 30 ms against 53.4% at 30 N), with more footfalls matched one to one (87.1% against 85.5%) and narrower stance limits (-0.13 to +0.09 s against -0.21 to +0.23 s). The figures quoted in D-012 are superseded by `results/weargait_threshold_check.txt`."
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
_Updated 2026-11-12 17:40 by Claude (cloud session) for Jamie · branch `jamie/T-034-end-statements` at `62945f2`_

- **Now:** `report/final/statements.md`: Anna's checked wording for her AI-use paragraph and her contributions (12 November), plus her review of #15; Yassien's rerun and reviews in his parts, for him to confirm; the reruns and cross-reviews in the verification paragraph; Jamie's review noted, with a placeholder for how he checked. New: a short AI-Assisted Work version (about 220 words, against about 770) proposed for the page limit, keeping the long version for the repository.
- **Validated:** each statement about a member traced to their log, the midterm statements, `DECISIONS.md` or the pull requests. **Not verified:** Yassien's and Jamie's confirmations; the group's choice of the short version.
- **Next:** Jamie writes one or two sentences on how he reviewed the AI work (which code, figures and drafts he read, and what he checked them against); Yassien confirms his parts; the group chooses the short or long AI statement; fill in the submitted commit; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** the short or long AI statement (group); the members' confirmations.
- **For teammates:** @anna: your wording is in, with your review of #15 added to your contributions; check it. @yassien: your parts now include the rerun and the reviews of #16 to #18; confirm and add the Conclusion. All: the short AI-Assisted Work version saves about half a page: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-034-end-statements/report/final/statements.md
- **Not pushed:** nothing.
