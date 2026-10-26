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
_Updated 2026-10-25 22:09 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `085ecfe`_

- **Now:** D-008 recorded (timing-based turn detection for gaitpdb). Exploration on the branch, all in `scripts/explore_*.py` with outputs in `results/` and `figures/explore_stride_rules/`: the timing-based turn detector (`explore_turn_timing.py`); clean strides per foot in both datasets with the first and last stride trimmed (`explore_stride_counts.py`); WearGait-PD's three straight-walking tasks pooled, with a sensor drift check (`explore_weargait_tasks.py`). WearGait-PD uses its video labels for turns. Nothing moves into `src/` until unit tests validate it. Draft `report/T-017_stride_rule_exploration.md` still needs the [Anna] sections.
- **Validated:** gaitpdb, after turn removal and trimming (161 walks; GaPt03 has no speed): median 74 (control) and 82 (PD) clean strides on the weaker foot; all 161 reach N = 20; three fall below 30, all truncated Ju files (JuCo03 25, JuPt05 26, JuCo02 27). WearGait-PD (169 participants with insoles): SelfPace alone gives a median of 8-9 clean strides (8 reach N = 20); pooling SelfPace, SelfPace_mat and SelfPace_matTURN adds almost nothing under the one-stride turn margin (32 reach 20), because the walkway tasks stop and turn on a 16 ft mat; without that margin 141 of 169 reach 20 (median 25-26), but most of those strides are speeding up or slowing down. Drift: insole force during swing unchanged across the three tasks (median 3.0 vs 3.5 and 3.0 N, p = 0.17 and 0.11); peak stance force 2% lower in the walkway tasks (p < 0.001; sensor or gait cannot be told apart). Turn detector: exactly 3 turns in 31 of 41 complete Ju walks. **Not verified:** WearGait-PD stride timing uses gaitpdb's 20 N threshold, which fails for some insoles (e.g. NLS056: swing force never drops below 20 N, strides merge); corridor lengths and the Si paper's values were typed from the papers and are not yet in `report/midterm/sources.md`; the simulation scripts are not in the repo.
- **Next:** team decision on N on 26 October; Anna is considering a different N per dataset, which makes the dataset-of-origin check (D-007) more important. **Anna to review:** whether each study's methods already exclude gait initiation and termination (the first/last-stride trim here is for technical start and stop effects such as delayed sensor start). Then: compare stride-time CV between the three WearGait-PD tasks (evidence for or against pooling); add the phase check to the turn detector (e.g. SiCo20); write unit tests before moving any of this into `src/`; move the simulation into the repo; write the [Anna] sections; add the scripts to the README file map before the pull request.
- **Blocked / needs a decision:** the group decides N (26 October); group to confirm Si walk 01 is overground; team to discuss notebooks.
- **For teammates:**
  - @jamie @yassien, Si treadmill question, resolved as far as the data allow: the Si paper (Frenkel-Toledo et al., Mov Disord 2005) recorded unassisted, walker and treadmill walking. Our Si walk 01 matches the **unassisted overground** condition: speed PD 1.11 vs 1.12 m/s and controls 1.25 vs 1.24 (walker and treadmill 1.05 and 1.21); PhysioNet defines walk 01 as "a usual, normal walk"; recordings are 121.2 s, matching the 2-min walk in the methods paper the Si study cites for its stride timing; IDs fit the paper's n (30 controls, 36 PD; 29 and 35 are public). Added 2026-10-23: the Si stride series show a turn rhythm matching a 35 m hallway (the paper's familiarisation hallway) for 82% of controls and 68% of PD, within 20%, further support for overground. Conclusion: likely overground, so no exclusion; not stated explicitly by the dataset, so the group should confirm and the methods should say how we decided. (Our values from `results/features_usual_walk.csv`; the paper's typed from the paper.)
  - @jamie @yassien, variability: our stride-time CV for Si was about 2× the paper's for these recordings, plausibly partly because their event detection uses the force slope rather than a fixed threshold; removing turns brings it close (see Validated).
  - @yassien, for T-018: slow stride-time fluctuation may itself characterise PD, so T-017 plans to remove only turns and other non-walking strides and leave the series unfiltered; features could then describe variability at two timescales (step-to-step and slow). One real hesitation can dominate a walk's CV (SiCo16), so a robust variability measure (median absolute deviation) alongside the CV may be worth adding.
  - @jamie: 10 of 53 Ju usual-walk files are shorter than 70% of the 100 m walk implied by `Speed_01` (truncated recordings); `Speed_01` looks like distance / walking time including turns (Ju walking time is 1.07 x 100 m / `Speed_01`).
  - All, walk length: could length let a model identify PD? Walking time is the same in both groups (median 120 s; AUC 0.57, p = 0.11) and so are strides kept under the team rules (AUC 0.52); after turn removal PD walks keep more strides than controls (168 vs 154; AUC 0.60, p = 0.025). The six model features do not include counts, so length could enter only indirectly (precision of the CV; length-dependent slow-timescale features). Suggestion: do not truncate PD walks to control duration; if needed, equalise the number of straight strides per walk as a pre-specified sensitivity analysis, and use equal-length segments for any slow-timescale features (T-018, T-022).
  - All, notebooks: the README says plain scripts, not notebooks; worth discussing notebooks for the model-training steps, where interactive figures help.
  - @jamie, for T-025: gaitpdb's 20 N threshold fails for some WearGait-PD insoles (e.g. NLS056, where swing force never drops below 20 N and strides merge to 4-11 s), so the insole loader needs its own threshold or the walkway contacts; 9 participants have no insole data and 3 controls (NLS145, NLS193, NLS207) have no SelfPace file.
  - All, N for tomorrow: counts per dataset are in `results/explore_stride_counts.txt` and `results/explore_weargait_tasks.txt` on branch `anna/T-017-preprocessing` (not yet on `main`). A common N of 20-30 fits gaitpdb but not WearGait-PD's short walkway passes. WearGait-PD's other two tasks (Version 1 SelfPace_mat and SelfPace_matTURN) are downloaded on Anna's machine only; their download list is in her `data/raw/weargait_pd/`, which git ignores.
- **Not pushed:** the simulation scratch scripts exist only on Anna's machine (to be moved into the repo). WearGait-PD data (SelfPace, SelfPace_mat, SelfPace_matTURN) in `data/raw/weargait_pd/` is ignored by git as intended.
