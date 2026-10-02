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

## T-005 · Re-clone outside OneDrive and do the one-time setup
_Updated 2026-10-02 15:30 by Claude (cloud session linked to Jamie's PC) · no branch, coordination only, main at `f9aed56`_

- **Now:** Fresh clone at `C:\Users\jamie\Documents\BMEN600_Group5` with `core.hooksPath=.githooks`, `core.filemode=false` and the git identity `Jamie Sanson <jamie.sanson@ucalgary.ca>` set locally. The old clone under OneDrive\Desktop is untouched (no uncommitted work in it) and can be deleted.
- **Validated:** `git fsck` clean, no stale lock files, all 24 tracked files byte-identical to a fresh clone, hook scripts LF. **Not verified:** `ruff` is not installed on the Windows side yet, so the hook will only warn about Python style until it is.
- **Next:** In the terminal Jamie normally uses Python from, run `python -m pip install -r C:\Users\jamie\Documents\BMEN600_Group5\requirements-dev.txt`, then `ruff --version`; the next `/start` sets this task to `done`.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: the GitHub ruleset on `main` now blocks force-pushes and branch deletion (nothing else); your first `/start` is unaffected.
- **Not pushed:** nothing.
