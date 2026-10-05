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
_Updated 2026-10-05 15:02 by Claude (cloud session) for Jamie · branch `jamie/T-009-background-gap` at `fba3c75` · pull request #3 open_

- **Now:** Draft 3 (about 660 words) is in the shared Google Doc and in `report/midterm/02_background_and_research_gap.md`; pull request #3 (https://github.com/Jsanson1/BMEN600_Group5/pull/3) carries the snapshot and the 14-source ledger. Jamie has read the draft and will edit it in the Doc.
- **Validated:** all 14 sources opened and checked on 2026-10-05 (`report/midterm/sources.md`). **Not verified:** not yet reviewed by Anna.
- **Next:** Anna reviews (in the Doc or on #3); Jamie edits in the Doc; once the wording settles, copy it back into the markdown on the branch, then merge #3, mark T-009 done, delete the branch.
- **Blocked / needs a decision:** Jamie to say whether WearGait-PD is a firm commitment or "if time permits" in §2 and §5 (D-005 still to be confirmed by the group).
- **For teammates:** @anna: the research question at the top of §1 in the Doc is a proposal; the last paragraph of §2 and §4 must say the same thing. @yassien: the verified dataset facts for §3 are in the Doc under §3 and in `sources.md` row S7.
- **Not pushed:** nothing.

## T-010 · Midterm §5 Preliminary Results (with T-007)
_Updated 2026-10-05 15:02 by Claude (cloud session) for Jamie · branch `jamie/T-010-preliminary-results` at `7e550ea` · pull request #2 open_

- **Now:** Finished on the full database. §5 draft 1 (about 690 words, Table 1, Figure 1) is in the Google Doc and in `report/midterm/05_preliminary_results.md`; `results/` and `figures/` on the branch are the full-data run; pull request #2 (https://github.com/Jsanson1/BMEN600_Group5/pull/2) also carries the T-007 structure (`src/gaitpdb`, `scripts/`, `requirements.txt`, `data/raw/README.md`). Headline: swing-time asymmetry separates PD from controls (AUC 0.76, p 1.5e-8) far better than stride-time variability (AUC 0.60, p 0.026, and 0.58 within the 60 to 80 year band); controls are 2.6 years younger than patients although the PhysioNet page says 66.3 years for both.
- **Validated:** all 311 files match PhysioNet's SHA256SUMS; loader run on the real `demographics.txt` (166 rows); Figure 1 trace inspected; every number in §5 traced to `results/figure1_summary.txt`, `results/event_detection_checks.txt` or `results/table1_participants.md`; Doc table cells checked against the CSV by script. **Not verified:** the event detection against a reference system (none in the database); a fresh install on Windows or macOS; Jamie's and Anna's reading of the text.
- **Next:** Anna reviews #2 (her agent can run the three scripts after unpacking the dataset per `data/raw/README.md`); Jamie edits §5 in the Doc; merge #2, mark T-010 and T-007 done, delete the branch; then T-008 (README front page) can start.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: build on `src/gaitpdb` rather than re-reading the text files; `record_features()` gives the per-record feature set and `results/features_usual_walk_by_group.csv` the single-feature AUCs on the usual walk. @yassien: for §3, the demographics file gives the controls a mean age of 63.7 y (PD 66.3 y) while the PhysioNet page says 66.3 y for both; `demographics.txt` has ragged trailing tabs and 69 empty lines (the loader handles it); the quirks are listed in §5 of the Doc and in `data/raw/README.md`.
- **Not pushed:** nothing.
