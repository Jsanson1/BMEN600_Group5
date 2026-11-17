"""Run scripts/run_cross_cohort.py unchanged, keeping each expensive call's result, so
that the step can be split across several commands (see run_all_in_parts.py).

    RCC_CACHE=<folder> [RCC_DEADLINE=<Unix time>] python scripts/run_cross_cohort_cached.py [run_cross_cohort.py's arguments]

This loads scripts/run_cross_cohort.py as a module and wraps the five functions its
main() calls for every model and set of inputs (load_script, cross_cohort_rows,
run_pooled, dataset_of_origin, stride_matched_reference). Each wrapped call is keyed
by the function, the model and the content of every argument (each table and array
hashed), and its return value is pickled to $RCC_CACHE; a call already there returns
the kept value, any other runs the repository's own function. No random state is
shared between these calls (each starts from a seed fixed inside it), so a value kept
from an earlier command is the value a single run computes. main() then assembles and
writes the outputs exactly as when run_cross_cohort.py is run directly.

Before a call that is not kept yet, if it could not finish before $RCC_DEADLINE, the
command exits with code 75, having written no output; the next command picks up
from the kept results. The cache holds Python pickles: use only one this script made.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STOP = 75
LONGEST = {  # seconds, an upper bound on one call (the SVM's) on a two-core machine
    "cross_cohort_rows": 6 * 60,
    "run_pooled": 40 * 60,
    "dataset_of_origin": 40 * 60,
    "stride_matched_reference": 30 * 60,
}


def digest(value, h) -> None:
    if isinstance(value, pd.DataFrame):
        h.update(b"df")
        h.update(repr(list(value.columns)).encode())
        h.update(repr([str(t) for t in value.dtypes]).encode())
        h.update(pd.util.hash_pandas_object(value, index=True).to_numpy().tobytes())
    elif isinstance(value, pd.Series):
        digest(value.to_frame(), h)
    elif isinstance(value, np.ndarray):
        h.update(b"nd" + repr((value.shape, str(value.dtype))).encode())
        h.update(np.ascontiguousarray(value).tobytes())
    elif isinstance(value, (list, tuple)):
        h.update(b"seq%d" % len(value))
        for v in value:
            digest(v, h)
    elif callable(value):
        h.update(b"callable")  # a model factory, fixed by the model and the inputs
    else:
        h.update(repr((type(value).__name__, value)).encode())


def main() -> None:
    cache = Path(os.environ["RCC_CACHE"])
    deadline = float(os.environ.get("RCC_DEADLINE", "inf"))
    cache.mkdir(parents=True, exist_ok=True)
    sys.argv = [str(ROOT / "scripts" / "run_cross_cohort.py"), *sys.argv[1:]]
    sys.path.insert(0, str(ROOT / "scripts"))
    os.chdir(ROOT)
    spec = importlib.util.spec_from_file_location(
        "run_cross_cohort", ROOT / "scripts" / "run_cross_cohort.py"
    )
    rcc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rcc)
    current = {"model": None}

    def cached(name: str, fn):
        def wrapper(*args, **kwargs):
            h = hashlib.sha256()
            h.update(name.encode())
            h.update(str(current["model"]).encode())
            digest(list(args), h)
            digest(sorted(kwargs.items()), h)
            path = cache / f"{name}_{current['model']}_{h.hexdigest()[:24]}.pkl"
            if path.exists():
                print(f"[kept] {name} {current['model']}: {path.name}", flush=True)
                return pickle.loads(path.read_bytes())
            if time.time() + LONGEST[name] > deadline:
                print(f"[kept] stopping before {name} {current['model']}", flush=True)
                sys.exit(STOP)
            t0 = time.time()
            value = fn(*args, **kwargs)
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL))
            tmp.replace(path)
            print(
                f"[kept] {name} {current['model']}: computed in "
                f"{time.time() - t0:.0f} s",
                flush=True,
            )
            return value

        return wrapper

    load_script_original = rcc.load_script

    def load_script(path):
        current["model"] = Path(path).stem
        return load_script_original(path)

    rcc.load_script = load_script
    for name in LONGEST:
        setattr(rcc, name, cached(name, getattr(rcc, name)))
    rcc.main()


if __name__ == "__main__":
    main()
