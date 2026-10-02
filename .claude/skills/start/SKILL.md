---
name: start
description: Start-of-session routine for the BMEN 600 Group 5 repo. Syncs main, reads the task board, the decisions and every member's handoff, and reports status to the user; given a task ID (/start T-007) it also claims that task and creates the work branch. Use at the beginning of every session in this repo, and whenever the user asks what's going on, what to work on next, or to pick up or claim a task.
argument-hint: "[task ID to claim, e.g. T-007]"
---

# /start

Task ID given: `$ARGUMENTS` (if that is blank or still reads `$ARGUMENTS`, no task was given).

1. Carry out `CLAUDE.md` section 4, steps 1 to 4, exactly as written there.
2. If a task ID was given: check that it can be claimed (section 5, first paragraph). If it can, claim it and create the branch, following section 5 step by step, including what to do when the push is rejected. If it cannot, do not claim anything; say why in the report.
3. Give the report from section 4, step 5, then wait for your human unless they already gave you work.
