# Detecting Parkinson's disease from foot-force gait recordings

BMEN 600, Fall 2026, University of Calgary. Group 5 ("The Singing Oats"): Jamie Sanson, Anna Klygina, Yassien Tawfik.

> **Working in this repo?** People: read [CONTRIBUTING.md](CONTRIBUTING.md). AI agents: follow [CLAUDE.md](CLAUDE.md). Tasks and deadlines: [TASKS.md](TASKS.md). Group decisions: [DECISIONS.md](DECISIONS.md).

## Research question

Can a small set of interpretable spatiotemporal gait features, computed from foot-force recordings alone and without clinical scores, separate people with Parkinson's disease (PD) from healthy controls when the classifier is tested on participants and recording protocols it has never seen, and which features carry that separation?

The question and the plan to answer it are set out in the Midterm Research Plan (due 16 October 2026); the wording above is the working version from that document.

## Why it matters

PD affects at least 1% of people over 60 and is the fastest-growing neurodegenerative disorder worldwide [1]. It is diagnosed on clinical grounds, and that diagnosis is wrong in roughly one case in five, with no improvement over 25 years and the poorest accuracy in early disease [2]. Gait is among the most common and disabling symptoms, it is rarely measured in routine care, and the gait changes of PD (shorter strides, higher stride-to-stride variability, left-right asymmetry) are well described at the group level [3], [4]. What is not settled is whether those changes separate an individual with PD from healthy ageing when a model is evaluated the way a screening tool would be used: on new people and new recording conditions. Published classifiers on the dataset below report accuracies above 95%, but many evaluate on recordings rather than participants, so the same person appears in training and test [5], [6]. This project measures how much of that performance survives a participant-level, cross-protocol and cross-cohort evaluation, using three classical models (logistic regression, support vector machine, random forest) on the same features.

## Data

| Dataset | Role | Access | Licence |
|---|---|---|---|
| PhysioNet "Gait in Parkinson's Disease" v1.0.0 [7], [8] | Development and primary evaluation. 93 PD and 73 controls, 306 recordings of about 2 min of self-paced walking with 8 force sensors under each foot at 100 Hz, three sub-studies (Ga, Ju, Si), Hoehn and Yahr and UPDRS scores. | Open, no account: https://physionet.org/content/gaitpdb/1.0.0/ (DOI 10.13026/C24H3N) | ODC-By 1.0 |
| WearGait-PD [9] | External test set. 100 PD and 85 controls recorded by a different group with inertial sensors, pressure insoles and an instrumented walkway. | Synapse (syn52540892), free account and acceptance of the data-use terms required | CC BY 4.0 |

Data are never committed. Download steps, checksums and the known quirks of the files are in [data/raw/README.md](data/raw/README.md); the PhysioNet ZIP unpacks into `data/raw/gaitpdb/`, which git ignores.

## What is in the repository

| Path | What it holds |
|---|---|
| `src/gaitpdb/` | The shared Python package: `io.py` reads the record files and `demographics.txt`; `events.py` finds heel strikes and toe offs from the per-foot total force and flags which strides to keep; `features.py` turns one recording into stride, swing and stance timing, their variability, cadence and left-right asymmetry; `evaluation.py` fixes the model inputs, the participant-grouped and leave-one-study-out splits and the metrics that all three models share. |
| `scripts/` | One script per output (see "How to run"). |
| `results/` | Tables and numbers produced by the scripts: `table1_participants.md`, `features_usual_walk.csv` (one row per usual-walk recording), `features_usual_walk_by_group.csv`, `figure1_summary.txt`, `event_detection_checks.txt`, `data_quality.txt`, `dual_task_check.txt`. |
| `figures/` | Figure 1 (events and the two headline features) and Figure 2 (the evaluation design), PNG and PDF. |
| `report/midterm/` | Markdown snapshots of the midterm sections that go with the code, and `sources.md`, the table of every reference with how it was verified and what it supports. |
| `data/raw/README.md` | How to obtain the data. |
| `members/`, `TASKS.md`, `DECISIONS.md` | Who did what, the task board, and the group's decisions (the paper's Author Contributions and AI-Assisted Work sections are written from `members/*/log.md`). |
| `CONTRIBUTING.md`, `CLAUDE.md`, `AGENTS.md` | How the team and its AI assistants work in this repository. |
| `requirements.txt`, `requirements-dev.txt`, `pyproject.toml` | Python dependencies and the ruff configuration; `.github/workflows/checks.yml` runs the same checks on every pull request. |

## How to run

Platform: plain Python scripts run from a terminal (no notebook or MATLAB), Python 3.11 or newer, packages numpy, pandas, scipy, scikit-learn, matplotlib and tabulate (`requirements.txt`). Tested on Linux; nothing in the code is platform-specific.

```
python -m pip install -r requirements.txt
# download and unpack the PhysioNet ZIP into data/raw/gaitpdb/ (see data/raw/README.md), then:
python scripts/verify_data.py            # every file against PhysioNet's SHA256SUMS.txt
python scripts/make_table1.py            # Table 1 -> results/table1_participants.{csv,md}, results/table1_notes.txt
python scripts/make_figure1.py           # Figure 1 -> figures/, plus results/features_usual_walk*.csv and results/figure1_summary.txt
python scripts/check_event_detection.py  # contact-threshold and stride-rule sensitivity -> results/event_detection_checks.{csv,txt}
python scripts/check_data_quality.py     # data-quality report -> results/data_quality.{txt,csv}
python scripts/check_dual_task.py        # does the pipeline reproduce the published dual-task effect? -> results/dual_task_check.txt
python scripts/run_logreg.py             # logistic regression under the shared evaluation -> results/logreg_*.{txt,csv}
python scripts/make_figure2.py           # Figure 2, the evaluation design drawn from the participant counts -> figures/
```

`python scripts/run_all.py` runs all of them in order (about five minutes) and regenerates every committed output; a run on a fresh checkout changes nothing but the PDFs' creation dates. Each script accepts `--data <folder>` if the data live elsewhere. `python -m pip install -r requirements-dev.txt && python -m pytest` runs the unit tests in `tests/` (synthetic signals, no dataset needed).

## Results so far

Table 1 (`results/table1_participants.md`) describes the participants and recordings by sub-study and group. Figure 1 shows the gait-event detection on one recording and the two features the literature singles out, on the usual walk of every participant:

![Figure 1: force trace with detected events; stride-time variability and swing-time asymmetry by group](figures/figure1_events_and_variability.png)

On the usual walk, the swing-time asymmetry between the legs separates PD from controls far better (AUC 0.76) than stride-time variability (AUC 0.60), and the latter weakens once the age difference between the groups is taken into account; the numbers are in `results/figure1_summary.txt`. The controls are younger than the patients (63.7 vs 66.3 years), which the PhysioNet description does not mention, and 54 of the 165 participants contribute more than one recording, which is why every evaluation splits by participant. A first logistic regression on six timing features, under the shared evaluation in `src/gaitpdb/evaluation.py`, reaches an AUC of 0.81 within protocol and 0.73 when each sub-study is held out (`results/logreg_summary.txt`, from `scripts/run_logreg.py`); age and sex alone give 0.58.

## Plan

Section leads for the midterm plan and owners for the project phase are in the task board ([TASKS.md](TASKS.md)) and in the group's [Project Plan sheet](https://docs.google.com/spreadsheets/d/1qsDRWUfYqdONmI8UFPvRK-xRhOAi-h_beDHfc5vx1Co/edit?usp=sharing). Three models, one owner each (random forest: Yassien; support vector machine: Anna; logistic regression: Jamie), are compared under repeated participant-grouped cross-validation with confidence intervals, leave-one-study-out validation across the three PhysioNet protocols, and a final test on WearGait-PD. The group chose this project over an alternative on music and striatal dopamine at its 2 October meeting ([DECISIONS.md](DECISIONS.md), D-004).

## References

[1] S. Zafar, F. Lui, and S. S. Yaddanapudi, "Parkinson disease," in *StatPearls* [Internet]. Treasure Island, FL, USA: StatPearls Publishing, updated Sep. 15, 2025. [Online]. Available: https://www.ncbi.nlm.nih.gov/books/NBK470193/ (accessed Oct. 5, 2026).

[2] G. Rizzo, M. Copetti, S. Arcuti, D. Martino, A. Fontana, and G. Logroscino, "Accuracy of clinical diagnosis of Parkinson disease: A systematic review and meta-analysis," *Neurology*, vol. 86, no. 6, pp. 566–576, Feb. 2016, doi: 10.1212/WNL.0000000000002350.

[3] A. Mirelman et al., "Gait impairments in Parkinson's disease," *Lancet Neurol.*, vol. 18, no. 7, pp. 697–708, Jul. 2019, doi: 10.1016/S1474-4422(19)30044-4.

[4] J. M. Hausdorff, J. Lowenthal, T. Herman, L. Gruendlinger, C. Peretz, and N. Giladi, "Rhythmic auditory stimulation modulates gait variability in Parkinson's disease," *Eur. J. Neurosci.*, vol. 26, no. 8, pp. 2369–2375, Oct. 2007, doi: 10.1111/j.1460-9568.2007.05810.x.

[5] S. Saeb, L. Lonini, A. Jayaraman, D. C. Mohr, and K. P. Kording, "The need to approximate the use-case in clinical machine learning," *GigaScience*, vol. 6, no. 5, pp. 1–9, May 2017, doi: 10.1093/gigascience/gix019.

[6] R. Mittal et al., "Machine learning approach to gait analysis for Parkinson's disease detection and severity classification," *Front. Robot. AI*, vol. 12, Art. no. 1623529, Dec. 2025, doi: 10.3389/frobt.2025.1623529.

[7] J. M. Hausdorff, "Gait in Parkinson's Disease (version 1.0.0)," PhysioNet, Feb. 2008, doi: 10.13026/C24H3N. [Online]. Available: https://physionet.org/content/gaitpdb/1.0.0/

[8] T. Pollard et al., "PhysioNet as a global platform for biomedical research," *Nature Health*, vol. 1, pp. 792–795, 2026, doi: 10.1038/s44360-026-00096-z.

[9] A. J. Anderson et al., "WearGait-PD: An open-access wearables dataset for gait in Parkinson's disease and age-matched controls," *Sci. Data*, vol. 13, Art. no. 440, Feb. 2026, doi: 10.1038/s41597-026-06806-2.

All references were checked against their publisher or PubMed records on 5 October 2026; the full verification table is `report/midterm/sources.md`.
