# Derived data (not committed)

Everything in `data/interim/` except this README is ignored by git. The files are built from `data/raw/` by code and are never edited by hand; rebuild them with

    python scripts/make_clean_strides.py

(also part of `python scripts/run_all.py`).

| File | What it holds |
|---|---|
| `clean_strides_gaitpdb.csv` | One row per stride of both feet, for each analysed usual walk (aged 50 or over, D-006): timing, `clean`, `reason` for removal, and `included` (D-011). |
| `clean_strides_weargait.csv` | The same for WearGait-PD, its SelfPace, SelfPace_mat and SelfPace_matTURN tasks pooled per participant (column `task`). |
| `clean_strides_turns_gaitpdb.csv` | The turns found in each gaitpdb walk and the turn interval used. |
| `clean_strides_provenance.json` | The code commit the tables were built from, whether there were uncommitted changes, and every cleaning parameter. |

The cleaning itself is `src/gaitpdb/clean_data.py` (decisions D-008, D-009 and D-011 in `DECISIONS.md`). A summary of who is included and why strides were removed is committed in `results/clean_strides_summary.txt`.
