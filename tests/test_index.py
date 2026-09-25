from pathlib import Path

import pytest

from cli import main


def put(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def records(root: Path) -> None:
    put(root, "vogon/requirements/TRK/REQ-TRK-2.md",
        "---\nid: REQ-TRK-2\ntype: requirement\ntitle: Report an edited record\n"
        "modules: [TRK, REC]\nstatus: accepted\n---\n")
    put(root, "vogon/requirements/TRK/REQ-TRK-10.md",
        "---\nid: REQ-TRK-10\ntype: requirement\ntitle: File the evidence | unchanged\n"
        "modules: [TRK]\nstatus: proposed\n---\n")
    put(root, "vogon/facts/FACT-001.md",
        "---\nid: FACT-001\ntype: fact\ntitle: A signature needs credentials\nmodules: [TRK]\n"
        "status: withdrawn\n---\n")
    put(root, "vogon/decisions/DEC-001.md",
        "---\nid: DEC-001\ntype: decision\ntitle: Records are plain text\nmodules: [REC]\n"
        "status: {superseded_by: DEC-002}\n---\n")


def index(root: Path) -> str:
    assert main(["index", "--root", str(root)]) == 0
    return (root / "vogon/out/index.md").read_text(encoding="utf-8")


def rows(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("| ") and "---" not in line][1:]


@pytest.mark.req("REQ-REC-6")
def test_index_lists_every_record_once_with_its_frontmatter_values(tmp_path, capsys):
    records(tmp_path)
    text = index(tmp_path)
    assert capsys.readouterr().out == "vogon/out/index.md\n"
    assert rows(text) == [
        "| REQ-TRK-2 | Report an edited record | accepted | TRK, REC |",
        "| REQ-TRK-10 | File the evidence \\| unchanged | proposed | TRK |",
        "| FACT-001 | A signature needs credentials | withdrawn | TRK |",
        "| DEC-001 | Records are plain text | superseded_by DEC-002 | REC |",
    ]


@pytest.mark.req("REQ-REC-6")
def test_rerun_without_change_is_byte_identical(tmp_path):
    records(tmp_path)
    first = (index(tmp_path), (tmp_path / "vogon/out/index.md").read_bytes())
    assert (index(tmp_path), (tmp_path / "vogon/out/index.md").read_bytes()) == first


@pytest.mark.req("REQ-REC-6")
def test_adding_a_constraint_adds_its_row_and_changes_nothing_else(tmp_path):
    records(tmp_path)
    before = index(tmp_path).splitlines()
    put(tmp_path, "vogon/constraints/CON-001.md",
        "---\nid: CON-001\ntype: constraint\ntitle: No machine approval\nmodules: [REC, TRK]\n"
        "status: accepted\n---\n")
    after = index(tmp_path).splitlines()
    added = "| CON-001 | No machine approval | accepted | REC, TRK |"
    assert [line for line in after if line != added] == before
    assert after.count(added) == 1


@pytest.mark.req("REQ-REC-6")
def test_index_writes_nothing_into_the_record_files(tmp_path):
    records(tmp_path)
    files = sorted((tmp_path / "vogon").rglob("*.md"))
    before = {p: p.read_bytes() for p in files}
    index(tmp_path)
    assert {p: p.read_bytes() for p in files} == before
