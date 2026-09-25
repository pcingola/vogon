import subprocess
from pathlib import Path

import pytest

from checks import sources as source_checks
from config import load

TRANSCRIPT = """---
title: Requirements workshop
date: 2026-09-17
kind: transcript
authority: informal
participants: [alice@example.com, bob@example.com]
---

Alice: The tracker holds the approval.
"""

SUMMARY = """---
title: Requirements workshop, summary
date: 2026-09-17
kind: summary
authority: informal
derived_from: vogon/sources/2026-09-17_workshop.md
---

The tracker holds the approval.
"""

PROCEDURE = """---
title: Electronic records procedure
date: 2026-04-02
kind: procedure
authority: procedure
original: 2026-04-02_procedure.pdf
---

Section 4. Approval is recorded in the tracker.
"""

REGULATION = """---
title: Electronic records; electronic signatures
date: 1997-03-20
kind: regulation
authority: regulation
retrieved_from: https://example.com/part11
---

Text.
"""

DECK = """---
title: Kick-off
date: 2026-01-10
kind: deck
authority: informal
---

Slides.
"""

HELD = {
    "vogon/sources/2026-09-17_workshop.md": TRANSCRIPT,
    "vogon/sources/2026-09-17_workshop.summary.md": SUMMARY,
    "vogon/sources/2026-04-02_procedure.md": PROCEDURE,
    "vogon/sources/1997-03-20_part11.md": REGULATION,
    "vogon/sources/2026-01-10_kickoff.md": DECK,
}


def put(root: Path, rel: str, text: str | bytes) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8")
    return path


def held_documents(root: Path) -> Path:
    for rel, text in HELD.items():
        put(root, rel, text)
    put(root, "vogon/sources/2026-04-02_procedure.pdf", b"%PDF-1.4 original\n")
    return root


def record(root: Path, rel: str, rid: str, kind: str, sources: list[str]) -> None:
    listed = "".join(f"  - {s}\n" for s in sources)
    put(root, rel, f"---\nid: {rid}\ntype: {kind}\ntitle: T\nstatus: accepted\nsource:\n{listed}---\n")


def check(root: Path, fn):
    return list(fn(load(root)))


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def init_repo(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "alice@example.com")
    git(root, "config", "user.name", "Alice")
    git(root, "config", "commit.gpgsign", "false")


def commit(root: Path, message: str) -> str:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD")[:10]


# REQ-REC-9: naming and frontmatter.


@pytest.mark.req("REQ-REC-9")
def test_held_documents_following_the_rules_produce_no_output(tmp_path):
    held_documents(tmp_path)
    assert check(tmp_path, source_checks.naming) == []


@pytest.mark.req("REQ-REC-9")
@pytest.mark.parametrize("name", [
    "procedure.pdf",
    "procedure.md",
    "2026-4-2_procedure.pdf",
    "2026-04-02-procedure.pdf",
    "2026-04-02_Electronic-Records.pdf",
    "2026-02-30_procedure.pdf",
])
def test_name_without_a_date_and_slug_is_reported(tmp_path, name):
    rel = f"vogon/sources/{name}"
    put(tmp_path, rel, "---\ntitle: P\ndate: 2026-04-02\nkind: procedure\nauthority: procedure\n---\n"
        if name.endswith(".md") else b"%PDF")
    found = check(tmp_path, source_checks.naming)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-9")]
    assert "YYYY-MM-DD" in found[0].message or "calendar date" in found[0].message


@pytest.mark.req("REQ-REC-9")
@pytest.mark.parametrize("old, new, words, line", [
    ("date: 2026-04-02", "date: 2026-04-03", ["2026-04-03", "2026-04-02", "agree"], 3),
    ("kind: procedure", "kind: memo", ["kind", "memo"], 4),
    ("authority: procedure", "authority: official", ["authority", "official"], 5),
    ("title: Electronic records procedure\n", "", ["title", "missing"], None),
    ("original: 2026-04-02_procedure.pdf", "original: 2026-04-02_procedure.docx",
     ["original", "does not resolve"], 6),
    ("original:", "owner: bob\noriginal:", ["owner", "not defined"], 6),
])
def test_frontmatter_breaking_a_rule_is_reported_with_the_rule(tmp_path, old, new, words, line):
    held_documents(tmp_path)
    rel = "vogon/sources/2026-04-02_procedure.md"
    put(tmp_path, rel, PROCEDURE.replace(old, new))
    found = check(tmp_path, source_checks.naming)
    assert [(f.path, f.line, f.requirement) for f in found] == [(rel, line, "REQ-REC-9")]
    assert all(w in found[0].message for w in words)


@pytest.mark.req("REQ-REC-9")
def test_markdown_without_frontmatter_is_reported_and_a_binary_original_is_not(tmp_path):
    put(tmp_path, "vogon/sources/2026-04-02_procedure.pdf", b"%PDF")
    put(tmp_path, "vogon/sources/2026-04-02_procedure.md", "Section 4.\n")
    found = check(tmp_path, source_checks.naming)
    assert [(f.path, f.requirement) for f in found] == [
        ("vogon/sources/2026-04-02_procedure.md", "REQ-REC-9")]
    assert "frontmatter" in found[0].message


@pytest.mark.req("REQ-REC-9")
def test_held_document_in_a_subdirectory_is_reported(tmp_path):
    rel = "vogon/sources/meetings/2026-09-17_workshop.md"
    put(tmp_path, rel, TRANSCRIPT)
    found = check(tmp_path, source_checks.naming)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-9")]
    assert "subdirector" in found[0].message


# REQ-REC-10: a held document is never edited after it was filed.


@pytest.mark.req("REQ-REC-10")
def test_held_document_edited_in_a_later_commit_is_reported_with_both_commits(tmp_path):
    init_repo(tmp_path)
    held_documents(tmp_path)
    added = commit(tmp_path, "file the sources")
    assert check(tmp_path, source_checks.unchanged) == []
    rel = "vogon/sources/2026-09-17_workshop.md"
    put(tmp_path, rel, TRANSCRIPT.replace("holds", "keeps"))
    edited = commit(tmp_path, "correct the transcript")
    found = check(tmp_path, source_checks.unchanged)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-10")]
    assert added in found[0].message and edited in found[0].message


@pytest.mark.req("REQ-REC-10")
def test_uncommitted_edit_of_a_held_document_is_reported(tmp_path):
    init_repo(tmp_path)
    held_documents(tmp_path)
    added = commit(tmp_path, "file the sources")
    put(tmp_path, "vogon/sources/2026-04-02_procedure.pdf", b"%PDF-1.4 edited\n")
    found = check(tmp_path, source_checks.unchanged)
    assert [(f.path, f.requirement) for f in found] == [
        ("vogon/sources/2026-04-02_procedure.pdf", "REQ-REC-10")]
    assert added in found[0].message and "working tree" in found[0].message


@pytest.mark.req("REQ-REC-10")
def test_new_version_filed_as_a_new_file_and_an_edit_reverted_are_not_reported(tmp_path):
    init_repo(tmp_path)
    held_documents(tmp_path)
    commit(tmp_path, "file the sources")
    put(tmp_path, "vogon/sources/2026-09-24_workshop.md",
        TRANSCRIPT.replace("2026-09-17", "2026-09-24").replace("holds", "keeps"))
    commit(tmp_path, "file the corrected transcript")
    rel = "vogon/sources/2026-01-10_kickoff.md"
    put(tmp_path, rel, DECK + "edit\n")
    commit(tmp_path, "edit")
    put(tmp_path, rel, DECK)
    commit(tmp_path, "revert")
    assert check(tmp_path, source_checks.unchanged) == []


# REQ-REC-11: source lists cite documents in the right order.


@pytest.mark.req("REQ-REC-11")
def test_source_list_weaker_before_stronger_is_reported(tmp_path):
    held_documents(tmp_path)
    rel = "vogon/constraints/CON-001.md"
    record(tmp_path, rel, "CON-001", "constraint",
           ["vogon/sources/2026-09-17_workshop.md", "vogon/sources/1997-03-20_part11.md"])
    found = check(tmp_path, source_checks.citations)
    assert [(f.path, f.line, f.requirement) for f in found] == [(rel, 6, "REQ-REC-11")]
    assert "1997-03-20_part11.md" in found[0].message and "strongest first" in found[0].message
    record(tmp_path, rel, "CON-001", "constraint",
           ["vogon/sources/1997-03-20_part11.md", "vogon/sources/2026-09-17_workshop.md"])
    assert check(tmp_path, source_checks.citations) == []


@pytest.mark.req("REQ-REC-11")
def test_fact_sourced_only_to_informal_documents_is_reported(tmp_path):
    held_documents(tmp_path)
    rel = "vogon/facts/FACT-001.md"
    record(tmp_path, rel, "FACT-001", "fact", ["vogon/sources/2026-01-10_kickoff.md"])
    found = check(tmp_path, source_checks.citations)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-11")]
    assert "informal" in found[0].message
    record(tmp_path, rel, "FACT-001", "fact",
           ["vogon/sources/2026-04-02_procedure.md", "vogon/sources/2026-01-10_kickoff.md"])
    assert check(tmp_path, source_checks.citations) == []


@pytest.mark.req("REQ-REC-11")
def test_requirement_sourced_to_informal_documents_only_is_not_reported(tmp_path):
    held_documents(tmp_path)
    record(tmp_path, "vogon/requirements/REQ-1.md", "REQ-1", "requirement",
           ["vogon/sources/2026-01-10_kickoff.md"])
    assert check(tmp_path, source_checks.citations) == []


@pytest.mark.req("REQ-REC-11")
def test_summary_cited_without_its_transcript_above_it_is_reported(tmp_path):
    held_documents(tmp_path)
    rel = "vogon/requirements/REQ-1.md"
    record(tmp_path, rel, "REQ-1", "requirement", ["vogon/sources/2026-09-17_workshop.summary.md"])
    found = check(tmp_path, source_checks.citations)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-11")]
    assert "2026-09-17_workshop.summary.md" in found[0].message
    record(tmp_path, rel, "REQ-1", "requirement",
           ["vogon/sources/2026-09-17_workshop.summary.md", "vogon/sources/2026-09-17_workshop.md"])
    assert len(check(tmp_path, source_checks.citations)) == 1
    record(tmp_path, rel, "REQ-1", "requirement",
           ["vogon/sources/2026-09-17_workshop.md", "vogon/sources/2026-09-17_workshop.summary.md"])
    assert check(tmp_path, source_checks.citations) == []
