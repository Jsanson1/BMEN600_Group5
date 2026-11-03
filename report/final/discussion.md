# Discussion (draft 1 for Section V of the final paper)

Draft by Jamie Sanson's AI assistant for task T-023, 2 November 2026, for the group to review before it goes into the shared Word file. Every number is quoted from an output file of the final run on branch `jamie/T-022-cross-cohort-run` (commit `47ebeca`); the table at the end gives the file for each. Citations use the labels of `report/midterm/sources.md` (S1 to S20) and `report/final/sources.md` (S21 onwards), renumbered in IEEE order at assembly. Figure numbers follow the repository and change with the paper's own numbering. The support vector machine (T-020) is not in these results yet; the paragraphs that compare models need a sentence for it once it is.

## A. Answer to the research question

Within one cohort, a handful of timing features computed from foot force alone separate people with PD from controls aged 50 and over moderately, and the separation survives a change of recording protocol within that cohort. In gaitpdb, the logistic regression reached an AUC of 0.79 (95% CI 0.70 to 0.88) on participants it had not seen and 0.73 (0.65 to 0.81) on a sub-study it had not seen; the random forest reached 0.75 and 0.70. The swing phase carries the separation: swing-time asymmetry alone reached 0.73 and 0.71, and neither multivariable model was significantly better than it. The separation did not survive a change of cohort. Fitted on gaitpdb and applied once to WearGait-PD, the models reached 0.532 (0.449 to 0.621) and 0.573 (0.486 to 0.659), and gaitpdb's threshold for 90% specificity flagged most WearGait-PD participants, patients and controls alike. The answer to our question is therefore split: yes within a cohort, through swing-phase timing; no across these two cohorts, with these features.

## B. Relation to previous work

Our within-cohort results sit well below the accuracies of up to 98% reported on the same database [S11] and below participant-level results with more flexible models: deep networks on the raw vertical ground reaction force reached a mean AUC of 0.94 under subject-wise splits [S13], and gradient boosting on gait features alone reached 0.84 on a participant-level holdout [S14]. Part of the gap is expected. Splitting recordings rather than participants lets a model recognise people instead of disease, and record-wise validation "often massively overestimates" accuracy [S12]; our splits keep each participant, and in the across-protocol test each sub-study, out of training. Our drop across protocols, to 0.66 on the Si sub-study for the logistic regression, agrees with the spread of 0.50 to 1.00 that Jin reported across the same three protocols [S14]. The source studies of the database established that stride and swing time variability are higher in PD [S4]–[S6]. In our data, variability separated the groups less well than swing-time asymmetry (AUC 0.66 for stride time variability alone, 0.69 for swing time variability), and it was the feature most changed by the recording protocol (Section V-C). Jin called for validation on an external cohort [S14]. Our cross-cohort test is such a validation, and it fails: participant-level validation within one database is necessary, but it does not show that a model will work in another cohort.

## C. Why the models do not transfer

The two datasets differ before any model is fitted (Fig. 4), and a model given only the five features told them apart with an AUC of 0.940. We weighed five explanations for the failed transfer against the evidence.

*Walking protocol.* WearGait-PD's straight walking is short. Its SelfPace task, for example, is four passes along a 16 ft (about 4.9 m) walkway [S9]. Its straight bouts had a median of 2 consecutive clean strides, against 18 in gaitpdb, so 62% of its clean strides open or close a bout. The first stride of a bout was on average 6.7% longer than the participant's median, and stride and swing time variability were about twice gaitpdb's (median coefficient of variation 4.96% against 2.41% for stride time). Strides after a turn are known to be longer than the walk average, by 3.2% in patients with movement disorders and 1.4% in healthy older adults; on a 10 m walkway, removing one more stride either side of each turn changed group variability by at most 0.5 percentage points [S21]. On WearGait-PD's shorter walkway, removing one stride at each bout end lowered the median stride time variability from 4.96% to 2.83% (gaitpdb: 2.27% after the same trimming). Bout ends thus appear to account for much of the excess variability, but the trimmed series are too short to settle it: 91 of the 169 participants fall below the minimum of 10 strides per foot. The protocol cannot be the whole explanation either, because the models without the variability features transferred no better (0.521 and 0.576).

*Number of strides.* WearGait-PD's participants contributed fewer clean strides (median 32 on the weaker foot, against 81). Recomputing gaitpdb's test features from WearGait-PD's stride counts cost at most 0.008 AUC within gaitpdb, so stride count alone does not explain the failure.

*Population.* WearGait-PD's controls were older than its patients (median 75 against 68 years), the reverse of gaitpdb (64 against 68), and its control group deliberately includes people with mild movement abnormalities such as essential tremor [S9]. In pairs of a patient and a control of the same sex within three years of age, the AUC rose to 0.646 (0.539 to 0.750) and 0.670 (0.566 to 0.771). The age structure therefore plausibly accounts for part of the failure, although these intervals overlap the main ones. Disease stage is similar in the two cohorts (Hoehn and Yahr 2.15 ± 0.61 in the WearGait-PD article [S9]; 2 to 3 in the Ga and 2 to 2.5 in the Si sub-studies [S4], [S5]). Medication state could not be compared: WearGait-PD records the time since the last dose [S9], and gaitpdb's records do not include it.

*Hardware and event detection.* gaitpdb used eight force sensors under each foot [S7], WearGait-PD pressure insoles [S9]. We used one contact rule for both, chosen on agreement with WearGait-PD's walkway. At that threshold, 83% of the walkway's footfalls had a one-to-one insole match and stride times agreed (median difference 0.00 s), but stance times agreed only within −0.15 to +0.11 s (95% limits of agreement), so the phase-based features, among them swing fraction and swing-time asymmetry, carry more measurement error in WearGait-PD than stride time does. At a fixed 20 N the cross-cohort result was the same (0.534 and 0.540), so the threshold is not the explanation; the hardware may still be part of it.

*Recruitment site.* Two of WearGait-PD's three sites contributed only one group each. A model fitted on gaitpdb cannot have learned these sites, and at the one site with both groups and similar ages, VA Puget Sound, the AUC was 0.555 and 0.554. Site does not explain the failure, although that subset is small (57 participants).

Standardising each dataset's features, which removes differences in their level and spread, left the AUCs at 0.535 and 0.538. The problem is therefore not only that WearGait-PD's values sit elsewhere, which recalibration could fix, but that the features rank its participants poorly. A check we added after the pre-specified analysis, and which is exploratory, points the same way: within WearGait-PD each feature alone gave an AUC between 0.520 and 0.584, a logistic regression trained and tested there reached 0.595 (0.500 to 0.690), and swing fraction, lower in PD in gaitpdb (AUC 0.283), was not lower in PD in WearGait-PD (0.527).

## D. What the study shows and what it does not

The study shows that five foot-force timing features that separate PD from controls within gaitpdb do not separate them in WearGait-PD, under an analysis whose code and inputs were committed before WearGait-PD's diagnoses were first used. The result holds at either contact threshold and is not explained by stride count, by standardisation or by the variability features. It suggests, but cannot establish, that WearGait-PD's short walkway passes and the make-up of its control group are the main reasons: the bout-end and age-matched analyses point that way, but protocol, hardware, population and site all change together between the two datasets, and two datasets cannot separate them. Nor can it establish that foot-force timing cannot detect PD in other settings: with 169 test participants the upper limits of the cross-cohort intervals reach 0.621 and 0.659, so a modest transfer is not excluded.

## E. What this means for patients and clinicians

Even within gaitpdb, the logistic regression found about half of the patients (sensitivity 0.53) at 90% specificity. At a prevalence of 1%, about that of PD in people over 60 [S15], this operating point gives a positive predictive value of 0.057: about 94 of every 100 people flagged would not have PD. Carried to the second cohort, the same threshold had no screening value (positive predictive value 0.011, barely above the prevalence). A classifier of this kind cannot be moved to another clinic or walking protocol without being validated there, and because the features barely separate the groups within WearGait-PD, recalibrating its threshold on local data would not be enough. Each false positive in screening also has a cost for the person flagged: worry, further tests and referral.

## F. Limitations

Beyond the alternative explanations above, five limitations bound these conclusions. First, the samples are modest (155 and 169 participants), and every interval is correspondingly wide. Second, turns in gaitpdb were located from the timing of the walking path rather than observed, and the Si sub-study's usual walk was assumed to be overground walking because the dataset does not state it (Methods). Third, each gaitpdb participant contributed one usual walk, while WearGait-PD's three tasks were pooled, which adds about 10% to stride time variability, and 11 of its 181 participants aged 50 or over had no insole data. Fourth, the contact threshold was chosen against WearGait-PD's walkway, the only reference available, and the walkway is itself a measurement rather than ground truth. Fifth, gaitpdb's records include no ethnicity or socioeconomic information, so how well either cohort represents a population that would be screened cannot be judged.

## G. Next step

The most useful next step is to separate the walking protocol from the population. Recording the same participants in both a continuous walk of a minute or more and short walkway passes, with the same insoles, would show directly how much of the separation the short passes remove; a dataset that already holds both conditions would serve equally well. Within WearGait-PD, the short passes could become a test rather than a weakness: its protocol is rich in turns, one of the challenging conditions under which quantitative gait measures detect PD more sensitively [S3], and turn-based measures could be taken from the same insole signals and evaluated exactly as here.

## Numbers and where they come from

All files are in `results/` on `jamie/T-022-cross-cohort-run` at `47ebeca`.

| Number in the text | File | Line or label |
| --- | --- | --- |
| 0.79 (0.70 to 0.88), 0.73 (0.65 to 0.81); 0.75, 0.70; Si 0.66 | `model_comparison.txt` | Logistic regression / Random forest: gait features |
| 0.73 and 0.71; not significantly better | `model_comparison.txt` | Swing-time asymmetry alone; paired differences (Holm) |
| 0.66, 0.69 | `model_comparison.txt` | Stride-time / swing-time variability alone, within protocol |
| sensitivity 0.53, PPV 0.057 | `model_comparison.txt` | Sensitivity at 90% specificity, logistic regression: gait features |
| 0.532 (0.449 to 0.621), 0.573 (0.486 to 0.659); flagged most; PPV 0.011 | `crosscohort_summary.txt` | `[logreg]` and `[rf]`, gait, cross-cohort (carried-over threshold: sensitivity 0.93 and specificity 0.12; 0.77 and 0.28) |
| 0.940 | `crosscohort_summary.txt` | dataset of origin |
| 0.008 | `crosscohort_summary.txt` | stride-matched reference, drop |
| 0.646 (0.539 to 0.750), 0.670 (0.566 to 0.771) | `crosscohort_summary.txt` | cross-cohort, age-matched |
| 0.555, 0.554; 57 participants | `crosscohort_summary.txt` | cross-cohort, VA Puget Sound only |
| 0.535, 0.538 | `crosscohort_summary.txt` | gait, standardised within dataset |
| 0.521, 0.576 | `crosscohort_summary.txt` | gait without variability |
| 0.534, 0.540 | `fixed_20N/crosscohort_summary.txt` | gait, cross-cohort |
| 0.520 to 0.584; 0.595 (0.500 to 0.690); 0.283, 0.527; ages 75, 68, 64 | `weargait_signal_check.txt` | weargait and gaitpdb blocks |
| median bout 2 and 18; 62%; 6.7%; 4.96%, 2.41%, 2.83%, 2.27%; 91 of 169; 32 and 81 | `feature_checks.txt` | sections 1 and 3 |
| about 10% | `feature_checks.txt` | section 2 (stride_s median 1.096) |
| 83%, 0.00 s, −0.15 to +0.11 s | `weargait_threshold_check.txt` | 5% of force level (one to one 83.4%; stride +0.000; stance limits −0.147 to +0.105) |
| 155, 169; 11 of 181 | `clean_strides_summary.txt`, `weargait_participants.txt` | inclusion counts |
