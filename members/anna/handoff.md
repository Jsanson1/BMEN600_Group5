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

## T-017 · Pre-processing pipeline (stride cleaning for both datasets)
_Updated 2026-11-01 13:22 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `2fe20b2`_

- **Now:** the cleaning is shared, tested code on the branch: `src/gaitpdb/clean_data.py` (`clean_gaitpdb`, `clean_weargait`, `meets_minimum`; every stride gets `clean` and a `reason`) with `tests/test_clean_data.py`. `scripts/make_clean_strides.py` (now in `run_all.py`) builds per-stride tables for both datasets in `data/interim/` (ignored by git; rebuilt, never edited) with a provenance file, and commits `results/clean_strides_summary.txt`. gaitpdb turns use a phase check: the strongest both-feet candidate anchors the turns, one is predicted every interval and confirmed within ±30% of it, none within 0.7 interval of a walk's start, nor of its end for Ju (fixed 100 m; Ga and Si record 2 min). WearGait-PD insole gaps up to 5 samples are filled by interpolation. Not yet on `main`: no pull request.
- **Validated:** all 49 tests pass (17 for cleaning), and each new test was checked to fail when its behaviour is broken. Ju known answer: exactly 3 turns in 34 of 41 complete walks (31 before the phase check). D-011 inclusion: gaitpdb 155 of 161 countable (excluded JuCo01, JuCo02, JuCo03, JuPt03, JuPt05, JuPt08; GaPt03 has no speed), WearGait-PD 164 of 170 (excluded HC109, NLS056, NLS162, NLS172, NLS185, WPD011). WearGait-PD missing data is 98% padding at the start and end of recordings; inside recordings almost every gap is one sample, in bursts (`scripts/explore_weargait_missing.py`), so strides removed for missing data fell from 17.6% to 0%. Corridor lengths checked in the full papers by Anna and recorded in `report/midterm/sources.md` (S4, S6, S19). A rerun of `make_clean_strides.py` reproduces its outputs exactly. **Not verified:** WearGait-PD stride timing uses gaitpdb's 20 N threshold, not validated for its insoles (T-025); about 4 real gaitpdb turns are missed by the phase check (GaPt04 30.7 s, GaPt27 78 s, SiPt09 29.1 s, SiPt16 95 s); the simulation scripts are not in the repo.
- **Next:** update the README file map (new module and scripts) and remove the outdated "unverified" notes in `scripts/explore_turn_timing.py` and the report draft; then open the pull request (reviewer: Jamie or Yassien). **Anna to review:** whether each study's methods already exclude gait initiation and termination. Later: the sharing notebook (D-010), the [Anna] sections of `report/T-017_stride_rule_exploration.md`.
- **Blocked / needs a decision:** none.
- **For teammates:**
  - @jamie @yassien, variability: our stride-time CV for Si was about 2× the paper's for these recordings, plausibly partly because their event detection uses the force slope rather than a fixed threshold; removing turns brings it close (see Validated).
  - @yassien, for T-018: slow stride-time fluctuation may itself characterise PD, so T-017 plans to remove only turns and other non-walking strides and leave the series unfiltered; features could then describe variability at two timescales (step-to-step and slow). One real hesitation can dominate a walk's CV (SiCo16), so a robust variability measure (median absolute deviation) alongside the CV may be worth adding.
  - @jamie: 10 of 53 Ju usual-walk files are shorter than 70% of the 100 m walk implied by `Speed_01` (truncated recordings); `Speed_01` looks like distance / walking time including turns (Ju walking time is 1.07 x 100 m / `Speed_01`).
  - @jamie, for T-025: gaitpdb's 20 N threshold fails for some WearGait-PD insoles (e.g. NLS056, where swing force never drops below 20 N and strides merge to 4-11 s), so the insole loader needs its own threshold or the walkway contacts; 9 participants have no insole data and 3 controls (NLS145, NLS193, NLS207) have no SelfPace file.
  - @yassien, for T-018: cleaned stride tables are ready to build on. From branch `anna/T-017-preprocessing` (or `main` once merged), run `python scripts/make_clean_strides.py` and read `data/interim/clean_strides_gaitpdb.csv` and `clean_strides_weargait.csv`: one row per stride of both feet with `participant`, `foot`, `stride_s`, `stance_s`, `swing_s`, `swing_pct`, `clean`, `reason` and `included` (D-011). Use the clean strides of included participants. The tables may still shift slightly (WearGait-PD insole threshold, T-025), so code against the columns rather than today's numbers. WearGait-PD needs all three tasks downloaded (SelfPace, SelfPace_mat, SelfPace_matTURN, Version 1); without them the script skips WearGait-PD.
  - All, following D-010: the README still says the project uses plain scripts and no notebooks, and Jupyter is not yet in `requirements-dev.txt`; both change on a branch with a pull request, ideally with the first notebook. (On Anna's Windows machine, Smart App Control blocked the newest matplotlib and Pillow releases, so Jupyter may need older versions there too.)
- **Not pushed:** the simulation scratch scripts exist only on Anna's machine (to be moved into the repo). WearGait-PD data (SelfPace, SelfPace_mat, SelfPace_matTURN) in `data/raw/weargait_pd/` is ignored by git as intended.
