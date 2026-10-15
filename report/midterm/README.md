# Midterm Research Plan drafts

Since 13 October the group writes the submission in one Word file on the IEEE conference template, kept in Anna's SharePoint; the earlier drafts are in the shared Google Doc "BMEN 600 Group 5 – Midterm Research Plan (draft)" (DECISIONS.md D-004). This folder keeps what belongs with the code: `sources.md`, the table of verified references everyone cites from, and a Markdown snapshot of each section at the time its figures or tables were produced, so a reader of the repository can see the text that goes with the scripts.

| File | Section | Lead | Reviewer |
|---|---|---|---|
| `01_introduction.md` | §1 Introduction and Motivation | Anna | Jamie |
| `02_background_and_research_gap.md` | §2 Background and Research Gap | Jamie | Anna |
| `03_dataset_and_responsible_use.md` | §3 Dataset and Responsible Use | Yassien | Jamie |
| `04_methods_and_evaluation.md` | §4 Proposed Methods and Evaluation | Anna | all |
| `05_preliminary_results.md` | §5 Preliminary Results | Jamie | Anna |
| `06_teamwork_and_plan.md` | §6 Teamwork and Project Plan | Yassien | all |
| `07_statements.md` | Data and Code Availability, AI-Assisted Work, Author Contributions | all (drafted by Jamie) | all |
| `sources.md` | References, verified | everyone adds | |

Rules that keep the sections consistent:

- Cite with the S-numbers from `sources.md`. Add a source to that table, with how you checked it, before citing it anywhere.
- Figures and tables come from code in this repo; name the script that produced each one in the caption.
- Plain prose, IEEE citations, no bullet lists inside the sections.

Assembling the PDF from the Word file (T-015): download it, then `python scripts/renumber_docx_citations.py midterm.docx -o midterm_numbered.docx`. In the Word file, citations are labels ([AK1], [S12], [SciPy], ...) and each reference entry starts with its label; the script numbers the labels in order of first citation, reorders and cleans the reference list, drops entries that are never cited, and lists any label that has no entry. Check its report, then export the numbered copy to PDF and run `python scripts/check_submission.py midterm_numbered.docx --pdf midterm_numbered.pdf`, which lists anything left to fix: template placeholders (including [DATE]), highlighted to-do text, unnumbered citation labels, numbered citations out of IEEE order or pointing past the reference list, reference entries never cited, comments or tracked changes still in the file, figures or tables cited without a caption, a missing repository link or commit ID, and the page on which the references start. Since 15 October the Word file carries numbers rather than labels (renumbered by hand in the file); with no labels left, skip the renumbering script and rely on the numbering check. For text kept as plain text instead (the Google Doc): export it, run `python scripts/renumber_citations.py midterm.txt -o midterm_numbered.txt`, and paste the renumbered text and reference list back. The script turns the S-numbers into IEEE numbers in order of first citation, builds the reference list from `sources.md`, and warns about any citation that is not in the ledger or any ledger entry that is never cited.
