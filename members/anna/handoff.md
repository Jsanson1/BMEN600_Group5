# Handoff: Anna Klygina (`anna`)

<!--
CURRENT STATE ONLY. Edited only by Anna's agents, and only on main (CLAUDE.md sections 3 and 7).
History goes in log.md, next to this file.

One section per task Anna is working on. At every stopping point, rewrite the section
for your task. Delete it only once the task is done (merged). Do not touch other sections:
another of Anna's sessions may own them. Keep each section to about 15 lines.
When there are no active tasks, the file ends with the line: _No active tasks._

Section format (keep the bold labels so the others can scan for them; Calgary time):

## T-007 · Short task title
_Updated 2026-10-02 15:40 by Claude Code for Anna · branch `anna/T-007-short-slug` at `abc1234`_

- **Now:** where the work stands, in one to three lines.
- **Validated:** what was actually run or checked. **Not verified:** what is still assumed.
- **Next:** the exact next action, specific enough for someone to start cold (for a finished task: the pull request link or who opens it, who reviews, then merge, mark done, delete the branch).
- **Blocked / needs a decision:** none, or what and from whom.
- **For teammates:** none, or a note such as "@jamie: the loader now returns one row per stride".
- **Not pushed:** nothing. (Anything listed here exists on one machine only.)
-->

## T-017 · Pre-processing pipeline (exploring the current stride rules on gaitpdb)
_Updated 2026-11-01 12:00 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `085ecfe`_

- **Now:** D-008 recorded (timing-based turn detection for gaitpdb). Exploration on the branch, all in `scripts/explore_*.py` with outputs in `results/` and `figures/explore_stride_rules/`: the timing-based turn detector (`explore_turn_timing.py`); clean strides per foot in both datasets with the first and last stride trimmed (`explore_stride_counts.py`); WearGait-PD's three straight-walking tasks pooled, with a sensor drift check (`explore_weargait_tasks.py`). WearGait-PD uses its video labels for turns. Nothing moves into `src/` until unit tests validate it. Draft `report/T-017_stride_rule_exploration.md` still needs the [Anna] sections.
- **Validated:** gaitpdb, after turn removal and trimming (161 walks; GaPt03 has no speed): median 74 (control) and 82 (PD) clean strides on the weaker foot; all 161 reach N = 20; three fall below 30, all truncated Ju files (JuCo03 25, JuPt05 26, JuCo02 27). WearGait-PD (169 participants with insoles): SelfPace alone gives a median of 8-9 clean strides (8 reach N = 20); pooling SelfPace, SelfPace_mat and SelfPace_matTURN adds almost nothing under the one-stride turn margin (32 reach 20), because the walkway tasks stop and turn on a 16 ft mat; without that margin 141 of 169 reach 20 (median 25-26), but most of those strides are speeding up or slowing down. Drift: insole force during swing unchanged across the three tasks (median 3.0 vs 3.5 and 3.0 N, p = 0.17 and 0.11); peak stance force 2% lower in the walkway tasks (p < 0.001; sensor or gait cannot be told apart). Turn detector: exactly 3 turns in 31 of 41 complete Ju walks. **Not verified:** WearGait-PD stride timing uses gaitpdb's 20 N threshold, which fails for some insoles (e.g. NLS056: swing force never drops below 20 N, strides merge); corridor lengths and the Si paper's values were typed from the papers and are not yet in `report/midterm/sources.md`; the simulation scripts are not in the repo.
- **Next:** apply D-011 (N = 40 gaitpdb, N = 10 WearGait-PD, N as an inclusion minimum): with the current exploration, gaitpdb includes 154 of 161 countable walks (excluded: the truncated Ju walks JuCo01, JuCo02, JuCo03, JuPt03, JuPt05, JuPt07, JuPt08; GaPt03 pending, no speed) and WearGait-PD 163 of the 169 with insole data (provisional until the insole threshold is validated, T-025). **Anna to review:** whether each study's methods already exclude gait initiation and termination (the first/last-stride trim here is for technical start and stop effects such as delayed sensor start). Then: compare stride-time CV between the three WearGait-PD tasks (now pooled under D-011); add the phase check to the turn detector (e.g. SiCo20); write unit tests before moving any of this into `src/`; move the simulation into the repo; write the [Anna] sections; add the scripts to the README file map before the pull request. Windowing is not decided; it could serve the cross-cohort test or a sensitivity analysis.
- **Blocked / needs a decision:** none for T-017. Recorded: D-008 (turn timing, gaitpdb), D-009 (Si overground), D-010 (notebooks alongside scripts), D-011 (N per dataset).
- **For teammates:**
  - @jamie @yassien, variability: our stride-time CV for Si was about 2× the paper's for these recordings, plausibly partly because their event detection uses the force slope rather than a fixed threshold; removing turns brings it close (see Validated).
  - @yassien, for T-018: slow stride-time fluctuation may itself characterise PD, so T-017 plans to remove only turns and other non-walking strides and leave the series unfiltered; features could then describe variability at two timescales (step-to-step and slow). One real hesitation can dominate a walk's CV (SiCo16), so a robust variability measure (median absolute deviation) alongside the CV may be worth adding.
  - @jamie: 10 of 53 Ju usual-walk files are shorter than 70% of the 100 m walk implied by `Speed_01` (truncated recordings); `Speed_01` looks like distance / walking time including turns (Ju walking time is 1.07 x 100 m / `Speed_01`).
  - @jamie, for T-025: gaitpdb's 20 N threshold fails for some WearGait-PD insoles (e.g. NLS056, where swing force never drops below 20 N and strides merge to 4-11 s), so the insole loader needs its own threshold or the walkway contacts; 9 participants have no insole data and 3 controls (NLS145, NLS193, NLS207) have no SelfPace file.
  - All, N decided (D-011): gaitpdb N = 40, WearGait-PD N = 10, as minimum clean strides per foot; counts behind it are in `results/explore_stride_counts.txt` and `results/explore_weargait_tasks.txt` on branch `anna/T-017-preprocessing`. WearGait-PD's SelfPace_mat and SelfPace_matTURN tasks are downloaded on Anna's machine only (download list in her `data/raw/weargait_pd/`, ignored by git); @jamie, the loader for T-025 will need all three tasks.
  - All, following D-010: the README still says the project uses plain scripts and no notebooks, and Jupyter is not yet in `requirements-dev.txt`; both change on a branch with a pull request, ideally with the first notebook. (On Anna's Windows machine, Smart App Control blocked the newest matplotlib and Pillow releases, so Jupyter may need older versions there too.)
- **Not pushed:** the simulation scratch scripts exist only on Anna's machine (to be moved into the repo). WearGait-PD data (SelfPace, SelfPace_mat, SelfPace_matTURN) in `data/raw/weargait_pd/` is ignored by git as intended.
