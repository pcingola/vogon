from pathlib import Path

import pytest

import writing
from config import load

HEAD = """---
id: REQ-REC-90
type: requirement
title: Report a duplicated record id
modules: [REC]
status: proposed
verification: test
gxp_risk: none
---
"""
BODY_LINE = 10  # the first line after HEAD

CLEAN = HEAD + """
# REQ-REC-90 — Report a duplicated record id

**Requirement.** VOGON MUST report any id carried by more than one record file.

**What this does not require.** Deciding which file is correct.

**Example.** Two files declare `id: REQ-REC-90`, and both are reported.

**Acceptance.** For any set of record files, a repeated id is reported with
every file that carries it.
"""

REQ_PATH = "vogon/requirements/REC/REQ-REC-90.md"


def put(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def run(root: Path, text: str, rel: str = REQ_PATH):
    put(root, rel, text)
    return list(writing.check(load(root)))


def lines(found):
    return sorted(f.line for f in found)


@pytest.mark.req("REQ-REC-8")
def test_record_free_of_violations_produces_no_findings(tmp_path):
    assert run(tmp_path, CLEAN) == []


@pytest.mark.req("REQ-REC-8")
@pytest.mark.parametrize("phrase", [
    "critically", "Importantly", "worth noting", "the key insight", "load-bearing",
    "gate", "North Star", "leverage", "best-in-class", "low-hanging fruit", "land-and-expand",
])
def test_banned_phrase_in_body_is_reported_with_file_and_line(tmp_path, phrase):
    found = run(tmp_path, HEAD + f"\nFirst line.\n\nThis is {phrase} here.\n")
    assert len(found) == 1
    assert found[0].is_error
    assert found[0].requirement == "REQ-REC-8"
    assert found[0].path == REQ_PATH
    assert found[0].line == BODY_LINE + 3
    assert phrase.lower() in found[0].message.lower()


@pytest.mark.req("REQ-REC-8")
def test_banned_phrase_in_title_is_reported_on_the_title_line(tmp_path):
    found = run(tmp_path, HEAD.replace("Report a duplicated", "Leverage a duplicated") + "\nBody.\n")
    assert lines(found) == [4]
    assert "leverage" in found[0].message.lower()


@pytest.mark.req("REQ-REC-8")
def test_banned_phrase_broken_across_lines_is_reported_on_its_first_line(tmp_path):
    found = run(tmp_path, HEAD + "\nIt is worth\nnoting that ids repeat.\n")
    assert lines(found) == [BODY_LINE + 1]


@pytest.mark.req("REQ-REC-8")
@pytest.mark.parametrize("text", [
    "The gateway forwards requests.",           # part of a longer word
    "Two gates close at night.",                 # a different word
    "The hook is registered as `gate`.",        # code span
    "```\nleverage = 3\n```",                    # code block
    "~~~yaml\nnorth star: true\n~~~",            # tilde code block
])
def test_banned_phrase_outside_whole_words_or_inside_code_is_not_reported(tmp_path, text):
    assert run(tmp_path, HEAD + "\n" + text + "\n") == []


@pytest.mark.req("REQ-REC-8")
@pytest.mark.parametrize("line", [
    "source: [N/A]", "source: n/a", "references: NA", "tags: TBD", "tags: [TODO]",
    "tags: none considered", "tags: '-'", "tags: null", "tags:", "tags: ''", "tags: []",
    "tags: none", "tracked_as: {tracker: TBD}",
])
def test_placeholder_where_a_field_should_be_absent_is_reported(tmp_path, line):
    text = HEAD.replace("status: proposed\n", f"status: proposed\n{line}\n") + "\nBody.\n"
    found = run(tmp_path, text)
    assert len(found) == 1
    assert found[0].line == 7
    assert line.split(":")[0] in found[0].message


@pytest.mark.req("REQ-REC-8")
def test_none_is_allowed_in_gxp_risk(tmp_path):
    assert "gxp_risk: none" in CLEAN
    assert run(tmp_path, CLEAN) == []


@pytest.mark.req("REQ-REC-8")
@pytest.mark.parametrize("text", [
    "## Why does the id repeat?",
    "**Is the id unique?** Yes, by construction.",
])
def test_heading_or_bold_label_phrased_as_a_question_is_reported(tmp_path, text):
    found = run(tmp_path, HEAD + "\nFirst line.\n\n" + text + "\n")
    assert lines(found) == [BODY_LINE + 3]
    assert "question" in found[0].message


@pytest.mark.req("REQ-REC-8")
@pytest.mark.parametrize("text", [
    "## Open questions", "## Open issues", "## TODO", "**TBD.** Undecided.",
    "### Next steps",
])
def test_heading_or_bold_label_naming_open_items_is_reported(tmp_path, text):
    found = run(tmp_path, HEAD + "\nFirst line.\n\n" + text + "\n")
    assert lines(found) == [BODY_LINE + 3]
    assert "open item" in found[0].message


@pytest.mark.req("REQ-REC-8")
def test_heading_inside_a_code_block_is_not_a_heading(tmp_path):
    assert run(tmp_path, HEAD + "\n```sh\n# what runs next?\n```\n") == []


@pytest.mark.req("REQ-REC-8")
@pytest.mark.parametrize("text", [
    "VOGON ships seven skills.", "All 35 tests pass.", "It runs the four checks.",
    "The repository holds twenty-one requirements.", "Two modules cite it.",
])
def test_count_of_repository_contents_is_reported(tmp_path, text):
    found = run(tmp_path, HEAD + "\n" + text + "\n")
    assert lines(found) == [BODY_LINE + 1]
    assert "count" in found[0].message


@pytest.mark.req("REQ-REC-8")
def test_count_in_the_example_block_is_not_reported(tmp_path):
    text = HEAD + """
**Requirement.** VOGON MUST report a repeated id.

**Example.** A project with 40 requirements and
three records sharing one id reports the three records.

**Acceptance.** VOGON reports seven checks.
"""
    found = run(tmp_path, text)
    assert lines(found) == [BODY_LINE + 6]
    assert "seven checks" in found[0].message


@pytest.mark.req("REQ-REC-8")
@pytest.mark.parametrize("kind, rel, limit", [
    ("requirement", REQ_PATH, 300),
    ("fact", "vogon/facts/FACT-090.md", 200),
    ("constraint", "vogon/constraints/CON-090.md", 200),
    ("decision", "vogon/decisions/DEC-090.md", 600),
])
def test_body_over_the_limit_for_its_type_is_reported(tmp_path, kind, rel, limit):
    record_id = Path(rel).stem
    head = HEAD.replace("REQ-REC-90", record_id).replace("type: requirement", f"type: {kind}")
    at_limit = head + "\n" + " ".join(["word"] * limit) + "\n"
    assert run(tmp_path, at_limit, rel) == []
    found = run(tmp_path, at_limit + "word\n", rel)
    assert len(found) == 1
    assert found[0].line == BODY_LINE
    assert str(limit + 1) in found[0].message and str(limit) in found[0].message


@pytest.mark.req("REQ-GEN-5")
@pytest.mark.parametrize("text", [
    "Because good enough is not compliant.",
    "COMPLIANCE · TRACEABILITY · RISK MANAGEMENT · A BRIGHTER TOMORROW",
    "Same problems. More process.",
    "It depends.",
    "Per SOP.",
    "The request was REJECTED.",
])
def test_brand_fixed_string_in_a_record_is_reported(tmp_path, text):
    found = run(tmp_path, HEAD + "\nFirst line.\n" + text + "\n")
    assert len(found) == 1
    assert found[0].requirement == "REQ-GEN-5"
    assert found[0].is_error
    assert (found[0].path, found[0].line) == (REQ_PATH, BODY_LINE + 2)


@pytest.mark.req("REQ-GEN-5")
def test_brand_fixed_string_in_any_file_under_the_records_directory_is_reported(tmp_path):
    put(tmp_path, "vogon/out/index.md", "# Index\n\nPer SOP.\n")
    found = list(writing.check(load(tmp_path)))
    assert [(f.path, f.line, f.requirement) for f in found] == [("vogon/out/index.md", 3, "REQ-GEN-5")]


@pytest.mark.req("REQ-GEN-5")
def test_ordinary_words_of_the_brand_strings_are_not_reported(tmp_path):
    text = HEAD + "\nIt depends on the configuration. Compliance and traceability are\n" \
                  "per SOP-12. The transition is rejected.\n"
    assert run(tmp_path, text) == []


@pytest.mark.req("REQ-GEN-5")
def test_held_document_is_not_checked_for_brand_strings(tmp_path):
    put(tmp_path, "vogon/sources/2026-09-01_kickoff.md", "Because good enough is not compliant.\n")
    assert list(writing.check(load(tmp_path))) == []
