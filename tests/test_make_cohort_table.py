"""The summaries in scripts/make_cohort_table.py, on small synthetic inputs."""

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "make_cohort_table.py"
spec = importlib.util.spec_from_file_location("make_cohort_table", SCRIPT)
table = importlib.util.module_from_spec(spec)
spec.loader.exec_module(table)


def test_median_iqr_and_range():
    x = pd.Series([1, 2, 3, 4, 5, np.nan])
    assert table.median_iqr(x) == "3 (2 to 4)"
    assert table.median_range(pd.Series([2, 2.5, 3, np.nan])) == "2.5 (2 to 3)"
    assert table.median_iqr(pd.Series([np.nan])) == "n/a"


def test_counts_by_orders_by_count_then_name():
    assert table.counts_by(pd.Series(["b", "a", "c", "c", "b"])) == "b 2, c 2, a 1"


def test_rows_per_group_with_stage_for_pd_only():
    features = pd.DataFrame(
        {
            "participant": ["p1", "p2", "p3", "c1", "c2"],
            "group": ["PD", "PD", "PD", "Control", "Control"],
            "Age": [60, 70, 80, 65, 75],
            "sex": ["F", "M", "M", "F", "F"],
            "n_strides_left": [50, 60, 70, 40, 45],
            "n_strides_right": [55, 58, 90, 41, 44],
        }
    )
    site = pd.Series(["A", "B", "B", "A", "A"], index=features.index)
    stage = pd.Series({"p1": 2.0, "p2": 3.0, "p3": np.nan, "c1": 0.0})
    rows = table.table_rows(features, "test", site, stage)
    pd_row, co_row = rows
    assert pd_row["Participants"] == 3 and co_row["Participants"] == 2
    assert pd_row["Sub-study or site"] == "B 2, A 1"
    assert pd_row["Age, years"] == "70 (65 to 75)"
    assert pd_row["Women, n (%)"] == "1 (33%)" and co_row["Women, n (%)"] == "2 (100%)"
    assert pd_row["Hoehn and Yahr stage"] == "2.5 (2 to 3), 1 missing"
    assert co_row["Hoehn and Yahr stage"] == ""
    # the foot with fewer clean strides: 50, 58, 70
    assert pd_row["Clean strides, foot with fewer"] == "58 (54 to 64)"


def test_weargait_stage_is_read_from_the_second_header_row(tmp_path):
    name = table.SHEETS["PD"][0]
    (tmp_path / name).write_text(
        "-,-.1,Part III\n"
        f"Subject ID,Sex,{table.WEARGAIT_HY}\n"
        "NLS001,M,2\n"
        "NLS002,F,-\n"
        ",,\n"
        "NLS003,F, 2.5\n",
        encoding="utf-8",
    )
    stage = table.weargait_hoehn_yahr(tmp_path)
    assert list(stage.index) == ["NLS001", "NLS002", "NLS003"]
    assert stage["NLS001"] == 2 and np.isnan(stage["NLS002"]) and stage["NLS003"] == 2.5
