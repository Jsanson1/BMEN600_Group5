"""Turn S-number citations into IEEE numbers, in order of first citation.

While the midterm is drafted, every citation is an S-number from
report/midterm/sources.md ([S7], [S13]), so sections can be written in any
order. For the PDF, IEEE wants [1], [2], ... in order of first appearance and a
reference list in the same order. This script does that for one text file
(a section snapshot, or the whole document exported from the Google Doc as
plain text) and reports anything inconsistent.

    python scripts/renumber_citations.py report/midterm/02_background_and_research_gap.md
    python scripts/renumber_citations.py --sources report/midterm/sources.md midterm.txt -o midterm_numbered.txt

Prints the renumbered text (or writes it with -o), followed by the reference
list; warns about citations missing from the ledger and ledger entries never
cited. Markdown emphasis in the ledger (*Journal*) is stripped, because the
output is pasted into a plain-text or Google Docs document.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CITE = re.compile(r"\[S(\d+)\]")
ROW = re.compile(r"^\|\s*S(\d+)\s*\|\s*(.+?)\s*\|\s*[^|]*\|\s*[^|]*\|\s*$")


def load_ledger(path: Path) -> dict[int, str]:
    refs = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m:
            refs[int(m.group(1))] = re.sub(r"\*(.+?)\*", r"\1", m.group(2)).strip()
    if not refs:
        raise SystemExit(f"no ledger rows found in {path}")
    return refs


def renumber(text: str, refs: dict[int, str]) -> tuple[str, list[int], list[str]]:
    order: list[int] = []
    for m in CITE.finditer(text):
        n = int(m.group(1))
        if n not in order:
            order.append(n)
    number = {s: i + 1 for i, s in enumerate(order)}
    out = CITE.sub(lambda m: f"[{number[int(m.group(1))]}]", text)
    problems = [
        f"[S{s}] is cited but not in the ledger" for s in order if s not in refs
    ]
    problems += [
        f"S{s} is in the ledger but never cited" for s in sorted(refs) if s not in order
    ]
    return out, order, problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("text", help="file with [S#] citations")
    ap.add_argument("--sources", default="report/midterm/sources.md")
    ap.add_argument(
        "-o", "--output", help="write the renumbered text here instead of stdout"
    )
    args = ap.parse_args()
    refs = load_ledger(Path(args.sources))
    text = Path(args.text).read_text(encoding="utf-8")
    out, order, problems = renumber(text, refs)
    reflist = "\n".join(
        f"[{i + 1}] {refs.get(s, '[UNVERIFIED: not in the ledger]')}"
        for i, s in enumerate(order)
    )
    if args.output:
        Path(args.output).write_text(
            out + "\n\nReferences\n\n" + reflist + "\n", encoding="utf-8"
        )
        print(
            f"wrote {args.output}: {len(order)} references in order of first citation"
        )
    else:
        print(out)
        print("\nReferences\n")
        print(reflist)
    for p in problems:
        print("warning:", p, file=sys.stderr)


if __name__ == "__main__":
    main()
