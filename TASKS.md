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
owner: group | status: done | branch: - | due: 2026-10-05 | updated: 2026-10-05

### T-003 · One-time repo setup and a first `/start` (CONTRIBUTING.md), then mark this done
owner: anna | status: todo | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-004 · One-time repo setup and a first `/start` (CONTRIBUTING.md), then mark this done
owner: yassien | status: todo | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-005 · Re-clone the repo outside OneDrive (CONTRIBUTING.md step 1; the old clone has no uncommitted work) and do the one-time setup
owner: jamie | status: done | branch: - | due: 2026-10-05 | updated: 2026-10-05

### T-006 · Confirm the repo workflow (D-002) and the pull request review rule (D-003)
owner: group | status: decide | branch: - | due: 2026-10-05 | updated: 2026-10-02

### T-007 · Set up the project structure: folders, requirements.txt, data/raw/README.md with the download steps (after T-002)
owner: jamie | status: review | branch: jamie/T-007-project-structure | due: 2026-10-09 | updated: 2026-10-05

### T-008 · README front page: research question, dataset access, file map, how to run (graded; after T-007)
owner: jamie | status: review | branch: jamie/T-008-readme-front-page | due: 2026-10-12 | updated: 2026-10-06

### T-009 · Midterm §2 Background and Research Gap: literature review, existing ML approaches and their limits, the gap (lead jamie, reviewer anna; mirrors the Project Timeline sheet)
owner: jamie | status: review | branch: jamie/T-009-background-gap | due: 2026-10-09 | updated: 2026-10-05

### T-010 · Midterm §5 Preliminary Results: at least one team-made table or figure from the dataset, what it shows, what it changes (lead jamie, reviewer anna)
owner: jamie | status: review | branch: jamie/T-010-preliminary-results | due: 2026-10-09 | updated: 2026-10-05

### T-011 · Midterm §1 Introduction and Motivation: the research question and its rationale (lead anna, reviewer jamie)
owner: anna | status: todo | branch: - | due: 2026-10-09 | updated: 2026-10-05

### T-012 · Midterm §3 Dataset and Responsible Use: source, size, participants, recording type, licence, consent, privacy, bias (lead yassien, reviewer jamie)
owner: yassien | status: todo | branch: - | due: 2026-10-09 | updated: 2026-10-05

### T-013 · Midterm §4 Proposed Methods and Evaluation: pipeline, metrics, participant-level splits and cross-validation, choice of models (lead anna, reviewers all)
owner: anna | status: todo | branch: - | due: 2026-10-09 | updated: 2026-10-05

### T-014 · Midterm §6 Teamwork and Project Plan: milestones, owners, check-in cadence, version control practices (lead yassien, reviewers all)
owner: yassien | status: todo | branch: - | due: 2026-10-09 | updated: 2026-10-05

### T-015 · Midterm: review and revise all sections, assemble the PDF (max 6 pages + references), add the repo link, submit on D2L (all)
owner: group | status: todo | branch: - | due: 2026-10-16 | updated: 2026-10-05

### T-016 · Onboarding for teammates who use the Claude desktop app and no terminal: GitHub Desktop steps in CONTRIBUTING.md, plain-language paste-in message, git lock-file note in CLAUDE.md
owner: jamie | status: done | branch: jamie/T-016-cowork-onboarding | due: 2026-10-06 | updated: 2026-10-05

### T-017 · Project: pre-processing pipeline for the gait records: cleaning rules, missing values, outlier strides, documentation of every step (lead anna, collaborators yassien, jamie; mirrors the Project Timeline sheet; builds on src/gaitpdb/events.py from T-010)
owner: anna | status: todo | branch: - | due: - | updated: 2026-10-05

### T-018 · Project: spatiotemporal feature extraction: define the feature set, implement it, produce the feature table and a feature dictionary (lead yassien, collaborators anna, jamie; builds on src/gaitpdb/features.py from T-010)
owner: yassien | status: todo | branch: - | due: - | updated: 2026-10-05

### T-019 · Project: random forest model: train, tune, report performance and feature importances under the agreed evaluation (lead yassien)
owner: yassien | status: todo | branch: - | due: - | updated: 2026-10-05

### T-020 · Project: support vector machine: scaling, kernel and regularisation choice, train, evaluate, report (lead anna)
owner: anna | status: todo | branch: - | due: - | updated: 2026-10-05

### T-021 · Project: logistic regression: fit, check assumptions, report coefficients and performance (lead jamie)
owner: jamie | status: doing | branch: jamie/T-021-logistic-regression | due: 2026-10-23 | updated: 2026-10-06

### T-022 · Project: compare the three models: shared splits and metrics, comparison tables and figures, statistical comparison where appropriate (lead jamie, collaborators all; after T-019, T-020, T-021)
owner: jamie | status: doing | branch: jamie/T-021-logistic-regression | due: 2026-11-06 | updated: 2026-10-06

### T-023 · Project: discussion: interpret the results against the research question and the background, limitations, ethics, future work (lead jamie, collaborators all; after T-022)
owner: jamie | status: todo | branch: - | due: - | updated: 2026-10-05

### T-024 · Project: conclusion: key findings, direct answer to the research question, next steps (lead yassien, collaborators all; after T-023)
owner: yassien | status: todo | branch: - | due: - | updated: 2026-10-05

### T-025 · Project: WearGait-PD external test: Synapse account and data-use terms, loader for its insole or walkway timings, run the final models on it (owner to be agreed; after T-022)
owner: - | status: todo | branch: - | due: - | updated: 2026-10-05

### T-026 · Data-quality report on the PhysioNet records for §3: missing demographics, recording lengths, pauses and gaps in the force signals, class and study balance (Jamie's reviewer part of T-012 per the Project Timeline sheet; after T-010)
owner: jamie | status: review | branch: jamie/T-026-data-quality | due: 2026-10-08 | updated: 2026-10-06
