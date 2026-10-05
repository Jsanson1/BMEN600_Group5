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

## T-009 · Midterm §2 Background and Research Gap
_Updated 2026-10-05 09:25 by Claude (cloud session) for Jamie · branch `jamie/T-009-background-gap` at `210234e`+1_

- **Now:** Draft 1 of §2 is on the branch: `report/midterm/02_background_and_research_gap.md` (about 790 words, needs cutting to about 600) and `report/midterm/sources.md` (14 verified sources with how each was checked and what it supports). Not yet reviewed by Jamie.
- **Validated:** every cited source was opened on 2026-10-05 (PubMed record, publisher page or PhysioNet page) and the cited numbers match the record. **Not verified:** nothing in the draft has been checked by a human yet; the closing paragraph states an analysis plan that still has to be agreed with Anna's §1 and §4.
- **Next:** Jamie reads the draft and `sources.md`, then either edits on the branch or sends comments; then open the pull request for Anna to review.
- **Blocked / needs a decision:** group needs to settle the research question wording, whether WearGait-PD is in scope, and the "four models" in the Methods row of the Project Timeline sheet (only three are listed).
- **For teammates:** @anna: the last paragraph of §2 must match §1 and §4 word for word; edit either side. @yassien: `sources.md` row S7 has the dataset facts for §3 (counts, sensors, licence ODC-By 1.0, DOI 10.13026/C24H3N). The README's "GaitPDB" DOI points at a Nature Health comment about PhysioNet, not at the dataset; the real one is https://physionet.org/content/gaitpdb/1.0.0/ (fix goes with T-008).
- **Not pushed:** nothing.

## T-010 · Midterm §5 Preliminary Results
_Updated 2026-10-05 09:25 by Claude (cloud session) for Jamie · branch `jamie/T-010-preliminary-results` not created yet, main at `30f0072`_

- **Now:** Waiting for the data. The PhysioNet "Gait in Parkinson's Disease" files (288.4 MB, 306 records, 166 participants) cannot be downloaded from the agent's side; Jamie downloads the ZIP into `data/raw/gaitpdb/` on his PC.
- **Validated:** data format read from `format.txt` on PhysioNet (19 columns: time, 8 left sensors, 8 right sensors, left total, right total; 100 Hz; names `<Study><Group><Subject>_<Walk>.txt`, walk 10 in Ga = dual task). `demographics.txt` read in full: one participant (JuCo10, listed as "Juc010") has no recording; Ju heights are in cm while Ga and Si are in m. **Not verified:** nothing run on the signals yet.
- **Next:** once the ZIP is in place: loader + manifest, Table 1 (participants and records by study and group, with age, sex, H&Y), Figure 1 (example VGRF trace with detected strides, stride-time variability by group), then the §5 text.
- **Blocked / needs a decision:** data download by Jamie; whether WearGait-PD (Synapse account needed) is in scope.
- **For teammates:** none.
- **Not pushed:** nothing.

## T-007 · Project structure
_Updated 2026-10-05 09:25 by Claude (cloud session) for Jamie · branch `jamie/T-007-project-structure` not created yet_

- **Now:** Claimed so the loader, `requirements.txt` and `data/raw/README.md` for T-010 have a home. Nothing written yet.
- **Validated:** nothing. **Not verified:** nothing.
- **Next:** create `src/`, `scripts/`, `data/raw/gaitpdb/README.md` (download steps, licence, version), `requirements.txt`, together with the first T-010 code.
- **Blocked / needs a decision:** none.
- **For teammates:** none.
- **Not pushed:** nothing.

## T-005 · Re-clone outside OneDrive and do the one-time setup
_Updated 2026-10-02 15:30 by Claude (cloud session linked to Jamie's PC) · no branch, coordination only_

- **Now:** Clone at `C:\Users\jamie\Documents\BMEN600_Group5` with hook, filemode and identity set; old OneDrive clone deleted on 2026-10-02 (it had no uncommitted work).
- **Validated:** `git fsck` clean, all tracked files identical to a fresh clone. **Not verified:** whether `ruff` is installed on the Windows side.
- **Next:** `python -m pip install -r requirements-dev.txt`, then `ruff --version`; the next `/start` sets this task to `done`.
- **Blocked / needs a decision:** none.
- **For teammates:** none.
- **Not pushed:** nothing.
