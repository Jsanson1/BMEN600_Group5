"""Which steps scripts/run_all.py runs, with and without WearGait-PD's files."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_all.py"
spec = importlib.util.spec_from_file_location("run_all", SCRIPT)
run_all = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_all)


def test_weargait_present_needs_both_sheets_and_a_task_file(tmp_path):
    assert not run_all.weargait_present(tmp_path)
    for name, _ in run_all.SHEETS.values():
        (tmp_path / name).write_text("")
    assert not run_all.weargait_present(tmp_path)
    (tmp_path / "csv").mkdir()
    (tmp_path / "csv" / "NLS001_SelfPace.csv").write_text("")
    assert run_all.weargait_present(tmp_path)


def test_with_weargait_every_step_runs_then_the_20N_analysis():
    steps = [step for step, _ in run_all.plan(True)]
    n = len(run_all.STEPS)
    assert steps[:n] == run_all.STEPS
    assert steps[n:] == [step for step, _ in run_all.SENSITIVITY_20N]


def test_without_weargait_nothing_that_describes_both_datasets_is_overwritten():
    plan = run_all.plan(False)
    steps = [step for step, _ in plan]
    assert steps == [s for s in run_all.STEPS if s not in run_all.NEEDS_WEARGAIT]
    assert "run_logreg.py" in steps and "compare_models.py" in steps
    extra = dict(plan)
    for step in ("make_clean_strides.py", "make_features.py"):
        flag = extra[step].index("--summary")
        assert extra[step][flag + 1].startswith("data/interim/")
    others = [
        s for s in steps if s not in ("make_clean_strides.py", "make_features.py")
    ]
    assert all(extra[s] == [] for s in others)


def test_the_paper_figure_runs_without_weargait_and_the_cohort_table_needs_it():
    without = [step for step, _ in run_all.plan(False)]
    assert "make_figure5.py" in without  # reads only results/
    assert "make_cohort_table.py" not in without  # reads WearGait-PD's PD sheet
    steps = run_all.STEPS
    assert steps.index("make_figure5.py") > steps.index("run_cross_cohort.py")
    assert steps.index("make_figure5.py") > steps.index("compare_models.py")
    assert "make_cohort_table.py" in run_all.TAKE_DATA
