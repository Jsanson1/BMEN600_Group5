# Feature dictionary

Columns of `results/features_gaitpdb.csv` and `results/features_weargait.csv` (`n_tasks` is in the WearGait-PD table only), written by `scripts/make_features.py` from `gaitpdb.features.FEATURE_DICTIONARY`. One row per participant who meets the minimum of clean strides per foot (DECISIONS.md D-011).

| Column | Unit | Definition |
|---|---|---|
| `participant` | - | Participant ID as in the dataset. |
| `dataset` | - | gaitpdb (PhysioNet) or weargait (WearGait-PD). |
| `study` | - | gaitpdb sub-study (Ga, Ju or Si) or WearGait-PD site prefix (NLS, HC, WPD or WHC). Never a model input: the prefixes WPD and WHC encode the diagnosis, and NLS and HC each recruited one group only. |
| `group` | - | PD or Control, from the dataset's participant table. |
| `Age` | years | Age in the dataset's participant table (all 50 or over, D-006). |
| `sex` | - | M or F, from the dataset's participant table. |
| `n_tasks` | count | WearGait-PD only: tasks (SelfPace, SelfPace_mat, SelfPace_matTURN) that contribute clean strides; their strides are pooled (D-011). |
| `n_strides_left` | count | Clean strides of the left foot used. |
| `n_strides_right` | count | Clean strides of the right foot used. |
| `stride_time_mean_s` | s | Mean stride time (heel strike to the next heel strike of the same foot), both feet. |
| `stride_time_cv_pct` | % | Stride-time variability: coefficient of variation (100 x SD / mean) of each foot's stride times, averaged over the two feet. |
| `stride_time_madcv_pct` | % | Robust stride-time variability: 100 x 1.4826 x median absolute deviation / median of each foot's stride times, averaged over the two feet. |
| `swing_time_mean_s` | s | Mean swing time (toe off to heel strike), both feet. |
| `swing_time_cv_pct` | % | Swing-time variability: coefficient of variation of each foot's swing times, averaged over the two feet. |
| `swing_time_madcv_pct` | % | Robust swing-time variability: as the robust stride-time variability, for swing times. |
| `stance_time_mean_s` | s | Mean stance time (heel strike to toe off), both feet. |
| `swing_pct_mean` | % of stride | Mean swing time as a share of its stride. |
| `stride_time_asymmetry_pct` | % | 100 x |left - right| / mean(left, right) of the two feet's mean stride times. Near zero in a continuous walk (each foot's strides span the same time), so it mostly reflects stride count and the walk's start and end. |
| `swing_time_asymmetry_pct` | % | Swing asymmetry: 100 x |left - right| / mean(left, right) of the two feet's mean swing times. |
