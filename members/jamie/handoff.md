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

## T-022 · Model comparison and cross-dataset analyses (pull request #22 open, for review)
_Updated 2026-11-13 17:45 by Claude (cloud session) for Jamie · `jamie/T-022-cross-cohort-run` at `ae2542e`; `jamie/T-022-model-comparison` merged as #16 (branch still to delete)_

- **Now:** the final rerun with Anna's SVM is done and committed (`56364d4`), and pull request #22 is open: https://github.com/Jsanson1/BMEN600_Group5/pull/22 (checks green). It ran from a fresh clone of `79228fa` in three parts (one command in this cloud session stops after 2 hours; a container restart stopped the second part, and the third resumed from the kept results): about 3.4 hours of computing. Figure 5's legend now goes on two lines with four entries (`e30209a`); the README has the SVM in its Results and the record of this rerun (`56364d4`, `ae2542e`). The SVM tells the same story: 0.78 and 0.72 within gaitpdb, 0.53 (0.45 to 0.62) across cohorts, 0.63 combined. With 13 paired tests the Holm-adjusted p values rose (0.43 to 0.80, 0.47 to 0.86); none significant, before or now.
- **Validated:** every output of the logistic regression and random forest identical to the committed one, cell for cell in every CSV; the other changed lines are the SVM's additions, the commit line in the two `features_summary.txt` files and #17's escaped `|` in `fixed_20N/feature_dictionary.md`; Figures 3 and 5 looked at; 139 tests; ruff clean. **Not verified:** the SVM's outputs by a second run (asked of Yassien in #22: one `python scripts/run_all.py` in one go); first code review of `run_cross_cohort.py`, `check_weargait_signal.py` and the figure and table scripts (about 1,650 lines with their tests).
- **Next:** Anna opens her SVM pull request and it is merged first (#22 contains her two commits); review of #22 (Yassien or Anna); merge; mark T-022 done; delete the branches.
- **Blocked / needs a decision:** none (the correction note to D-012 is now D-014, appended on 16 November after Jamie confirmed the group agreed).
- **For teammates:** @anna: please open your SVM pull request (reviewer Jamie or Yassien) so it can be merged before #22; `svm.py` cites Platt under the preprint's title and 1999, while the published chapter is "Probabilities for SV machines", MIT Press, 2000, pp. 61–74, doi: 10.7551/mitpress/1113.003.0008 (S25 in `report/final/sources.md`). @yassien: #22 asks for one uninterrupted `python scripts/run_all.py` on your PC; the SVM's probabilities may differ from this rerun in about the fifth decimal (most likely the stopping tolerance of the logistic curve fitted to its distances, not tested), the rest should match to the last digits.
- **Not pushed:** nothing.

## T-023 · Discussion (in draft pull request #23, for the group's comments)
_Updated 2026-11-16 14:31 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion`, merged into `jamie/T-037-paper-assembly` for #23_

- **Now:** `report/final/discussion.md`, draft 3 (about 1,900 words), with the SVM (13 November) and the ledger `report/final/sources.md` (S21 to S32).
- **Validated:** every number in the prose found in the output files at `56364d4`, except S1's 80.6%. **Not verified:** the group has not read it.
- **Next:** the group's comments on #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23, a draft pull request that holds all five section drafts and the assembly script; merge after #22); changes go on this task's branch and are merged again into `jamie/T-037-paper-assembly`, or straight onto that branch; once #23 is merged, mark done and delete the branch.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comment inline on #23.
- **Not pushed:** nothing.

## T-032 · Results section of the final paper (in draft pull request #23, for the group's comments)
_Updated 2026-11-16 14:31 by Claude (cloud session) for Jamie · branch `jamie/T-032-results-section`, merged into `jamie/T-037-paper-assembly` for #23_

- **Now:** `report/final/results.md`, draft 4 (about 1,700 words), with the SVM from the final rerun and the captions of Tables I and II and of the paper's two figures (the repository's Figs. 4 and 5).
- **Validated:** every number in the prose found in the output files at `56364d4`, except two percentages traced by hand. **Not verified:** the group has not read it.
- **Next:** the group's comments on #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23, a draft pull request that holds all five section drafts and the assembly script; merge after #22); changes go on this task's branch and are merged again into `jamie/T-037-paper-assembly`, or straight onto that branch; once #23 is merged, mark done and delete the branch.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comment inline on #23.
- **Not pushed:** nothing.

## T-033 · Dataset and Methods section of the final paper (in draft pull request #23, for the group's comments)
_Updated 2026-11-16 14:31 by Claude (cloud session) for Jamie · branch `jamie/T-033-methods-section`, merged into `jamie/T-037-paper-assembly` for #23_

- **Now:** `report/final/methods.md`, draft 2 (about 2,350 words). On 16 November: about 85 words cut; no figure cited (the evaluation-design figure goes to the presentation, as the group agreed through Jamie); the Synapse Pledge and Section G's AI sentence confirmed by Jamie.
- **Validated:** every number against the outputs and code; the SVM's settings against `svm.py`. **Not verified:** the group has not read it.
- **Next:** the group's comments on #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23, a draft pull request that holds all five section drafts and the assembly script; merge after #22); changes go on this task's branch and are merged again into `jamie/T-037-paper-assembly`, or straight onto that branch; once #23 is merged, mark done and delete the branch.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comment inline on #23.
- **Not pushed:** nothing.

## T-034 · End statements of the final paper (in draft pull request #23, for the group's comments)
_Updated 2026-11-16 14:31 by Claude (cloud session) for Jamie · branch `jamie/T-034-end-statements`, merged into `jamie/T-037-paper-assembly` for #23_

- **Now:** `report/final/statements.md`, draft 4: the short AI statement (D-015) pointing to `report/final/ai_use.md`; Jamie's contributions confirmed; Anna's and Yassien's parts with their bracketed notes for them to resolve.
- **Validated:** each statement about a member traced to their log, `DECISIONS.md` or the pull requests; the short statement restored word for word after the error in `a286bfe` (see the log). **Not verified:** the group has not read it.
- **Next:** the group's comments on #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23, a draft pull request that holds all five section drafts and the assembly script; merge after #22); changes go on this task's branch and are merged again into `jamie/T-037-paper-assembly`, or straight onto that branch; once #23 is merged, mark done and delete the branch.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comment inline on #23.
- **Not pushed:** nothing.

## T-035 · Introduction of the final paper (in draft pull request #23, for the group's comments)
_Updated 2026-11-16 14:31 by Claude (cloud session) for Jamie · branch `jamie/T-035-introduction`, merged into `jamie/T-037-paper-assembly` for #23_

- **Now:** `report/final/introduction.md`, draft 1 (about 1,350 words), built from Anna's midterm Introduction and Jamie's midterm Background, with seven new checked sources (S26 to S32).
- **Validated:** each new source against Crossref and its text (four from the abstract only); the closing numbers against the outputs at `56364d4`. **Not verified:** the group has not read it.
- **Next:** the group's comments on #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23, a draft pull request that holds all five section drafts and the assembly script; merge after #22); changes go on this task's branch and are merged again into `jamie/T-037-paper-assembly`, or straight onto that branch; once #23 is merged, mark done and delete the branch.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comment inline on #23.
- **Not pushed:** nothing.

## T-037 · Assemble the final paper (draft pull request #23 open; abstract and conclusion to come)
_Updated 2026-11-16 14:31 by Claude (cloud session) for Jamie · branch `jamie/T-037-paper-assembly` at `26e2420`_

- **Now:** claimed for Jamie on 16 November as lead of the assembly; the submission itself stays everyone's. `scripts/assemble_paper.py` (7 tests; 110 pass on the branch) puts the drafts in `report/final/` into one .docx in the IEEE conference layout for the midterm's `renumber_docx_citations.py` and `check_submission.py`; with `--template` it fills the IEEE Word template (not yet in hand). The five section drafts are merged into this branch, and draft pull request #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23) holds them all for the group's comments; it is to be merged after #22. Second full draft generated and sent to Jamie.
- **Decided on 16 November (Jamie, approving for the group):** the evaluation-design figure stays out of the paper and goes to the presentation; page 1 counts toward the 10 pages until the meaning of "title page" is confirmed; the IEEE template's "Abstract—" and "Keywords—" are kept; the task split: abstract to Yassien (with his Conclusion), the presentation led by Anna, the assembly by Jamie (Anna and Yassien still to accept).
- **Page budget:** in the second draft (LibreOffice layout, outputs of #22) the References start a fifth of the way down page 10, so the text takes about 9.2 pages; the abstract and conclusion add about half a page, leaving about 0.3 of a page. To check in Word.
- **Validated:** citation labels all in the ledgers and numbered in order of first appearance; figures and tables placed after their first mention; `check_submission.py` lists only the expected open items. **Not verified:** the layout in Word or the IEEE template.
- **Next:** the group's comments on #23; Yassien's abstract and conclusion (`report/final/abstract.md` with a heading `## Abstract`, `report/final/conclusion.md` with `## Conclusion`, the headings the script looks for); the IEEE Word template from the midterm's file; the final pass in Word; the commit ID; a final clean rerun at that commit; PDF on D2L.
- **Blocked / needs a decision:** Anna's and Yassien's acceptance of the task split.
- **For teammates:** @yassien: if you take the abstract, put it in `report/final/abstract.md` under `## Abstract`, and the Conclusion in `report/final/conclusion.md` under `## Conclusion`, on your own branch; the script picks them up. @anna: if you lead the presentation, `figures/figure2_evaluation_design.png` (on #22) is the evaluation-design figure the paper no longer uses.
- **Not pushed:** nothing.
