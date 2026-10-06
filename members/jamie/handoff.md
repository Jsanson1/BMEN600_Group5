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
_Updated 2026-10-06 12:40 by Claude (cloud session) for Jamie · branch `jamie/T-009-background-gap` at `cb62fba` · pull request #3 open_

- **Now:** Draft 4 (draft 3 trimmed by about a tenth for the page budget, about 1.1 pages; nothing cited removed) is in the shared Google Doc and in `report/midterm/02_background_and_research_gap.md`; pull request #3 (https://github.com/Jsanson1/BMEN600_Group5/pull/3) carries the snapshot and the 16-source ledger. Jamie read draft 3 and may still edit in the Doc.
- **Validated:** all 16 sources opened and checked on 2026-10-05 (`report/midterm/sources.md`; S15 and S16 are the README's two references, now verified so §1 can cite them). **Not verified:** not yet reviewed by Anna.
- **Next:** Anna reviews (in the Doc or on #3); Jamie edits in the Doc; once the wording settles, copy it back into the markdown on the branch, then merge #3, mark T-009 done, delete the branch.
- **Blocked / needs a decision:** none for the text. For the group on Friday: D-005 says WearGait-PD "if time allows"; §2 and §5 now commit to it as the external test set (Jamie: both datasets are used). D-005 needs a superseding entry once the group agrees.
- **For teammates:** @anna: the research question at the top of §1 in the Doc is a proposal, yours to settle; §4 decides the method and the last paragraph of §2 follows it (the note under §4 in the Doc lists what §2 currently says). The Project Timeline sheet still says "four models" in the §4 row; D-004 made it three. One conflict to settle in §1: the README says the gait patterns in PD "are not well understood" and cites Kim et al. 2018 for a PD-versus-control claim, but that paper has no healthy controls; §2 says the group-level changes are well established (S3 to S6). A reconciling wording is in the note under §1 in the Doc. @yassien: the verified dataset facts for §3 are in the Doc under §3 (updated today with the age discrepancy and the file quirks) and in `sources.md` row S7.
- **Not pushed:** nothing.

## T-010 · Midterm §5 Preliminary Results (with T-007)
_Updated 2026-10-06 13:18 by Claude (cloud session) for Jamie · branch `jamie/T-010-preliminary-results` at `e05c111` · pull request #2 open_

- **Now:** Pull request #2 carries four tasks on one line of commits (T-007, T-008, T-010, T-026; head `e05c111`, which also adds `scripts/check_dual_task.py`, the pipeline reproducing the published dual-task effect in the 21 Ga patients with both walks, and `scripts/verify_data.py`, a cross-platform checksum check), so the team has one code review to do before Friday. §5 draft 1 (about 760 words, Table 1, Figure 1; says that the proposal's named uncertainty, finding gait events from the force data alone, is resolved) is in the Google Doc and in `report/midterm/05_preliminary_results.md`; `results/` and `figures/` on the branch are the full-data run; pull request #2 (https://github.com/Jsanson1/BMEN600_Group5/pull/2) also carries the T-007 structure (`src/gaitpdb`, `scripts/`, `requirements.txt`, `data/raw/README.md`). Headline: swing-time asymmetry separates PD from controls (AUC 0.76, p 1.5e-8) far better than stride-time variability (AUC 0.60, p 0.026, and 0.58 within the 60 to 80 year band); controls are 2.6 years younger than patients although the PhysioNet page says 66.3 years for both.
- **Validated:** all 311 files match PhysioNet's SHA256SUMS; loader run on the real `demographics.txt` (166 rows); Figure 1 trace inspected; every number in §5 traced to `results/figure1_summary.txt`, `results/event_detection_checks.txt` or `results/table1_participants.md`; Doc table cells checked against the CSV by script; a fresh virtual environment (Python 3.13, Linux, `pip install -r requirements.txt`) reproduces every committed results file and the PNG byte for byte (`tabulate` was missing from `requirements.txt` and is now in). **Not verified:** the event detection against a reference system (none in the database); a fresh install on Windows or macOS; Jamie's and Anna's reading of the text.
- **Next:** a teammate reviews #2 (any of them; their agent can run the four scripts after unpacking the dataset per `data/raw/README.md`); Jamie edits §5 in the Doc; merge #2, mark T-007, T-008, T-010 and T-026 done, delete the four branches. Nobody had reviewed or written anything as of 2026-10-06 12:20.
- **Blocked / needs a decision:** none.
- **For teammates:** the project-phase rows of the Project Timeline sheet are now on the board as T-017 to T-025 with the sheet's leads, so your agents can claim them. @anna: T-017 (pre-processing) starts from the cleaning rules in `src/gaitpdb/events.py`; change them as you see fit, the scripts only need `record_features()` to keep returning one row per record. @yassien: T-018 (features, feature dictionary) starts from `src/gaitpdb/features.py` and `FEATURE_COLUMNS`. Both: `results/features_usual_walk_by_group.csv` has the single-feature AUCs on the usual walk; build on `src/gaitpdb` rather than re-reading the text files. @yassien: for §3, the demographics file gives the controls a mean age of 63.7 y (PD 66.3 y) while the PhysioNet page says 66.3 y for both; `demographics.txt` has ragged trailing tabs and 69 empty lines (the loader handles it); the quirks are listed in §5 of the Doc and in `data/raw/README.md`.
- **Not pushed:** nothing.

## T-026 · Data-quality report for §3 (Jamie's reviewer part of T-012)
_Updated 2026-10-06 12:22 by Claude (cloud session) for Jamie · branch `jamie/T-026-data-quality` at `d920207`, folded into pull request #2_

- **Now:** done; `scripts/check_data_quality.py` and `results/data_quality.{txt,csv}` are in pull request #2, and the findings are under §3 in the Doc for Yassien.
- **Validated:** ran on the full, checksum-verified data; flagged recordings inspected stride by stride. **Not verified:** ethics and consent statements of the three source papers (abstracts only); Yassien's reading of the note.
- **Next:** merges with #2; then mark done and delete the branch.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna: two behaviours for T-017 (pre-processing): shuffling with incomplete unloading (JuPt26 walks 03 to 07) and standing pauses (GaCo13_10); the current stride rules remove them, a lower contact threshold or an event definition based on the force slope may recover the strides.
- **Not pushed:** nothing.

## T-008 · README front page
_Updated 2026-10-06 12:22 by Claude (cloud session) for Jamie · branch `jamie/T-008-readme-front-page` at `ef109e8`, folded into pull request #2_

- **Now:** done; the README now has the research question, why it matters, both datasets with the correct PhysioNet link, the file map, how to run, results so far, the plan and verified references. The proposal-stage text (two candidate projects) is replaced; the alternative project is mentioned in one sentence with D-004.
- **Validated:** every factual sentence traced to `report/midterm/sources.md` or to a results file; the Figure 1 image renders from the repository path. **Not verified:** how it renders on GitHub after the merge (the image path assumes `figures/` is on `main`, which #2 provides); the team's view of the wording.
- **Next:** merges with #2; Anna may want the research-question paragraph to match her final §1 wording, which is a one-line follow-up.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna: the research question in the README is the working version from the Doc; tell Jamie if §1 changes it. The old README cited Kim et al. 2018 for a PD-versus-control claim; the new one does not cite it (see `sources.md` S16).
- **Not pushed:** nothing.

## T-021 · Logistic regression (with the shared evaluation for T-022)
_Updated 2026-10-06 13:18 by Claude (cloud session) for Jamie · branch `jamie/T-021-logistic-regression` at `1a3ef5b` · pull request #4 open (stacked on #2)_

- **Now:** `src/gaitpdb/evaluation.py` fixes the feature set, covariates, participant-grouped repeated cross-validation, leave-one-study-out and metrics for all three models; `scripts/run_logreg.py` is the logistic regression under it. Result on the usual walk: gait features alone AUC 0.81 (0.79 to 0.83) under 5x20 grouped CV, 0.73 (0.65 to 0.81) with each sub-study held out; age and sex alone 0.58; adding them leaves per-study AUCs unchanged but lowers the pooled out-of-study AUC to 0.66 (age differs between sub-studies). The assumption check (squared-term LR test) failed for raw swing-time asymmetry, so it enters as log(1 + x), which passes; Brier score and a calibration table are reported. §5 is now draft 2 on this branch and in the Doc: trimmed to about 650 words plus the table and figure, with the baseline paragraph and a sentence on the dual-task validation. `scripts/make_figure2.py` draws Figure 2, the evaluation design (participant-grouped CV, leave-one-study-out, external test) from the participant counts; it is offered to Anna for §4 in the Doc with a caption. `scripts/run_all.py` regenerates every output in one command (about five minutes); a full run reproduces every CSV, TXT and PNG byte for byte. T-022 stays `doing` for the comparison itself, which waits for T-019 and T-020.
- **Validated:** deterministic (two runs identical); inner tuning sees training participants only; odds ratios and VIFs sensible; linearity in the logit checked; in line with the published participant-level numbers (S14). **Not verified:** cued and dual-task walks unused for the model; no teammate review yet.
- **Next:** teammate review of #4 (any of them); merge after #2; mark T-021 done. Anna (T-020) and Yassien (T-019) write their model scripts in the shape of `run_logreg.py` and call the same `evaluate` and `loso_predictions`; then T-022 compiles the comparison.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: the pull request description says how to plug your model in; do not change `evaluation.py` for one model, ask and we change it once for all three. The feature table is `results/features_usual_walk.csv` (one row per participant); if T-017 or T-018 changes the features, re-run `make_figure1.py` and then every model script.
- **Not pushed:** nothing.

## T-027 · Unit tests for the shared code
_Updated 2026-10-06 13:05 by Claude (cloud session) for Jamie · branch `jamie/T-027-unit-tests` at `3d481a8`+merge · pull request #5 open (stacked on #4)_

- **Now:** twelve tests in `tests/` on synthetic signals (events, stride rules, loaders, demographics layout, grouped splits); `python -m pytest` passes in about two seconds; pytest added to `requirements-dev.txt`.
- **Validated:** all tests pass locally; ruff clean. **Not verified:** GitHub Actions does not run pytest (shared workflow file; needs the group's OK to add one line).
- **Next:** review and merge after #4; ask the group on Friday to add `python -m pytest` to `.github/workflows/checks.yml`.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: when T-017 or T-018 changes a rule in `events.py` or `features.py`, change the matching test on purpose in the same pull request.
- **Not pushed:** nothing.

## T-028 · Citation renumbering helper (for T-015)
_Updated 2026-10-06 13:10 by Claude (cloud session) for Jamie · branch `jamie/T-028-assembly-helper` at `5808fe0` · pull request #6 open (stacked on #3)_

- **Now:** `scripts/renumber_citations.py` turns [S#] citations into IEEE numbers in order of first citation and emits the reference list from `sources.md`; `report/midterm/README.md` says how to use it at assembly (export the Doc as plain text, run, paste back).
- **Validated:** on §5 followed by §2 (13 references, correct order, warnings for the uncited ledger rows). **Not verified:** the Doc's plain-text export.
- **Next:** merge after #3; use on 14 to 16 October when the sections are final.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: keep citing with S-numbers from `sources.md`; the renumbering is automatic at the end.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (preparation only)
_Updated 2026-10-06 13:30 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` at `d5118c5` · pull request #7 open_

- **Now:** Claimed for the parts that do not wait on T-022. The Scientific Data article describing WearGait-PD was read in full and turned into a section of `data/raw/README.md` (source, licence, how access works, participants, sites, the ten task codes, file layout, how we plan to use it, the authors' caveats) plus one sentence in the README plan; pull request #7 (https://github.com/Jsanson1/BMEN600_Group5/pull/7, stacked on #4). The same facts are in the Google Doc as notes under §3 (dataset facts and responsible use, for Yassien) and §4 (external test design, for Anna).
- **Validated:** every fact against the article text (doi 10.1038/s41597-026-06806-2) and its citation metadata on 2026-10-06. **Not verified:** the files themselves (nobody has a Synapse account yet), the column names and units (the article's Supplementary Table S5, not read), and my stride-count estimate for the short walkway passes.
- **Next:** a person registers at https://www.synapse.org (name, e-mail, the Synapse terms and the Synapse Pledge) and follows the "Data Access" tab of project syn52540892; downloads the "CSV files" folder and the clinical spreadsheets into `data/raw/weargait_pd/`; then a loader for the SelfPace (SP) files can be written against the real columns, cross-checked against the walkway's foot contacts, and the test runs once T-022 has the three models. A teammate reads #7.
- **Blocked / needs a decision:** the Synapse registration (a person, in their own name; Jamie or whoever the group agrees on Friday); the test itself waits for T-019, T-020 and T-022. The task was unowned ("owner to be agreed"); Jamie took the preparation so the midterm plan can describe the test concretely, and can hand the rest over at Friday's meeting.
- **For teammates:** @yassien: the WearGait-PD paragraph for §3 is under §3 in the Doc (ethics approvals, consent and licence are stated in the article, unlike PhysioNet). @anna: the external test design for §4 is under §4 in the Doc; the main limitation to state is that the controls there are older than the patients, the reverse of PhysioNet.
- **Not pushed:** nothing.
