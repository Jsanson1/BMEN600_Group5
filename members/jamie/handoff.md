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

## T-009, T-010 · Midterm Background and Preliminary Results (and the three end statements) in the group's Word file
_Updated 2026-10-15 15:46 by Claude (cloud session) for Jamie · text in the group's Word file (Anna's SharePoint); pull request #12 merged by Jamie on 15 October; `jamie/T-010-preliminary-results` at `024c9ff`, one commit not yet in a pull request_

- **Now:** the shared file as of 13:05 on 15 October (copy: `BMEN600_shared_doc_2026-10-15_1305.docx` in Jamie's `Coursework\BMEN 600` folder) has Yassien's Dataset and Responsible Use (with a new Table I of both datasets' characteristics) and Teamwork and Project Plan (with a milestone Table III); Jamie's table is now Table II, and every mention of it was updated. All citations were renumbered by hand in the file (labels gone; references [20], Frenkel-Toledo 2005 Mov. Disord., and [21], the WearGait-PD Synapse dataset, added; 28 entries), which also fixed Anna's two label slips. Nothing else in Jamie's sections changed. Methods is not yet revised (still 10 repeats, MinMaxScaler and find_peaks, no research question). Jamie's group message of 14 October was sent (the attachment failed and was re-sent on 15 October with v6). Pull request #12 (merged) extends `scripts/check_submission.py` for numbered citations and [DATE] placeholders. Commit `024c9ff` on `jamie/T-010-preliminary-results`, not yet in a pull request, renames Table I to Table II in the snapshots, puts Jamie's verification sentence into `07_statements.md` and adds S19 and S20 (Yassien's two new references) to `sources.md`; open its pull request on Friday together with any later wording changes.
- **Validated:** every renumbered citation compared with the 14 October labelled copy (each number points to its label's paper; first citations run 1 to 28 in order; every entry cited). Yassien's facts checked against the WearGait-PD article (nature.com; physician-diagnosed PD, Moticon OpenGo, insole-walkway delay, IRBs and consent, controls with essential tremor), `data/raw/README.md`, the two participant sheets, the PhysioNet page (idiopathic PD, Pollard et al. as the requested citation, no ethics or medication statement), Europe PMC (the treadmill paper) and DataCite (the Synapse DOI). Problems found, drafted for Jamie to send to Yassien: three [DATE] spots (PhysioNet downloaded 5 October 2026, WearGait-PD accessed 14 October 2026); [21] year 2024 and registered title "Wearables for gait in Parkinson's Disease and age-matched controls"; [20] title "...as an external pacemaker...", Sep. 2005, doi 10.1002/mds.20507; the sheets give years since DBS surgery, not dates; one visit per participant in Version 1; the "team's Kaggle copies" claim to confirm or cut; the final is due 4 December 2026; Table III gives the WearGait-PD loader to Anna while T-025 is Jamie's; the final presentation is missing from Table III. Length (LibreOffice and Word): 6 pages, References start about a fifth of the way down page 6. Correction at 15:50: turning is an annotated activity after all (Fig. 4A of the article labels Standing, Walking, Turning and a freezing episode, as Yassien pointed out), so his sentence on turns stands; the same figure plots the insole force in newtons. **Not verified:** WearGait-PD's supplementary tables (full annotation list, insole column units in the files).
- **Next:** Jamie sent the fixes to Yassien (15 October). Jamie, before submission: the three checks his AI-Assisted Work sentence states, with the citations now numbered [7], [17] and [19] (formerly S1, S9, S12): Table II against `results/table1_participants.md`, the AUCs 0.82 and 0.77 against lines 18 and 33 of `results/logreg_summary.txt`, and the seven sentences in Sections II and V citing [7], [17] or [19] against Rizzo 2016, Anderson 2026 and Saeb 2017. When Anna and Yassien are done (Thursday night): save a fresh copy, rerun the label-to-number check against this copy for any new citation, review Methods against the code (20 repeats, 20 N threshold) and the design sentence once T-030 is settled. Friday, on a download of the live file: no renumbering (the file carries numbers); place Fig. 1 and the tables; check the 6-page limit; copy any changed wording of Jamie's sections (and the Table II name) into `report/midterm/` on `jamie/T-010-preliminary-results`; put the commit ID of `main` into Data and Code Availability; `python scripts/check_submission.py final.docx --pdf final.pdf`; export the PDF; submit by 11:59 pm. Optional: Delete branch on pull request #10.
- **Blocked / needs a decision:** T-030 (the evaluation design) is being discussed in the group chat; Background, Dataset, Preliminary Results and Teamwork assume the combined analysis plus the cross-dataset test. Who leads the WearGait-PD loader (Table III says Anna, the board says Jamie) needs agreeing.
- **For teammates:** @yassien: the fixes listed under Validated (sent by Jamie in the group chat on 15 October). @anna: Methods still needs 20 repeats, the 20 N threshold wording and a research question (comments in v6); the citations are now numbers, so a new citation means shifting the later numbers by hand.
- **Not pushed:** nothing.

## T-022 · Model comparison (scaffolding and baselines merged; the three-model comparison waits for T-019 and T-020)
_Updated 2026-10-14 10:10 by Claude (cloud session) for Jamie · branch `jamie/T-022-model-comparison` (merged into `main` on 9 October)_

- **Now:** `scripts/run_baselines.py` and `scripts/compare_models.py` are on `main`; pull request #10 (merged 14 October) reran them on the 162 analysed participants. Pull requests #4 to #8 were merged locally into `main` on 9 October and are now closed on GitHub with a note.
- **Validated:** see the T-029 entries in `log.md` (13 and 14 October). **Not verified:** the SVM and random forest (not written).
- **Next:** when T-019 and T-020 write their result files through `write_model_outputs`, run `compare_models.py`. If the group confirms T-030, the comparison also needs the pooled and cross-cohort schemes (new code in `evaluation.py`, once for all three models) and sensitivity at 90% specificity (§4 asks for it; the code reports metrics at 0.5 only).
- **Blocked / needs a decision:** T-019 (Yassien), T-020 (Anna), T-030 (group).
- **For teammates:** @anna @yassien: your model appears in the comparison as soon as your script writes `results/<svm|rf>_{folds,cv_predictions,loso_predictions}.csv` through `write_model_outputs`.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (participant sheets in hand; sensor files not yet)
_Updated 2026-10-14 15:25 by Claude (cloud session) for Jamie · participant check on `main` (pull request #10, merged 14 October)_

- **Now:** Jamie has a Synapse account (14 October). The two participant sheets of the "Version 1 (Cross-sectional)" folder (`PD - Demographic+Clinical - datasetV1.csv`, syn55105530 version 3; `CONTROLS - Demographic+Clinical - datasetV1.csv`, syn55105521 version 4) are in `data/raw/weargait_pd/` of Jamie's local clone (ignored by git; also still in his Downloads folder). `src/gaitpdb/weargait.py` reads them and `scripts/check_weargait_participants.py` gives 185 participants, four under 50 (NLS158, NLS159 with PD; WHC003, WHC005 controls), 181 analysed (98 PD, 83 controls). `data/raw/README.md` records the versions, MD5s and download date. The project also has a "Version 2 (Longitudinal)" folder (syn74686228) that the article does not describe.
- **Validated:** both files' MD5s match the checksums Synapse lists; counts, ages (PD 67.0 ± 8.3, controls 74.1 ± 9.2) and the patients' sexes match the article. **Not verified:** the controls sheet lists 47 women and 38 men where the article reports 48 and 37 (cause unknown); the sensor files, their columns and units (supplementary Table S5 not read); what Version 2 contains.
- **Next:** after the midterm: download the SelfPace sensor CSVs (ask Jamie first: name, source and size), write the loader for the insole total force, check the 20 N threshold against the walkway's foot contacts before any cross-cohort run. The board's due date (14 October) has passed; the milestone list in the Google Doc suggests Friday 23 October for the loader, which is Jamie's call.
- **Blocked / needs a decision:** T-030 (how WearGait-PD is used: combined, held out, or both).
- **For teammates:** whoever already has the WearGait-PD files: no need to send the participant sheets now; the sensor files can come later if that is quicker than downloading them.
- **Not pushed:** nothing.
