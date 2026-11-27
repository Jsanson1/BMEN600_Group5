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

## T-037 · Assemble and submit the final paper (being finished in Word; submission held for the group's review)
_Updated 2026-11-27 15:30 by Claude (cloud session) for Jamie · the paper is now edited in Word on SharePoint; last repository build from main `735cc85` (#23, #24)_

- **Now:** the group is finishing the paper in Word. The copy Anna shared from SharePoint (attached by Jamie on 27 November) is the current version. Since the 23 November build from `735cc85` (11 pages, `check_submission.py` "ready to submit") it has a new title and author block, edits to the Introduction, to the Methods' participant, threshold and turn paragraphs, to the AI-Assisted Work statement and to Anna's Author Contributions line; its Results, Discussion and Conclusion are unchanged, and no number or citation changed. On 27 November Jamie's session sent `Paper_suggested_edits_27Nov.docx`: that copy with 35 suggested edits as tracked changes and 2 comments. 29 are in the Discussion and Conclusion (the "X, not Y" and "rather than" constructions Anna flagged, and hard-to-parse sentences); 6 are in the Word-edited parts, including a factual error (the Introduction promised earlier access to "treatment that slows progression", but reference [2] says no treatment slows PD) and a garbled Methods sentence ("Table I. describes that of gaitpdb's ..."). One comment asks whether the new AI-statement sentence, "Each written section was then verified, rewritten, and finalized by a member of the team", is true of every section. The analysis code is unchanged since the final rerun at `02e69c9`.
- **Validated:** the suggestions file passes the docx validator against the original (every change tracked); with every suggestion accepted, no number or citation changes in any paragraph and the paper stays at 11 pages (scripts); the treatment claim checked against the StatPearls chapter [2] (updated 15 September 2025: no available disease-modifying or slowing therapy); the word-by-word comparison of the Word copy with the 23 November build, by script. **Not verified:** whether the SharePoint copy has changed since it was downloaded on 27 November; the group's view of the suggestions; the layout if the file is saved from Word.
- **Next:** the group goes through the suggestions in Word (Review tab: accept or reject each; if the SharePoint copy has changed since 27 November, apply the accepted ones there by hand) and settles the AI-statement sentence. Before submitting: export the final PDF from Word, compare its text with the 23 November build so any changed number is caught, and commit that PDF under `report/final/` through a pull request, with a README note that the Word version supersedes the Markdown drafts, so the repository holds what was submitted. Then Jamie uploads the PDF to D2L by Fri 4 December, 11:59 p.m., and sets T-037 to done. Delete the merged branches on GitHub by hand (the session cannot; checked 18 November that none has a commit main lacks): jamie/T-008-readme-front-page, T-009-background-gap, T-010-preliminary-results, T-016-cowork-onboarding, T-017-d012-threshold, T-018-feature-extraction, T-018-readme-run-all, T-019-random-forest, T-021-logistic-regression, T-022-cross-cohort-run, T-022-model-comparison, T-023-discussion, T-025-weargait-access, T-026-data-quality, T-027-unit-tests, T-028-assembly-helper, T-031-midterm-snapshots, T-032-results-section, T-033-methods-section, T-034-end-statements, T-035-introduction, T-037-paper-assembly, T-039-framing (all `jamie/`).
- **Blocked / needs a decision:** the group: whether every section was in fact rewritten by a member, as the AI statement now says; if not, the comment suggests wording that matches what happened.
- **For teammates:** @anna @yassien: please go through `Paper_suggested_edits_27Nov.docx` (Jamie is sending it) and its two comments, and check your own lines in the Author Contributions and AI-Assisted Work. @anna: #21 and your SVM are merged, so T-017 and T-020 can be set to done.
- **Not pushed:** nothing.

## T-038 · Final presentation (in Google Slides, condensed and rescripted 27 November)
_Updated 2026-11-27 15:30 by Claude (cloud session) for Jamie · Google Slides deck "BMEN 600 Group 5 Final Presentation" in Jamie's Drive, shared with Anna and Yassien; no branch_

- **Now:** the deck moved to Google Slides, where Anna restyled it and cut it to nine slides. On 27 November, after the teaching team said every slide had too many words, Jamie's session cut the on-slide text (about 650 words across the deck to 420, mostly on slides 5 to 9) with find-and-replace, so Anna's formatting is untouched. It also corrected two slide-2 labels whose shortening had changed their meaning, swapped the slide-2 source Rizzo for Tolosa, and put the participant numbers on the data slide ("Comparable sample sizes (155 and 169), but differing walking protocols"). The speaker notes hold a new script of about 640 words, about 4:40 at a steady pace: Jamie slides 1, 5, 6 (about 1:25), Anna 2 to 4 (about 1:40), Yassien 7 to 9 (about 1:35). Each member has a set of printable flash cards (Word files sent to Jamie, not in the repository): their own slides shaded, start times and cues, two Q&A cards and a card on their own contribution.
- **Validated:** every number in the script and on the slides against the paper's text and Table II; the live deck re-exported at 15:20 (last changed at 13:54, by Jamie's session): 420 words on the slides and every slide's notes identical to the script; the cards rendered and looked at, and the contribution cards checked against the paper's Author Contributions and AI-Assisted Work. **Not verified:** the timing spoken aloud; Anna and Yassien have not yet seen the new notes or their cards. Anna's card also lists editing the final paper (formatting, Introduction, Methods) and restyling the slides, which her Word copy and the deck support but the paper's Author Contributions does not yet mention. Yassien's card lists only work recorded in the paper and the repository; if he also edited the paper in Word, he can add it. Anna's old note that turn removal took more data from controls is in neither the paper nor the repository and stays out.
- **Next:** each member checks their contribution card and rehearses with a timer (over 5:00 means speaking slower than about 150 words a minute); the talk is on Mon 30 November; set to done after it.
- **Blocked / needs a decision:** whether the 1-minute (brief) or 2-minute (course-introduction slide) speaking minimum applies; three people cannot each speak 2 minutes in 5.
- **For teammates:** @anna @yassien: your lines are in the speaker notes of the Google Slides deck, and Jamie is sending each of you a set of flash cards; please check the contribution card at the end of yours. The PowerPoint from 17 November is out of date.
- **Not pushed:** nothing (the deck lives in Google Slides).
