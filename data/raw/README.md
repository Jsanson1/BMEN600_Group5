# Raw data (not committed)

Everything in `data/raw/` except the README files is ignored by git. Each dataset is downloaded by hand to its own folder; the analysis code reads it from there and never modifies it.

## gaitpdb: PhysioNet "Gait in Parkinson's Disease" v1.0.0

- Source: https://physionet.org/content/gaitpdb/1.0.0/ (DOI 10.13026/C24H3N), contributed by J. M. Hausdorff; published 25 Feb 2008.
- Licence: Open Data Commons Attribution License v1.0 (ODC-By 1.0). Cite the database and the PhysioNet platform paper (see `report/midterm/sources.md`, S7 and S8).
- Access: open, no account.
- Size: 288.4 MB unpacked; 306 record files plus `demographics.txt`, `format.txt`, `SHA256SUMS.txt`.

Download steps:

1. Open the page above and click "Download the ZIP file (288.4 MB)". Browser downloads of this file have stalled part-way for us; if the file stops growing, restart it (the ZIP is only readable once it is complete). In a terminal, `wget -c https://physionet.org/static/published-projects/gaitpdb/gait-in-parkinsons-disease-1.0.0.zip` resumes an interrupted download.
2. Save or move the ZIP to `data/raw/gaitpdb/` and unpack it there, so that the records sit in `data/raw/gaitpdb/gait-in-parkinsons-disease-1.0.0/` (the loader also accepts the files directly in `data/raw/gaitpdb/`).
3. Check the files against the checksum list: from the repository folder run `python scripts/verify_data.py` (any platform); it should end with `311 files match, 0 mismatch, 0 missing`. (`sha256sum -c SHA256SUMS.txt` inside the unpacked folder does the same on a Mac or in Git Bash.)

What is in a record: 19 tab-separated columns at 100 Hz, time (s), 8 left-foot sensors (N), 8 right-foot sensors (N), left total (N), right total (N). File names: `<Study><Group><Subject>_<Walk>.txt`, study Ga / Ju / Si, group Co (control) or Pt (patient). `format.txt` defines only walk 01 (usual walk) and walk 10 (dual-task walk, Ga study); the other walk numbers (02 for 39 Ga recordings, 02 to 07 for 13 Ju patients) are not documented there or on the PhysioNet page (the Ju ones match the cueing conditions of its source paper). Walk 01 is the one used for the preliminary results. `demographics.txt` has one row per participant (group, sex, age, height, weight, Hoehn and Yahr, UPDRS, timed up-and-go, walking speeds).

Known quirks (handled by `src/gaitpdb/io.py`): `Juc010` in demographics is `JuCo10`, who has no recording; Ju heights are in centimetres while Ga and Si are in metres; `demographics.txt` has a ragged number of trailing tabs per line and 69 empty lines at the end, so `pandas.read_csv` refuses it; the Si controls have no UPDRS scores and the Ju and Si controls no Hoehn and Yahr stage; timestamps are printed with four decimals, so an interval occasionally reads 0.0099 s. The PhysioNet page gives a mean age of 66.3 years for both groups, but the demographics file gives 63.7 years for the controls.

## weargait_pd: WearGait-PD (external test set; not downloaded yet)

- Source: Synapse project syn52540892, https://www.synapse.org/Synapse:syn52540892/wiki/623751 (dataset DOI 10.7303/syn52540892), collected by the US FDA Center for Devices and Radiological Health with Johns Hopkins and the VA Puget Sound Health Care System. Described in Anderson et al., *Sci. Data*, vol. 13, art. 440, 2026 (`report/midterm/sources.md`, S9). The column definitions (Table S5) and the annotation event definitions (Tables S1 to S3) are in that article's Supplementary Material, which we have not read yet.
- Licence: CC BY 4.0. Cite the Synapse record and the article.
- Access: a free Synapse account (name and e-mail address, acceptance of the Synapse terms of use and of the Synapse Pledge), then the instructions on the "Data Access" tab of the project page. A person has to do this: the account is in an individual's name.
- Version: the article describes the initial release, 1,568 trials from 185 participants. Write the Synapse version number of the downloaded files and the download date here when the data arrive.

Download steps (to be completed once we have the data):

1. Register at https://www.synapse.org and follow the Data Access tab of the project page.
2. Download the "CSV files" folder (one file per participant and task, named `<SubjectID>_<Task>.csv`) and the clinical and demographic spreadsheets. The one-MAT-file-per-participant copies hold the same data and are not needed.
3. Put everything in `data/raw/weargait_pd/` (ignored by git) and record the version and date above.

What is in it (from the article; we have not seen the files):

- 185 participants: 100 with PD (35 women, 65 men; 67 ± 8 years; modified Hoehn and Yahr 2.15 ± 0.61; MDS-UPDRS part III 25 ± 10, range 6 to 59) and 85 controls (48 women, 37 men; 74 ± 9 years). Three sites, given by the prefix of the participant ID: NLS (Johns Hopkins Outpatient Center), HC (Johns Hopkins Bayview) and WPD or WHC (VA Puget Sound, Seattle), all with the same hardware, software versions and protocol.
- Clinical and demographic spreadsheets: one row per participant with the ID in the first column; age, sex and gender, height, weight, race, time since diagnosis, medication and time since the last dose, the MDS-UPDRS item scores where available, and the modified Hoehn and Yahr stage. Medication state was not controlled; time since the last dose stands in for it.
- Sensor files: up to 10 per participant, one per task, each holding the video annotations, the ProtoKinetics Zeno walkway data (8 columns), the Moticon OpenGo insole data (38 columns; each insole has 16 pressure sensors and its own accelerometer and gyroscope) and 13 Xsens MTw Awinda inertial units, 346 variables in all, every stream at 100 Hz on the walkway's clock.
- Tasks, with the code used in the file names: SelfPace (SP; four passes along the 16 ft walkway at a comfortable pace, starting and turning about 5 ft off its ends), HurriedPace (HP; the same at a hurried pace), SelfPace_mat and HurriedPace_mat (SPm, HPm; start, stop and turn on the walkway), SelfPace_matTURN (SPmT; five passes, alternating the turn direction), TandemGait (TG; two heel-to-toe passes), Timed Up and Go (TUG; three trials in one recording), Balance (B; six stances of 10 s), SelfPace_doorpat (SPdoorpat; four passes through a mock door frame over a line pattern) and FreeWalk (FW; out of the room, along corridors, a short staircase where available, a chair, and back). The tasks were recorded in this order with the sensors left in place.

How we plan to use it (task T-025 on the board):

- Task: SP is the closest match to the PhysioNet protocol (over-ground walking at a comfortable pace, turns made off the walkway), so it is the primary test task, with HP as a second condition. Each pass is only about 8 m, so a participant contributes a few dozen strides where a two-minute PhysioNet walk gives about a hundred per foot, and the variability features will be noisier. FW is longer but includes stairs and sitting down.
- Signals: the total vertical force under each foot from the insoles (summed from the 16 pressure sensors if the files give no total; the thresholds in `src/gaitpdb/events.py` are in newtons, so the force must be in newtons rather than normalised to body weight) goes through the same event detection and stride rules as the PhysioNet records. The walkway's own left and right foot-contact data, labelled by the authors and checked by a second person, are an independent measurement to compare our insole-derived stride and swing times against.
- Caveats stated in the article: the insoles are aligned to the walkway on the recording-stop signal and, after a site-specific constant correction, a small random delay remains, so the authors advise aligning the insole total force to the walkway pressure by cross-correlation before any comparison that depends on precise timing; NaN padding at the start and end of the insole columns is expected, and missing sensors are NaN in the MAT files and absent from the CSV files; 17% of trials are missing some insole or inertial data (dropouts of seven frames or more, or a lost sensor); the controls are older than the patients, the reverse of the PhysioNet database, so a model that leans on age is penalised here and the gait-only models are the ones to test; and the control group deliberately includes people with mild movement abnormalities such as essential tremor.
