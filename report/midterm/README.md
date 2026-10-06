# Midterm Research Plan drafts

The live document is the shared Google Doc "BMEN 600 Group 5 – Midterm Research Plan (draft)" (link in DECISIONS.md D-004 and in the group chat). This folder keeps what belongs with the code: `sources.md`, the table of verified references everyone cites from, and a Markdown snapshot of each section at the time its figures or tables were produced, so a reader of the repository can see the text that goes with the scripts.

| File | Section | Lead | Reviewer |
|---|---|---|---|
| `01_introduction.md` | §1 Introduction and Motivation | Anna | Jamie |
| `02_background_and_research_gap.md` | §2 Background and Research Gap | Jamie | Anna |
| `03_dataset_and_responsible_use.md` | §3 Dataset and Responsible Use | Yassien | Jamie |
| `04_methods_and_evaluation.md` | §4 Proposed Methods and Evaluation | Anna | all |
| `05_preliminary_results.md` | §5 Preliminary Results | Jamie | Anna |
| `06_teamwork_and_plan.md` | §6 Teamwork and Project Plan | Yassien | all |
| `sources.md` | References, verified | everyone adds | |

Rules that keep the sections consistent:

- Cite with the S-numbers from `sources.md`. Add a source to that table, with how you checked it, before citing it anywhere.
- Figures and tables come from code in this repo; name the script that produced each one in the caption.
- Plain prose, IEEE citations, no bullet lists inside the sections.

Assembling the PDF (T-015): export the Google Doc as plain text, run `python scripts/renumber_citations.py midterm.txt -o midterm_numbered.txt`, and paste the renumbered text and reference list back. The script turns the S-numbers into IEEE numbers in order of first citation, builds the reference list from `sources.md`, and warns about any citation that is not in the ledger or any ledger entry that is never cited.
