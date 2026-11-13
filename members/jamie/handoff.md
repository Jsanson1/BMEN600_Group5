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

## T-022 · Model comparison and cross-dataset analyses (pull request #22 open, for review)
_Updated 2026-11-13 17:45 by Claude (cloud session) for Jamie · `jamie/T-022-cross-cohort-run` at `ae2542e`; `jamie/T-022-model-comparison` merged as #16 (branch still to delete)_

- **Now:** the final rerun with Anna's SVM is done and committed (`56364d4`), and pull request #22 is open: https://github.com/Jsanson1/BMEN600_Group5/pull/22 (checks green). It ran from a fresh clone of `79228fa` in three parts (one command in this cloud session stops after 2 hours; a container restart stopped the second part, and the third resumed from the kept results): about 3.4 hours of computing. Figure 5's legend now goes on two lines with four entries (`e30209a`); the README has the SVM in its Results and the record of this rerun (`56364d4`, `ae2542e`). The SVM tells the same story: 0.78 and 0.72 within gaitpdb, 0.53 (0.45 to 0.62) across cohorts, 0.63 combined. With 13 paired tests the Holm-adjusted p values rose (0.43 to 0.80, 0.47 to 0.86); none significant, before or now.
- **Validated:** every output of the logistic regression and random forest identical to the committed one, cell for cell in every CSV; the other changed lines are the SVM's additions, the commit line in the two `features_summary.txt` files and #17's escaped `|` in `fixed_20N/feature_dictionary.md`; Figures 3 and 5 looked at; 139 tests; ruff clean. **Not verified:** the SVM's outputs by a second run (asked of Yassien in #22: one `python scripts/run_all.py` in one go); first code review of `run_cross_cohort.py`, `check_weargait_signal.py` and the figure and table scripts (about 1,650 lines with their tests).
- **Next:** Anna opens her SVM pull request and it is merged first (#22 contains her two commits); review of #22 (Yassien or Anna); merge; mark T-022 done; delete the branches.
- **Blocked / needs a decision:** the correction note to D-012: Jamie confirms that the group agreed, then it is appended as D-014: "D-014 · Correction to the evidence of D-012 (no change to the decision). The threshold check behind D-012 counted every walkway footfall, turns and stops included, because its script did not load the video labels (fixed in #15, `24037b8`). On the 12,397 straight-walking footfalls 5% of the force level still ranks first (53.5% within 30 ms against 53.4% at 30 N), with more footfalls matched one to one (87.1% against 85.5%) and narrower stance limits (-0.13 to +0.09 s against -0.21 to +0.23 s). The figures quoted in D-012 are superseded by `results/weargait_threshold_check.txt`."
- **For teammates:** @anna: please open your SVM pull request (reviewer Jamie or Yassien) so it can be merged before #22; `svm.py` cites Platt under the preprint's title and 1999, while the published chapter is "Probabilities for SV machines", MIT Press, 2000, pp. 61–74, doi: 10.7551/mitpress/1113.003.0008 (S25 in `report/final/sources.md`). @yassien: #22 asks for one uninterrupted `python scripts/run_all.py` on your PC; the SVM's probabilities may differ from this rerun in about the fifth decimal (most likely the stopping tolerance of the logistic curve fitted to its distances, not tested), the rest should match to the last digits.
- **Not pushed:** nothing.

## T-023 · Discussion (draft 3 on its branch, for the group's comments)
_Updated 2026-11-13 17:45 by Claude (cloud session) for Jamie · branch `jamie/T-023-discussion` at `551cdf2`_

- **Now:** `report/final/discussion.md`, draft 3 (about 1,900 words), now with the SVM from the final rerun (`56364d4`): its within-gaitpdb AUCs in Section A and, wherever the three models are summarised together, the range of their values. One statement changed in kind: with age and sex in the combined analysis, the AUC among gaitpdb's participants rose for the SVM where it fell for the other two, so Section C now says the gain was "not consistent" there. `report/final/sources.md` (on this branch) now also holds S25, Platt's chapter, checked against Crossref.
- **Validated:** every number in the prose found in the output files at `56364d4` (a script listed the unmatched ones: only S1's 80.6%). **Not verified:** the group has not read draft 3 as a whole; S25's chapter text (not open access; its method as described by Lin, Lin and Weng).
- **Next:** the group's comments; trim to fit the page budget if needed; paste into the Word file and open the pull request (with `sources.md`).
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-023-discussion/report/final/discussion.md
- **Not pushed:** nothing.

## T-032 · Results section of the final paper (draft 4 on its branch, for the group's comments)
_Updated 2026-11-13 17:45 by Claude (cloud session) for Jamie · branch `jamie/T-032-results-section` at `a433cfa`_

- **Now:** `report/final/results.md`, draft 4 (about 1,700 words of text, two tables, two figures): the SVM in every section from the final rerun (`56364d4`), triples in the order logistic regression, SVM, random forest (as in Table II and Fig. 5), the Holm-adjusted p values for 13 tests (0.80, 1.00, 0.86), and the combined analysis's gain from age and sex described as "mostly" from WearGait-PD's participants (the SVM's AUC among gaitpdb's rose).
- **Validated:** all 364 numbers in the prose found in the output files at `56364d4` except the two bout-position percentages (6.7%, 4.2%), unchanged since they were traced by hand. **Not verified:** the group has not read it.
- **Next:** the group's comments; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** none.
- **For teammates:** @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-032-results-section/report/final/results.md
- **Not pushed:** nothing.

## T-033 · Dataset and Methods section of the final paper (draft 2 on its branch, for the group's comments)
_Updated 2026-11-13 17:45 by Claude (cloud session) for Jamie · branch `jamie/T-033-methods-section` at `02d5c07`_

- **Now:** `report/final/methods.md`, draft 2 (about 2,400 words). On 13 November: the SVM described in Section E from `src/gaitpdb/svm.py` and `scripts/run_svm.py` (kernel, C and γ chosen by the log-loss of Platt-scaled inner out-of-fold distances, citing Platt's chapter, S25), `run_svm.py` and 139 tests in Section G, and the final rerun in Section G's bracketed note.
- **Page budget:** the trial layout rebuilt on 13 November with today's drafts (Results, Discussion and Methods together about 260 words longer, Table II one column wider, Fig. 5 one legend line taller) is still 10 pages with an Introduction of 1,500 or 1,700 words and the short AI statement; page 10's second column ends at about three quarters of its height in both. The estimate is noisy (how figures and tables float changes from build to build, and Word's layout may differ by about half a page), so 1,500 words remains the safe target.
- **Validated:** every number in the Methods against the outputs and code; the SVM's settings against `svm.py`. **Not verified:** the Synapse Pledge's wording; the group has not read it.
- **Next:** Jamie reads the Synapse Pledge while signed in; the group's comments; the submitted commit in Section G; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** Fig. 1 (regenerate with the final cleaning, or drop; dropping it also saves space).
- **For teammates:** @anna: Section E's SVM sentence is written from your code; check it says what you meant. @anna @yassien: comments welcome: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-033-methods-section/report/final/methods.md
- **Not pushed:** nothing.

## T-034 · End statements of the final paper (draft 3 on its branch, for each member to check their part)
_Updated 2026-11-13 14:35 by Claude (cloud session) for Jamie · branch `jamie/T-034-end-statements` at `0775172`_

- **Now:** `report/final/statements.md`: Anna's checked wording for her AI-use paragraph and her contributions (12 November), plus her review of #15; Yassien's reruns (the whole analysis; on 13 November #15's threshold check and the SVM) and his reviews (#15 to #18) in his parts, for him to confirm (`0775172`); the reruns and cross-reviews in the verification paragraph. Jamie's review is now in his words (13 November, `c5f6e0c`): he skimmed all of the code, drafts and figures for errors, with a placeholder for the longer pass he plans before submission. A short AI-Assisted Work version (about 220 words, against about 770) is proposed for the page limit, keeping the long one for the repository.
- **Validated:** each statement about a member traced to their log, the midterm statements, `DECISIONS.md` or the pull requests. **Not verified:** Yassien's confirmation; the group's choice of the short version.
- **Next:** Yassien confirms his parts; the group chooses the short or long AI statement; after his longer pass, Jamie describes it in one clause; fill in the submitted commit and the reviews of the last pull requests; paste into the Word file and open the pull request.
- **Blocked / needs a decision:** the short or long AI statement (group); Yassien's confirmation.
- **For teammates:** @yassien: your parts now include your 13 November reruns and your review of #15; confirm them, and add the Conclusion. All: the short AI-Assisted Work version saves about half a page: https://github.com/Jsanson1/BMEN600_Group5/blob/jamie/T-034-end-statements/report/final/statements.md
- **Not pushed:** nothing.
