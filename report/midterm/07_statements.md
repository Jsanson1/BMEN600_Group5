# Data and Code Availability, AI-Assisted Work, Author Contributions

_Drafts, 2026-10-13, written for Jamie with his parts filled in; the parts in square brackets are for Anna, Yassien and Jamie to complete in the group's Word file. The live copy is that file; this is the snapshot._

## Data and Code Availability

The PhysioNet “Gait in Parkinson’s Disease” database v1.0.0 [S7], [S8] is openly available under the Open Data Commons Attribution License v1.0. WearGait-PD [S9] is available under CC BY 4.0 through Synapse (syn52540892) after registration and acceptance of its data-use terms. Neither dataset is redistributed in our repository; its file data/raw/README.md gives the download steps, and every PhysioNet file we use matches the database’s published SHA-256 checksums. All code, results and figures are in the public repository https://github.com/Jsanson1/BMEN600_Group5. Its README lists the software (plain Python scripts, Python 3.11 or newer with NumPy, pandas, SciPy, scikit-learn and matplotlib) and the script that produces each table and figure, and python scripts/run_all.py regenerates every output in this plan from the raw files. The version corresponding to this submission is commit [commit ID, filled in at submission].

## AI-Assisted Work

The main AI tool was Claude (Anthropic), used through Claude Code and the Claude desktop app. For Jamie it searched and checked literature, drafted Sections II and V, the repository’s README and collaboration protocol, and wrote the analysis code (data loader, gait-event detection, features, data-quality checks, the shared evaluation, the logistic regression and the model comparison). [Anna: tools and uses.] [Yassien: tools and uses.] Every reference in Sections II and V was checked against its PubMed or publisher record, and the repository file report/midterm/sources.md records what each one supports. Every number, table and figure in this plan is produced by a script in the repository, and a run from a clean Python environment reproduces them; the event detection was checked against the published dual-task effect and for sensitivity to its threshold. AI-assisted commits are authored by the responsible member and name the tool, and each member’s members/<name>/log.md records what the AI did and how it was checked. [Jamie: what you checked yourself, e.g. read the sources, inspected the figure, reviewed the code.]

## Author Contributions

J. Sanson: literature review and reference verification (Section II); data curation and quality assessment; software (gait-event detection, features, shared evaluation, logistic regression, model comparison); formal analysis and visualisation (Table I, Fig. 1); writing of Sections II and V and the repository README; repository and collaboration workflow; review of Sections I and III. A. Klygina: [contributions, e.g. Sections I and IV, ...]. Y. Tawfik: [contributions, e.g. Sections III and VI, ...]. All three chose the research question and dataset together.
