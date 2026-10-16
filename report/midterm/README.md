# Midterm Research Plan

The Midterm Research Plan was submitted on 16 October 2026. It was written in one Word file on the IEEE conference template, kept in Anna's SharePoint (earlier drafts are in the shared Google Doc "BMEN 600 Group 5 – Midterm Research Plan (draft)", DECISIONS.md D-004), and the code and results it reports are at commit `50a86e9`. This folder keeps what belongs with the code: the sections whose numbers, table and figure come from this repository, the end statements, and `sources.md`, the table of verified references those sections cite. Sections I, III, IV and VI (Introduction, Dataset and Responsible Use, Methods, Teamwork and Project Plan) were written directly in the Word file and are not kept here.

| File | What it holds | Lead | Reviewer |
|---|---|---|---|
| `02_background_and_research_gap.md` | Section II, Background and Research Gap, as submitted | Jamie | Anna |
| `05_preliminary_results.md` | Section V, Preliminary Results, as submitted, with Table II and Fig. 1 and the script behind each number | Jamie | Anna |
| `07_statements.md` | Data and Code Availability, AI-Assisted Work and Author Contributions, as submitted | all (drafted by Jamie) | all |
| `sources.md` | The verified references cited in Sections II and V, with how each was checked and what it supports | Jamie | |

The snapshots cite with the S-numbers of `sources.md`; the submitted PDF numbers its references in IEEE order, and each snapshot's header gives the mapping where it matters.

Rules that keep the sections consistent:

- Cite with the S-numbers from `sources.md`. Add a source to that table, with how you checked it, before citing it anywhere.
- Figures and tables come from code in this repo; name the script that produced each one in the caption.
- Plain prose, IEEE citations, no bullet lists inside the sections.

Assembling the PDF from the Word file (T-015): download it, then `python scripts/renumber_docx_citations.py midterm.docx -o midterm_numbered.docx`. In the Word file, citations are labels ([AK1], [S12], [SciPy], ...) and each reference entry starts with its label; the script numbers the labels in order of first citation, reorders and cleans the reference list, drops entries that are never cited, and lists any label that has no entry. Check its report, then export the numbered copy to PDF and run `python scripts/check_submission.py midterm_numbered.docx --pdf midterm_numbered.pdf`, which lists anything left to fix: template placeholders (including [DATE]), highlighted to-do text, unnumbered citation labels, numbered citations out of IEEE order or pointing past the reference list, reference entries never cited, comments or tracked changes still in the file, figures or tables cited without a caption, a missing repository link or commit ID, and the page on which the references start. Since 15 October the Word file carries numbers rather than labels (renumbered by hand in the file); with no labels left, skip the renumbering script and rely on the numbering check. For text kept as plain text instead (the Google Doc): export it, run `python scripts/renumber_citations.py midterm.txt -o midterm_numbered.txt`, and paste the renumbered text and reference list back. The script turns the S-numbers into IEEE numbers in order of first citation, builds the reference list from `sources.md`, and warns about any citation that is not in the ledger or any ledger entry that is never cited.
