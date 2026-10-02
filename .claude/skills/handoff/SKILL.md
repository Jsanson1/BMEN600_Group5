---
name: handoff
description: Wrap-up routine for the BMEN 600 Group 5 repo. Commits and pushes the work branch, opens the pull request if the task is finished, then on main updates the task in TASKS.md, rewrites the member's handoff section, appends to their log, and pushes. Use before ending any session in which files changed, when a task is finished or blocked, at natural stopping points in long sessions, and whenever the user says wrap up, hand off, stop, or done for today.
argument-hint: "[optional: finished | blocked <reason> | a note for the handoff]"
---

# /handoff

Note from your human: `$ARGUMENTS` (blank, or still reading `$ARGUMENTS`, means no note). `finished` means the task's work is complete and ready for a pull request; `blocked <reason>` means set the task to `blocked` and record the reason.

Carry out `CLAUDE.md` section 7, steps 1 to 5, exactly as written there. Before step 1, run `ruff check --fix` and then `ruff format` on any Python files or notebooks you changed. End with the three-line message from step 5, naming who should review the pull request if you opened one.
