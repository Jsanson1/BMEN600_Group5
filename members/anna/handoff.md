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
_Updated 2026-10-23 11:28 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `1e6e855`_

- **Now:** exploration committed on the branch (`scripts/explore_stride_rules.py` → `figures/explore_stride_rules/`, `results/explore_stride_rules.txt`; draft `report/T-017_stride_rule_exploration.md`, interpretation sections still to write). Working towards a timing-based turn detector: expected turn interval = path length / `Speed_01` (Ga and Ju 25 m, Si 35 m), turns located on both feet, each turn's time window removed from both feet plus one stride either side. No change to `src/` yet.
- **Validated:** no filtering in `src/`; removal rates by group (median 1.7% PD vs 1.3% control, p = 0.07). On simulated walks (100 seeds), an amplitude threshold on the band-passed stride series cannot separate modest turns from PD slow wander (false removals in 49 of 100 PD-like runs). The slow rhythm of the stride series matches path / `Speed_01` within 20% for 67% of the 162 walks (Si 82% control, 68% PD; misses are mostly half-period harmonics). In the six example walks, most strides we had called stops or artefacts (GaPt23 8 s, JuCo02 2.3 s, JuPt19 and SiPt33 spikes) fall at predicted turn times. **Not verified:** the simulation and timing checks come from scratch scripts not yet in the repo; turn locations not checked beyond the six walks.
- **Next:** build the timing-based detector (search the rhythm within 0.7-1.5 x the prediction; for walks with fewer than ~2.5 predicted turns use the prediction directly), check it on the six walks, then count removals on all 162 by group; write the [Anna] sections; add the script to the README file map before the pull request.
- **Blocked / needs a decision:** group to confirm Si walk 01 is overground (below); team to discuss notebooks (below).
- **For teammates:** @jamie @yassien: Si treadmill question, resolved as far as the data allow: the Si paper (Frenkel-Toledo et al., Mov Disord 2005) recorded unassisted, walker and treadmill walking. Our Si walk 01 matches the **unassisted overground** condition: speed PD 1.11 vs 1.12 m/s and controls 1.25 vs 1.24 (walker and treadmill 1.05 and 1.21); PhysioNet defines walk 01 as "a usual, normal walk"; recordings are 121.2 s, matching the 2-min walk in the group's methods paper; IDs fit the paper's n (30 controls, 36 PD; 29 and 35 are public). Conclusion: likely overground, so no exclusion; not stated explicitly by the dataset, so the group should confirm and the methods should say how we decided. (Our values from `results/features_usual_walk.csv`; the paper's typed from the paper.) Side note for T-017: our stride-time CV is about 2× the paper's for these recordings, plausibly partly because their event detection uses the force slope rather than a fixed threshold. Added 2026-10-23: the Si stride series show a turn rhythm matching a 35 m hallway (the paper's familiarisation hallway) for 82% of controls and 68% of PD, within 20%, further support for overground. @yassien, for T-018: slow stride-time fluctuation may itself characterise PD, so T-017 plans to remove only turns and other non-walking strides and leave the series unfiltered; features could then describe variability at two timescales (step-to-step and slow). @jamie: 10 of 53 Ju usual-walk files are shorter than 70% of the 100 m walk implied by `Speed_01` (truncated recordings); `Speed_01` looks like distance / walking time including turns (Ju walking time is 1.07 x 100 m / `Speed_01`). All: the README says plain scripts, not notebooks; worth discussing notebooks for the model-training steps, where interactive figures help.
- **Not pushed:** the simulation and turn-timing scratch scripts exist only on Anna's machine (to be moved into the repo with the detector). WearGait-PD data in `data/raw/weargait_pd/` is ignored by git as intended.
