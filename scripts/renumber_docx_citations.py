"""Turn labelled citations in the group's Word file into IEEE numbers (midterm assembly).

The group writes citations as labels, such as [AK1], [S12] or [SciPy], and keeps each entry
of the reference list starting with its label, "[S12] S. Saeb, ...". This script reads a
.docx and writes a new one in which

* the labels are numbered in order of first citation in the body (everything before the
  "References" heading), and every citation group becomes [n] or [n], [m], with three or
  more consecutive numbers written as [n]-[m] (en dash);
* the reference entries are put in that order and lose their "[label] " prefix, and the
  numbered list style supplies [1], [2], ...;
* entries that are never cited are removed, and listed;
* anything in square brackets that looks like a label but has no entry is left as it is,
  and listed, so it can be fixed by hand.

Nothing else in the file changes. Always keep the labelled original; run this on a copy.

    python scripts/renumber_docx_citations.py midterm.docx -o midterm_numbered.docx
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

TOKEN_RE = re.compile(
    r"<w:p(?: [^>]*)?/>|<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>|<w:sectPr.*?</w:sectPr>",
    re.S,
)
GROUP_RE = re.compile(r"\[([^\[\]]+)\]")
LABEL_START_RE = re.compile(r"\s*\[([^\]]+)\]\s")
WT_RE = re.compile(r"(<w:t(?: [^>]*)?>)([^<]*)(</w:t>)")
PARA_RE = re.compile(r"<w:p[ >].*?</w:p>", re.S)


def text_of(xml: str) -> str:
    return "".join(m.group(2) for m in WT_RE.finditer(xml))


def edit_text(xml: str, edits: list[tuple[int, int, str]]) -> str:
    """Apply (start, end, new text) edits given as offsets in text_of(xml).

    Word often splits one citation over several runs, for example "[", "pandasPaper",
    ", ", "pandasZenodo", "]" around its spell-check marks. The new text goes into the
    run where the edited span starts, and the rest of the span is removed from the runs
    it covers, so the runs and their formatting stay as they are.
    """
    pieces = list(WT_RE.finditer(xml))
    texts = [m.group(2) for m in pieces]
    starts, ends, pos = [], [], 0
    for t in texts:
        starts.append(pos)
        pos += len(t)
        ends.append(pos)

    def piece_at(offset: int) -> int:  # in the original text, before any edit
        return next(k for k in range(len(texts)) if starts[k] <= offset < ends[k])

    for s, e, new in sorted(edits, reverse=True):  # last first: earlier offsets hold
        i, j = piece_at(s), piece_at(e - 1)
        a, b = s - starts[i], e - starts[j]
        if i == j:
            texts[i] = texts[i][:a] + new + texts[i][b:]
        else:
            texts[i] = texts[i][:a] + new
            for k in range(i + 1, j):
                texts[k] = ""
            texts[j] = texts[j][b:]
    out, pos = [], 0
    for m, t in zip(pieces, texts):
        out.append(xml[pos : m.start()] + m.group(1) + t + m.group(3))
        pos = m.end()
    return "".join(out) + xml[pos:]


def render(numbers: list[int]) -> str:
    """[3], [5] for scattered numbers; [3]-[5] (en dash) for three or more in a row."""
    nums = sorted(set(numbers))
    out, i = [], 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1:
            j += 1
        if j - i >= 2:
            out.append(f"[{nums[i]}]–[{nums[j]}]")
        else:
            out.extend(f"[{n}]" for n in nums[i : j + 1])
        i = j + 1
    return ", ".join(out)


def renumber(document_xml: str) -> tuple[str, dict]:
    """Return the rewritten document.xml and a report of what was done."""
    d = document_xml.replace("<w:lastRenderedPageBreak/>", "")
    d = d.replace("<w:t>", '<w:t xml:space="preserve">')
    d = d.replace('</w:t><w:t xml:space="preserve">', "")  # w:t pieces of one run
    b0 = d.index("<w:body>") + len("<w:body>")
    b1 = d.index("</w:body>")
    inner = d[b0:b1]
    items, pos = [], 0
    for m in TOKEN_RE.finditer(inner):
        if inner[pos : m.start()].strip():
            raise ValueError("unexpected content between body elements")
        items.append(m.group(0))
        pos = m.end()

    heads = [
        i
        for i, x in enumerate(items)
        if 'w:val="Heading5"' in x and text_of(x).strip() == "References"
    ]
    if len(heads) != 1:
        raise ValueError("expected exactly one 'References' heading (style Heading 5)")
    ref_head = heads[0]
    ref_idx = [
        i
        for i, x in enumerate(items)
        if i > ref_head
        and 'w:val="references"' in x
        and LABEL_START_RE.match(text_of(x))
    ]
    labels = {LABEL_START_RE.match(text_of(items[i])).group(1): i for i in ref_idx}

    order, unknown = [], set()
    for x in items[:ref_head]:
        for para in PARA_RE.findall(x):  # a table's cells one by one
            for g in GROUP_RE.findall(text_of(para)):
                toks = [t.strip() for t in g.split(",")]
                if all(t in labels for t in toks):
                    order.extend(t for t in toks if t not in order)
                elif any(t in labels for t in toks) or re.fullmatch(
                    r"(AK|S)\d+", toks[0]
                ):
                    unknown.add(g)
    num = {lab: n for n, lab in enumerate(order, start=1)}

    def number_paragraph(m: re.Match) -> str:
        para = m.group(0)
        edits = []
        for g in GROUP_RE.finditer(text_of(para)):
            toks = [t.strip() for t in g.group(1).split(",")]
            if all(t in num for t in toks):
                edits.append((g.start(), g.end(), render([num[t] for t in toks])))
        return edit_text(para, edits) if edits else para

    for i in range(ref_head):
        items[i] = PARA_RE.sub(number_paragraph, items[i])

    def drop_label(entry: str, lab: str) -> str:
        m = re.match(r"\s*\[" + re.escape(lab) + r"\]\s+", text_of(entry))
        return edit_text(entry, [(m.start(), m.end(), "")])

    entries = {lab: drop_label(items[i], lab) for lab, i in labels.items()}
    first, last = min(ref_idx), max(ref_idx)
    others = [
        x for k, x in enumerate(items[first : last + 1], first) if k not in ref_idx
    ]
    items = items[:first] + [entries[lab] for lab in order] + others + items[last + 1 :]
    report = {
        "order": order,
        "uncited": [lab for lab in labels if lab not in num],
        "unknown": sorted(unknown),
    }
    return d[:b0] + "".join(items) + d[b1:], report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("docx", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.resolve() == args.docx.resolve():
        raise SystemExit("write to a new file; keep the labelled original")
    with zipfile.ZipFile(args.docx) as zin:
        new_xml, report = renumber(zin.read("word/document.xml").decode("utf-8"))
        with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename == "word/document.xml":
                    data = new_xml.encode("utf-8")
                zout.writestr(info, data)
    print("numbered in order of first citation:")
    print(
        "  " + ", ".join(f"{lab} = [{n}]" for n, lab in enumerate(report["order"], 1))
    )
    print(f"uncited entries removed: {', '.join(report['uncited']) or 'none'}")
    print(
        "labels cited but not in the reference list (left as they are): "
        + (", ".join(f"[{u}]" for u in report["unknown"]) or "none")
    )


if __name__ == "__main__":
    main()
