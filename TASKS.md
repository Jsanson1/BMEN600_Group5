# Tasks and deadlines

How this file works (full rules: CLAUDE.md sections 5 and 7):

- Edit it only on `main`, and push straight away so everyone sees the change.
- To claim a task, edit only its metadata line: your short name as `owner`, `status: doing`, your branch name, today's date. If your push is rejected, pull and check that nobody claimed it first.
- Statuses: `todo`, `doing`, `review` (finished, waiting for a pull request review), `done` (merged), `blocked` (reason in the owner's handoff), `decide` (a group decision; agents never start these).
- Task IDs are permanent. New tasks go at the end of the board with the next free number. Keep one blank line between tasks: it lets two people edit different tasks at the same time without a merge conflict.

## Deadlines

| When | What |
|---|---|
| Fri 2026-10-09, in class | Team Discussion 5: analysis workflow and GitHub repository |
| **Fri 2026-10-16, 11:59 pm** | **Midterm Research Plan** on D2L: one PDF, at most 6 pages excluding title page and references, including the repo link. 24 h grace period, then 20% per day. |
| Mon 2026-10-19 | Midterm ITP teamwork evaluation |
| Fri 2026-10-23, 10-30 and 11-06, in class | Team Discussions 6 to 8: working data analysis; results and evidence; data validation |
| 2026-11-09 to 11-13 | Reading week |
| Fri 2026-11-20 and Mon 11-23, in class | Team Discussions 9 and 10: oral communication and drafting; peer review |
| Mon 2026-11-30 or Fri 12-04 | Final presentation: 5 minutes plus about 5 minutes of questions; everyone speaks for at least 1 minute |
| **Fri 2026-12-04, 11:59 pm** | **Final Project** on D2L: one PDF, at most 10 pages excluding title page and references, including the repo link and the commit ID of the graded version. Final ITP evaluation the same day. |

Team contract: set internal due dates early enough for a team review before every real deadline. Put them in each task's `due` field. The group's higher-level project plan is the Google Sheet linked from README.md; this board is the day-to-day work list that the agents read.

## Board

### T-001 · Set up the collaboration system (board, handoffs, logs, agent protocol, checks)
owner: jamie | status: done | branch: bootstrap commit on main | due: 2026-10-02 | updated: 2026-10-02

### T-002 · Decide the final topic, research question and dataset
owner: group | status: decide | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-003 · One-time repo setup and a first `/start` (CONTRIBUTING.md), then mark this done
owner: anna | status: todo | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-004 · One-time repo setup and a first `/start` (CONTRIBUTING.md), then mark this done
owner: yassien | status: todo | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-005 · Re-clone the repo outside OneDrive (CONTRIBUTING.md step 1; the old clone has no uncommitted work) and do the one-time setup
owner: jamie | status: doing | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-006 · Confirm the repo workflow (D-002) and the pull request review rule (D-003)
owner: group | status: decide | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-007 · Set up the project structure: folders, requirements.txt, data/raw/README.md with the download steps (after T-002)
owner: - | status: todo | branch: - | due: 2026-10-09 | updated: 2026-10-02

### T-008 · README front page: research question, dataset access, file map, how to run (graded; after T-007)
owner: - | status: todo | branch: - | due: 2026-10-12 | updated: 2026-10-02
