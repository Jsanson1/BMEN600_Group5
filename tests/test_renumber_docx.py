"""The Word-file citation renumbering used to assemble the midterm PDF."""

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "renumber_docx_citations.py"
spec = importlib.util.spec_from_file_location("renumber_docx_citations", SCRIPT)
renumber_docx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renumber_docx)


def p(text: str, style: str = "BodyText") -> str:
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
    )


def document(*paragraphs: str) -> str:
    return (
        '<w:document xmlns:w="w"><w:body>'
        + "".join(paragraphs)
        + "<w:sectPr/></w:body></w:document>"
    )


def texts(xml: str) -> list[str]:
    import re

    body = xml[xml.index("<w:body>") :]
    return [
        "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", x))
        for x in re.findall(r"<w:p>.*?</w:p>", body)
    ]


def test_numbers_follow_first_citation_and_entries_are_reordered():
    xml = document(
        p("Gait [S9] and diagnosis [AK1, S2]. Again [S9], [AK1]."),
        p("Tools [SciPy]. Not a citation: [Anna: to do]."),
        p("References", style="Heading5"),
        p("[AK1] First author.", style="references"),
        p("[S2] Second author.", style="references"),
        p("[S9] Ninth author.", style="references"),
        p("[SciPy] SciPy authors.", style="references"),
        p("[S99] Never cited.", style="references"),
    )
    out, report = renumber_docx.renumber(xml)
    assert report["order"] == ["S9", "AK1", "S2", "SciPy"]
    assert report["uncited"] == ["S99"]
    assert report["unknown"] == []
    t = texts(out)
    assert t[0] == "Gait [1] and diagnosis [2], [3]. Again [1], [2]."
    assert t[1] == "Tools [4]. Not a citation: [Anna: to do]."
    assert t[3:] == [
        "Ninth author.",
        "First author.",
        "Second author.",
        "SciPy authors.",
    ]


def split_p(*pieces: str, style: str = "BodyText") -> str:
    """One paragraph whose text Word has split into runs at spell-check marks."""
    mark = '<w:proofErr w:type="spellStart"/>'
    runs = mark.join(f"<w:r><w:t>{t}</w:t></w:r>" for t in pieces)
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{runs}</w:p>'


def test_labels_split_over_several_runs():
    xml = document(
        split_p(
            "using pandas [", "pandasPaper", ", ", "pandasZenodo", "], and [SciPy]."
        ),
        split_p("Nested cross-validation [", "nestedCV", "]. Then [S1] and [", "S2]."),
        p("References", style="Heading5"),
        p("[pandasPaper] McKinney.", style="references"),
        p("[pandasZenodo] The pandas team.", style="references"),
        p("[SciPy] Virtanen.", style="references"),
        split_p("[", "nestedCV", "] Cawley and Talbot.", style="references"),
        p("[S1] One.", style="references"),
        p("[S2] Two.", style="references"),
    )
    out, report = renumber_docx.renumber(xml)
    assert report["order"] == [
        "pandasPaper",
        "pandasZenodo",
        "SciPy",
        "nestedCV",
        "S1",
        "S2",
    ]
    t = texts(out)
    assert t[0] == "using pandas [1], [2], and [3]."
    assert t[1] == "Nested cross-validation [4]. Then [5] and [6]."
    assert t[3:] == [
        "McKinney.",
        "The pandas team.",
        "Virtanen.",
        "Cawley and Talbot.",
        "One.",
        "Two.",
    ]
    assert out.count("<w:proofErr") == xml.count("<w:proofErr")  # runs kept


def test_ranges_and_unknown_labels():
    assert renumber_docx.render([5, 3, 4]) == "[3]–[5]"
    assert renumber_docx.render([1, 2, 4]) == "[1], [2], [4]"
    xml = document(
        p("Cited [S1] and a slip [AK4]."),
        p("References", style="Heading5"),
        p("[S1] Only entry.", style="references"),
    )
    out, report = renumber_docx.renumber(xml)
    assert report["unknown"] == ["AK4"]
    assert texts(out)[0] == "Cited [1] and a slip [AK4]."
