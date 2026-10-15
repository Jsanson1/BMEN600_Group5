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
_Updated 2026-10-14 18:45 by Claude (cloud session) for Jamie · text in the group's Word file (Anna's SharePoint); snapshots on `main` (pull request #11 merged by Jamie on 14 October, `f6296b7`); `jamie/T-010-preliminary-results` kept for Friday's snapshot updates_

- **Now:** Jamie's sections are in the live Word file: Background and Research Gap, Preliminary Results (Fig. 1, Table I), Data and Code Availability, AI-Assisted Work (with Jamie's verification sentence), Author Contributions, and his references [S1] to [S18] after Anna's. On 14 October about 16:35, with Jamie's approval, Claude used Word on his computer to remove the template's leftover text (the four cyan instructions and an empty line under References, three empty numbered lines, the Eason and Maxwell samples, "©2026 IEEE" in the first-page footer) and, after Jamie said the Study column looked cut off, to add to the Table I note: "Study: PhysioNet’s labels for its three sub-studies, Ga [S4], Ju [S6] and Si [S5]." Pull request #11 (merged) put that sentence in `report/midterm/05_preliminary_results.md` and fixes `scripts/renumber_docx_citations.py`, which left labels that Word splits over several runs unnumbered ([pandasPaper, pandasZenodo] and [nestedCV] in Methods). Review copy for the group chat: `BMEN600_Midterm_review_copy_v6.docx` in Jamie's `Coursework\BMEN 600` folder, the live file's text as of 16:40 plus 26 comments on Anna's Introduction and Methods (v6 reports the [AK5] full-text and pandas checks). Jamie sent the group-chat message at 18:43 on 14 October (drafted by Claude, intro edited by Jamie, review copy v6 attached); it asks Anna to work through the comments, Yassien to write his two sections, everyone to fill in their highlighted spots by Thursday night, and the group to confirm the design (T-030).
- **Validated:** `BMEN600_shared_doc_snapshot_2026-10-14_cleaned.docx` (same folder, saved from the live file after the edits) differs from the 15:00 snapshot only by Jamie's sentence, the table note, the ten removed template paragraphs and the empty footer (paragraph-by-paragraph diff; 2 tables, 1 drawing and 3 section breaks unchanged; no comments, tracked changes or bookmarks; no teammate edits since 15:00). Word: 5 pages, the text before References fills 4 pages and two lines, so about 1.9 pages remain under the 6-page limit if page 1 counts. Friday's steps rehearsed on that copy: with the fixed script all 25 cited references are numbered, the output passes the Office XML validation, and `check_submission.py` lists only the open items (teammates' placeholders and highlights, [AK4], the commit ID). [AK5] (Burtscher 2024) full text read: it supports the gait sentence and the "too subtle for clinical observation" clause. **Not verified:** the pandas entries' DOI pages (rate-limited; checked against pandas' own citing page); how Word lays out the final pages once Yassien's sections are in.
- **Next:** Jamie: if not yet done, the three checks his AI-Assisted Work sentence states (Table I and the two AUCs against `results/table1_participants.md` and `results/logreg_summary.txt`; the sentences citing [S1], [S9] and [S12] against those papers), and a read of his sections in the live file. Watch the group chat for the design answer (T-030) and who submits on D2L; when the group confirms, append the decision to `DECISIONS.md`. Optional: the Delete branch button on pull request #10 (the merged `jamie/T-029-age-restriction`; this session is not allowed to delete branches). Thursday: review Yassien's Dataset and Teamwork sections and Anna's Methods changes; T-030. Friday, on a download of the live file: `python scripts/renumber_docx_citations.py final.docx -o final_numbered.docx`; place Fig. 1 (it currently jumps to the top of the right column on page 3, leaving about 2.7 in of the left column empty) and Table I; check the 6-page limit; copy any changed wording of Jamie's sections into `report/midterm/` on `jamie/T-010-preliminary-results`; put the commit ID of `main` into Data and Code Availability; `python scripts/check_submission.py final_numbered.docx --pdf final_numbered.pdf`; export the PDF; submit by 11:59 pm.
- **Blocked / needs a decision:** T-030 (the design that Background, Methods and Preliminary Results assume) needs the group's confirmation.
- **For teammates:** @anna: your references were all checked on 14 October and exist as listed and support their sentences; [AK5]'s full text supports both the gait sentence and the "too subtle for clinical observation" clause. Small fixes: [AK2] is the June 2021 issue; [AK6] vol. 52, no. 6, November 2025; [nestedCV]'s second author is N. L. C. Talbot; [pandasPaper] is in the proceedings of the 9th Python in Science Conference, with "Python" capitalised; a capital P in "Parkinson" in [AK1], [AK3], [AK5]; the pandas Zenodo entry should name the version used. The 26 comments in v6 cover the rest; most important: the pre-processing paragraph describes MinMaxScaler and find_peaks while the code and Preliminary Results use a 20 N threshold; Methods says 10 repeats, the code 20; [AK5] and [AK4] in the Introduction should be [AK6] and [AK5]; the Introduction needs an explicit research question; the analysed PhysioNet cohort is 162, not 163. @yassien: Dataset and Teamwork are still placeholders; the verified dataset facts are under the Dataset heading in the Google Doc and in `sources.md` (S7, S9); just under 2 pages are left for both sections plus any Methods additions.
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
