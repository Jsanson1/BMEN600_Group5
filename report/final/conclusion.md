# Conclusion (draft 1 for the final paper)

Draft by Jamie Sanson's AI assistant for task T-024, 16 November 2026. The task was Yassien's; the team asked, through Jamie, for the paper to be finished, so this draft was written for Yassien and the group to check and rewrite as they see fit. The brief asks for about half a page that states the answer to the research question, the project's main contribution and its most important qualification, without new results or unsupported claims about causality, clinical usefulness, generalisability or readiness for deployment. Every statement below is made, with its numbers, in the Results (T-032) or the Discussion (T-023); the table at the end says where. About 276 words.

## Conclusion

Five timing features computed from foot force alone, without clinical scores, separated people with PD from controls aged 50 and over moderately within gaitpdb, on unseen participants and largely across its three recording protocols, with swing-time asymmetry carrying much of the separation. Applied to WearGait-PD, an independent cohort recorded with different insoles, a walking protocol of short passes and controls older than its patients, models fitted on gaitpdb gave a separation that could not be distinguished from chance. This held at a second contact threshold, with standardised inputs and without the variability features, and was not explained by the number of strides. Our contribution is this participant-level, cross-cohort evaluation of three simple models on interpretable features, with the analysis and its checks committed before any model was scored against the second cohort's diagnoses, and every step public in code. It shows that participant-level validation within one database is not sufficient: models that pass it can still fail in another cohort. The main qualification is that protocol, hardware, population and site all differ between the two datasets, so this study cannot say which difference matters most or how much the age of the controls explains, and the upper limits of the cross-cohort intervals (0.62 to 0.66) do not exclude a modest transfer. Both datasets also compare diagnosed patients with volunteer controls rather than the early, undiagnosed disease a screening aid would meet. Before foot-force timing is used to flag people for referral, a model has to be validated with the device, walking protocol and population where it would be used; the next step is to separate the walking protocol from the population within WearGait-PD itself.

## Where each statement comes from

| Statement | Where it is in the paper |
|---|---|
| moderate separation within gaitpdb, on unseen participants and largely across protocols, swing-time asymmetry carrying much of it | Discussion IV-A; Results III-B and III-D |
| different insoles, short passes, controls older than its patients | Discussion IV-C; Results III-A |
| not distinguishable from chance in WearGait-PD | Results III-B (intervals include 0.5); Discussion IV-A |
| held at 20 N, with standardised inputs, without the variability features; not explained by stride count | Results III-C; Discussion IV-D |
| checks committed before scoring; public code | Results III-C (fixed before WearGait-PD's diagnoses were used); Discussion IV-D |
| participant-level validation necessary but not sufficient | Discussion IV-B |
| protocol, hardware, population and site differ together; how much age explains remains open; upper limits 0.62 to 0.66 | Discussion IV-C and IV-D; `results/crosscohort_summary.txt`, gait, cross-cohort (0.621, 0.620, 0.659) |
| diagnosed patients and volunteer controls, not early undiagnosed disease | Discussion IV-E and IV-F |
| validate where it would be used; separate protocol from population within WearGait-PD | Discussion IV-E and IV-G |
