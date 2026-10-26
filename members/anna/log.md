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

### 2026-10-23 · T-017 · Turn removal: filters, simulation, turn timing
- **Did:** committed the exploration as a reproducible script, `scripts/explore_stride_rules.py`
  (figures in `figures/explore_stride_rules/`, numbers in `results/explore_stride_rules.txt`), and a report
  skeleton, `report/T-017_stride_rule_exploration.md`, whose interpretation sections Anna will write.
  Checked the turn-removal idea three ways. (1) Simulated walks built from the real participants' turn
  shapes and PD slow wander, 100 random seeds, reporting per-stride sensitivity and specificity for three
  removal rules (band-pass peaks, hysteresis, hysteresis capped at 3 strides; all with one stride removed
  either side): an amplitude threshold cannot separate modest turns from PD slow wander. (2) The same rules
  on the six example walks. (3) Turn timing: expected interval = path length / speed (25 m Ga and Ju, 35 m
  Si, from the sub-studies' papers), against each walk's slow stride rhythm (Lomb-Scargle) on all 162
  analysed walks: within 20% for 67%; Si fits a 35 m hallway. Most "stops" and "artefacts" in the six
  examples fall at predicted turn times. Decided with Anna: remove only turns and other non-walking strides
  (each turn's time window from both feet, plus one stride either side) and leave the stride series
  unfiltered, because slow fluctuation and asymmetry may characterise PD.
- **CRediT roles:** Investigation, Formal analysis, Methodology, Software, Validation.
- **AI use:** Claude Code (Claude Opus 5.5) wrote the exploration script and the scratch simulation and
  timing scripts, ran them and drafted the report skeleton and handoff. Anna directed the work: chose to
  share findings as a script and markdown report rather than a notebook (to raise notebooks with the team),
  chose mean removal before filtering, asked for a test on a simulated turn (Claude proposed the harder,
  data-matched version and the capped extension; Anna agreed), asked for sensitivity and specificity and
  for removing the stride before and after each turn, rejected high-passing the series because slow wander may be a
  PD signal, required that removal across both feet must not distort gait asymmetry, and supplied the
  walking paths of the Ga, Ju and Si protocols from their papers. Anna had the script walked through
  section by section before it was committed.
- **Verified:** the script reproduces the earlier scratch numbers; ruff passes; mean vs median removal
  before filtering gives identical output (checked numerically). **Not verified:** the simulation and
  timing results come from scratch scripts not yet in the repo; turn locations are not checked beyond six
  walks; the protocol papers' path lengths were typed in by Anna and the references are not yet in
  `report/midterm/sources.md`.

### 2026-10-25 · T-017 · D-008 recorded; clean-stride counts; WearGait-PD task pooling and drift
- **Did:** recorded the group's decision as D-008 (turns in gaitpdb found from walking-path timing).
  Counted clean strides per foot in both datasets (`scripts/explore_stride_counts.py`): gaitpdb with the
  timing-based turn removal plus the first and last stride trimmed; WearGait-PD SelfPace with its video
  labels for turns. Downloaded WearGait-PD's SelfPace_mat and SelfPace_matTURN tasks (Version 1) and tested
  pooling the three straight-walking tasks, with a sensor drift check (`scripts/explore_weargait_tasks.py`).
  Findings: gaitpdb meets N = 20 for all 161 countable walks and N = 30 for all but three truncated Ju
  files; WearGait-PD's short walkway passes give a median of 8-10 clean strides even when pooled, or 25-26
  without the one-stride turn margin; no sign of insole drift in the swing-phase force; gaitpdb's 20 N
  threshold fails for some insoles.
- **CRediT roles:** Data curation, Formal analysis, Investigation, Methodology, Software.
- **AI use:** Claude Code (Claude Opus 5.5) wrote and ran both scripts, built the figures, drafted the
  D-008 entry from Anna's wording (suggesting two typo fixes, "turns" and "sub-study", which Anna
  confirmed) designed the sensor-level
  drift checks (swing-phase force, peak stance force) and drafted the handoff. Anna brought the group's decision and its wording, proposed checking
  N = 30 (suggested by Jamie) and then N = 20, chose to use WearGait-PD's labels and to keep everything
  exploratory until unit tests exist, set the purpose of the first/last-stride trim (technical start and
  stop effects, not gait initiation), asked for the extra tasks and the drift figure, ran the Synapse
  download herself, and raised a different N per dataset with the dataset-of-origin check.
- **Verified:** all 368 downloaded files match Synapse's sizes (download list); both scripts ran to
  completion and pass ruff (`explore_weargait_tasks.py` was not rerun after its final formatting and
  warning change); the zero-stride case (NLS056) was traced to the insole force never dropping
  below 20 N. **Not verified:** WearGait-PD stride timing (20 N threshold not validated for the insoles);
  whether the 2% lower peak force in the walkway tasks is sensor or gait; the WearGait-PD counts are
  provisional.
