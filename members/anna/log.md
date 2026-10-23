# Log: Anna Klygina (`anna`)

<!--
APPEND-ONLY HISTORY. Edited only by Anna's agents, and only on main (CLAUDE.md sections 3 and 7).
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

### 2026-10-16 · T-011, T-013 · Midterm Research Plan: Introduction (§I) and Methods (§IV)
- **Did:** identified the problem space; researched and wrote Section I (Introduction and Motivation);
  developed the methodology and wrote Section IV (Proposed Methods and Evaluation); made the initial draft
  of the project timeline spreadsheet. With Jamie and Yassien, chose the research question and dataset.
  Text written in the group's shared Word file; nothing for these sections is in the repository. The plan
  was submitted on D2L on 2026-10-16. (Logged on 2026-10-23, after submission.)
- **CRediT roles:** Conceptualization, Methodology, Writing – original draft, Writing – review & editing,
  Project administration (initial timeline).
- **AI use:** Anna wrote the sections herself. Claude (Anthropic), through the Claude desktop app, supported
  brainstorming potential mechanisms for the methodology in Section IV, drafted the statistical-analysis
  phrasing in Section IV, helped with limited phrasing and revision, and quality-checked the content of
  Sections I and IV.
- **Verified:** Anna checked the AI-suggested wording against the cited papers.

### 2026-10-22 · T-003 · One-time repo setup
- **Did:** switched on the repository's pre-commit hook (`git config core.hooksPath .githooks`); installed
  ruff and the project's packages in a local virtual environment (`.venv`, not committed); marked T-003 done.
  Pinned local plotting packages to matplotlib 3.9.4 and Pillow 11.3.0 because Windows Smart App Control
  blocked the compiled files of the newest releases (local environment only; `requirements.txt` unchanged).
- **CRediT roles:** none (setup).
- **AI use:** Claude Code (Claude Opus 5.5) ran the setup commands, diagnosed the blocked DLLs and proposed the
  older versions; Anna approved each command and ran the matplotlib install herself.
- **Verified:** `repo checks: OK` printed on commit; the 32 unit tests pass with the pinned versions; a
  matplotlib test figure saves.

### 2026-10-23 · T-017 · Data access, exploring the stride rules, Si walking condition
- **Did:** downloaded gaitpdb locally and the WearGait-PD Version 1 participant sheets and 185 SelfPace CSVs
  with Anna's own Synapse account (`data/raw/`, not committed). Found that the WearGait-PD copy on Anna's
  OneDrive was the Version 2 (longitudinal, PD-only) release and replaced it with Version 1. Explored what the
  current stride rules in `src/gaitpdb/events.py` remove on three PD/control pairs (GaCo08/GaPt23,
  JuCo02/JuPt19, SiCo03/SiPt33): raw force traces, stride durations, stride-to-stride differences, power
  spectra of the stride series, and Butterworth band-pass (0.03-0.18 cycles/stride) and high-pass (0.18)
  filters. Findings: the relative 0.7-1.3 x median rule removes few strides and not systematically more in
  PD (median 1.7% vs 1.3%, p = 0.07), but it keeps most turn strides and removed one plausible PD stride via
  the 10% swing rule; turn patterns differ by sub-study; a high-pass removes slow drift but not the sharp apex
  of turns; a 2 x median "double stride" rule mislabels pivot turns. Established, from the Si paper
  (Frenkel-Toledo et al., 2005) and its methods reference, that Si walk 01 most likely is unassisted
  overground walking (speed matches in both groups); flagged to the team in the handoff. Noted our Si
  stride-time CV is about 2 x the paper's. Claimed T-017.
- **CRediT roles:** Investigation, Formal analysis, Methodology, Data curation.
- **AI use:** Claude Code (Claude Opus 5.5) wrote and ran all exploratory scripts (in a scratch folder
  outside the repo), produced the figures and summary numbers, and drafted the handoff notes. Anna directed
  the analysis: questioned the arbitrariness and possible PD bias of the 0.7-1.3 rule, asked for the check
  that no low-pass filtering hides the mid-stance dip, proposed the FFT, the stride-to-stride derivative and
  a Butterworth filter (chosen over a rolling median for defensibility), chose the participants' sub-studies
  to compare, found and read the Si paper and its methods reference, supplied the paper's values, and chose
  not to tune the pipeline to the paper's variability (to avoid overfitting). All handoff text was approved
  by Anna before committing.
- **Verified:** gaitpdb checksums (311 files match); WearGait-PD sheet MD5s match the versions in
  `data/raw/README.md`; cohort counts reproduce the team's (162 gaitpdb, 181 WearGait-PD); the flat PD force
  is in the raw 100 Hz sensor data. **Not verified:** the exploratory numbers and figures come from scratch
  scripts not yet in the repo, and cover six participants only; the paper's values were typed in by Anna.
