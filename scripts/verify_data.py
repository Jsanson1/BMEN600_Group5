"""Check the downloaded PhysioNet files against the database's SHA256SUMS.txt.

Works on any platform (no sha256sum command needed):

    python scripts/verify_data.py [--data data/raw/gaitpdb]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gaitpdb import find_data_dir  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/raw/gaitpdb")
    args = ap.parse_args()
    root = find_data_dir(args.data)
    sums = root / "SHA256SUMS.txt"
    if not sums.exists():
        raise SystemExit(f"{sums} not found; unpack the whole ZIP, it is part of it")
    ok = bad = missing = 0
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        p = root / name.strip()
        if not p.exists():
            missing += 1
            print("missing:", name)
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() == digest:
            ok += 1
        else:
            bad += 1
            print("CHECKSUM MISMATCH:", name)
    print(
        f"{ok} files match, {bad} mismatch, {missing} missing (of {ok + bad + missing} listed)"
    )
    if bad or missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
