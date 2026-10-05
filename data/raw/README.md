# Raw data (not committed)

Everything in `data/raw/` except the README files is ignored by git. Each dataset is downloaded by hand to its own folder; the analysis code reads it from there and never modifies it.

## gaitpdb: PhysioNet "Gait in Parkinson's Disease" v1.0.0

- Source: https://physionet.org/content/gaitpdb/1.0.0/ (DOI 10.13026/C24H3N), contributed by J. M. Hausdorff; published 25 Feb 2008.
- Licence: Open Data Commons Attribution License v1.0 (ODC-By 1.0). Cite the database and the PhysioNet platform paper (see `report/midterm/sources.md`, S7 and S8).
- Access: open, no account.
- Size: 288.4 MB unpacked; 306 record files plus `demographics.txt`, `format.txt`, `SHA256SUMS.txt`.

Download steps:

1. Open the page above and click "Download the ZIP file (288.4 MB)", or in a terminal run `wget -r -N -c -np https://physionet.org/files/gaitpdb/1.0.0/`.
2. Save or move the ZIP to `data/raw/gaitpdb/` and unpack it there, so that the records sit in `data/raw/gaitpdb/gait-in-parkinsons-disease-1.0.0/` (the loader also accepts the files directly in `data/raw/gaitpdb/`).
3. Check the files against the checksum list: from `data/raw/gaitpdb/gait-in-parkinsons-disease-1.0.0/` run `sha256sum -c SHA256SUMS.txt` (Git Bash on Windows, Terminal on a Mac). Every line should say OK.

What is in a record: 19 tab-separated columns at 100 Hz, time (s), 8 left-foot sensors (N), 8 right-foot sensors (N), left total (N), right total (N). File names: `<Study><Group><Subject>_<Walk>.txt`, study Ga / Ju / Si, group Co (control) or Pt (patient), walk 01 = usual walk, 10 = dual-task walk (Ga study only), 02 to 07 = other conditions of the Ju study. `demographics.txt` has one row per participant (group, sex, age, height, weight, Hoehn and Yahr, UPDRS, timed up-and-go, walking speeds).

Known quirks (handled by `src/gaitpdb/io.py`): `Juc010` in demographics is `JuCo10`, who has no recording; Ju heights are in centimetres while Ga and Si are in metres; timestamps are printed with four decimals, so an interval occasionally reads 0.0099 s.
