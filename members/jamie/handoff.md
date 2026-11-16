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

## T-037 · Assemble the final paper (draft pull request #23; final rerun running)
_Updated 2026-11-16 15:20 by Claude (cloud session) for Jamie · branch `jamie/T-037-paper-assembly` at `e2ecfed`; main at `02e69c9`_

- **Now:** #22 is merged into main (`02e69c9`) after an independent read-only review (no code or statistical error; four wording mismatches, all fixed: `6cdc106` on the run branch, `264a886` here), and main is merged into this branch (`ead07df`). The paper is complete in draft (D-016): title, abstract and keywords, Introduction, Methods, Results, Discussion, Conclusion and the three statements. Without the IEEE template, the assembly now numbers the references itself (`4ee45f0`). About 190 words were cut for the page limit (`e2ecfed`); in LibreOffice's layout the References start three quarters of the way down page 10. Running: the final clean rerun of every step from a fresh clone of `02e69c9` (in two-hour parts, as on 13 November), and an independent review of the whole assembled paper.
- **Validated:** 146 tests pass on this branch, ruff clean; the threshold wording against `crosscohort.py` and `bd4c61f`; the positive predictive values against `model_comparison.txt` and `crosscohort_summary.txt`. **Not verified:** the layout in Word; the group has not read the abstract, the Conclusion or the cuts.
- **Next:** take in the paper review's confirmed findings; when the rerun ends, compare its outputs with the committed ones and write the Methods' reproducibility sentence from it; fill the commit ID at assembly; a README section on how the paper is assembled; undraft and merge #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23); build the final PDF from the merged commit and run `check_submission.py`; PDF on D2L by a human.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: the whole paper is in #23; please read your own lines in `report/final/statements.md` and `report/final/ai_use.md`, now written from your logs and GitHub reviews, and say if anything is wrong. @anna: #21 was merged on 13 November and your SVM reached main with #22 today, so T-017 and T-020 can be set to done when you next start.
- **Not pushed:** nothing.

## T-036, T-024 · Title, abstract, keywords and Conclusion (drafted for the group, D-016)
_Updated 2026-11-16 15:20 by Claude (cloud session) for Jamie · branch `jamie/T-037-paper-assembly` at `4ee45f0`_

- **Now:** `report/final/abstract.md` (title, a 250-word abstract, keywords) and `report/final/conclusion.md` (about 275 words), drafted by Jamie's AI at the team's request; they summarise the other sections and add nothing to them, and each ends with a table of where every number or statement comes from.
- **Validated:** every number against `results/model_comparison.txt` and `results/crosscohort_summary.txt`; every statement against the Results and Discussion. **Not verified:** the group, and Yassien for his Conclusion, has not read them.
- **Next:** the group's comments on #23; merged with #23, then done.
- **Blocked / needs a decision:** none.
- **For teammates:** @yassien: the Conclusion was your task; change anything you like (a comment on #23, or your own branch from `jamie/T-037-paper-assembly`).
- **Not pushed:** nothing.

## T-038 · Final presentation (deck drafted, D-016)
_Updated 2026-11-16 15:20 by Claude (cloud session) for Jamie · a Slides artifact in Jamie's Claude account, private until Jamie shares it; no branch_

- **Now:** a nine-slide deck for the 5-minute talk, with speaker notes, drafted by Jamie's AI: the problem, question and datasets (Anna, about 1 min 45 s); the workflow with the evaluation-design figure and the result within gaitpdb (Jamie, about 1 min 25 s); the cross-cohort result with Figure 5, why it does not transfer, and what it means (Yassien, about 1 min 50 s).
- **Validated:** every number against the outputs; each slide rendered and looked at. **Not verified:** the timing spoken aloud; the group has not seen it.
- **Next:** Jamie shares the deck with Anna and Yassien from its Share menu; each rehearses their part and changes the split or wording as they like.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: your parts and speaker notes are in the deck once Jamie shares it.
- **Not pushed:** nothing (the deck lives in the artifact).

## T-023, T-032, T-033, T-034, T-035 · Section drafts of the final paper (in draft pull request #23)
_Updated 2026-11-16 15:20 by Claude (cloud session) for Jamie · edited on `jamie/T-037-paper-assembly` since 16 November; the five task branches are no longer updated_

- **Now:** Discussion (T-023), Results (T-032), Methods (T-033), statements (T-034, draft 5) and Introduction (T-035) are all in #23. Today: the threshold carried to WearGait-PD is described as the code sets it (one cross-validation repeat; Methods II-F, Results III-B) and the Results give the positive predictive values (`264a886`); the statements' notes are resolved from the members' logs and GitHub reviews (`26b88ab`); about 190 words of repetition cut (`e2ecfed`).
- **Validated:** each change against the code or the output files named in its commit. **Not verified:** the group has not read the drafts.
- **Next:** merged with #23 (https://github.com/Jsanson1/BMEN600_Group5/pull/23); then set the five tasks to done and delete their branches (on GitHub, by hand: the session cannot delete branches).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comment inline on #23.
- **Not pushed:** nothing.
