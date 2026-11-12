# Handoff: Yassien Tawfik (`yassien`)

<!--
CURRENT STATE ONLY. Edited only by Yassien's agents, and only on main (CLAUDE.md sections 3 and 7).
History goes in log.md, next to this file.

One section per task Yassien is working on. At every stopping point, rewrite the section
for your task. Delete it only once the task is done (merged). Do not touch other sections:
another of Yassien's sessions may own them. Keep each section to about 15 lines.
When there are no active tasks, the file ends with the line: _No active tasks._

Section format (keep the bold labels so the others can scan for them; Calgary time):

## T-007 · Short task title
_Updated 2026-10-02 15:40 by Claude Code for Yassien · branch `yassien/T-007-short-slug` at `abc1234`_

- **Now:** where the work stands, in one to three lines.
- **Validated:** what was actually run or checked. **Not verified:** what is still assumed.
- **Next:** the exact next action, specific enough for someone to start cold (for a finished task: the pull request link or who opens it, who reviews, then merge, mark done, delete the branch).
- **Blocked / needs a decision:** none, or what and from whom.
- **For teammates:** none, or a note such as "@jamie: the loader now returns one row per stride".
- **Not pushed:** nothing. (Anything listed here exists on one machine only.)
-->

## T-012, T-014 · Midterm Dataset and Responsible Use (§3) and Teamwork and Project Plan (§6), in the group's Word file
_Updated 2026-10-16 02:05 by Claude (Cowork) for Yassien · text in the group's Word file (Anna's SharePoint); no branch, nothing in the repo for these tasks_

- **Now:** both sections are in the shared file with Jamie's fixes and the two consistency fixes (the copy downloaded on 16 October matches). Yassien's three placeholders in the end statements (his AI uses, his log and checks, his Author Contributions) are filled in a copy of that file, sent to Yassien to put into the live file. Feedback on Anna's Methods posted on 16 October.
- **Validated:** a text comparison of the filled copy against the 16 October download (only the AI-Assisted Work and Author Contributions paragraphs change); in a LibreOffice render the body still ends on page 6. **Not verified:** Word's layout of the live file after the paste; a line-by-line check of Table I by Yassien.
- **Next (before Friday 16 October, 11:59 pm):** put the three filled statements into the live file; the AI-Assisted Work text points to this log, so it must stay pushed. After submission, mark T-012 and T-014 done. After the midterm: T-018 (features) and T-019 (random forest).
- **Blocked / needs a decision:** T-030 (evaluation design): Yassien agreed in the chat to keep both, combined plus training on gaitpdb and testing on WearGait-PD; Table III assumes this.
- **For teammates:** @anna: your three end-statement placeholders are still yellow (the shared log placeholder is now "[Anna: your log.]"); Methods feedback is in the group chat. @jamie: Table III gives the WearGait-PD loader to you (T-025); Yassien suggests testing a threshold relative to body weight next to 20 N. Commit `66ae695` reformatted README.md directly on main (markdown tidy-up only: table rules, link brackets, a code-fence language); the pre-commit hook is now on in Yassien's clone, so that is blocked from now on.
- **Not pushed:** nothing.

## T-022 · Second-machine rerun of the run branch, for Jamie (done; waiting for Jamie to read it)
_Updated 2026-11-08 14:40 by Claude (Cowork) for Yassien · no branch; checked `jamie/T-022-cross-cohort-run` at `87b45f5` (detached copy, nothing committed from the run)_

- **Now:** full rerun with both datasets on Windows (44.7 minutes, every step ran): every reported number reproduces, the WearGait-PD outputs included, and only the expected commit line changes in the two `features_summary.txt` files. Windows noise on top of that: 41 files differ only in CRLF line endings, 21 CSVs in the last digits (at most 9.7e-14 absolute, 9.5e-14 relative), 7 PNGs in their bytes but not their pixels. WearGait-PD Version 1 downloaded and checked (both sheets and 553 of 553 task files match). Details in `log.md` (2026-11-08, second entry).
- **Validated:** MD5s of the download and of the copies; the run log; `git diff` with and without `--ignore-cr-at-eol`; every changed CSV cell compared numerically; the PNGs pixel by pixel. **Not verified:** the cause of the last-digit differences (Windows, the CPU, or NumPy 2.5.4 and pandas 3.1.1 against 2.5.3 and 3.0.5).
- **Next:** Jamie reads this; then delete this section.
- **Blocked / needs a decision:** none.
- **For teammates:** @jamie: on Windows the README's "byte for byte" holds for every reported number but not for the files themselves (line endings, last digits in 21 CSVs, PNG bytes); your call whether the README should say so. The full run took 45 minutes on 24 cores here (the README gives 85 to 90 on two).
- **Not pushed:** nothing.
