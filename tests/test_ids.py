import subprocess
from pathlib import Path

import pytest

import ids


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def init_repo(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "alice@example.com")
    git(root, "config", "user.name", "Alice")


def record(root: Path, rel: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nid: {path.stem}\n---\n")
    return path


@pytest.mark.req("REQ-REC-13")
@pytest.mark.parametrize("text, valid", [
    ("REQ-TRK-2", True),
    ("REQ-7", True),
    ("FACT-004", True),
    ("REQ-A1-3", True),
    ("REQ-trk-2", False),
    ("RQ-2", False),
    ("TODO-1", False),
    ("REQ-TRK-", False),
    ("REQ-TRK-2a", False),
])
def test_grammar(text, valid):
    assert ids.is_valid(text) is valid


@pytest.mark.req("REQ-REC-3")
def test_numbers_compare_numerically():
    assert ids.parse("REQ-TRK-2").key == ids.parse("REQ-TRK-02").key
    assert ids.parse("REQ-TRK-2").key != ids.parse("REQ-REC-2").key


@pytest.mark.req("REQ-REC-7")
@pytest.mark.parametrize("prefix, module, used, expected", [
    ("REQ", "TRK", [], "REQ-TRK-1"),
    ("REQ", "TRK", ["REQ-TRK-1", "REQ-TRK-2", "REQ-REC-3"], "REQ-TRK-3"),
    ("REQ", "TRK", ["REQ-TRK-1", "REQ-TRK-3"], "REQ-TRK-2"),
    ("DEC", None, [], "DEC-001"),
    ("DEC", None, ["DEC-001", "DEC-002"], "DEC-003"),
    ("REQ", None, ["REQ-1", "REQ-2"], "REQ-3"),
    ("CON", None, ["CON-0001"], "CON-0002"),
])
def test_next_id_is_the_lowest_unused_number_in_the_namespace(prefix, module, used, expected):
    assert str(ids.next_id(prefix, module, used)) == expected


@pytest.mark.req("REQ-REC-7")
def test_withdrawn_record_still_holds_its_id(tmp_path):
    records = tmp_path / "vogon"
    path = record(tmp_path, "vogon/decisions/DEC-001.md")
    path.write_text("---\nid: DEC-001\nstatus: withdrawn\n---\n")
    assert str(ids.mint(tmp_path, records, "DEC", None)) == "DEC-002"


@pytest.mark.req("REQ-REC-7")
def test_id_of_a_deleted_record_is_never_reused(tmp_path):
    init_repo(tmp_path)
    records = tmp_path / "vogon"
    record(tmp_path, "vogon/requirements/TRK/REQ-TRK-1.md")
    deleted = record(tmp_path, "vogon/requirements/TRK/REQ-TRK-2.md")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "add")
    deleted.unlink()
    git(tmp_path, "commit", "-q", "-am", "delete")
    assert str(ids.mint(tmp_path, records, "REQ", "TRK")) == "REQ-TRK-3"


@pytest.mark.req("REQ-REC-7")
def test_record_path_is_named_for_the_id(tmp_path):
    assert ids.record_path(tmp_path, ids.parse("REQ-TRK-3")) == tmp_path / "requirements/TRK/REQ-TRK-3.md"
    assert ids.record_path(tmp_path, ids.parse("FACT-006")) == tmp_path / "facts/FACT-006.md"


@pytest.mark.req("REQ-TRC-9")
def test_ids_are_found_in_free_text():
    text = "Implement REQ-TRK-2 and DEC-004; see MYTICKET-12, not REQ-TRK-."
    assert ids.find_in_text(text) == ["REQ-TRK-2", "DEC-004"]


# `vogon id`: mint the next unused id and create the file named for it.

from cli import main  # noqa: E402
from records import parse  # noqa: E402


def rec_module(root: Path) -> None:
    (root / "vogon").mkdir(exist_ok=True)
    (root / "vogon/modules.yaml").write_text("REC: Records\nTRK: Tracker\n")
    for n in range(1, 8):
        path = record(root, f"vogon/requirements/REC/REQ-REC-{n}.md")
        if n == 4:
            path.write_text("---\nid: REQ-REC-4\nstatus: withdrawn\n---\n")


@pytest.mark.req("REQ-REC-7")
def test_id_command_creates_the_file_for_the_next_unused_id(tmp_path, capsys):
    rec_module(tmp_path)
    assert main(["id", "REQ", "--module", "REC", "--title", "Mint ids", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out == "REQ-REC-8 vogon/requirements/REC/REQ-REC-8.md\n"
    created = parse(tmp_path / "vogon/requirements/REC/REQ-REC-8.md")
    assert created.meta == {"id": "REQ-REC-8", "type": "requirement", "title": "Mint ids",
                            "modules": ["REC"], "status": "proposed"}


@pytest.mark.req("REQ-REC-7")
def test_id_command_skips_an_id_held_only_in_the_history(tmp_path, capsys):
    init_repo(tmp_path)
    rec_module(tmp_path)
    extra = record(tmp_path, "vogon/requirements/REC/REQ-REC-8.md")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "add")
    extra.unlink()
    assert main(["id", "requirement", "-m", "REC", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out.split()[0] == "REQ-REC-9"
    assert (tmp_path / "vogon/requirements/REC/REQ-REC-9.md").is_file()
    assert not (tmp_path / "vogon/requirements/REC/REQ-REC-8.md").exists()


@pytest.mark.req("REQ-REC-7")
def test_id_command_mints_unmoduled_types(tmp_path, capsys):
    record(tmp_path, "vogon/decisions/DEC-001.md")
    assert main(["id", "DEC", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out == "DEC-002 vogon/decisions/DEC-002.md\n"
    assert parse(tmp_path / "vogon/decisions/DEC-002.md").meta == {
        "id": "DEC-002", "type": "decision", "status": "proposed"}


@pytest.mark.req("REQ-REC-7", "REQ-REC-14")
def test_id_command_refuses_an_undeclared_module_and_creates_nothing(tmp_path, capsys):
    rec_module(tmp_path)
    assert main(["id", "REQ", "--module", "TRCK", "--root", str(tmp_path)]) == 1
    assert "TRCK" in capsys.readouterr().out
    assert not (tmp_path / "vogon/requirements/TRCK").exists()
