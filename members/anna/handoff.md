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
_Updated 2026-10-23 11:52 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `16ad3d0`_

- **Now:** a timing-based turn detector is committed on the branch (`scripts/explore_turn_timing.py` → `results/explore_turn_timing.{txt,csv}`, figures 08-09): expected turn interval = corridor length / `Speed_01` (Ga, Ju 25 m; Si 35 m), refined by each walk's own stride rhythm; each turn's window (±2 s) is removed from both feet, plus one stride either side, together with the 0.5-2.5 s and 10-70% swing limits and a rule for one-foot missed heel strikes. Exploratory; no change to `src/` yet. Earlier exploration: `scripts/explore_stride_rules.py` and the draft `report/T-017_stride_rule_exploration.md` (interpretation sections still to write).
- **Validated:** on 161 analysed walks (GaPt03 has no speed): known-answer check, exactly 3 turns in 31 of 41 complete Ju walks (100 m = 4 lengths); turns show on both feet 92-96% of the time; median stride-time CV falls from 3.6-4.9% (team rules) to 2.2-3.2%, PD above control in every sub-study, clearly in Ga and Ju, barely in Si (Ga 3.18 vs 2.18, Ju 3.12 vs 2.61, Si 2.57 vs 2.47), and Si moves close to the Si paper's values (2.24% PD, 1.94% control); the fixed limits remove almost nothing beyond the turns; no one-foot missed heel strikes found (every ~2x stride examined involves both feet). Removal is 17-33% of strides, more in controls (21.4% vs 17.7%, p = 0.005), because faster walkers turn more often. Earlier: an amplitude threshold on band-passed strides cannot separate modest turns from PD slow wander (simulation, 100 seeds). **Not verified:** turn locations checked by eye on six walks only; the corridor lengths and the Si paper's values were typed in from the papers, and those references are not yet in `report/midterm/sources.md`; the simulation scripts are not in the repo.
- **Next:** add a phase check (turns at the spacing of the others, e.g. SiCo20's missed turn at ~29 s, which a count cap misses); decide what to do with genuine mid-walk events (SiCo16's hesitation raises its CV from 2.99 to 7.34; real gait, so kept); move the simulation into the repo; write the [Anna] sections; add both scripts to the README file map before the pull request.
- **Blocked / needs a decision:** group to confirm Si walk 01 is overground; team to discuss notebooks and the length question (below).
- **For teammates:**
  - @jamie @yassien, Si treadmill question, resolved as far as the data allow: the Si paper (Frenkel-Toledo et al., Mov Disord 2005) recorded unassisted, walker and treadmill walking. Our Si walk 01 matches the **unassisted overground** condition: speed PD 1.11 vs 1.12 m/s and controls 1.25 vs 1.24 (walker and treadmill 1.05 and 1.21); PhysioNet defines walk 01 as "a usual, normal walk"; recordings are 121.2 s, matching the 2-min walk in the methods paper the Si study cites for its stride timing; IDs fit the paper's n (30 controls, 36 PD; 29 and 35 are public). Added 2026-10-23: the Si stride series show a turn rhythm matching a 35 m hallway (the paper's familiarisation hallway) for 82% of controls and 68% of PD, within 20%, further support for overground. Conclusion: likely overground, so no exclusion; not stated explicitly by the dataset, so the group should confirm and the methods should say how we decided. (Our values from `results/features_usual_walk.csv`; the paper's typed from the paper.)
  - @jamie @yassien, variability: our stride-time CV for Si was about 2× the paper's for these recordings, plausibly partly because their event detection uses the force slope rather than a fixed threshold; removing turns brings it close (see Validated).
  - @yassien, for T-018: slow stride-time fluctuation may itself characterise PD, so T-017 plans to remove only turns and other non-walking strides and leave the series unfiltered; features could then describe variability at two timescales (step-to-step and slow). One real hesitation can dominate a walk's CV (SiCo16), so a robust variability measure (median absolute deviation) alongside the CV may be worth adding.
  - @jamie: 10 of 53 Ju usual-walk files are shorter than 70% of the 100 m walk implied by `Speed_01` (truncated recordings); `Speed_01` looks like distance / walking time including turns (Ju walking time is 1.07 x 100 m / `Speed_01`).
  - All, walk length: could length let a model identify PD? Walking time is the same in both groups (median 120 s; AUC 0.57, p = 0.11) and so are strides kept under the team rules (AUC 0.52); after turn removal PD walks keep more strides than controls (168 vs 154; AUC 0.60, p = 0.025). The six model features do not include counts, so length could enter only indirectly (precision of the CV; length-dependent slow-timescale features). Suggestion: do not truncate PD walks to control duration; if needed, equalise the number of straight strides per walk as a pre-specified sensitivity analysis, and use equal-length segments for any slow-timescale features (T-018, T-022).
  - All, notebooks: the README says plain scripts, not notebooks; worth discussing notebooks for the model-training steps, where interactive figures help.
- **Not pushed:** the simulation scratch scripts exist only on Anna's machine (to be moved into the repo). WearGait-PD data in `data/raw/weargait_pd/` is ignored by git as intended.
