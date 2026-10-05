# Log: Jamie Sanson (`jamie`)

<!--
APPEND-ONLY HISTORY. Edited only by Jamie's agents, and only on main (CLAUDE.md sections 3 and 7).
Add new entries at the BOTTOM. Never edit or delete earlier entries.

Write one entry per session or per meaningful piece of work, including work done outside the
repo (reading papers, writing in the Google Doc, meetings). The paper's Author Contributions
and AI-Assisted Work sections are written from these entries, so be specific and honest.

Entry format:

### 2026-10-02 · T-007 · Short title
- **Did:** what was produced or decided, with file paths or pull request links.
- **CRediT roles:** any of Conceptualization, Data curation, Formal analysis, Investigation,
  Methodology, Project administration, Resources, Software, Supervision, Validation,
  Visualization, Writing – original draft, Writing – review & editing.
- **AI use:** which tool did what, and what the human decided or changed ("not yet reviewed
  by <name>" is an honest answer). "None" is fine.
- **Verified:** what was actually checked and how (ran X, opened the DOI of Y, compared Z
  against the raw signal). Say what is not verified yet.
-->

### 2026-10-02 · T-001, T-005 · Collaboration system bootstrapped; local clone moved out of OneDrive
- **Did:** Set up the repo's collaboration system (commits `f906e7c`, `9c6a7a7` on main): `CLAUDE.md` agent protocol, `CONTRIBUTING.md`, `TASKS.md` board, `DECISIONS.md` (D-002, D-003 proposed), `members/` handoff and log files, `/start` and `/handoff` skills, pre-commit hook + `tools/repo_checks.sh`, GitHub Actions `checks.yml`, ruff config, `.gitattributes`, `.claude/settings.json`. Added a GitHub ruleset on `main` (block force pushes, restrict deletions). Cloned the repo to `C:\Users\jamie\Documents\BMEN600_Group5` with the hook switched on (T-005, ruff install still to do).
- **CRediT roles:** Project administration, Software.
- **AI use:** Claude (cloud session linked to Jamie's PC) designed and wrote every file above from Jamie's one-line brief ("set up a good system for collaboration, maybe a handoff file"), ran the tests, created the ruleset through the browser and did the clone. Jamie chose the approach, granted the GitHub app access and the folder permissions, and had not yet reviewed the file contents line by line at the time of this entry.
- **Verified:** Local simulation with three clones against a local bare remote (51 checks: claim races, rebase conflicts, every hook rule, merge commits, CI modes, CRLF); a blind dry run by a separate agent acting as Anna (`/start T-007`, work, `/handoff`); GitHub Actions green on both commits; ruleset confirmed through the GitHub API (`deletion`, `non_fast_forward` on the default branch); the new clone passes `git fsck` and matches a fresh clone file for file. Not verified: the hook on Windows (Git Bash) and macOS has not been run by a teammate yet.

### 2026-10-05 · T-009, T-010, T-007 · Midterm §2 draft, dataset verification, board set up for the midterm
- **Did:** Added the midterm section tasks (T-009 to T-015) to `TASKS.md` from the Project Timeline sheet and claimed T-007, T-009, T-010. Verified both datasets: WearGait-PD (Sci Data 2026; Synapse, account required, CC BY 4.0) and PhysioNet Gait in PD v1.0.0 (open, ODC-By 1.0, 93 PD / 73 controls, 306 records); found that the README's "GaitPDB" DOI resolves to a Nature Health comment about PhysioNet rather than the dataset. Drafted §2 (`report/midterm/02_background_and_research_gap.md`, branch `jamie/T-009-background-gap`) with a ledger of 14 verified sources (`report/midterm/sources.md`). Found the closest prior work, Jin (Appl. Sci. 2026) and Choi et al. (Bioengineering 2026), both of which already do participant-level evaluation on this dataset, and framed the gap around gait-only features, uncertainty, cross-protocol and cross-cohort validation.
- **CRediT roles:** Investigation, Writing – original draft, Project administration.
- **AI use:** Claude (cloud session with the browser on Jamie's PC) ran the searches, read each source's record, wrote the ledger and the draft, and set up the board. Jamie supplied the responsibilities sheet and the dataset pointers; the draft is not yet reviewed by Jamie.
- **Verified:** each of the 14 sources opened and read on 2026-10-05 (PubMed or publisher page); dataset facts read from the PhysioNet page, `format.txt` and `demographics.txt`, and from the WearGait-PD article. Not verified: no data file has been opened yet; the analysis plan in the draft's last paragraph is provisional until the group confirms the research question.
