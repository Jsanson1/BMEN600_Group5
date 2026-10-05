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
_Updated 2026-10-05 13:05 by Claude (cloud session) for Jamie · branch `jamie/T-009-background-gap` at `fba3c75`_

- **Now:** Draft 3 (about 660 words, written after reading a sample of Jamie's own writing) replaced draft 2 in the shared Google Doc, in place, and is the snapshot in `report/midterm/02_background_and_research_gap.md`. Jamie has read it and will edit it in the Doc.
- **Validated:** all 14 sources opened and checked on 2026-10-05 (`report/midterm/sources.md`). **Not verified:** not yet reviewed by Anna.
- **Next:** Jamie edits in the Doc; Anna reviews there (comments or direct edits). Once the text settles, copy the final wording back into the markdown snapshot and open the pull request for the branch (markdown + `sources.md`), reviewer Anna.
- **Blocked / needs a decision:** D-005 (dataset emphasis) still to be confirmed by the group; Jamie's position is that both datasets must appear in the plan, which D-005 already does (WearGait-PD as the external test set).
- **For teammates:** @anna: the research question at the top of §1 in the Doc is a proposal; the last paragraph of §2 and §4 must say the same thing. @yassien: the verified dataset facts for §3 are in the Doc under §3 and in `sources.md` row S7.
- **Not pushed:** nothing.

## T-010 · Midterm §5 Preliminary Results
_Updated 2026-10-05 13:58 by Claude (cloud session) for Jamie · branch `jamie/T-010-preliminary-results` at `f2709a7`_

- **Now:** §5 draft 1 is in the Google Doc (prose, Table 1 as a real table, Figure 1 image) and in `report/midterm/05_preliminary_results.md`, with PROVISIONAL numbers: Jamie's PhysioNet download stalled at 234.5 of 288 MB (unchanged since 12:08; Jamie asked twice to restart it, no reply yet), so everything was run on the 237 of 306 recordings that are intact in the partial ZIP. `results/` and `figures/` on the branch are that provisional run (`results/PROVISIONAL.txt`). Code changes today: relative stride rule (0.7 to 1.3 x the record median), `scripts/check_event_detection.py` (thresholds 10/20/50 N with and without the rule), swing-time asymmetry panel in Figure 1, `load_demographics` rewritten for the real file. Headline so far: swing-time asymmetry separates PD from controls far better (AUC 0.79) than stride-time CV (AUC 0.63); controls are 2.6 years younger than patients although the PhysioNet description says 66.3 years for both.
- **Validated:** 240 of 240 downloaded files match PhysioNet's SHA256SUMS; the real `demographics.txt` was fetched from PhysioNet (checksum matches) and the loader reads it (166 rows, 93 PD / 73 controls; Table 1 identical to the one built from `demographics.html`); Figure 1 trace inspected; stride-time CV stable across 10, 20 and 50 N with the rule (AUC 0.62 to 0.64). **Not verified:** nothing on the 69 missing recordings; the usual-walk statistics will move once they are in.
- **Next:** when the ZIP is complete (automatic check every 40 to 60 min): stage it, `sha256sum -c SHA256SUMS.txt`, run `scripts/make_table1.py`, `scripts/make_figure1.py`, `scripts/check_event_detection.py`, commit `results/` and `figures/` (delete `results/PROVISIONAL.txt`), replace every provisional number in the markdown and the Doc (prose, Table 1 cells via `update_table.py` in the session scratchpad, status line, re-insert the figure image), check that the sentence about the turn in panel A still matches the new example record (default `GaPt03_01`), then open the pull request (reviewer Anna).
- **Blocked / needs a decision:** the download (only Jamie can restart it, or OK a download by the agent in the built-in browser). Jamie to say whether WearGait-PD is a firm commitment or "if time permits" in §2 and §5.
- **For teammates:** @anna @yassien: build on `src/gaitpdb` rather than re-reading the text files; `record_features()` gives the per-record feature set and `results/features_usual_walk_by_group.csv` the single-feature AUCs. @yassien: for §3, the demographics file gives the controls a mean age of 63.7 y (PD 66.3 y) while the PhysioNet page says 66.3 y for both; `demographics.txt` has ragged trailing tabs and 69 empty lines (the loader handles it); quirks are listed in §5 of the Doc.
- **Not pushed:** nothing.

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
_Updated 2026-10-05 13:05 by Claude (cloud session) for Jamie · branch `jamie/T-009-background-gap` at `fba3c75`_

- **Now:** Draft 3 (about 660 words, written after reading a sample of Jamie's own writing) replaced draft 2 in the shared Google Doc, in place, and is the snapshot in `report/midterm/02_background_and_research_gap.md`. Jamie has read it and will edit it in the Doc.
- **Validated:** all 14 sources opened and checked on 2026-10-05 (`report/midterm/sources.md`). **Not verified:** not yet reviewed by Anna.
- **Next:** Jamie edits in the Doc; Anna reviews there (comments or direct edits). Once the text settles, copy the final wording back into the markdown snapshot and open the pull request for the branch (markdown + `sources.md`), reviewer Anna.
- **Blocked / needs a decision:** D-005 (dataset emphasis) still to be confirmed by the group; Jamie's position is that both datasets must appear in the plan, which D-005 already does (WearGait-PD as the external test set).
- **For teammates:** @anna: the research question at the top of §1 in the Doc is a proposal; the last paragraph of §2 and §4 must say the same thing. @yassien: the verified dataset facts for §3 are in the Doc under §3 and in `sources.md` row S7.
- **Not pushed:** nothing.

## T-010 · Midterm §5 Preliminary Results
_Updated 2026-10-05 13:05 by Claude (cloud session) for Jamie · branch `jamie/T-010-preliminary-results` at `c4d198c`_

- **Now:** §5 draft 1 is in the Google Doc and in `report/midterm/05_preliminary_results.md`, with PROVISIONAL numbers: Jamie's PhysioNet download stalled at 234.5 of 288 MB (unchanged since 12:08), so Table 1, Figure 1 and the checks were run on the 237 of 306 recordings that are intact in the partial ZIP (demographics complete, read from `demographics.html`). The analysis code gained a relative stride rule (strides outside 0.7 to 1.3 x the record median are dropped) after one double-length stride per record was found to double the stride-time CV, plus `scripts/check_event_detection.py` (threshold sensitivity, effect of the rule). Headline so far: swing-time asymmetry separates PD from controls far better (AUC 0.79) than stride-time CV (AUC 0.63); controls are 2.6 years younger than patients although the PhysioNet description says 66.3 years for both.
- **Validated:** 240 of 240 downloaded files match PhysioNet's SHA256SUMS; event markers inspected on the Figure 1 trace; stride-time CV stable across 10, 20 and 50 N thresholds with the new rule (AUC 0.62 to 0.64). **Not verified:** nothing on the full dataset; `load_demographics` has not yet been run on the real `demographics.txt` (it was written from the PhysioNet description and a converted copy of the HTML table); `results/` and `figures/` are deliberately not committed until the full-data run.
- **Next:** when the ZIP is complete (Jamie was asked at 12:31 to restart the download; a reminder is set for 13:21): stage it, `sha256sum -c SHA256SUMS.txt`, run `scripts/make_table1.py`, `scripts/make_figure1.py`, `scripts/check_event_detection.py`, commit `results/` and `figures/`, replace every provisional number in the markdown and the Doc (prose, Table 1 cells, status line), insert the Figure 1 image in the Doc, then open the pull request (reviewer Anna).
- **Blocked / needs a decision:** the download (only Jamie can restart it).
- **For teammates:** @anna @yassien: build on `src/gaitpdb` rather than re-reading the text files; `record_features()` gives the per-record feature set and `results/features_usual_walk_by_group.csv` (after the full run) the single-feature AUCs. @yassien: for §3, the demographics file gives the controls a mean age of 63.7 y (PD 66.3 y) while the PhysioNet page says 66.3 y for both; quirks are listed in §5 of the Doc.
- **Not pushed:** nothing.

## T-007 · Project structure
_Updated 2026-10-05 13:05 by Claude (cloud session) for Jamie · folded into the T-010 branch_

- **Now:** `src/`, `scripts/`, `requirements.txt`, `data/raw/README.md` (download steps, licence, checksum) exist on `jamie/T-010-preliminary-results`; `results/` and `figures/` are created by the scripts.
- **Validated:** `ruff check` and `ruff format` clean; GitHub Actions green on every push of the branch. **Not verified:** a fresh install from `requirements.txt` on Windows.
- **Next:** merge with T-010; then T-008 (README front page) can start.
- **Blocked / needs a decision:** none.
- **For teammates:** none.
- **Not pushed:** nothing.
