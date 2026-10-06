# Log: Jamie Sanson (`jamie`)

<!--
APPEND-ONLY HISTORY. Edited only by Jamie's agents, and only on main (CLAUDE.md sections 3 and 7).
Add new entries at the BOTTOM. Never edit or delete earlier entries.

Write one entry per session or per meaningful piece of work, including work done outside the
repo (reading papers, writing in the Google Doc, meetings). The paper's Author Contributions
and AI-Assisted Work sections are written from these entries, so be specific and honest.

Entry format:

### 2026-10-02 · T-007 · Short title
- **Did:** what was produced or decided, with file paths or pull request links.
- **CRediT roles:** any of Conceptualization, Data curation, Formal analysis, Investigation,
  Methodology, Project administration, Resources, Software, Supervision, Validation,
  Visualization, Writing – original draft, Writing – review & editing.
- **AI use:** which tool did what, and what the human decided or changed ("not yet reviewed
  by <name>" is an honest answer). "None" is fine.
- **Verified:** what was actually checked and how (ran X, opened the DOI of Y, compared Z
  against the raw signal). Say what is not verified yet.
-->

### 2026-10-02 · T-001, T-005 · Collaboration system bootstrapped; local clone moved out of OneDrive
- **Did:** Set up the repo's collaboration system (commits `f906e7c`, `9c6a7a7` on main): `CLAUDE.md` agent protocol, `CONTRIBUTING.md`, `TASKS.md` board, `DECISIONS.md` (D-002, D-003 proposed), `members/` handoff and log files, `/start` and `/handoff` skills, pre-commit hook + `tools/repo_checks.sh`, GitHub Actions `checks.yml`, ruff config, `.gitattributes`, `.claude/settings.json`. Added a GitHub ruleset on `main` (block force pushes, restrict deletions). Cloned the repo to `C:\Users\jamie\Documents\BMEN600_Group5` with the hook switched on (T-005, ruff install still to do).
- **CRediT roles:** Project administration, Software.
- **AI use:** Claude (cloud session linked to Jamie's PC) designed and wrote every file above from Jamie's one-line brief ("set up a good system for collaboration, maybe a handoff file"), ran the tests, created the ruleset through the browser and did the clone. Jamie chose the approach, granted the GitHub app access and the folder permissions, and had not yet reviewed the file contents line by line at the time of this entry.
- **Verified:** Local simulation with three clones against a local bare remote (51 checks: claim races, rebase conflicts, every hook rule, merge commits, CI modes, CRLF); a blind dry run by a separate agent acting as Anna (`/start T-007`, work, `/handoff`); GitHub Actions green on both commits; ruleset confirmed through the GitHub API (`deletion`, `non_fast_forward` on the default branch); the new clone passes `git fsck` and matches a fresh clone file for file. Not verified: the hook on Windows (Git Bash) and macOS has not been run by a teammate yet.

### 2026-10-05 · T-009, T-010, T-007 · Midterm §2 draft, dataset verification, board set up for the midterm
- **Did:** Added the midterm section tasks (T-009 to T-015) to `TASKS.md` from the Project Timeline sheet and claimed T-007, T-009, T-010. Verified both datasets: WearGait-PD (Sci Data 2026; Synapse, account required, CC BY 4.0) and PhysioNet Gait in PD v1.0.0 (open, ODC-By 1.0, 93 PD / 73 controls, 306 records); found that the README's "GaitPDB" DOI resolves to a Nature Health comment about PhysioNet rather than the dataset. Drafted §2 (`report/midterm/02_background_and_research_gap.md`, branch `jamie/T-009-background-gap`) with a ledger of 14 verified sources (`report/midterm/sources.md`). Found the closest prior work, Jin (Appl. Sci. 2026) and Choi et al. (Bioengineering 2026), both of which already do participant-level evaluation on this dataset, and framed the gap around gait-only features, uncertainty, cross-protocol and cross-cohort validation.
- **CRediT roles:** Investigation, Writing – original draft, Project administration.
- **AI use:** Claude (cloud session with the browser on Jamie's PC) ran the searches, read each source's record, wrote the ledger and the draft, and set up the board. Jamie supplied the responsibilities sheet and the dataset pointers; the draft is not yet reviewed by Jamie.
- **Verified:** each of the 14 sources opened and read on 2026-10-05 (PubMed or publisher page); dataset facts read from the PhysioNet page, `format.txt` and `demographics.txt`, and from the WearGait-PD article. Not verified: no data file has been opened yet; the analysis plan in the draft's last paragraph is provisional until the group confirms the research question.

### 2026-10-05 · T-009, T-010, T-016, T-002 · Google Doc, §2 draft 2, analysis code, onboarding for Cowork users
- **Did:** Created the shared Google Doc for the Midterm Research Plan with all required sections, leads, §2 draft 2 and the IEEE reference list. Recorded D-004 (project, three models, leads) and proposed D-005 (dataset emphasis); closed T-002 and T-005. Wrote `src/gaitpdb` (loader, gait events, features) and the Table 1 / Figure 1 scripts; ran them on the 47 records downloaded so far. Rewrote CONTRIBUTING.md for teammates who use GitHub Desktop and the Claude desktop app and opened pull request #1.
- **CRediT roles:** Software, Formal analysis, Writing – original draft, Project administration.
- **AI use:** Claude (cloud session with Jamie's PC linked) wrote the code, the drafts and the Doc, and verified the sources. Jamie reviewed §2 draft 1 (asked for plainer, less generic wording), answered the scoping questions, downloaded the dataset and connected Google Drive. Draft 2 and the code are not yet reviewed by Jamie.
- **Verified:** gait-event detection checked visually on one record and numerically on 47 (plausible stride and swing times, threshold sensitivity as expected). Not verified: anything on the full dataset; Table 1 not yet produced.

### 2026-10-05 · T-010, T-009 · §5 draft on partial data, stride rule, §2 draft 3 into the Doc
- **Did:** The PhysioNet download on Jamie's PC stalled at 234.5 of 288 MB, so the 237 intact recordings (checksums verified) were used for a provisional run. Found that a single double-length stride per record (a foot that never unloads below the threshold between two steps) doubled the stride-time CV and made its group comparison depend on the contact threshold; added a relative stride rule (0.7 to 1.3 x the record median) to `stride_table`, fixed cadence to count all strides, added a swing-time asymmetry panel to Figure 1 and a per-feature group comparison, and wrote `scripts/check_event_detection.py`. Drafted §5 (`report/midterm/05_preliminary_results.md`, provisional numbers flagged) and put it in the Google Doc with Table 1 as a real table. Replaced §2 draft 2 with draft 3 in the Doc in place. Commits `f764e83`, `53bc1d8`, `c4d198c` on `jamie/T-010-preliminary-results`.
- **CRediT roles:** Software, Formal analysis, Validation, Visualization, Writing – original draft.
- **AI use:** Claude (cloud session with Jamie's PC linked and the Google Docs connector) did all of the above. Jamie approved §2 draft 3 ("seems good, I'll be editing after") and asked for the work to proceed; he has not yet reviewed the code, the stride rule or §5.
- **Verified:** 240 of 240 downloaded files match `SHA256SUMS.txt`; Figure 1 trace inspected (markers on the force rise and fall, the turn at the end of the window excluded); with the new rule the stride-time CV changes by at most 0.15 percentage points between 10, 20 and 50 N and its AUC stays at 0.62 to 0.64 (`results/event_detection_checks.txt`, provisional). Not verified: anything on the full dataset; `load_demographics` on the real `demographics.txt`; the group-level numbers in §5 will change once the remaining 69 recordings are in.

### 2026-10-05 · T-010 · Loader checked against the real demographics file; provisional outputs and figure into the Doc
- **Did:** Fetched the real `demographics.txt` from PhysioNet through the browser on Jamie's PC (SHA-256 matches `SHA256SUMS.txt`) and found that `pd.read_csv` refuses it (26 to 30 fields per line, 69 empty lines); rewrote `load_demographics` to parse it by hand, Table 1 unchanged. Made the relative stride rule switchable so `scripts/check_event_detection.py` reproduces the no-rule numbers quoted in §5; added walking speed and cadence to the Figure 1 summary for the same reason. Committed the provisional `results/` and `figures/` (237 of 306 recordings) and put Figure 1 into the Google Doc. Commits `d8a9bb5`, `888c064`, `f2709a7` on `jamie/T-010-preliminary-results`.
- **CRediT roles:** Software, Data curation, Validation.
- **AI use:** Claude (cloud session with Jamie's PC linked) did all of it; Jamie has not yet reviewed it. The download of the remaining 69 recordings is waiting on Jamie.
- **Verified:** checksum of the fetched demographics file; loader output against the HTML table (identical counts, ages, sex, Hoehn and Yahr); every number in §5 traced to a line in `results/figure1_summary.txt`, `results/event_detection_checks.txt` or `results/table1_participants.md`. Not verified: the full dataset.

### 2026-10-05 · T-010, T-009, T-007 · Full-data run, §5 final numbers, pull requests #2 and #3
- **Did:** Jamie's restarted download completed at 14:39; verified all 311 files against `SHA256SUMS.txt`, ran `make_table1.py`, `make_figure1.py` and `check_event_detection.py` on all 306 recordings, committed `results/` and `figures/` (replacing the provisional run), updated every number in §5 (markdown and Google Doc, including the Table 1 cells and the figure image) and opened pull request #2 (T-010 with T-007) and pull request #3 (T-009). Final usual-walk numbers: 93 PD, 72 controls; swing-time asymmetry AUC 0.76; stride-time CV AUC 0.60 and 0.58 within the 60 to 80 year band.
- **CRediT roles:** Formal analysis, Software, Validation, Visualization, Writing – original draft.
- **AI use:** Claude (cloud session with Jamie's PC linked and the Google Docs connector) did the run, the text updates and the pull requests. Jamie restarted the download; he has not yet reviewed the code, the figures or §5.
- **Verified:** checksums of all 311 files; the Doc's Table 1 cells compared with `results/table1_participants.csv` by script; every number in the Doc text compared with the results files by script; the figure inspected. Not verified: the pull requests' CI runs were still queued when this entry was written.

### 2026-10-05 · T-009, T-010, board · Alignment with the Project Timeline sheet
- **Did:** Read the Project Timeline sheet and the Doc again: nobody else has written yet. Made the plan text consistent with Jamie's position that both datasets are used (WearGait-PD is now the external test set in §2 and §5, not an option), said in §5 that the proposal's named uncertainty (gait events from force data alone) is resolved, and reframed `src/gaitpdb` as the first version that the pre-processing task (Anna) and the feature task (Yassien) build on, in §5, in pull request #2 and in the Doc's notes under §3 and §4. Added the sheet's project-phase rows to the board as T-017 to T-025 with the sheet's leads (T-025, the WearGait-PD test, has no owner yet). Commits `eb0f49f` (T-009 branch), `99589ee` (T-010 branch).
- **CRediT roles:** Project administration, Writing – review & editing.
- **AI use:** Claude (cloud session) did all of it from Jamie's instruction to keep working and stay congruent with the team's plan; Jamie has not yet reviewed. The sheet's status column was not touched (it is the group's).
- **Verified:** the sheet was read on 2026-10-05 and the task owners on the board match its Lead column. Not verified: whether the teammates agree with the task split as mirrored; D-005 still says "if time allows".

### 2026-10-05 · T-010, T-009 · Fresh-install check, README references verified, notes for §1 and §6
- **Did:** Reproduced all three scripts from a clean virtual environment; found `tabulate` missing from `requirements.txt` (Table 1 would have failed on a teammate's machine) and added it; pinned the figure font and text hinting so the PNG is byte-identical across machines (commit `559859e`). Verified the README's two references (StatPearls; Kim et al. 2018) and added them to `sources.md` as S15 and S16 (commit `75bdbf7`); Kim et al. has no healthy control group, so the README sentence that cites it for a PD-versus-control claim needs rewording in §1. Added to the Doc: the two references, a note under §1 reconciling the README's "not well understood" with §2's "well established", and a suggested milestone schedule under §6 built from the course dates and the new board tasks, for Yassien to revise. Re-inserted the Figure 1 image from the new commit.
- **CRediT roles:** Validation, Software, Investigation, Project administration.
- **AI use:** Claude (cloud session with Jamie's PC linked) did all of it; Jamie has not yet reviewed. The two references were read in the browser on Jamie's PC (NCBI Bookshelf; dnd.or.kr).
- **Verified:** byte-for-byte comparison of the committed `results/` files and the PNG between the clean environment and the working one; the two references' authors, titles, venues and years against the publisher pages. Not verified: Windows or macOS installs; whether Anna and Yassien accept the notes left for them.

### 2026-10-05 · T-026 · Data-quality report for §3
- **Did:** Claimed T-026 (Jamie's "explore the data and report on quality issues" part of the Dataset section, as assigned in the Project Timeline sheet). Wrote `scripts/check_data_quality.py` and ran it on all 306 recordings; `results/data_quality.txt` holds the report and `results/data_quality_records.csv` one row per recording (commit `d920207` on `jamie/T-026-data-quality`). Put the findings under §3 in the Doc and corrected `data/raw/README.md` on the walk numbers (`9f3e320` on the T-010 branch). Added Jamie's input on the logistic regression to the §4 note, as the sheet asks of each model owner.
- **CRediT roles:** Data curation, Validation, Investigation.
- **AI use:** Claude (cloud session) wrote and ran the script and wrote the notes; Jamie has not yet reviewed. The PhysioNet page and `format.txt` were read in full for the walk-number question.
- **Verified:** every number in the §3 note comes from the script's output on the checksum-verified data; the flagged recordings were inspected stride by stride. Not verified: ethics and consent statements in the source papers (abstracts only); nothing has been run on Windows or macOS.

### 2026-10-06 · T-008, T-026, T-010 · README front page; one pull request for the code line
- **Did:** Claimed T-008 (unassigned, graded) and wrote the README front page (commit `ef109e8`): research question, why it matters (with the README's old misreading of Kim et al. 2018 removed), data access with the correct PhysioNet link, file map, how to run, results so far, plan, verified references. Folded the T-026 and T-008 branches into the T-010 line so pull request #2 is one review for the whole code side (T-007, T-008, T-010, T-026). Checked the Doc and the repository first: no teammate text or review since the Doc was created on 5 October.
- **CRediT roles:** Writing – original draft, Project administration.
- **AI use:** Claude (cloud session) wrote the README from the verified ledger and the results files, after Jamie said to keep working and get the project done; Jamie has not yet reviewed the text.
- **Verified:** each README claim against `sources.md` or a results file; the branch fast-forwards cleanly; GitHub checks on the pull request. Not verified: the README's rendering on GitHub before the merge; the team's view of the wording.

### 2026-10-06 · T-021, T-022 · Shared evaluation harness and the logistic regression baseline
- **Did:** Claimed T-021 and the shared-splits part of T-022. Wrote `src/gaitpdb/evaluation.py` (features, covariates, participant-grouped repeated CV, leave-one-study-out, metrics, intervals) and `scripts/run_logreg.py`; ran it on the usual walk of 165 participants (commits `162d951`, `57acb0a`, `65b1eaf`); opened pull request #4, stacked on #2. Added the baseline paragraph to §5 in the markdown and the Doc. Headline: gait-only AUC 0.81 within protocol, 0.72 across protocols; age and sex alone 0.58; swing-time asymmetry and swing fraction dominate.
- **CRediT roles:** Methodology, Software, Formal analysis, Writing – original draft.
- **AI use:** Claude (cloud session) designed and wrote the harness and the script, ran them and wrote the paragraph, after Jamie said to keep working and get the project done; Jamie has not yet reviewed the design (feature set, folds, metrics) or the text.
- **Verified:** determinism (two runs identical); the guard against several rows per participant; the numbers against the published participant-level results in S14; ruff and repo checks. Not verified: calibration of the predicted probabilities; teammate review.

### 2026-10-06 · Doc · Group-section drafts and the §4 note on the evaluation code
- **Did:** In the Doc: told §4 that the evaluation now exists as code and listed the software; drafted the Data and Code Availability paragraph and Jamie's parts of AI-Assisted Work and Author Contributions (from this log), marked as drafts for the others to add to.
- **CRediT roles:** Writing – original draft.
- **AI use:** Claude (cloud session) drafted them from the repository's own records; Jamie to confirm what he verified himself (a bracketed prompt is left in the AI-Assisted Work draft).
- **Verified:** the facts in the drafts (licences, Synapse ID, checksum match, clean-environment reproduction) against sources.md and this log. Not verified: Jamie's own review.

### 2026-10-06 · T-009, T-010, T-021 · Page-budget trims, dual-task validation, rubric status
- **Did:** Read the assignment rubric again and put a status line against its eight criteria at the top of the Doc (to be deleted before submission). Trimmed §2 to about 1.1 pages (draft 4, `cb62fba`) and §5 to about 650 words plus the table and figure (draft 2, `02c6bc2`, `ade87b8`), in the markdown and the Doc, without removing any cited claim or number. Wrote `scripts/check_dual_task.py` (`4384dab`): in the 21 Ga patients recorded with and without the counting task, stride-time variability and swing-time asymmetry rise under the dual task (p = 0.006 each), as the source study reported, which validates the event detection against a published finding; only 6 control dual-task walks exist in the database, so the control side is untestable. One sentence on it in §5. Added the platform line to the README.
- **CRediT roles:** Writing – review & editing, Validation, Software.
- **AI use:** Claude (cloud session) did the trims, the script and the status line; Jamie has not yet reviewed. The trims keep Jamie's register from draft 3 and every verified number.
- **Verified:** the Doc's §2 and §5 compared paragraph by paragraph with the markdown by script (identical); the dual-task numbers come from the script on the checksum-verified data. Not verified: the page count in the assembled PDF (estimated from characters); Jamie's and Anna's reading.

### 2026-10-06 · T-027, T-021 · Unit tests; calibration of the baseline
- **Did:** Added the Brier score to the shared metrics and a calibration table to the baseline script (`c5e9e8c` on the T-021 branch; the out-of-fold probabilities are reasonably calibrated). Claimed T-027 and wrote twelve unit tests on synthetic signals for the event detection, stride rules, loaders, demographics parsing and the grouped splits (`3d481a8`, pull request #5, stacked on #4); pytest added to `requirements-dev.txt`; README says how to run them.
- **CRediT roles:** Software, Validation.
- **AI use:** Claude (cloud session) wrote the tests and the calibration code; Jamie has not yet reviewed them.
- **Verified:** the tests pass; the baseline re-run reproduces the earlier numbers exactly with the new metric added. Not verified: pytest in GitHub Actions (shared workflow; the group's call).

### 2026-10-06 · T-021 · Assumption check and the log transform of asymmetry
- **Did:** Added the linearity-in-the-logit check the sheet asks of the regression owner (squared-term likelihood-ratio test per input). Raw swing-time asymmetry failed it (p 0.004); it now enters the model as log(1 + x), which passes (p 0.66) and improves the fit: gait-only AUC 0.81 within protocol, 0.73 across (per study 0.81, 0.75, 0.71). Found that adding age and sex leaves per-study AUCs unchanged but lowers the pooled out-of-study AUC to 0.66, because age differs between sub-studies (`698f968`). Updated §5 (markdown and Doc), the README's results line and pull request #4.
- **CRediT roles:** Formal analysis, Methodology, Software.
- **AI use:** Claude (cloud session) ran the check, chose the transform and wrote the text; Jamie has not yet reviewed. The transform was adopted because a stated assumption check failed, not because it raised the score.
- **Verified:** the check passes after the transform; the numbers in §5 match `results/logreg_summary.txt`. Not verified: teammate review.

### 2026-10-06 · T-021 · Figure 2, the evaluation design
- **Did:** `scripts/make_figure2.py` draws the three levels of evaluation (within protocol, across protocols, across cohorts) from the participant counts in the data (`53fe00d`); placed in the Doc under §4 with a caption as an option for Anna's section, since the assignment recommends figures that explain decisions.
- **CRediT roles:** Visualization.
- **AI use:** Claude (cloud session) designed and drew it; Jamie has not yet reviewed.
- **Verified:** counts in the figure come from `build_manifest` on the checksum-verified data; the WearGait-PD counts from `sources.md` S9. Not verified: whether Anna wants it in §4.

### 2026-10-06 · T-028 · Citation renumbering helper
- **Did:** Claimed T-028 and wrote `scripts/renumber_citations.py` with a note in `report/midterm/README.md` (`5808fe0`, pull request #6, stacked on #3).
- **CRediT roles:** Software, Project administration.
- **AI use:** Claude (cloud session) wrote and tested it; Jamie has not yet reviewed.
- **Verified:** run on the two drafted sections. Not verified: the Google Doc's plain-text export.

### 2026-10-06 · T-010, T-021 · One-command reproduction and a cross-platform checksum check
- **Did:** `scripts/verify_data.py` (checksums on any platform; the data README now points at it) on the T-010 line (`e05c111`); `scripts/run_all.py` on the T-021 line (`1a3ef5b`), which runs the eight scripts in order. A full run on the committed data changed nothing but the PDFs' creation dates.
- **CRediT roles:** Software, Validation.
- **AI use:** Claude (cloud session); Jamie has not yet reviewed.
- **Verified:** the full run and `git status` afterwards (only the two PDFs differ, by metadata). Not verified: the run on Windows or macOS.

### 2026-10-06 · T-025 · WearGait-PD: access, contents and external-test plan documented
- **Did:** Claimed T-025 for the preparation (the test waits for T-022). Read the WearGait-PD data descriptor in full and wrote the second dataset's section of `data/raw/README.md` (access via Synapse, CC BY 4.0, participants and sites, task codes, file layout, how the SelfPace files will go through our event detection with the walkway contacts as a check, the authors' caveats on insole-to-walkway alignment, NaN padding and partial data loss) and a sentence in the README plan (`d5118c5`, pull request #7). Added the dataset facts under §3 and the test design under §4 of the Google Doc.
- **CRediT roles:** Data curation, Writing (original draft).
- **AI use:** Claude (cloud session) read the article in the built-in browser, drafted the text and the Doc notes; Jamie has not yet reviewed.
- **Verified:** each statement against the article's text and citation metadata on the day. Not verified: the data files (no Synapse account yet; the registration must be done by a person), the column definitions in the supplement, and the stride-count estimate for the 16 ft walkway passes.

### 2026-10-06 · T-021, T-022, T-027, T-009 · Corrected intervals, baselines and the model comparison
- **Did:** Replaced the cross-validation interval (the spread of the 20 repeat means, which ignores that folds share training participants) with the Nadeau and Bengio corrected interval: gait-only AUC 0.81, 95% CI 0.75 to 0.87 (`9871d07` on the T-021 branch, pull request #4). Added to `src/gaitpdb/evaluation.py` what the comparison and the other models need: `evaluate_model`, `write_model_outputs`, `corrected_ttest`, `paired_bootstrap_auc`, `rank_auc`, and the shared split settings and log transform (`d33a300`, `f8621fb`). Wrote `scripts/run_baselines.py` and `scripts/compare_models.py` with Figure 3 (`a895ced`, pull request #8): swing-time asymmetry alone gives 0.76 within and 0.75 across protocols, the six-feature regression 0.81 and 0.73 (drop 0.08, 0.04 to 0.13), so its gain within a protocol (+0.054, -0.002 to +0.111) does not carry across (-0.021, -0.078 to +0.039). Seven unit tests for the new functions (`58ad0c3`, #5). §5 draft 3 in the markdown and the Doc, with the corrected interval, the single-feature comparison and two rounding fixes (0.80 not 0.81; odds ratio 1.95 not 2.0); S17 and S18 added to `sources.md` (`ea9293b`, #3) and the Doc's reference list; the §4 note in the Doc now describes the comparison method for Anna.
- **CRediT roles:** Formal analysis, Methodology, Software, Validation, Visualization, Writing – review & editing.
- **AI use:** Claude (cloud session) chose the corrected interval and the paired tests, found the two rounding slips while checking §5, wrote the code, the tests, the figure and the text changes; Jamie has not yet reviewed any of it.
- **Verified:** the logistic regression's fold metrics and out-of-study predictions are identical to the files before these changes (checked column by column); `rank_auc` matches `roc_auc_score` to 2e-16 on 3000 random cases; the comparison is byte-identical across two runs and stops when folds or participants differ (tested by corrupting a copy); all 19 tests pass; S18 read in full, S17's record checked and its method read in the authors' 1999 conference paper and in S18 (the 2003 article itself not opened); every number in §5 rechecked against its results file at full precision. Not verified: the comparison with the SVM and random forest, which do not exist yet; teammate review.

### 2026-10-06 · T-021, T-022 · Independent review; penalty tuned by log-loss; numbers in the previous entry superseded
- **Did:** Had a separate agent, which had not seen the work, review the comparison statistics, the scripts and every number in §5. It confirmed the corrected interval, the paired tests, the Holm values and the drop by hand, and found three problems, all fixed: (1) the regression's penalty was tuned on AUC, which ignores the scale of the coefficients, so C ranged from 0.001 to 100 across folds and the leave-one-study-out models predicted on different scales, pulling down the pooled cross-protocol AUC; it is now tuned on log-loss (`06bbe94`); (2) the odds ratios quoted in §5 came from the fit with age and sex, not the six-feature model the sentence describes; both fits are now reported, labelled; (3) "at most a small gain" overstated what the interval supports. Reran the comparison (`feff7ae`) and rewrote §5 (draft 4, `0941d06`), the README, the Doc's §5 and §4 note, and pull requests #4 and #8. The numbers in the previous entry are superseded: within protocol 0.81 (0.75 to 0.88), across protocols 0.76 (0.68 to 0.83), drop 0.057 (0.025 to 0.093); gain over swing-time asymmetry alone +0.057 (+0.002 to +0.113) within and +0.005 (-0.049 to +0.065) across; age and sex add nothing, so the earlier explanation that age lowered the pooled cross-protocol AUC to 0.66 was an artefact of the tuning and is withdrawn.
- **CRediT roles:** Validation, Formal analysis, Software, Writing – review & editing.
- **AI use:** Claude (cloud session) ran the review through a separate subagent, checked each finding itself before acting (the spread of chosen C values and the prediction scales of the held-out models were reproduced), made the fixes and rewrote the text; Jamie has not yet reviewed.
- **Verified:** a fresh virtual environment built from `requirements.txt` reproduces every logreg, baseline and comparison output byte for byte; the Doc's §5 matches the markdown paragraph by paragraph; all numbers in §5 checked against the results files at full precision. Not verified: teammate review.
