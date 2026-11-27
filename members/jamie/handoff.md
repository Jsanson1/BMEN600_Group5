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

## T-037 · Assemble and submit the final paper (merged; submission held for the group's review)
_Updated 2026-11-23 13:46 by Claude (cloud session) for Jamie · paper at main `735cc85` (#23, #24)_

- **Now:** the paper is complete and merged, with the reframed abstract and Introduction (T-039, #24, D-017). The final PDF and Word file were rebuilt on 23 November from a fresh clone of `735cc85` in IEEE's conference template, with that commit ID written in (`scripts/assemble_paper.py --template conference-template-letter.docx --commit 735cc85`, then `renumber_docx_citations.py`, LibreOffice and `check_submission.py`, which reports "ready to submit"): 11 pages, the References from page 10; Jamie has both files. The analysis code is unchanged since the final rerun at `02e69c9`.
- **Validated:** `check_submission.py` on the final build; main's checks green at `4a660d6`; every result number in the paper found in an output by script and traced by an independent review; 150 tests. **Not verified:** the layout if the Word file is saved from Word (the PDF uses Liberation Serif, LibreOffice's metric twin of Times New Roman); the group has not read the final paper.
- **Next:** on 18 November Jamie said the group will hold off on submitting until it has reviewed the paper further; the in-class peer review (Team Discussion 10, Mon 23 November) is the natural point for it. Then Jamie uploads `BMEN600_Group5_Final_Paper.pdf` to D2L by Fri 4 December, 11:59 p.m.; any change before then goes through a new pull request and a rebuild with the new commit ID; then set T-037 to done. Delete the merged branches on GitHub by hand (the session cannot; checked 18 November that none has a commit main lacks): jamie/T-008-readme-front-page, T-009-background-gap, T-010-preliminary-results, T-016-cowork-onboarding, T-017-d012-threshold, T-018-feature-extraction, T-018-readme-run-all, T-019-random-forest, T-021-logistic-regression, T-022-cross-cohort-run, T-022-model-comparison, T-023-discussion, T-025-weargait-access, T-026-data-quality, T-027-unit-tests, T-028-assembly-helper, T-031-midterm-snapshots, T-032-results-section, T-033-methods-section, T-034-end-statements, T-035-introduction, T-037-paper-assembly, T-039-framing (all `jamie/`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: please read the final paper (the PDF Jamie shares) and your own lines in `report/final/statements.md` and `report/final/ai_use.md`. @yassien: the Conclusion was your task and was drafted by Jamie's AI (D-016); change anything you like through a pull request. @anna: #21 and your SVM are merged, so T-017 and T-020 can be set to done.
- **Not pushed:** nothing.

## T-038 · Final presentation (in Google Slides, condensed and rescripted 27 November)
_Updated 2026-11-27 13:51 by Claude (cloud session) for Jamie · Google Slides deck "BMEN 600 Group 5 Final Presentation" in Jamie's Drive, shared with Anna and Yassien; no branch_

- **Now:** the deck moved to Google Slides, where Anna restyled it and cut it to nine slides. On 27 November, after the teaching team said every slide had too many words, Jamie's session cut the on-slide text (about 650 words across the deck to about 420, mostly on slides 5 to 9) with find-and-replace, so Anna's formatting is untouched; it also corrected two slide-2 labels whose shortening had changed their meaning, and swapped the slide-2 source Rizzo for Tolosa (the 80.6% card is gone). The speaker notes now hold a new script of about 640 words, about 4:40 at a steady pace: Jamie slides 1, 5, 6 (about 1:25), Anna 2 to 4 (about 1:40), Yassien 7 to 9 (about 1:35). Jamie has it as printable flash cards with Q&A and contribution cards (Word file, not in the repository).
- **Validated:** every number in the script and on the edited slides against the paper's text and Table II; the deck re-exported after the edits, its notes identical to the script. **Not verified:** the timing spoken aloud; Anna and Yassien have not yet seen the new notes; Anna's old note that turn removal took more data from controls, who walk faster, is in neither the paper nor the repository and was left out.
- **Next:** each rehearses with a timer (over 5:00 means speaking slower than about 150 words a minute); the talk is on 30 November; set to done after it.
- **Blocked / needs a decision:** whether the 1-minute (brief) or 2-minute (course-introduction slide) speaking minimum applies; three people cannot each speak 2 minutes in 5.
- **For teammates:** @anna @yassien: your new lines are in the speaker notes of the Google Slides deck; the PowerPoint from 17 November is out of date.
- **Not pushed:** nothing (the deck lives in Google Slides).
