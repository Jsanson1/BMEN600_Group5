"""scripts/assemble_paper.py: section extraction, Markdown pieces, figure numbering,
ledgers, and a small assembled document that the midterm's citation renumbering
accepts."""

import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest
from docx.oxml.ns import qn
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look their module up while loading
    spec.loader.exec_module(module)
    return module


ap = load("assemble_paper")
renumber_docx = load("renumber_docx_citations")


def test_extract_keeps_only_the_text_between_the_headings():
    text = "# Draft\n\nnotes for the group\n\n## A. Data\n\nBody [S1].\n\n## Numbers and where\n\n| x |"
    body = ap.extract(text, "## A. Data", "## Numbers and where")
    assert body == "Body [S1]."
    with pytest.raises(ValueError):
        ap.extract(text, "## B. Missing", None)


def test_sections_that_start_at_a_subsection_keep_its_heading():
    # A section whose start marker is its first subsection heading must keep that
    # heading, or the paper loses it and prints the rest of the line as text.
    text = "# Draft\n\nnotes\n\n## A. Participants and the two datasets\n\nBody.\n\n## B. Next\n\nMore."
    for name in ("methods", "results", "discussion"):
        assert ap.SECTIONS[name].keep_start
    body = ap.extract(text, "## A. Participants", None, keep_start=True)
    assert ap.blocks(body)[:2] == [
        ("h2", "Participants and the two datasets"),
        ("p", "Body."),
    ]


def test_blocks_make_headings_without_their_letters_and_join_lines():
    md = "## A. Datasets\n\nFirst line\nsecond line.\n\n| a | b |\n|---|---|\n\n## B. Models"
    assert ap.blocks(md) == [
        ("h2", "Datasets"),
        ("p", "First line second line."),
        ("h2", "Models"),
    ]


def test_spans_mark_emphasis_and_drafting_notes_but_not_citations():
    pieces = ap.spans(
        "A *journal* and **bold** with `code`, a [link](https://x.org), [S1], [S2, S3]"
        " and [Jamie: confirm.]"
    )
    kinds = {text: kind for kind, text in pieces}
    assert kinds["journal"] == "i" and kinds["bold"] == "b"
    assert kinds["[Jamie: confirm.]"] == "note"
    assert "".join(t for _, t in pieces).count("link") == 1
    assert all(k != "note" for k, t in pieces if "[S" in t)


def test_figures_are_numbered_in_order_of_first_mention():
    texts = ["the design (Fig. 2)", "Fig. 5 and Fig. 4A; again Fig. 2"]
    order = ap.figure_order(texts)
    assert order == [2, 5, 4]
    mapping = {n: k for k, n in enumerate(order, start=1)}
    assert ap.renumber_figures("Fig. 4A and Fig. 5", mapping) == "Fig. 3A and Fig. 2"


def test_ledgers_stop_at_their_first_section_and_must_not_overlap(tmp_path):
    a = tmp_path / "a.md"
    a.write_text(
        "# Sources\n\n| Label | Ref | Check | Supports |\n|---|---|---|---|\n"
        "| S1 | A. Author, *J.*, 2020. | ok | x |\n\n## Further checks\n\n"
        "| S1 | rechecked | ok | x |\n",
        encoding="utf-8",
    )
    b = tmp_path / "b.md"
    b.write_text("| S2 | B. Author, 2021. | ok | y |\n", encoding="utf-8")
    assert ap.ledger_entries([a, b]) == {
        "S1": "A. Author, *J.*, 2020.",
        "S2": "B. Author, 2021.",
    }
    with pytest.raises(ValueError):
        ap.ledger_entries([a, a])


def test_adjacent_citation_groups_merge():
    assert ap.merge_citation_runs(
        "gait [S15], [S26]. Data [S7], [S8, S9]; and [S1]."
    ) == ("gait [S15, S26]. Data [S7, S8, S9]; and [S1].")


def test_cited_labels_in_order_and_captions():
    assert ap.cited_labels(["[S3], then [S1, S3]", "[S2]"]) == ["S3", "S1", "S2"]
    md = "**Table I.** Participants.\n\n**Fig. 4.** The two datasets\ncompared.\n"
    assert ap.captions(md) == {
        "Table I": "Participants.",
        "Fig. 4": "The two datasets compared.",
    }


def test_column_widths_fit_the_longest_word_and_sum_to_the_total():
    rows = [["Dataset", "Participants"], ["WearGait-PD", "87"], ["gaitpdb", "155"]]
    widths = ap.column_widths(rows, 3.5)
    assert abs(sum(widths) - 3.5) < 1e-9
    assert widths[0] >= len("WearGait-PD") * ap.CHAR_IN + ap.CELL_PAD_IN
    assert widths[1] >= len("Participants") * ap.CHAR_IN + ap.CELL_PAD_IN


def test_commit_fills_only_the_placeholder():
    texts = {
        "methods": "repository (submitted version: commit [to fill at submission]).",
        "statements": "is commit [to fill at submission]. [Anna: check.]",
        "conclusion": None,
    }
    filled = ap.fill_commit(texts, "abc1234")
    assert filled["methods"] == "repository (submitted version: commit abc1234)."
    assert filled["statements"] == "is commit abc1234. [Anna: check.]"
    assert filled["conclusion"] is None


def test_assembled_document_is_numbered_by_the_midterm_renumbering(tmp_path):
    fig_dir, res_dir = tmp_path / "figures", tmp_path / "results"
    fig_dir.mkdir()
    res_dir.mkdir()
    for n, name in ap.FIGURE_FILES.items():
        Image.new("RGB", (700 if n == 5 else 1440, 300), "white").save(
            fig_dir / name, dpi=(200, 200)
        )
    for name in ap.TABLE_FILES.values():
        (res_dir / name).write_text(
            "| A | B |\n|---|---|\n| 1 | 2 |\n", encoding="utf-8"
        )
    ledger = tmp_path / "sources.md"
    ledger.write_text(
        "| S1 | First, *J.*, 2020. | ok | x |\n| S2 | Second, 2021. | ok | y |\n"
        "| S3 | Never cited, 2022. | ok | z |\n",
        encoding="utf-8",
    )
    texts = {name: None for name in ap.SECTIONS}
    texts["introduction"] = "Gait [S2] and more [S1]."
    texts["methods"] = (
        "## A. Design\n\nFour levels (Fig. 2); Table I. [Jamie: confirm.]"
    )
    texts["results"] = "Table II and Fig. 5, then Fig. 4A [S1]."
    texts["statements"] = "Data here.\n\n## Author Contributions\n\nAll three."
    captions_md = "**Table I.** One.\n\n**Table II.** Two.\n\n**Fig. 4.** Four.\n\n**Fig. 5.** Five."
    paper, report = ap.assemble(texts, captions_md, [ledger], res_dir, fig_dir)
    assert report["figures"] == {
        "Fig. 2": "Fig. 1",
        "Fig. 5": "Fig. 2",
        "Fig. 4": "Fig. 3",
    }
    assert report["figures_not_placed"] == [] and report["tables_not_placed"] == []
    assert report["missing_sections"] == [
        "title",
        "abstract",
        "keywords",
        "discussion",
        "conclusion",
    ]
    out = tmp_path / "paper.docx"
    paper.save(out)
    # Without a template, the reference entries are numbered by their style, and
    # table cells use a different style, so only the entries get [1], [2], ...
    refs = paper.doc.styles["references"].element
    assert refs.find(qn("w:pPr")).find(qn("w:numPr")) is not None
    cell_styles = {
        p.style.name
        for t in paper.doc.tables
        for row in t.rows
        for c in row.cells
        for p in c.paragraphs
    }
    assert cell_styles == {"table copy"}
    xml = zipfile.ZipFile(out).read("word/document.xml").decode("utf-8")
    numbered, numbering = renumber_docx.renumber(xml)
    assert numbering["order"] == ["S2", "S1"]
    assert numbering["uncited"] == ["S3"]
    text = renumber_docx.text_of(numbered)
    assert "Gait [1] and more [2]." in text
    assert "then Fig. 3A [2]" in text
    assert "Never cited" not in text
