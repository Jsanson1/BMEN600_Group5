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
_Updated 2026-10-22 19:47 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `1e7f788` (no work commits yet)_

- **Now:** exploring what the current stride rules in `src/gaitpdb/events.py` remove, on one control (GaCo08) and one PD participant (GaPt23), before changing anything. No code changes yet.
- **Validated:** no filtering or smoothing anywhere in `src/` (searched); the flat PD stance-phase force is in the raw 100 Hz data, sensor by sensor. Removal rates by group from `results/features_usual_walk.csv`: median 1.7% of strides (PD) vs 1.3% (control), Mann-Whitney p = 0.07, not consistent across sub-studies. **Not verified:** the exploratory plots and numbers above come from scratch scripts, not yet from code in the repo.
- **Next:** decide how to detect turn strides in gaitpdb (current rules keep most of them); put the exploration in a notebook for the team.
- **Blocked / needs a decision:** whether Si's walk 01 is treadmill walking (see below).
- **For teammates:** @jamie @yassien: PhysioNet's `format.txt` labels the Si study "Treadmill walking in PD" (Frenkel-Toledo et al., Mov Disord 2005), and our methods exclude treadmill walking. The same file defines walk 01 as "a usual, normal walk" for all studies, and every Si recording is a single 121 s walk 01, so Si's walk 01 is probably overground, but this needs confirming in the paper's methods. If it is treadmill, excluding Si would remove 62 of the 162 analysed participants (leaving 100: 57 PD, 43 control; derived from `results/data_quality.txt`, not yet produced by a script). Raising for a group decision; nobody should change the cohort before then.
- **Not pushed:** nothing. (WearGait-PD Version 1 participant sheets and 185 SelfPace CSVs are downloaded in `data/raw/weargait_pd/`, ignored by git as intended.)
