# BMEN 600 Project - Fall 2026

## Team Name - Group 5: “The Singing Oats”🎤🥣

### Team members: Jamie Sanson, Yassien Tawfik, Anna Klygina

## Candidate Project 1

Evaluating gait data to diagnose Parkingson’s disease using gait and motion analysis vertical ground reaction forces.

### Biomedical Problem

Parkinson disease (PD) is the fastest-growing neurodegenerative disorder worldwide, affecting approximately 1% of the global population of individuals older than 60 years of age [1]. Gait disturbance, in addition to cognitive decline, has been observed as a common symptom of Parkinson’s disease, however the specific gait patterns in PD patients are not well understood [2]. These gait disturbances have been previously characterized by a slowed gait, shorter step length, and postural instability, however these gait parameters may not be statistically significant between PD patients and those without cognitive decline [2]. It remains to be answered whether the diagnosis of PD can be better supported with gait and motion analysis data, especially for patient populations in rural communities that may lack a neurological specialist, and may require telehealth support to provide care.

### Possible Research Question

Are the gait deficits associated with Parkinson's disease sufficient for diagnosis?

### Dataset

- A) [https://physionet.org/content/multimodal-gait-dataset/1.0.0/](https://physionet.org/content/multimodal-gait-dataset/1.0.0/)
- B) [https://physionet.org/content/gaitpdb/1.0.0/](https://physionet.org/content/gaitpdb/1.0.0/)

### Biggest Uncertainty

It is unclear whether the Parkinson dataset segments the force plate data into the various phases of gait. We expect that we can quantify differences in the vertical ground reaction forces across heel strike, foot flat, and toe off in either proportional time duration or mean forces, however this is dependent on whether or not we can identify those segments of gait from the force place data alone.

[1] S. Zafar, F. Lui, and S. Yaddanapudi, “Parkinson disease,” Parkinson Disease, [https://www.ncbi.nlm.nih.gov/books/NBK470193/](https://www.ncbi.nlm.nih.gov/books/NBK470193/) (accessed Sep. 18, 2026).
[2] S. M. Kim, D. H. Kim, Y. Yang, S. W. Ha, and J. H. Han, “Gait patterns in parkinson’s disease with or without cognitive impairment,” Dementia and Neurocognitive Disorders, vol. 17, no. 2, p. 57, Jul. 2018. doi:10.12779/dnd.2018.17.2.57

...

## Candidate Project 2

### Biomedical Problem

The presence of music and its genre are known to modulate phasic D1 activity in the dorsal striatum. The dorsal striatum is highly associated with cognitive arousal, however the relationship between cognitive arousal and the perturbations to local dopamine dynamics elicited from music remains unclear. Establishing a framework for how music interacts with arousal could inform future clinical interventions for ADHD.

Fritz, T.H., Girbardt, J., Rullmann, M. et al. Music engages the phasic dopaminergic D1-receptor system in humans: a PET-fMRI study using [11C]SCH23390. Eur J Nucl Med Mol Imaging 53, 4689–4699 (2026). [https://doi.org/10.1007/s00259-026-07837-y](https://doi.org/10.1007/s00259-026-07837-y)

### Possible Research Question

Does listening to music meaningfully alter arousal, quantified by dopamine dynamics in the dorsal striatum?

### Dataset

- A) [https://physionet.org/content/multimodal-nback-music/1.0.0/](https://physionet.org/content/multimodal-nback-music/1.0.0/)
- B) [https://link.springer.com/article/10.1007/s00259-026-07837-y](https://link.springer.com/article/10.1007/s00259-026-07837-y)

### Biggest Uncertainty

Whether we’ll be able to quantify cognitive arousal in a manner that divorces itself from dopamine dynamics in the striatum. One idea may be to find a dataset which quantifies arousal using a standardized working memory task (e.g., delayed-match-to-sample), however we still need to find a dataset for this.

## Current Decision

We are currently leaning toward Candidate Project 1 because it more closely aligns with our interests, and because we feel that it would be a more powerful project to pursue in terms of the types of analyses available to us. Moreover, our second candidate project relies on a dataset that we have not yet found.
