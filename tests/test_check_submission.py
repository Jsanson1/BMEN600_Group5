"""The pre-submission check's citation-numbering and placeholder rules."""

import importlib.util
import re
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_submission.py"
spec = importlib.util.spec_from_file_location("check_submission", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def p(text: str, style: str = "BodyText") -> str:
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'
    )


def test_cited_numbers_expand_ranges_in_order():
    assert check.cited_numbers("a [1], b [3]–[5] and [2]") == [1, 3, 4, 5, 2]
    assert check.cited_numbers("no citations (95% CI 0.75 to 0.90)") == []


def test_numbering_in_ieee_order_passes():
    body = ["x [1], [2]", "y [3]–[5] and again [2]"]
    assert check.numbering_problems(body, 5) == []


def test_numbering_problems_are_reported():
    out_of_order = check.numbering_problems(["x [2]", "y [1]"], 2)
    assert len(out_of_order) == 1 and "order of first citation" in out_of_order[0]
    beyond = check.numbering_problems(["x [1], [2], [3]"], 2)
    assert beyond == [
        "cited numbers with no reference entry: [3] (the list has 2 entries)"
    ]
    uncited = check.numbering_problems(["x [1]"], 2)
    assert uncited == ["reference entries never cited: [2]"]


def test_reference_entries_skip_empty_lines():
    xml = (
        p("Body [1].")
        + p("References", style="Heading5")
        + p("First author.", style="references")
        + p("", style="references")
        + p("Second author.", style="references")
    )
    assert check.reference_entries(xml) == ["First author.", "Second author."]


def test_date_placeholders_are_caught():
    text = "WearGait-PD was accessed on [DATE]."
    assert any(re.search(pat, text) for pat in check.PLACEHOLDERS)
    assert check.PLACEHOLDER_WORDS.fullmatch("DATE")
