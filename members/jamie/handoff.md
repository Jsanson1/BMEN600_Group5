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
_Updated 2026-10-16 13:40 by Claude (cloud session) for Jamie · the agreed Word file (Anna's SharePoint, sourcedoc E5A3FEFB-335B-4130-9847-77BA96948D21); pull request #13 open from `jamie/T-010-preliminary-results` at `fa5c202`, checks green_

- **Now:** the group agreed (12:42) to submit from the Word file at https://uofc-my.sharepoint.com/:w:/r/personal/anna_klygina_ucalgary_ca/_layouts/15/doc2.aspx?sourcedoc=%7BE5A3FEFB-335B-4130-9847-77BA96948D21%7D&file=BMEN%20600%20Midterm%20Research%20Plan.docx. Its 12:58 state (snapshot `BMEN600_agreed_doc_2026-10-16_1258.docx` in Jamie's Downloads) has Anna's Methods revision, Yassien's fixes and both teammates' statements. At Jamie's request ("get it done", 13:02) Claude made 22 text replacements in that file through Word for the web (Find and Replace, one match each): research question "tested on", the rigidity sentence, the software paragraph, Data Cleaning wording, the body-weight sentence and duplicate standardising clause removed from Pre-Processing, the evaluation paragraph's three input sets and single description of the cross-dataset test (gaitpdb throughout), Modelling "from these inputs", the Statistical Analysis sentence and prevalence wording with [6], Comparisons typos, and the AI-Assisted Work log sentence (Yassien's log only) plus Jamie's "wording adopted in parts of Section IV". Pull request #13 carries `024c9ff`, `8aaa1bb` and `fa5c202` (snapshots of Sections II, V and the end statements; the body-weight threshold check).
- **Validated:** before the edits each search string occurred exactly once in the saved file; afterwards none remain, each replacement occurs once, and exactly the 11 expected paragraphs changed, each matching the expected text by hash. LibreOffice render of the 12:58 file: the body ends about a third of the way down page 6. Equations 1 and 2 (PPV, NPV) are correct. Reference [5] (Burtscher 2024) supports the moved sentence on subtle early changes. **Not verified:** reference [3] for the early-onset sentence; whether the Synapse terms allow the team's private Kaggle copies; Word's own page layout.
- **Next:** (1) Jamie tells the group the edits are in. (2) Jamie does the three checks his verification sentence states (Table II against `results/table1_participants.md`; AUCs 0.82 and 0.77 against lines 18 and 33 of `results/logreg_summary.txt`; the sentences citing [7], [17], [19] against Rizzo 2016, the WearGait-PD article and Saeb 2017). (3) Jamie merges pull request #13. (4) Put `main`'s merge commit into Data and Code Availability in place of "[commit ID, filled in at submission]" and remove its yellow highlight. (5) Delete Anna's two comments (both answered in the group chat). (6) Export the PDF from Word, run `python scripts/check_submission.py <docx> --pdf <pdf>` (the "Fig. 4" note is Fig. 4A of [17], not ours), check pages, submit by 11:59 pm.
- **Blocked / needs a decision:** who submits; Jamie merges pull request #13 (this session cannot merge).
- **For teammates:** @anna @yassien: the agreed file now has the fixes from Jamie's 1 pm list. @anna: members/anna/log.md has no entries yet, so the AI-Assisted Work sentence names only Yassien's log; add an entry when you can.
- **Not pushed:** nothing.

## T-022 · Model comparison (scaffolding and baselines merged; the three-model comparison waits for T-019 and T-020)
_Updated 2026-10-16 10:00 by Claude (cloud session) for Jamie (D-007 noted; otherwise as of 2026-10-14 10:10) · branch `jamie/T-022-model-comparison` (merged into `main` on 9 October)_

- **Now:** `scripts/run_baselines.py` and `scripts/compare_models.py` are on `main`; pull request #10 (merged 14 October) reran them on the 162 analysed participants. Pull requests #4 to #8 were merged locally into `main` on 9 October and are now closed on GitHub with a note.
- **Validated:** see the T-029 entries in `log.md` (13 and 14 October). **Not verified:** the SVM and random forest (not written).
- **Next:** when T-019 and T-020 write their result files through `write_model_outputs`, run `compare_models.py`. Under D-007 (T-030), the comparison also needs the pooled and cross-cohort schemes (new code in `evaluation.py`, once for all three models) and sensitivity at 90% specificity (§4 asks for it; the code reports metrics at 0.5 only).
- **Blocked / needs a decision:** T-019 (Yassien), T-020 (Anna).
- **For teammates:** @anna @yassien: your model appears in the comparison as soon as your script writes `results/<svm|rf>_{folds,cv_predictions,loso_predictions}.csv` through `write_model_outputs`.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (participant sheets in hand; sensor files not yet)
_Updated 2026-10-16 10:00 by Claude (cloud session) for Jamie (D-007 noted; otherwise as of 2026-10-14 15:25) · participant check on `main` (pull request #10, merged 14 October)_

- **Now:** Jamie has a Synapse account (14 October). The two participant sheets of the "Version 1 (Cross-sectional)" folder (`PD - Demographic+Clinical - datasetV1.csv`, syn55105530 version 3; `CONTROLS - Demographic+Clinical - datasetV1.csv`, syn55105521 version 4) are in `data/raw/weargait_pd/` of Jamie's local clone (ignored by git; also still in his Downloads folder). `src/gaitpdb/weargait.py` reads them and `scripts/check_weargait_participants.py` gives 185 participants, four under 50 (NLS158, NLS159 with PD; WHC003, WHC005 controls), 181 analysed (98 PD, 83 controls). `data/raw/README.md` records the versions, MD5s and download date. The project also has a "Version 2 (Longitudinal)" folder (syn74686228) that the article does not describe.
- **Validated:** both files' MD5s match the checksums Synapse lists; counts, ages (PD 67.0 ± 8.3, controls 74.1 ± 9.2) and the patients' sexes match the article. **Not verified:** the controls sheet lists 47 women and 38 men where the article reports 48 and 37 (cause unknown); the sensor files, their columns and units (supplementary Table S5 not read); what Version 2 contains.
- **Next:** after the midterm: download the SelfPace sensor CSVs (ask Jamie first: name, source and size), write the loader for the insole total force, check the 20 N threshold against the walkway's foot contacts before any cross-cohort run. The board's due date (14 October) has passed; the milestone list in the Google Doc suggests Friday 23 October for the loader, which is Jamie's call.
- **Blocked / needs a decision:** none; D-007 (16 October) uses WearGait-PD both in the combined analysis and as the cross-cohort test set.
- **For teammates:** whoever already has the WearGait-PD files: no need to send the participant sheets now; the sensor files can come later if that is quicker than downloading them.
- **Not pushed:** nothing.
