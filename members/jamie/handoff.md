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

## T-039 · Frame the abstract and Introduction around what the study tests (pull request #24, waiting for review)
_Updated 2026-11-23 13:42 by Claude (cloud session) for Jamie · branch `jamie/T-039-framing`, https://github.com/Jsanson1/BMEN600_Group5/pull/24_

- **Now:** after a slide in class (23 November) contrasted "dataset, models, best accuracy" with "what the field measures wrong, a question that changes a decision, a method that answers it, evidence that survives attack", the abstract and the Introduction's last paragraph now lead with what the study tests. The abstract says that gait classifiers for PD are mostly tested within one database, which cannot show whether they will work in another clinic, and it ends with what follows for validation. The Introduction's question is whether performance within one database tells a clinic that a model will work on its own patients, device and protocol. No result changes.
- **Validated:** abstract 250 words; every number in the changed text is already in the outputs and the paper; the paper rebuilt from the branch passes `check_submission.py` (11 pages, References from page 10). **Not verified:** the group's agreement with the framing; the layout in Word.
- **Next:** Anna and Yassien review #24; merge; set T-039 to done; rebuild the final PDF with the new commit ID (T-037).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: please read the new abstract and the last paragraph of the Introduction in #24.
- **Not pushed:** nothing.

## T-037 · Assemble and submit the final paper (merged; submission held for the group's review)
_Updated 2026-11-18 11:05 by Claude (cloud session) for Jamie · merged into main as `4a660d6` (#23)_

- **Now:** the paper is complete and merged. The final PDF was built from a fresh clone of `4a660d6` in IEEE's conference template, with that commit ID written in (`scripts/assemble_paper.py --template conference-template-letter.docx --commit 4a660d6`, then `renumber_docx_citations.py`, LibreOffice and `check_submission.py`, which reports "ready to submit"): 11 pages, the text ending on page 10, then the References. Jamie has the PDF and the Word file from the session. The final rerun from a clean clone of `02e69c9` rewrote 83 of the 106 committed outputs byte for byte (only the commit line of the two `features_summary.txt` differs), and the paper's version changes no analysis code.
- **Validated:** `check_submission.py` on the final build; main's checks green at `4a660d6`; every result number in the paper found in an output by script and traced by an independent review; 150 tests. **Not verified:** the layout if the Word file is saved from Word (the PDF uses Liberation Serif, LibreOffice's metric twin of Times New Roman); the group has not read the final paper.
- **Next:** on 18 November Jamie said the group will hold off on submitting until it has reviewed the paper further; the in-class peer review (Team Discussion 10, Mon 23 November) is the natural point for it. Then Jamie uploads `BMEN600_Group5_Final_Paper.pdf` to D2L by Fri 4 December, 11:59 p.m.; any change before then goes through a new pull request and a rebuild with the new commit ID; then set T-037 to done. Delete the merged branches on GitHub by hand (the session cannot; checked 18 November that none has a commit main lacks): jamie/T-008-readme-front-page, T-009-background-gap, T-010-preliminary-results, T-016-cowork-onboarding, T-017-d012-threshold, T-018-feature-extraction, T-018-readme-run-all, T-019-random-forest, T-021-logistic-regression, T-022-cross-cohort-run, T-022-model-comparison, T-023-discussion, T-025-weargait-access, T-026-data-quality, T-027-unit-tests, T-028-assembly-helper, T-031-midterm-snapshots, T-032-results-section, T-033-methods-section, T-034-end-statements, T-035-introduction, T-037-paper-assembly (all `jamie/`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: please read the final paper (the PDF Jamie shares) and your own lines in `report/final/statements.md` and `report/final/ai_use.md`. @yassien: the Conclusion was your task and was drafted by Jamie's AI (D-016); change anything you like through a pull request. @anna: #21 and your SVM are merged, so T-017 and T-020 can be set to done.
- **Not pushed:** nothing.

## T-038 · Final presentation (deck drafted, D-016)
_Updated 2026-11-16 18:27 by Claude (cloud session) for Jamie · a Slides artifact in Jamie's Claude account, private until Jamie shares it; no branch_

- **Now:** a nine-slide deck for the 5-minute talk with speaker notes, its title matching the paper's: the problem, question and datasets (Anna, about 1 min 45 s); the workflow with the evaluation-design figure and the result within gaitpdb (Jamie, about 1 min 25 s); the cross-cohort result with Figure 5, why it does not transfer, and what it means (Yassien, about 1 min 50 s).
- **Validated:** every number against the outputs; each slide rendered and looked at. **Not verified:** the timing spoken aloud; the group has not seen it.
- **Next:** Jamie sent Anna and Yassien the deck as a downloaded PowerPoint on 17 November (a copy: a later change to the deck means sending it again); each rehearses their part and changes the split or wording as they like; set to done after the talk.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: your parts are in the speaker notes of the PowerPoint Jamie sent (Anna slides 1 to 4, Jamie 5 and 6, Yassien 7 to 9).
- **Not pushed:** nothing (the deck lives in the artifact).
