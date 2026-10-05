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
_Updated 2026-10-05 11:05 by Claude (cloud session) for Jamie · branch `jamie/T-009-background-gap` at `bb198d3`+2_

- **Now:** Draft 2 of §2 is in the shared Google Doc "BMEN 600 Group 5 – Midterm Research Plan (draft)" (owner Jamie; link in the group chat) and mirrored in `report/midterm/02_background_and_research_gap.md`. Jamie read draft 1 and found it stilted; draft 2 is plainer. Still about 760 words against a 600-word target.
- **Validated:** all 14 sources opened and checked on 2026-10-05 (`report/midterm/sources.md`). **Not verified:** draft 2 not yet reviewed by Jamie or Anna.
- **Next:** Jamie sends a sample of his own writing; §2 gets one more pass in his voice and is cut to one page; then Anna reviews in the Doc.
- **Blocked / needs a decision:** D-005 (dataset emphasis) to be confirmed by the group.
- **For teammates:** @anna: the research question at the top of §1 in the Doc is a proposal; the last paragraph of §2 and §4 must say the same thing. @yassien: the verified dataset facts for §3 are in the Doc under §3 and in `sources.md` row S7.
- **Not pushed:** nothing.

## T-010 · Midterm §5 Preliminary Results
_Updated 2026-10-05 11:05 by Claude (cloud session) for Jamie · branch `jamie/T-010-preliminary-results` at `3b86da6`+1_

- **Now:** Loader, gait-event detection (20 N threshold on the per-foot total force, 0.1 s minimum phase), spatiotemporal features (stride, swing, stance timing, CV, cadence, asymmetry) and the two scripts (`scripts/make_table1.py`, `scripts/make_figure1.py`) are written and pushed. Jamie's download of the PhysioNet ZIP is in progress (61 of 288 MB at 11:04); the scripts have been run only on the 47 records available so far.
- **Validated:** on those 47 records: stride times 0.9 to 1.3 s, swing 29 to 37% of stride, at most 6 strides removed per record; stride time insensitive to the threshold (10, 20, 50 N). Figure 1 panel A inspected: markers sit on the force rise and fall. Usual walks so far (14 control, 9 PD): stride-time CV median 5.5% vs 7.1%, p = 0.14 (Mann-Whitney), swing-time asymmetry 1.5% vs 4.1%. **Not verified:** nothing on the full dataset; Table 1 not yet produced (demographics.txt is not among the files downloaded so far).
- **Next:** when the ZIP is complete: `sha256sum -c SHA256SUMS.txt`, run both scripts on the full data, commit `results/` and `figures/`, write §5 (about one page: Table 1, Figure 1, what they show, what changes, the main remaining limitation, the work left).
- **Blocked / needs a decision:** the download. A reminder is set for 12:25 to pick this up.
- **For teammates:** @anna @yassien: `src/gaitpdb` is the shared loader; build on it rather than re-reading the text files. Turns in the corridor inflate stride-time CV; tighter outlier rules are a known refinement, see the branch's commit message.
- **Not pushed:** nothing.

## T-016 · Onboarding without a terminal
_Updated 2026-10-05 11:05 by Claude (cloud session) for Jamie · branch `jamie/T-016-cowork-onboarding` at `8847d24`, pull request #1 open_

- **Now:** CONTRIBUTING.md rewritten for teammates who use GitHub Desktop and the Claude desktop app (no terminal); CLAUDE.md §4 step 3 and §10 adjusted. Pull request #1 is open with checks green.
- **Validated:** repo checks and GitHub Actions pass. **Not verified:** the GitHub Desktop steps have not been clicked through by a teammate.
- **Next:** Jamie merges #1 (the agent's merge was stopped by the no-merge-without-review rule), then marks T-016 done and deletes the branch.
- **Blocked / needs a decision:** none.
- **For teammates:** none.
- **Not pushed:** nothing.

## T-007 · Project structure
_Updated 2026-10-05 11:05 by Claude (cloud session) for Jamie · folded into the T-010 branch_

- **Now:** `src/`, `scripts/`, `requirements.txt`, `data/raw/README.md` (download steps, licence, checksum) exist on `jamie/T-010-preliminary-results`; `results/` and `figures/` are created by the scripts.
- **Validated:** `ruff check` and `ruff format` clean. **Not verified:** a fresh install from `requirements.txt` on Windows.
- **Next:** merge with T-010; then T-008 (README front page) can start.
- **Blocked / needs a decision:** none.
- **For teammates:** none.
- **Not pushed:** nothing.
