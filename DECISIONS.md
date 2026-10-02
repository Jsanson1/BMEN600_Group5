# Decisions

What the group has decided, so nobody, human or agent, re-argues it or quietly drifts away from it.

- **Agents:** follow every `Accepted` entry. Treat a `Proposed` entry as the default until the group confirms or changes it. Never edit or delete an entry, and record a new one only when your human says the group made that decision (team contract: decisions by majority).
- **Changing a decision:** append a new entry that names the one it supersedes. After that, and only then, the old entry's `Status` line may be changed to `Superseded by D-xxx`; nothing else in it.
- **Adding an entry:** edit on `main`, append at the bottom with the next free ID, push straight away. If two people add one at the same moment, the second push gets a conflict: keep both entries and renumber yours.

### D-001 · 2026-09-11 · Team working agreements (from our team contract)
Status: Accepted (team contract, signed 2026-09-11)
- Decisions are made as equals, by majority vote. There is no project manager.
- We meet in person after class: Mondays as an optional check-in, Fridays as a deliberate debrief. Google Meet when we cannot meet in person. WhatsApp for messages.
- A meeting log in Google Docs is filled in before each meeting (work done, questions) and after it (decisions, assignments for the coming week).
- Files are shared through this GitHub repository. Each member keeps to their own branches, and ruff checks keep everyone's code in one format.
- Everyone sets internal deadlines ahead of the real ones, so there is time for team review.

### D-002 · 2026-10-02 · How we work in this repository
Status: Proposed by Jamie, who set it up on 2026-10-02. To be confirmed at the next meeting (T-006).
- Work is tracked on the board in `TASKS.md`, and a task is claimed before anyone starts it.
- Two lanes. Coordination files (`TASKS.md`, `DECISIONS.md`, `members/*/handoff.md`, `members/*/log.md`) are committed directly on `main`. Everything else is done on personal branches named `<short>/<task-id>-<slug>` and reaches `main` by pull request.
- Each member has `members/<short>/handoff.md` (current state, one section per active task) and `members/<short>/log.md` (history: work done, CRediT roles, AI use, verification).
- Guardrails: a pre-commit hook (two-lane rule, conflict markers, files over 10 MB, secret files, ruff) and a GitHub Actions workflow (ruff lint and format with a pinned version, the same repository checks, and the two-lane rule for pull requests).
- Python style: `ruff format` with line length 88; lint rules E4, E7, E9, F (ruff's defaults) plus I (import sorting).
- The full procedure for agents is `CLAUDE.md`; for people, `CONTRIBUTING.md`.

### D-003 · 2026-10-02 · Reviewing pull requests
Status: Proposed by Jamie. To be confirmed at the next meeting (T-006).
- Every pull request gets a look from one teammate before it is merged. Their AI can do a first-pass review, but a human approves. The checks must be green, then the author merges.
- Exception: tiny docs or typo fixes may be self-merged; say so in the pull request.
- Why: every member has to be able to explain the data, methods and results in the final presentation, and reviewing each other's work is the cheapest way to share that understanding.
