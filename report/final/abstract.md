# Title, abstract and keywords (draft 1 for the final paper)

Draft by Jamie Sanson's AI assistant for task T-036, 16 November 2026. The group's proposal of that day gave the abstract to Yassien; the team then asked, through Jamie, for the paper to be finished, so this draft was written for the group to check and change. It summarises the Introduction (T-035), Results (T-032) and Discussion (T-023) and adds nothing to them: every number is in `results/model_comparison.txt` or `results/crosscohort_summary.txt` at commit `56364d4`, and the table at the end says where. The brief asks for about 200 to 250 words covering the problem and question, the dataset and population, the approach, the most important result, its interpretation and the main limitations; the abstract below has 250. Draft 2 (23 November, T-039) leads with what the study tests, that a model tested within one database cannot show it will work in another clinic, and ends with what follows for validation; it names the five features in Methods only. The IEEE template asks for no symbols, special characters, footnotes or mathematics in the title or abstract, so neither cites a source or uses a symbol.

## Title

Foot-Force Gait Timing Separates Parkinson's Disease Within One Cohort but Does Not Transfer to an Independent Cohort

## Abstract

Parkinson's disease (PD) is diagnosed clinically, late in its course, and access to neurologists is uneven; force-sensing insoles could help decide whom to refer. Gait classifiers for PD are mostly tested within one database, which cannot show whether they will work in another clinic. We asked whether five interpretable timing features from foot force alone separate people with PD from controls aged 50 and over on participants, protocols and a cohort the models have not seen. One pipeline derived them from the PhysioNet Gait in Parkinson's Disease database (gaitpdb; 87 with PD, 68 controls) and WearGait-PD (94 with PD, 75 controls). Three models (logistic regression, support vector machine, random forest) were tested on unseen gaitpdb participants and sub-studies, on both datasets combined and, fitted on gaitpdb, once on WearGait-PD, with checks fixed in advance. Within gaitpdb, the area under the receiver operating characteristic curve (AUC) was 0.75 to 0.79 on unseen participants and 0.70 to 0.73 on unseen sub-studies (swing-time asymmetry alone: 0.73); with both datasets combined, 0.63 to 0.67. On WearGait-PD they reached 0.53 to 0.57, indistinguishable from chance, also at a second contact threshold, with standardised inputs and without the variability features; only pairs matched on sex and age, mostly from different sites, reached 0.65 to 0.67. Validation by participant within one database did not predict performance in a cohort with different insoles, protocol and population; such models need validating where they will be used. Two datasets cannot show which difference matters; both compare diagnosed patients with volunteers.

## Keywords

Parkinson's disease, gait analysis, force-sensing insoles, machine learning, external validation, generalisability

## Numbers and where they come from

| Number in the abstract | Source at `56364d4` |
|---|---|
| 87 with PD, 68 controls | `results/model_comparison.txt`, first line (155 participants, 87 PD, 68 controls) |
| 94 with PD, 75 controls | `results/crosscohort_summary.txt`, second line (169 participants, 94 PD) |
| 0.75 to 0.79 on unseen participants | `results/model_comparison.txt`, gait features, within protocol: random forest 0.75, SVM 0.78, logistic regression 0.79 |
| 0.70 to 0.73 on unseen sub-studies | the same lines, across protocols: 0.70, 0.72, 0.73 |
| swing-time asymmetry alone 0.73 | `results/model_comparison.txt`, "Swing-time asymmetry alone", within protocol |
| both datasets combined, 0.63 to 0.67 | `results/crosscohort_summary.txt`, gait, pooled: 0.628, 0.632 and 0.666 |
| 0.53 to 0.57 on WearGait-PD | `results/crosscohort_summary.txt`, gait, cross-cohort: 0.532, 0.534 and 0.573, intervals 0.449 to 0.621, 0.451 to 0.620 and 0.486 to 0.659, all including 0.5 |
| second contact threshold, standardised inputs, without the variability features | `results/fixed_20N/crosscohort_summary.txt` (0.53, 0.53, 0.54 as reported in Results III-C) and `results/crosscohort_summary.txt`, "gait, standardised within dataset" (0.535 to 0.538) and "gait without variability" (0.521 to 0.576); none near the within-gaitpdb values (Results III-C) |
| matched pairs 0.65 to 0.67, mostly from different sites | `results/crosscohort_summary.txt`, gait, cross-cohort, age-matched: 0.646, 0.649 and 0.670; 49 of the 56 pairs across sites, Results III-E |
