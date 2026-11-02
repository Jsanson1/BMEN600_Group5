| Model                                         | AUC within protocol   | AUC across protocols (pooled)   |   Ga |   Ju |   Si | Sensitivity at 90% specificity   |   Balanced accuracy |   Brier |
|:----------------------------------------------|:----------------------|:--------------------------------|-----:|-----:|-----:|:---------------------------------|--------------------:|--------:|
| Logistic regression: gait features            | 0.79 (0.70 to 0.88)   | 0.73 (0.65 to 0.81)             | 0.8  | 0.8  | 0.66 | 0.53 (0.36 to 0.63)              |                0.68 |   0.187 |
| Logistic regression: gait features + age, sex | 0.79 (0.71 to 0.88)   | 0.74 (0.67 to 0.81)             | 0.8  | 0.82 | 0.66 | 0.46 (0.32 to 0.65)              |                0.68 |   0.185 |
| Logistic regression: age and sex only         | 0.60 (0.51 to 0.69)   | 0.58 (0.49 to 0.67)             | 0.52 | 0.64 | 0.62 | 0.14 (0.06 to 0.27)              |                0.5  |   0.246 |
| Random forest: gait features                  | 0.75 (0.65 to 0.85)   | 0.70 (0.62 to 0.78)             | 0.79 | 0.69 | 0.65 | 0.43 (0.31 to 0.58)              |                0.66 |   0.205 |
| Random forest: gait features + age, sex       | 0.74 (0.64 to 0.83)   | 0.73 (0.65 to 0.80)             | 0.78 | 0.74 | 0.69 | 0.45 (0.32 to 0.57)              |                0.65 |   0.208 |
| Swing-time asymmetry alone                    | 0.73 (0.64 to 0.81)   | 0.71 (0.63 to 0.79)             | 0.68 | 0.73 | 0.77 | 0.46 (0.26 to 0.59)              |                0.66 |   0.213 |
| Swing fraction of the stride alone            | 0.71 (0.61 to 0.82)   | 0.70 (0.61 to 0.77)             | 0.88 | 0.71 | 0.58 | 0.41 (0.22 to 0.53)              |                0.64 |   0.213 |
| Swing-time variability alone                  | 0.69 (0.61 to 0.78)   | 0.69 (0.61 to 0.77)             | 0.7  | 0.7  | 0.68 | 0.20 (0.08 to 0.43)              |                0.64 |   0.229 |
| Stride-time variability alone                 | 0.66 (0.56 to 0.75)   | 0.66 (0.57 to 0.74)             | 0.73 | 0.72 | 0.54 | 0.31 (0.17 to 0.45)              |                0.59 |   0.226 |
| Mean stride time alone                        | 0.56 (0.46 to 0.65)   | 0.52 (0.43 to 0.60)             | 0.51 | 0.4  | 0.68 | 0.10 (0.02 to 0.26)              |                0.48 |   0.247 |
| Chance (share of PD in training)              | 0.50 (0.50 to 0.50)   | 0.47 (0.39 to 0.56)             | 0.5  | 0.5  | 0.5  | 0.08 (0.02 to 0.26)              |                0.5  |   0.246 |
