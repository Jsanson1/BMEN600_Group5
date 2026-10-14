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
_Updated 2026-10-14 16:04 by Claude (cloud session) for Jamie · text in the group's Word file (Anna's SharePoint); snapshots on `jamie/T-029-age-restriction` at `39bb841` (pull request #10)_

- **Now:** Jamie's sections are in the group's live Word file as of 14 October, about 15:00: Background and Research Gap (draft 6, 660 words), Preliminary Results (draft 6, 859 words, with Table I and the one-column Fig. 1), Data and Code Availability, AI-Assisted Work and Author Contributions (teammates' parts highlighted in yellow), and Jamie's 16 references ([S1] to [S18], still labelled) after Anna's. His affiliation now reads Hotchkiss Brain Institute. Claude pasted them through Word on Jamie's computer, with his approval, from `BMEN600_Jamie_sections_paste_source.docx` (v4 plus bookmarks around each block; the bookmarks were removed from the live file afterwards). Jamie's own verification sentence is in the last yellow spot of AI-Assisted Work (he is doing the three checks it describes: Table I and the main AUCs against the results files, and the sentences citing [S1], [S9] and [S12] against those papers). The review copy for Anna is `BMEN600_Midterm_review_copy_v5.docx` (26 comments on her Introduction and Methods; v5 adds what the reference and WearGait-PD checks found; the document body is identical to v4). Both are in Jamie's `Coursework\BMEN 600` folder, with `BMEN600_shared_doc_snapshot_2026-10-14.docx`, a copy of the live file saved right after the paste.
- **Validated:** the snapshot matches the expected result paragraph by paragraph (type, style and text): the file as downloaded on 13 October with Jamie's blocks in place of the template placeholders and his affiliation corrected, and nothing else changed except that one of the template's four empty lines in the reference list was absorbed during the paste. No comments, tracked changes or bookmarks came across; one figure, two tables. The renumbering script runs on it (citations [1] to [25]; it flags Anna's [AK4] slip and that [AK6] and [S18] are not cited yet), and it renders to 5 pages with Yassien's sections still placeholders. Earlier: every Preliminary Results number checked by script (32 checks) and by an independent review (about 130 numbers). **Not verified:** Anna's references AK1 to AK6 (search results confirm only that AK1, AK3, AK6 and the Cawley and Talbot entry exist under those titles); how Word lays out the final pages.
- **Next:** Jamie sends the group message (drafted 14 October in group-chat wording, sections named) with v5 attached; Jamie merges pull request #10 himself (this session's safety check refuses a merge without a teammate's review, so Claude cannot), Thursday evening at the latest; final pass Friday morning on a download of the live file: delete the template's leftover text (the cyan reference instructions, the empty numbered lines, the Eason and Maxwell sample entries, any remaining TEXT placeholders), run `python scripts/renumber_docx_citations.py final.docx -o final_numbered.docx`, check where Fig. 1 and Table I land and the 6-page limit, run `python scripts/check_submission.py final_numbered.docx --pdf final_numbered.pdf`, add the commit ID, submit by Friday 16 October 11:59 pm. Afterwards, copy any later wording changes back into the snapshots.
- **Blocked / needs a decision:** T-030 (the design that the Background, Methods and Preliminary Results assume) needs the group's confirmation; the WearGait-PD participant sheet is needed to check the "185 to 181" in Methods.
- **For teammates:** @anna: your references were checked on 14 October against PubMed, PMC, the publisher or the journal: AK1 to AK6 and the software entries exist as listed and support their sentences; [AK5]'s abstract does not name speed, stride length or variability (its open-access full text is on UNIL's repository and has not been read); small fixes: [AK2] is the June 2021 issue, [AK6] vol. 52, no. 6, November 2025, second author of [nestedCV] N. L. C. Talbot, a capital P in the titles of [AK1], [AK3], [AK5]. Also 26 comments on the Introduction and Methods in Jamie's review copy (v5, for the group chat), most importantly: the pre-processing paragraph describes MinMaxScaler and find_peaks while the shared code (and Preliminary Results) uses a 20 N threshold crossing; Methods says 10 repeats while the code uses 20; [AK5] and [AK4] in the Introduction should be [AK6] and [AK5]; the Introduction needs an explicit research question; the analysed PhysioNet cohort is 162, not 163 (JuCo10 has no recording). @yassien: the Dataset and Teamwork sections are still placeholders in the Word file; the verified dataset facts are under the Dataset heading in the Google Doc and in `sources.md` (S7, S9), and Table I covers the analysed participants.
- **Not pushed:** nothing.

## T-022 · Model comparison (scaffolding and baselines merged; the three-model comparison waits for T-019 and T-020)
_Updated 2026-10-14 10:10 by Claude (cloud session) for Jamie · branch `jamie/T-022-model-comparison` (merged into `main` on 9 October)_

- **Now:** `scripts/run_baselines.py` and `scripts/compare_models.py` are on `main`; pull request #10 reruns them on the 162 analysed participants. Pull requests #4 to #8 were merged locally into `main` on 9 October and are now closed on GitHub with a note.
- **Validated:** see T-029. **Not verified:** the SVM and random forest (not written).
- **Next:** when T-019 and T-020 write their result files through `write_model_outputs`, run `compare_models.py`. If the group confirms T-030, the comparison also needs the pooled and cross-cohort schemes (new code in `evaluation.py`, once for all three models) and sensitivity at 90% specificity (§4 asks for it; the code reports metrics at 0.5 only).
- **Blocked / needs a decision:** T-019 (Yassien), T-020 (Anna), T-030 (group).
- **For teammates:** @anna @yassien: your model appears in the comparison as soon as your script writes `results/<svm|rf>_{folds,cv_predictions,loso_predictions}.csv` through `write_model_outputs`.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (participant sheets in hand; sensor files not yet)
_Updated 2026-10-14 15:25 by Claude (cloud session) for Jamie · participant check on `jamie/T-029-age-restriction` (pull request #10)_

- **Now:** Jamie has a Synapse account (14 October). The two participant sheets of the "Version 1 (Cross-sectional)" folder (`PD - Demographic+Clinical - datasetV1.csv`, syn55105530 version 3; `CONTROLS - Demographic+Clinical - datasetV1.csv`, syn55105521 version 4) are in `data/raw/weargait_pd/` of Jamie's local clone (ignored by git; also still in his Downloads folder). `src/gaitpdb/weargait.py` reads them and `scripts/check_weargait_participants.py` gives 185 participants, four under 50 (NLS158, NLS159 with PD; WHC003, WHC005 controls), 181 analysed (98 PD, 83 controls). `data/raw/README.md` records the versions, MD5s and download date. The project also has a "Version 2 (Longitudinal)" folder (syn74686228) that the article does not describe.
- **Validated:** both files' MD5s match the checksums Synapse lists; counts, ages (PD 67.0 ± 8.3, controls 74.1 ± 9.2) and the patients' sexes match the article. **Not verified:** the controls sheet lists 47 women and 38 men where the article reports 48 and 37 (cause unknown); the sensor files, their columns and units (supplementary Table S5 not read); what Version 2 contains.
- **Next:** after the midterm: download the SelfPace sensor CSVs (ask Jamie first: name, source and size), write the loader for the insole total force, check the 20 N threshold against the walkway's foot contacts before any cross-cohort run. The board's due date (14 October) has passed; the milestone list in the Google Doc suggests Friday 23 October for the loader, which is Jamie's call.
- **Blocked / needs a decision:** T-030 (how WearGait-PD is used: combined, held out, or both).
- **For teammates:** whoever already has the WearGait-PD files: no need to send the participant sheets now; the sensor files can come later if that is quicker than downloading them.
- **Not pushed:** nothing.
