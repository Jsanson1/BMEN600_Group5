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

### D-004 · 2026-10-02 · Project, models and section leads for the midterm
Status: Accepted (group decision at the Friday 2 October meeting, reported by Jamie on 5 October)
- Candidate Project 1 is the project: detecting Parkinson's disease from gait recordings.
- Three models, one owner each: random forest (Yassien), support vector machine (Anna), regression (Jamie). The earlier "four models" wording is superseded.
- Section leads and reviewers for the Midterm Research Plan are as in the Project Timeline sheet (linked from README.md) and mirrored on the board as T-009 to T-015.
- The writing happens in the shared Google Doc "BMEN 600 Group 5 – Midterm Research Plan (draft)"; the repository holds code, results, figures and the verified-sources ledger (`report/midterm/sources.md`).

### D-005 · 2026-10-05 · Which dataset the midterm analyses use
Status: Superseded by D-007
- All midterm analyses use the PhysioNet "Gait in Parkinson's Disease" database v1.0.0 (open access, no account, downloaded). One independent case is one participant; participants contribute 1 to 7 recordings and are never split across training and test folds.
- WearGait-PD (Synapse, account required) is named in the plan as an external test set "if time allows". Nobody starts on it before the midterm is submitted.
- The README's "GaitPDB" link points at a Nature Health comment about PhysioNet, not at the dataset; it is corrected under T-008.

### D-006 · 2026-10-13 · Participants under 50 are excluded from both datasets
Status: Accepted (group decision, reported by Jamie on 13 October)
- Every analysis uses only participants aged 50 or over, by the age in each dataset's demographic table, in the PhysioNet database and in WearGait-PD. The plan's intended use is screening people over 50 (Midterm Research Plan, section 1).
- PhysioNet: this removes JuPt25, SiPt24 and SiCo12 (aged 45, 36 and 37). The analysed cohort is the 162 participants aged 50 or over who have a usual-walk recording: 91 with PD and 71 controls. WearGait-PD: the counts are checked once its participant table is downloaded.
- The rule lives in one place in the shared code (T-029), so every model, table and figure uses the same participants.

### D-007 · 2026-10-16 · Evaluation design: the two datasets combined, plus a cross-cohort test (supersedes D-005)
Status: Accepted (proposed by Jamie in the group chat on 15 October, agreed by Yassien on 16 October; recorded by Jamie on 16 October)
- Main analysis: the PhysioNet "Gait in Parkinson's Disease" database v1.0.0 and WearGait-PD combined, with the models compared under the shared participant-grouped, stratified cross-validation (`src/gaitpdb/evaluation.py`).
- Cross-cohort test: models trained on PhysioNet and tested on WearGait-PD. The plan's title and research gap rest on this test.
- Also in the plan (Midterm Research Plan, Table III): within PhysioNet, each of its three sub-studies held out in turn, and a check of whether a model can tell which dataset a recording came from.
- Kept from D-005: one independent case is one participant, and a participant's recordings are never split between training and test folds.
- Supersedes D-005, under which WearGait-PD was an optional external test set and every midterm analysis used PhysioNet only. The midterm's preliminary results still use PhysioNet only.

### D-008 · 2026-10-25 · Turns in gaitpdb are found from walking-path timing
Status: Accepted (group decision, reported by Anna on 25 October)
- After comparing several algorithms (i.e. a frequency-based, a derivative-based, and a timing-based approach) to detect turns, timing-based was selected to avoid filtering out jitters in stride duration that may be characteristic of PD gait, and to avoid misclassifying a more variable stride duration as a turn.
- Thus, each sub-study of gaitpdb will estimate the expected turn location based on the distance of the walkway within its corresponding methodology, as well as the participant's average velocity.
- The strides immediately preceding and following a turn will also be removed.

### D-009 · 2026-10-23 · Si walk 01 is analysed as overground walking
Status: Accepted (group decision at the full-team discussion on 23 October, reported by Anna on 25 October)
- The Si sub-study's usual walk (walk 01) is treated as unassisted overground walking, so the methods' exclusion of treadmill walking does not remove the Si participants.
- Basis: walking speed matches the Si paper's unassisted condition in both groups, PhysioNet defines walk 01 as "a usual, normal walk", and the stride series show a turn rhythm matching a 35 m hallway (`members/anna/log.md`, 23 October). The dataset does not state the condition explicitly, so this is an assumption, and the methods say so.

### D-010 · 2026-10-23 · The team uses Jupyter notebooks alongside scripts
Status: Accepted (group decision at the full-team discussion on 23 October, reported by Anna on 25 October)
- The team will use Jupyter notebooks alongside the scripts, so that results and figures can be shared more easily within the team.
- This changes the README's statement that the project uses plain Python scripts and no notebooks.
