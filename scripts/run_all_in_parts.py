"""Run scripts/run_all.py's plan in parts, for machines where one command cannot run
for the three to four hours the whole plan takes.

    python scripts/run_all_in_parts.py STATE_DIR MINUTES

Each call runs the steps of `run_all.plan(True)` (both datasets) in order, each built
exactly as `run_all.main()` builds it, until the next step might not finish within
MINUTES; it then stops with exit code 75 ("run again"). Finished steps are recorded
in STATE_DIR/done.txt, so the next call carries on from the first unfinished one,
and the call that finishes prints "ALL STEPS DONE". The two runs of
`run_cross_cohort.py` (the main analysis and the 20 N one) go through
`run_cross_cohort_cached.py`, which keeps each expensive call's result in
STATE_DIR/rcc_cache, so that step too can be split across calls. Every random draw
in those calls starts from a seed fixed inside the call, so the outputs are those of
a single uninterrupted run. Run it from the repository's root, with the data in
data/raw/ as data/raw/README.md describes. The final outputs of 13 and 16 November
2026 were made this way, because a command in the cloud session that ran them stops
after two hours.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STOP = 75
EXPECTED = {  # seconds, from earlier full runs on a two-core machine, with a margin
    "run_random_forest.py": 2100,
    "run_svm.py": 2700,
    "make_clean_strides.py": 900,
    "check_weargait_threshold.py": 420,
}


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__.split("\n\n")[1])
    state, budget = Path(sys.argv[1]).resolve(), float(sys.argv[2]) * 60
    spec = importlib.util.spec_from_file_location(
        "run_all", ROOT / "scripts" / "run_all.py"
    )
    run_all = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_all)
    if not run_all.weargait_present():
        raise SystemExit("WearGait-PD's files are needed (data/raw/README.md)")

    state.mkdir(parents=True, exist_ok=True)
    done_file = state / "done.txt"
    done = set(done_file.read_text().split()) if done_file.exists() else set()
    start = time.time()
    for i, (step, extra) in enumerate(run_all.plan(True)):
        if str(i) in done:
            continue
        if step == "run_cross_cohort.py":
            script = ROOT / "scripts" / "run_cross_cohort_cached.py"
            cmd = [sys.executable, str(script)]
        else:
            cmd = [sys.executable, str(ROOT / "scripts" / step)]
            left = budget - (time.time() - start)
            if EXPECTED.get(step, 600) > left:
                print(f"time limit: stopping before step {i} {step}", flush=True)
                sys.exit(STOP)
        if step in run_all.TAKE_DATA:
            cmd += ["--data", "data/raw/gaitpdb"]
        cmd += extra
        env = dict(
            os.environ,
            RCC_CACHE=str(state / "rcc_cache"),
            RCC_DEADLINE=str(start + budget),
        )
        print(f"== [{i}] {step} {' '.join(extra)}".rstrip(), flush=True)
        t0 = time.time()
        rc = subprocess.run(cmd, cwd=ROOT, env=env).returncode
        if rc == STOP:
            print(f"   stopped at the time limit after {time.time() - t0:.0f} s")
            sys.exit(STOP)
        if rc != 0:
            raise SystemExit(f"{step} failed with exit code {rc}")
        print(f"   done in {time.time() - t0:.0f} s", flush=True)
        done.add(str(i))
        done_file.write_text("\n".join(sorted(done, key=int)) + "\n")
    print("ALL STEPS DONE", flush=True)


if __name__ == "__main__":
    main()
