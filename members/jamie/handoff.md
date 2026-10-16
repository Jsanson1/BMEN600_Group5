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
_Updated 2026-10-16 10:00 by Claude (cloud session) for Jamie · text in the group's Word file (Anna's SharePoint); `jamie/T-010-preliminary-results` at `8aaa1bb` (pushed), commits `024c9ff` and `8aaa1bb` not yet in a pull request_

- **Now:** Jamie's copy of the shared file saved at 09:31 on 16 October (`BMEN600_shared_doc_2026-10-16.docx` in `Coursework\BMEN 600`) has exactly the same text as the 13:05 copy of 15 October. Methods is unrevised (MinMaxScaler, find_peaks, 10 repeats, "SciPy for signal processing", age and BMI, only the combined analysis, no method for PPV and NPV at low prevalence); Yassien's three [DATE]s and the rest of the 15 October list are not in; both teammates' AI-use and contributions lines are placeholders. At about 09:49 Jamie sent the group a reply to Yassien's overnight points (design agreed; body-weight threshold tested; scaling; 5 folds repeated 20 times; his Claude's three comments confirmed) and a nine-point Methods list for Anna with suggested wording, asking for all edits by 4 pm. The design is recorded as D-007 (T-030 done, `98a6722`). Commit `8aaa1bb` adds thresholds as a share of body weight and of each recording's force to `scripts/check_event_detection.py`; the six existing rows are unchanged.
- **Validated:** Yassien's points against the code (`events.py`, `evaluation.py`, StandardScaler inside the model pipelines), the data (weight recorded for 159 of 162 analysed PhysioNet participants and all 185 in WearGait-PD) and the WearGait-PD article (Technical Validation: insole forces normalised to body weight for the averaged waveforms; walkway foot-contact signals); age and sex alone AUC 0.59 (`results/model_comparison.md`); the age gaps (`results/table1_participants.md`, `results/weargait_participants.txt`); `scripts/run_all.py` exists. New check (`results/event_detection_checks.txt`): 2.5% and 5% of body weight give swing-time asymmetry AUC 0.76, as 20 N does on the same 159; 20 N is 1.9 to 4.3% of body weight; 2.5% of the recording's force level gives 0.80, which is why the suggested Methods picks the threshold by agreement with the walkway, not by AUC. Full `run_all.py` rerun (377 s) changed only the event-detection outputs (and the PDF creation dates, restored); 32 tests pass. LibreOffice render of the 16 October copy: the body ends near the top of page 6. **Not verified:** that reference [3] supports Anna's early-onset sentence in Data Cleaning; that every released WearGait-PD trial carries the walking and turning labels; Word's own page layout after today's edits.
- **Next:** when Anna and Yassien say they are done (asked for 4 pm), Jamie saves a fresh copy (File > Save a Copy into `Coursework\BMEN 600`; computer use could not open Word on 16 October); diff it against the 16 October copy; check any new citation (numbers in order of first citation, 28 entries now); review Methods against the nine points; run `python scripts/check_submission.py copy.docx --pdf copy.pdf`. Then: place Fig. 1 and the tables; check the 6-page limit; copy any changed wording of Jamie's sections into `report/midterm/` on `jamie/T-010-preliminary-results` and open its pull request (`024c9ff`, `8aaa1bb` and that wording) for Jamie to merge; put the commit ID of `main` into Data and Code Availability; export the PDF; submit by 11:59 pm. Jamie's three checks behind his AI-use sentence (Table II, the AUCs 0.82 and 0.77, the sentences citing [7], [17] and [19]) if not done yet. Optional: Delete branch on pull request #10.
- **Blocked / needs a decision:** none for the design (D-007). Who submits, and who leads the WearGait-PD loader (Table III says Anna, the board says Jamie), still need agreeing.
- **For teammates:** @anna: Methods, the nine points Jamie sent on 16 October, and your AI-use and contributions lines. @yassien: the three [DATE]s (PhysioNet downloaded 5 October 2026, WearGait-PD accessed 14 October 2026), the rest of the 15 October list, and your AI-use and contributions lines.
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
