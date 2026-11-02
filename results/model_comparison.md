| Model                                         | AUC within protocol   | AUC across protocols (pooled)   |   Ga |   Ju |   Si | Sensitivity at 90% specificity   |   Balanced accuracy |   Brier |
|:----------------------------------------------|:----------------------|:--------------------------------|-----:|-----:|-----:|:---------------------------------|--------------------:|--------:|
| Logistic regression: gait features            | 0.82 (0.75 to 0.90)   | 0.77 (0.70 to 0.84)             | 0.83 | 0.78 | 0.74 | 0.52 (0.30 to 0.69)              |                0.76 |   0.176 |
| Logistic regression: gait features + age, sex | 0.81 (0.73 to 0.88)   | 0.77 (0.70 to 0.84)             | 0.83 | 0.77 | 0.75 | 0.52 (0.27 to 0.66)              |                0.74 |   0.181 |
| Logistic regression: age and sex only         | 0.59 (0.49 to 0.69)   | 0.57 (0.48 to 0.66)             | 0.53 | 0.61 | 0.64 | 0.13 (0.01 to 0.32)              |                0.49 |   0.248 |
| Swing-time asymmetry alone                    | 0.76 (0.69 to 0.84)   | 0.76 (0.68 to 0.83)             | 0.76 | 0.73 | 0.78 | 0.45 (0.26 to 0.61)              |                0.68 |   0.201 |
| Swing fraction of the stride alone            | 0.76 (0.67 to 0.84)   | 0.75 (0.67 to 0.82)             | 0.88 | 0.74 | 0.64 | 0.45 (0.31 to 0.61)              |                0.69 |   0.203 |
| Swing-time variability alone                  | 0.68 (0.60 to 0.75)   | 0.66 (0.58 to 0.75)             | 0.72 | 0.58 | 0.74 | 0.23 (0.11 to 0.41)              |                0.62 |   0.224 |
| Stride-time variability alone                 | 0.60 (0.49 to 0.70)   | 0.57 (0.47 to 0.66)             | 0.46 | 0.55 | 0.74 | 0.11 (0.02 to 0.20)              |                0.58 |   0.241 |
| Mean stride time alone                        | 0.55 (0.47 to 0.63)   | 0.51 (0.42 to 0.60)             | 0.51 | 0.42 | 0.67 | 0.13 (0.04 to 0.25)              |                0.48 |   0.246 |
| Stride-time asymmetry alone                   | 0.47 (0.38 to 0.57)   | 0.42 (0.33 to 0.50)             | 0.38 | 0.58 | 0.38 | 0.00 (0.00 to 0.11)              |                0.49 |   0.25  |
| Chance (share of PD in training)              | 0.50 (0.50 to 0.50)   | 0.46 (0.38 to 0.55)             | 0.5  | 0.5  | 0.5  | 0.11 (0.02 to 0.20)              |                0.5  |   0.246 |
