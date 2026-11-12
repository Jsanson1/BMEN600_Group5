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
_Updated 2026-11-12 16:50 by Claude Code for Anna · branch `anna/T-017-preprocessing` at `51f953d` · pull request #21 (https://github.com/Jsanson1/BMEN600_Group5/pull/21)_

- **Now:** finished and in review as #21. `src/gaitpdb/clean_data.py` cleans both datasets (every stride gets `clean` and a `reason`; D-008, D-011) with the contact threshold of D-012 (Jamie's #19, merged into the branch on 2 November); `scripts/make_clean_strides.py`, in `run_all.py` just before `make_features.py`, builds the tables in `data/interim/` and `results/clean_strides_summary.txt` (`--fixed-threshold 20` for the 20 N sensitivity analysis). `main` merged into the branch today (only conflict: `run_all.py`'s docstring, combined); README file map and run steps updated; the outdated "unverified" corridor notes now point to `sources.md` S4, S6, S19.
- **Validated:** a rebuild at `51f953d` reproduces the committed summary exactly: gaitpdb 155 of 161 walks included (excluded JuCo01-03, JuPt03, JuPt05, JuPt08; GaPt03 has no speed), WearGait-PD 169 of 170 participants with insole data (excluded NLS162). 75 tests pass locally and ruff is clean; Ju known answer 34 of 41. **Not verified:** `tests/test_forest.py` and `tests/test_check_features.py` cannot load on Anna's machine (Smart App Control blocks a scikit-learn file), so they rely on GitHub's checks; about 4 real gaitpdb turns missed (GaPt04 30.7 s, GaPt27 78 s, SiPt09 29.1 s, SiPt16 95 s); the simulation scripts are not in the repo.
- **Next:** review of #21 (Jamie or Yassien); Anna merges once approved and checks are green; set T-017 to done, delete this section and the branch. **Anna to review:** whether each sub-study's methods already exclude gait initiation and termination. Later: the [Anna] sections of `report/T-017_stride_rule_exploration.md`; the sharing notebook (D-010).
- **Blocked / needs a decision:** a reviewer for #21. Open question from Jamie: whether WearGait-PD strides during a labelled freeze should be dropped (now kept if they pass the stride limits).
- **For teammates:**
  - @jamie: please review #21 (https://github.com/Jsanson1/BMEN600_Group5/pull/21; requested on GitHub, checks green). Once it is merged, the feature steps on `main` find the clean-stride tables and the run branch can merge `main`. @yassien: comments welcome too.
  - @yassien: earlier notes for T-018 still stand: slow stride-time fluctuation may itself characterise PD (the series is left unfiltered), and a robust variability measure alongside the CV helps when one hesitation dominates a walk (SiCo16).
  - @jamie: 10 of 53 Ju usual-walk files are shorter than 70% of the 100 m walk implied by `Speed_01` (truncated recordings).
  - All, following D-010: the README still says the project uses plain scripts and no notebooks, and Jupyter is not yet in `requirements-dev.txt`; both change on a branch with a pull request, ideally with the first notebook. (On Anna's Windows machine, Smart App Control blocked the newest matplotlib and Pillow releases, and now a scikit-learn file, so Jupyter may need older versions there too.)
- **Not pushed:** the simulation scratch scripts exist only on Anna's machine (to be moved into the repo). WearGait-PD data in `data/raw/weargait_pd/` is ignored by git as intended.
