"""Assemble the final paper's section drafts into one Word file (task T-037).

    python scripts/assemble_paper.py -o paper_labelled.docx [--template ieee.docx]
        [--section NAME=PATH ...] [--results results] [--figures figures]
    python scripts/renumber_docx_citations.py paper_labelled.docx -o paper_numbered.docx
    python scripts/check_submission.py paper_numbered.docx --pdf paper_numbered.pdf

The sections are drafted in Markdown in report/final/ and reviewed by pull request;
this script puts them into one .docx in the IEEE conference layout, in the paper's
order: title block, Abstract, I Introduction, II Dataset and Methods, III Results,
IV Discussion, V Conclusion, the end statements and the References. It

* takes the paper's text from each draft between fixed headings (SECTIONS below),
  so the drafting notes above and the source tables below a draft stay out;
* keeps every citation as its label, [S12], and writes every entry of the two
  source ledgers (report/midterm/sources.md, report/final/sources.md) under a
  "References" heading as "[S12] ...", which is the form the midterm's
  renumber_docx_citations.py turns into IEEE numbers (and drops uncited entries);
* numbers the figures in order of first mention (the repository's Fig. 2 can
  become the paper's Fig. 1) and places each figure and table after the paragraph
  that first mentions it, across both columns when it is wider than one;
* keeps anything else in square brackets, a drafting note, highlighted, so
  check_submission.py reports it until someone resolves it; a section with no
  draft yet gets a highlighted placeholder.

With --template (the IEEE conference template .docx), the template's page setup
and styles are used and its body is replaced; without it, the same style names
are created with the template's sizes, so the result can be pasted into it, and
the "references" style numbers its entries [1], [2], ... as the template's does.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FINAL = "report/final"


@dataclass(frozen=True)
class Section:
    """Where one part of the paper is in its draft: from `start` up to `stop`."""

    path: str
    start: str
    stop: str | None = None  # None: to the end of the file
    heading: str | None = None  # the paper's heading; None for the end statements


SECTIONS = {
    "title": Section(f"{FINAL}/abstract.md", "## Title", "## Abstract"),
    "abstract": Section(f"{FINAL}/abstract.md", "## Abstract", "## Keywords"),
    "keywords": Section(f"{FINAL}/abstract.md", "## Keywords", "## Numbers and where"),
    "introduction": Section(
        f"{FINAL}/introduction.md", "## I. Introduction", None, "Introduction"
    ),
    "methods": Section(
        f"{FINAL}/methods.md",
        "## A. Datasets",
        "## Settings and where",
        "Dataset and Methods",
    ),
    "results": Section(
        f"{FINAL}/results.md", "## A. Participants", "## Tables and figures", "Results"
    ),
    "discussion": Section(
        f"{FINAL}/discussion.md", "## A. Answer", "## Numbers and where", "Discussion"
    ),
    "conclusion": Section(
        f"{FINAL}/conclusion.md", "## Conclusion", "## Where each", "Conclusion"
    ),
    "statements": Section(f"{FINAL}/statements.md", "## Data and Code Availability"),
}
BODY = ("introduction", "methods", "results", "discussion", "conclusion")
CAPTIONS = Section(f"{FINAL}/results.md", "## Tables and figures", "\n## ")
LEDGERS = ("report/midterm/sources.md", "report/final/sources.md")
# The repository's figure and table files, by their numbers in the drafts.
FIGURE_FILES = {
    2: "figure2_evaluation_design.png",
    4: "figure4_feature_checks.png",
    5: "figure5_generalisation.png",
}
TABLE_FILES = {"I": "cohort_table.md", "II": "crosscohort_table.md"}
FIGURE_CAPTIONS = {  # captions not drafted with the Results
    2: (
        "Evaluation design. The participants of the final analysis and the four "
        "levels at which every model is tested: (A) unseen gaitpdb participants, "
        "(B) unseen gaitpdb sub-studies, (C) both datasets combined, the main "
        "analysis of our plan, and (D) a model fitted on gaitpdb and applied once "
        "to WearGait-PD. Hatched blocks are held out for testing."
    ),
}
FALLBACK_STYLES = {  # when a template lacks a style name, the nearest it has
    "Affiliation": ("Author",),
    "Keywords": ("Abstract",),
    "Body Text": ("Normal",),
}
COLUMN_IN, PAGE_IN = 3.5, 7.0  # IEEE conference column and text widths (inches)

CITE_GROUP = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]")
FIG_REF = re.compile(r"\b(Figs?)\. (\d+)([A-Z]?)\b")
TABLE_REF = re.compile(r"\bTables? (I{1,3}|IV)\b")
NOTE = re.compile(r"\[(?!S\d+(?:\s*,\s*S\d+)*\])[^\[\]]*\s[^\[\]]*\]")
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`)")


def extract(text: str, start: str, stop: str | None) -> str:
    """The text after the line `start` and before `stop` (or the end)."""
    i = text.find(start)
    if i < 0:
        raise ValueError(f"heading {start!r} not found")
    body = text[i + len(start) :]
    if stop is not None:
        j = body.find(stop)
        if j < 0:
            raise ValueError(f"{stop!r} not found after {start!r}")
        body = body[:j]
    return body.strip("\n")


def blocks(markdown: str) -> list[tuple[str, str]]:
    """Paragraphs as (kind, text): kind is 'h2' for '## X. Title' and 'p' otherwise.
    Lines of one paragraph are joined; tables (lines starting with '|') are skipped."""
    out = []
    for block in re.split(r"\n\s*\n", markdown):
        lines = [ln for ln in block.strip().splitlines() if not ln.startswith("|")]
        if not lines:
            continue
        if lines[0].startswith("## "):
            out.append(("h2", re.sub(r"^##\s+(?:[A-Z]\.\s+)?", "", lines[0]).strip()))
            lines = lines[1:]
            if not lines:
                continue
        out.append(("p", " ".join(ln.strip() for ln in lines)))
    return out


def spans(text: str) -> list[tuple[str, str]]:
    """Split a paragraph into (style, text) pieces: 'b' bold, 'i' italic, 'note' a
    drafting note in square brackets, '' plain. Links keep their text only; code
    spans become plain text."""
    text = LINK.sub(r"\1", text)
    out: list[tuple[str, str]] = []
    pos = 0
    for m in NOTE.finditer(text):
        out += _inline(text[pos : m.start()])
        out.append(("note", m.group(0)))
        pos = m.end()
    out += _inline(text[pos:])
    return [(k, t) for k, t in out if t]


def _inline(text: str) -> list[tuple[str, str]]:
    out, pos = [], 0
    for m in INLINE.finditer(text):
        out.append(("", text[pos : m.start()]))
        tok = m.group(0)
        if tok.startswith("**"):
            out.append(("b", tok[2:-2]))
        elif tok.startswith("`"):
            out.append(("", tok[1:-1]))
        else:
            out.append(("i", tok[1:-1]))
        pos = m.end()
    out.append(("", text[pos:]))
    return out


def figure_order(texts: list[str]) -> list[int]:
    """Repository figure numbers in order of first mention ('Figs. 4 and 5' counts 4)."""
    order = []
    for t in texts:
        for m in FIG_REF.finditer(t):
            n = int(m.group(2))
            if n not in order:
                order.append(n)
    return order


def renumber_figures(text: str, mapping: dict[int, int]) -> str:
    """Fig. 4A -> Fig. 2A with mapping {4: 2}; numbers not in the mapping stay."""

    def sub(m: re.Match) -> str:
        n = int(m.group(2))
        return f"{m.group(1)}. {mapping.get(n, n)}{m.group(3)}"

    return FIG_REF.sub(sub, text)


def ledger_entries(paths: list[Path]) -> dict[str, str]:
    """{'S12': 'S. Saeb, ... *GigaScience* ...'} from each ledger's main table: its
    first two columns, up to the ledger's first '## ' heading (after which come
    re-checks of earlier entries, or candidates that must not be cited)."""
    row = re.compile(r"^\|\s*(S\d+)\s*\|\s*(.+?)\s*\|")
    out: dict[str, str] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                break
            m = row.match(line)
            if m:
                if m.group(1) in out:
                    raise ValueError(f"{m.group(1)} is in more than one ledger")
                out[m.group(1)] = m.group(2)
    return out


def cited_labels(texts: list[str]) -> list[str]:
    order = []
    for t in texts:
        for g in CITE_GROUP.finditer(t):
            for lab in re.split(r"\s*,\s*", g.group(1)):
                if lab not in order:
                    order.append(lab)
    return order


def captions(results_md: str) -> dict[str, str]:
    """{'Table I': '...', 'Fig. 4': '...'} from the Results draft's list of captions."""
    out = {}
    for m in re.finditer(
        r"\*\*((?:Table [IV]+|Fig\. \d+))\.\*\*\s*(.+?)(?=\n\s*\n|\Z)", results_md, re.S
    ):
        out[m.group(1)] = " ".join(m.group(2).split())
    return out


def md_table(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and not set(line) <= set("|:- "):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


# ---------------------------------------------------------------- Word output


class Paper:
    """A .docx in the IEEE conference layout, with the template's style names."""

    def __init__(self, template: Path | None):
        self.doc = Document(str(template)) if template else Document()
        if template:
            body = self.doc.element.body
            for child in list(body):
                if child.tag != qn("w:sectPr"):
                    body.remove(child)
        else:
            self._setup()
        self.columns = 1
        # The template numbers its headings itself (I., A.); the fallback styles do not.
        self.numbered_headings = template is not None

    def _setup(self) -> None:
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        sec.top_margin, sec.bottom_margin = Inches(0.75), Inches(1.0)
        sec.left_margin = sec.right_margin = Inches(0.625)
        normal = self.doc.styles["Normal"]
        normal.font.name, normal.font.size = "Times New Roman", Pt(10)
        normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        pf = normal.paragraph_format
        pf.space_before, pf.space_after = Pt(0), Pt(0)
        pf.line_spacing_rule, pf.line_spacing = WD_LINE_SPACING.EXACTLY, Pt(11.5)
        specs = {  # name: size, bold, italic, small caps, alignment, before, after
            "paper title": (24, False, False, False, "center", 0, 6),
            "Author": (11, False, False, False, "center", 0, 0),
            "Affiliation": (10, False, True, False, "center", 0, 6),
            "Abstract": (9, True, False, False, "justify", 0, 4),
            "Keywords": (9, True, False, False, "justify", 0, 6),
            "Body Text": (10, False, False, False, "justify", 0, 0),
            "Heading 1": (10, False, False, True, "center", 8, 3),
            "Heading 2": (10, False, True, False, "left", 4, 2),
            "Heading 5": (8, False, False, True, "center", 8, 3),
            "figure caption": (8, False, False, False, "justify", 2, 6),
            "table head": (8, False, False, True, "center", 6, 2),
            "table copy": (8, False, False, False, "left", 0, 0),
            "references": (8, False, False, False, "justify", 0, 1),
        }
        align = {
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        }
        styles = self.doc.styles
        for name, (size, bold, italic, caps, al, before, after) in specs.items():
            try:
                st = styles[name]
            except KeyError:
                st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
                st.base_style = styles["Normal"]
            st.font.name, st.font.size = "Times New Roman", Pt(size)
            st.font.bold, st.font.italic, st.font.small_caps = bold, italic, caps
            st.font.color.rgb = None
            st.paragraph_format.alignment = align[al]
            st.paragraph_format.space_before = Pt(before)
            st.paragraph_format.space_after = Pt(after)
            st.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
            st.paragraph_format.line_spacing = Pt(size + 1.5)
            st.paragraph_format.keep_with_next = name.startswith("Heading")
            if name == "Body Text":
                st.paragraph_format.first_line_indent = Inches(0.2)
        self._number_references(styles["references"])

    def _number_references(self, style) -> None:
        """Give the fallback "references" style the template's list numbering,
        [1], [2], ..., with a hanging indent: renumber_docx_citations.py removes
        each entry's label and leaves the number to the style."""
        numbering = self.doc.part.numbering_part.element
        used = [
            int(n.get(qn("w:abstractNumId")))
            for n in numbering.findall(qn("w:abstractNum"))
        ]
        used += [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
        num_id = str(max(used, default=0) + 1)
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), num_id)
        level_type = OxmlElement("w:multiLevelType")
        level_type.set(qn("w:val"), "singleLevel")
        lvl = OxmlElement("w:lvl")
        lvl.set(qn("w:ilvl"), "0")
        for tag, value in (
            ("w:start", "1"),
            ("w:numFmt", "decimal"),
            ("w:pStyle", style.style_id),
            ("w:lvlText", "[%1]"),
            ("w:lvlJc", "left"),
        ):
            el = OxmlElement(tag)
            el.set(qn("w:val"), value)
            lvl.append(el)
        ppr = OxmlElement("w:pPr")
        ind = OxmlElement("w:ind")
        ind.set(qn("w:left"), "360")
        ind.set(qn("w:hanging"), "360")
        ppr.append(ind)
        lvl.append(ppr)
        abstract.append(level_type)
        abstract.append(lvl)
        nums = numbering.findall(qn("w:num"))  # every abstractNum precedes every num
        if nums:
            nums[0].addprevious(abstract)
        else:
            numbering.append(abstract)
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), num_id)
        ref = OxmlElement("w:abstractNumId")
        ref.set(qn("w:val"), num_id)
        num.append(ref)
        numbering.append(num)
        num_pr = style.element.get_or_add_pPr().get_or_add_numPr()
        num_pr.get_or_add_numId().val = int(num_id)
        style.paragraph_format.left_indent = Inches(0.25)
        style.paragraph_format.first_line_indent = Inches(-0.25)

    def set_columns(self, n: int) -> None:
        """Start a continuous section with n columns (0.25 in apart)."""
        if n == self.columns:
            return
        sec = self.doc.add_section(WD_SECTION.CONTINUOUS)
        found = sec._sectPr.xpath("./w:cols")
        cols = found[0] if found else OxmlElement("w:cols")
        cols.set(qn("w:num"), str(n))
        cols.set(qn("w:space"), str(int(0.25 * 1440)))
        if not found:
            sec._sectPr.append(cols)
        self.columns = n

    def style(self, name: str) -> str:
        """`name` if the document has that style, else the nearest one it has."""
        names = {s.name for s in self.doc.styles}
        for candidate in (name, *FALLBACK_STYLES.get(name, ()), "Normal"):
            if candidate in names:
                return candidate
        return "Normal"

    def paragraph(self, text: str, style: str = "Body Text", lead: str = ""):
        p = self.doc.add_paragraph(style=self.style(style))
        if lead:
            r = p.add_run(lead)
            r.italic = True
        for kind, piece in spans(text):
            r = p.add_run(piece)
            if kind == "b":
                r.bold = True
            elif kind == "i":
                r.italic = True
            elif kind == "note":
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        return p

    def heading(self, number: str, text: str, level: int) -> None:
        label = text if self.numbered_headings else f"{number}. {text}"
        self.doc.add_paragraph(label, style=self.style(f"Heading {level}"))

    def figure(self, path: Path, number: int, caption: str) -> None:
        w, h = Image.open(path).size
        dpi = Image.open(path).info.get("dpi", (200, 200))[0] or 200
        width = min(w / dpi, PAGE_IN)
        self.set_columns(1 if width > COLUMN_IN + 0.05 else 2)
        p = self.doc.add_paragraph(style=self.style("Body Text"))
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Inches(0)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.add_run().add_picture(str(path), width=Inches(width))
        self.paragraph(caption, "figure caption", lead=f"Fig. {number}. ")
        self.set_columns(2)

    def table(self, label: str, caption: str, rows: list[list[str]]) -> None:
        width_need = [max(len(r[j]) for r in rows) for j in range(len(rows[0]))]
        total = PAGE_IN if sum(width_need) > 60 else COLUMN_IN
        self.set_columns(1 if total > COLUMN_IN else 2)
        self.doc.add_paragraph(f"Table {label}", style=self.style("table head"))
        self.paragraph(caption, "figure caption")
        t = self.doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        t.autofit = False
        weights = [n**0.8 for n in width_need]
        widths = [total * w / sum(weights) for w in weights]
        for gc, w in zip(t._tbl.tblGrid.findall(qn("w:gridCol")), widths):
            gc.set(qn("w:w"), str(int(w * 1440)))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                cell = t.cell(i, j)
                cell.width = Inches(widths[j])
                para = cell.paragraphs[0]
                para.style = self.doc.styles[self.style("table copy")]
                run = para.add_run(re.sub(r"[*`]", "", value))
                run.bold = i == 0
        self.doc.add_paragraph(style=self.style("Body Text"))
        self.set_columns(2)

    def save(self, path: Path) -> None:
        self.doc.save(str(path))


# ---------------------------------------------------------------- assembly


def load_sections(overrides: dict[str, Path]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for name, sec in SECTIONS.items():
        same_file = "abstract" if name in ("title", "keywords") else name
        path = overrides.get(name, overrides.get(same_file, ROOT / sec.path))
        if not path.exists():
            out[name] = None
            continue
        out[name] = extract(path.read_text(encoding="utf-8"), sec.start, sec.stop)
    return out


def assemble(
    texts: dict[str, str | None],
    captions_md: str,
    ledgers: list[Path],
    results_dir: Path,
    figures_dir: Path,
    template: Path | None = None,
) -> tuple[Paper, dict]:
    body_texts = [texts[n] or "" for n in BODY]
    order = figure_order(body_texts)
    mapping = {n: k for k, n in enumerate(order, start=1)}
    caps = captions(captions_md)
    pending_figures = list(order)
    pending_tables = ["I", "II"]
    paper = Paper(template)

    title = texts.get("title") or "[Title to be decided with the abstract, T-036]"
    paper.paragraph(" ".join(title.split()), "paper title")
    paper.paragraph("Anna Klygina, Jamie Sanson, Yassien Tawfik", "Author")
    paper.paragraph(
        "Biomedical Engineering, University of Calgary, Calgary, Canada", "Affiliation"
    )
    paper.set_columns(2)
    abstract = texts["abstract"] or "[Abstract to come, T-036.]"
    paper.paragraph(" ".join(abstract.split()), "Abstract", lead="Abstract—")
    keywords = texts.get("keywords") or "[Keywords to choose, T-036.]"
    paper.paragraph(" ".join(keywords.split()), "Keywords", lead="Keywords—")

    def place_floats(text: str) -> None:
        for m in FIG_REF.finditer(text):
            n = int(m.group(2))
            if n in pending_figures and n in FIGURE_FILES:
                caption = caps.get(f"Fig. {n}") or FIGURE_CAPTIONS.get(n, "")
                caption = renumber_figures(caption, mapping)
                paper.figure(figures_dir / FIGURE_FILES[n], mapping[n], caption)
                pending_figures.remove(n)
        for m in TABLE_REF.finditer(text):
            label = m.group(1)
            if label in pending_tables:
                rows = md_table(results_dir / TABLE_FILES[label])
                paper.table(label, caps.get(f"Table {label}", ""), rows)
                pending_tables.remove(label)

    romans = iter(["I", "II", "III", "IV", "V"])
    for name in BODY:
        sec = SECTIONS[name]
        paper.heading(next(romans), sec.heading, 1)
        text = texts[name]
        if text is None:
            paper.paragraph(f"[{sec.heading} to come.]")
            continue
        letters = iter("ABCDEFGHIJKLMNOP")
        for kind, piece in blocks(text):
            if kind == "h2":
                paper.heading(next(letters), piece, 2)
            else:
                paper.paragraph(renumber_figures(piece, mapping))
                place_floats(piece)

    if texts["statements"]:
        first = SECTIONS["statements"].start[3:]
        paper.doc.add_paragraph(first, style=paper.style("Heading 5"))
        for kind, piece in blocks(texts["statements"]):
            if kind == "h2":
                paper.doc.add_paragraph(piece, style=paper.style("Heading 5"))
            else:
                paper.paragraph(renumber_figures(piece, mapping))

    paper.doc.add_paragraph("References", style=paper.style("Heading 5"))
    entries = ledger_entries(ledgers)
    for label, entry in entries.items():
        paper.paragraph(f"[{label}] {entry}", "references")

    all_texts = [texts[n] or "" for n in ("abstract", *BODY, "statements")]
    cited = cited_labels(all_texts)
    report = {
        "figures": {f"Fig. {n}": f"Fig. {k}" for n, k in mapping.items()},
        "figures_not_placed": pending_figures,
        "tables_not_placed": pending_tables,
        "cited_not_in_ledgers": [c for c in cited if c not in entries],
        "missing_sections": [n for n, t in texts.items() if t is None],
        "notes": sum(len(NOTE.findall(t)) for t in all_texts),
    }
    return paper, report


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--template", type=Path, help="the IEEE conference template")
    ap.add_argument(
        "--section",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help=f"use another file for a section ({', '.join(SECTIONS)}, captions)",
    )
    ap.add_argument("--results", type=Path, default=ROOT / "results")
    ap.add_argument("--figures", type=Path, default=ROOT / "figures")
    ap.add_argument("--ledger", type=Path, action="append", help="source ledgers")
    ap.add_argument("--pdf", action="store_true", help="also convert with LibreOffice")
    args = ap.parse_args()
    overrides = dict(s.split("=", 1) for s in args.section)
    overrides = {k: Path(v) for k, v in overrides.items()}
    texts = load_sections(overrides)
    cap_path = overrides.get("captions", ROOT / CAPTIONS.path)
    captions_md = extract(
        cap_path.read_text(encoding="utf-8"), CAPTIONS.start, CAPTIONS.stop
    )
    ledgers = args.ledger or [ROOT / p for p in LEDGERS]
    paper, report = assemble(
        texts, captions_md, ledgers, args.results, args.figures, args.template
    )
    paper.save(args.output)
    print(f"wrote {args.output}")
    for key, value in report.items():
        print(f"  {key}: {value}")
    if args.pdf:
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir"]
            + [str(args.output.parent), str(args.output)],
            check=True,
            capture_output=True,
        )
        print(f"wrote {args.output.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
