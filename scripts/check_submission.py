"""Pre-submission checks on the group's Word file (run on the numbered copy).

    python scripts/check_submission.py final_numbered.docx [--pdf final_numbered.pdf]

Reports, in order: template placeholders and teammates' to-do markers left in the text,
highlighted text, citation labels that were never turned into numbers, comments and
tracked changes still in the file, figure and table references against the captions,
the repository link and commit ID, and (with --pdf) the page on which References starts.
Exit code 1 if anything blocks submission.
"""

import argparse
import re
import subprocess
import sys
import zipfile

PLACEHOLDERS = [
    r"^TEXT\.?$",
    r"^(JAMIE|YASSIEN|ANNA) TEXT$",
    r"^Header$",
    r"^Table Type Styles$",
    r"\[(Anna|Yassien|Jamie)\b[^\]]*\]",
    r"\[commit ID[^\]]*\]",
    r"\{RANGE\}",
    r"\[CITE\]",
    r"\[VERSION\]",
    r"FIGURE X",
    r"\bFig\. X\b",
    r"\[contributions[^\]]*\]",
]


def paragraphs(xml: str) -> list[str]:
    out = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        out.append("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--pdf")
    args = ap.parse_args()
    z = zipfile.ZipFile(args.docx)
    xml = z.read("word/document.xml").decode("utf-8")
    paras = paragraphs(xml)
    body_end = next(
        (i for i, t in enumerate(paras) if t.strip() == "References"), len(paras)
    )
    body = paras[:body_end]
    blocking, notes = [], []

    for i, t in enumerate(paras):
        for pat in PLACEHOLDERS:
            for m in re.finditer(pat, t.strip()):
                blocking.append(
                    f"placeholder in paragraph {i}: {m.group(0)!r} ({t.strip()[:60]!r})"
                )

    hl = re.findall(
        r"<w:r>(?:(?!</w:r>).)*?<w:highlight [^>]*/>(?:(?!</w:r>).)*?<w:t[^>]*>([^<]*)</w:t>",
        xml,
        flags=re.S,
    )
    for h in hl:
        blocking.append(f"highlighted text: {h[:70]!r}")

    for i, t in enumerate(body):
        for g in re.findall(r"\[([^\[\]]+)\]", t):
            if (
                re.fullmatch(
                    r"(AK\d+|S\d+|[A-Za-z][A-Za-z-]+)(\s*,\s*(AK\d+|S\d+|[A-Za-z][A-Za-z-]+))*",
                    g.strip(),
                )
                and not g.strip().isdigit()
            ):
                if any(c.isalpha() for c in g) and not re.fullmatch(r"\d+", g):
                    blocking.append(
                        f"citation label not numbered in paragraph {i}: [{g}]"
                    )

    n_comments = len(re.findall(r"<w:commentReference ", xml))
    if n_comments:
        blocking.append(
            f"{n_comments} comments still in the file: delete them, or export with markup hidden"
        )
    n_ins, n_del = len(re.findall(r"<w:ins ", xml)), len(re.findall(r"<w:del ", xml))
    if n_ins or n_del:
        blocking.append(
            f"tracked changes still in the file ({n_ins} insertions, {n_del} deletions): accept or reject them"
        )

    text = "\n".join(body)
    figs_cited = sorted(set(int(n) for n in re.findall(r"Fig\. (\d+)", text)))
    tables_cited = sorted(set(re.findall(r"Table ([IVX]+)\b", text)))
    n_fig_captions = len(re.findall(r'<w:pStyle w:val="figurecaption"/>', xml))
    n_table_captions = len(re.findall(r'<w:pStyle w:val="tablehead"/>', xml))
    notes.append(
        f"figures cited {figs_cited}, figure captions {n_fig_captions}; tables cited {tables_cited}, table captions {n_table_captions}"
    )
    if figs_cited and max(figs_cited) > n_fig_captions:
        blocking.append("a figure is cited that has no caption")
    if len(tables_cited) > n_table_captions:
        blocking.append("a table is cited that has no caption")

    if "github.com/Jsanson1/BMEN600_Group5" not in "\n".join(paras):
        blocking.append("repository link missing")
    if not re.search(r"commit [0-9a-f]{7,40}\b", "\n".join(paras)):
        blocking.append('commit ID missing ("commit <hash>")')

    if args.pdf:
        out = subprocess.run(
            ["pdftotext", "-layout", args.pdf, "-"], capture_output=True, text=True
        ).stdout
        pages = out.split("\f")
        ref_page = next(
            (k + 1 for k, pg in enumerate(pages) if re.search(r"\bREFERENCES\b", pg)),
            None,
        )
        notes.append(
            f"PDF pages: {len([p for p in pages if p.strip()])}; References heading on page {ref_page}"
        )

    for n in notes:
        print("note:", n)
    for b in blocking:
        print("FIX: ", b)
    print(
        "\nready to submit"
        if not blocking
        else f"\n{len(blocking)} item(s) to fix before submitting"
    )
    sys.exit(1 if blocking else 0)


if __name__ == "__main__":
    main()
