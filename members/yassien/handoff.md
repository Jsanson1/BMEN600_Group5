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
_Updated 2026-11-08 11:50 by Claude (Cowork) for Yassien · no branch; checked `jamie/T-022-cross-cohort-run` at `87b45f5` (detached copy, nothing committed from the run)_

- **Now:** PhysioNet-only rerun on Windows (15 minutes): no reported number changed. Not byte for byte: 25 text files differ only in CRLF line endings; 10 CSVs differ in the last digits (at most 9.7e-14 absolute, 9.5e-14 relative); the 5 PNGs differ in bytes, not in pixels. PDFs, every `.txt` and `.md` summary and the `rf_*` outputs are identical. Details and environment in `log.md` (2026-11-08).
- **Validated:** `verify_data.py` (311 match); `git diff` with and without `--ignore-cr-at-eol`; every changed CSV cell compared numerically; the PNGs pixel by pixel. **Not verified:** the cause of the last-digit differences (Windows, the CPU, or NumPy 2.5.4 and pandas 3.1.1 against 2.5.3 and 3.0.5); the full rerun with WearGait-PD (Yassien's local copy is Version 2, not used).
- **Next:** Jamie reads this; then delete this section.
- **Blocked / needs a decision:** none.
- **For teammates:** @jamie: on Windows, the README's "without the WearGait-PD files it changes no committed file at all" holds for every reported number but not byte for byte (line endings, last digits in 10 CSVs, PNG bytes); your call whether the README should say so. A full rerun on a second machine needs someone with the Version 1 WearGait-PD files.
- **Not pushed:** nothing.
