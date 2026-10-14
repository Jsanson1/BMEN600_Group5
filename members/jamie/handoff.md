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

## T-029 · Age rule (D-006) in the shared code, every output rerun
_Updated 2026-10-14 10:10 by Claude (cloud session) for Jamie · branch `jamie/T-029-age-restriction` at `583f519` · pull request #10 open_

- **Now:** `src/gaitpdb/cohort.py` holds the rule (under 50 left out, both datasets); `load_feature_table`, Table 1, Figures 1 and 2, the event-detection and dual-task checks go through it, so every model and figure uses the same 162 participants (91 PD, 71 controls). The logistic regression's C grid is now 1e-4 to 1e4 (17 values), as §4 states. Headline: gait-only AUC 0.82 (0.75 to 0.90) within, 0.77 (0.70 to 0.84) across protocols; asymmetry alone 0.76 both; gain within +0.061 (+0.012 to +0.110), across +0.016 (-0.043 to +0.074). Pull request #10 also carries the T-009/T-010 snapshots, the one-column Figure 1 and `scripts/renumber_docx_citations.py` (https://github.com/Jsanson1/BMEN600_Group5/pull/10).
- **Validated:** 24 tests pass, ruff clean; two clean reruns (one by an independent review agent in a fresh virtual environment) reproduce every results file and PNG byte for byte; who the rule removes checked against the raw demographics independently of the new code. **Not verified:** the WearGait-PD side (its participant table is not in hand).
- **Next:** a teammate looks at #10 (D-003), then Jamie merges it, ideally by Thursday 15 October so `main` matches the submitted text; then mark T-029 done and delete the branch in the GitHub UI.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: read the feature table through `gaitpdb.evaluation.load_feature_table` and your models get the age rule with no change; `results/features_usual_walk.csv` keeps all 165 usual walks with a `meets_age_rule` column.
- **Not pushed:** nothing.

## T-009, T-010 · Midterm Background and Preliminary Results (and the three end statements) in the group's Word file
_Updated 2026-10-14 15:12 by Claude (cloud session) for Jamie · text in the group's Word file (Anna's SharePoint); snapshots on `jamie/T-029-age-restriction` at `39bb841` (pull request #10)_

- **Now:** Jamie's sections are in the group's live Word file as of 14 October, about 15:00: Background and Research Gap (draft 6, 660 words), Preliminary Results (draft 6, 859 words, with Table I and the one-column Fig. 1), Data and Code Availability, AI-Assisted Work and Author Contributions (teammates' parts highlighted in yellow), and Jamie's 16 references ([S1] to [S18], still labelled) after Anna's. His affiliation now reads Hotchkiss Brain Institute. Claude pasted them through Word on Jamie's computer, with his approval, from `BMEN600_Jamie_sections_paste_source.docx` (v4 plus bookmarks around each block; the bookmarks were removed from the live file afterwards). The review copy for Anna is `BMEN600_Midterm_Jamie_sections_and_review_v4.docx` (26 comments on her Introduction and Methods, sections named rather than numbered). Both are in Jamie's `Coursework\BMEN 600` folder, with `BMEN600_shared_doc_snapshot_2026-10-14.docx`, a copy of the live file saved right after the paste.
- **Validated:** the snapshot matches the expected result paragraph by paragraph (type, style and text): the file as downloaded on 13 October with Jamie's blocks in place of the template placeholders and his affiliation corrected, and nothing else changed except that one of the template's four empty lines in the reference list was absorbed during the paste. No comments, tracked changes or bookmarks came across; one figure, two tables. The renumbering script runs on it (citations [1] to [25]; it flags Anna's [AK4] slip and that [AK6] and [S18] are not cited yet), and it renders to 5 pages with Yassien's sections still placeholders. Earlier: every Preliminary Results number checked by script (32 checks) and by an independent review (about 130 numbers). **Not verified:** Anna's references AK1 to AK6 (search results confirm only that AK1, AK3, AK6 and the Cawley and Talbot entry exist under those titles); how Word lays out the final pages.
- **Next:** Jamie sends the group message (drafted 14 October in group-chat wording, sections named) with v4 attached; Jamie writes his own verification sentence in AI-Assisted Work (yellow); Jamie makes a free Synapse account so the WearGait-PD participant sheet can be downloaded to check "185 to 181"; pull request #10 goes into `main` Thursday evening unless a teammate asks to look first; final pass Friday morning on a download of the live file: delete the template's leftover text (the cyan reference instructions, the empty numbered lines, the Eason and Maxwell sample entries, any remaining TEXT placeholders), run `python scripts/renumber_docx_citations.py final.docx -o final_numbered.docx`, check where Fig. 1 and Table I land and the 6-page limit, run `python scripts/check_submission.py final_numbered.docx --pdf final_numbered.pdf`, add the commit ID, submit by Friday 16 October 11:59 pm. Afterwards, copy any later wording changes back into the snapshots.
- **Blocked / needs a decision:** T-030 (the design that the Background, Methods and Preliminary Results assume) needs the group's confirmation; the WearGait-PD participant sheet is needed to check the "185 to 181" in Methods.
- **For teammates:** @anna: 26 comments on the Introduction and Methods in Jamie's review copy (v4, for the group chat), most importantly: the pre-processing paragraph describes MinMaxScaler and find_peaks while the shared code (and Preliminary Results) uses a 20 N threshold crossing; Methods says 10 repeats while the code uses 20; [AK5] and [AK4] in the Introduction should be [AK6] and [AK5]; the Introduction needs an explicit research question; the analysed PhysioNet cohort is 162, not 163 (JuCo10 has no recording). @yassien: the Dataset and Teamwork sections are still placeholders in the Word file; the verified dataset facts are under the Dataset heading in the Google Doc and in `sources.md` (S7, S9), and Table I covers the analysed participants.
- **Not pushed:** nothing.

## T-022 · Model comparison (scaffolding and baselines merged; the three-model comparison waits for T-019 and T-020)
_Updated 2026-10-14 10:10 by Claude (cloud session) for Jamie · branch `jamie/T-022-model-comparison` (merged into `main` on 9 October)_

- **Now:** `scripts/run_baselines.py` and `scripts/compare_models.py` are on `main`; pull request #10 reruns them on the 162 analysed participants. Pull requests #4 to #8 were merged locally into `main` on 9 October and are now closed on GitHub with a note.
- **Validated:** see T-029. **Not verified:** the SVM and random forest (not written).
- **Next:** when T-019 and T-020 write their result files through `write_model_outputs`, run `compare_models.py`. If the group confirms T-030, the comparison also needs the pooled and cross-cohort schemes (new code in `evaluation.py`, once for all three models) and sensitivity at 90% specificity (§4 asks for it; the code reports metrics at 0.5 only).
- **Blocked / needs a decision:** T-019 (Yassien), T-020 (Anna), T-030 (group).
- **For teammates:** @anna @yassien: your model appears in the comparison as soon as your script writes `results/<svm|rf>_{folds,cv_predictions,loso_predictions}.csv` through `write_model_outputs`.
- **Not pushed:** nothing.

## T-025 · WearGait-PD external test (preparation; data not yet in hand)
_Updated 2026-10-14 10:10 by Claude (cloud session) for Jamie · branch `jamie/T-025-weargait-access` (documentation merged into `main` on 9 October)_

- **Now:** a teammate has the WearGait-PD data (Jamie, 13 October). The access, contents and caveats are documented in `data/raw/README.md`, which now also states the age rule for this dataset.
- **Validated:** the article's facts (see the 6 October log entry). **Not verified:** the files, their columns and units (supplementary Table S5 not read), the 185 to 181 count after the age rule.
- **Next:** the participant spreadsheet into `C:\Users\jamie\Documents\BMEN600_Group5\data\raw\weargait_pd\` (git ignores it) to check the count; then the SelfPace files, a loader for the insole total force, and a check of the 20 N threshold against the walkway's foot contacts before any cross-cohort run.
- **Blocked / needs a decision:** the files (from the teammate who has them); T-030 for the analysis design.
- **For teammates:** whoever has WearGait-PD: please send Jamie the clinical and demographic spreadsheet(s) first; the sensor files can follow.
- **Not pushed:** nothing.
