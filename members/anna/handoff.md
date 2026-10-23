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
_Updated 2026-10-23 10:15 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `1e7f788` (no work commits yet)_

- **Now:** exploring what the current stride rules in `src/gaitpdb/events.py` remove, and whether a Butterworth filter on the stride-duration series can separate turns from step-to-step variability, on three PD/control pairs (Ga, Ju, Si). Turn patterns differ by sub-study; no method chosen yet. No code changes yet.
- **Validated:** no filtering or smoothing anywhere in `src/` (searched); the flat PD stance-phase force is in the raw 100 Hz data, sensor by sensor. Removal rates by group from `results/features_usual_walk.csv`: median 1.7% of strides (PD) vs 1.3% (control), Mann-Whitney p = 0.07, not consistent across sub-studies. **Not verified:** the exploratory plots and numbers above come from scratch scripts, not yet from code in the repo.
- **Next:** decide how to detect turn strides in gaitpdb (current rules keep most of them); put the exploration in a notebook for the team.
- **Blocked / needs a decision:** group to confirm that Si's walk 01 is overground walking (see below).
- **For teammates:** @jamie @yassien: Si treadmill question, resolved as far as the data allow: the Si paper (Frenkel-Toledo et al., Mov Disord 2005) recorded unassisted, walker and treadmill walking. Our Si walk 01 matches the **unassisted overground** condition: speed PD 1.11 vs 1.12 m/s and controls 1.25 vs 1.24 (walker and treadmill 1.05 and 1.21); PhysioNet defines walk 01 as "a usual, normal walk"; recordings are 121.2 s, matching the 2-min walk in the group's methods paper; IDs fit the paper's n (30 controls, 36 PD; 29 and 35 are public). Conclusion: likely overground, so no exclusion; not stated explicitly by the dataset, so the group should confirm and the methods should say how we decided. (Our values from `results/features_usual_walk.csv`; the paper's typed from the paper.) Side note for T-017: our stride-time CV is about 2× the paper's for these recordings, plausibly partly because their event detection uses the force slope rather than a fixed threshold.
- **Not pushed:** nothing. (WearGait-PD Version 1 participant sheets and 185 SelfPace CSVs are downloaded in `data/raw/weargait_pd/`, ignored by git as intended.)
