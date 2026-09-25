import subprocess
from pathlib import Path

import pytest

from cli import main


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def repo(root: Path) -> None:
    """A repository whose main branch holds REQ-TRK-2 and DEC-004, with a
    branch `feature` checked out."""
    for rel, rid, kind in [("requirements/TRK/REQ-TRK-2.md", "REQ-TRK-2", "requirement"),
                           ("decisions/DEC-004.md", "DEC-004", "decision")]:
        path = root / "vogon" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nid: {rid}\ntype: {kind}\ntitle: T\nstatus: accepted\n---\n")
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.email", "alice@example.com")
    git(root, "config", "user.name", "Alice")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "Records")
    git(root, "checkout", "-q", "-b", "feature")


def commit(root: Path, message: str) -> str:
    git(root, "commit", "-q", "--allow-empty", "-m", message)
    return git(root, "rev-parse", "HEAD")[:10]


def change(root: Path, capsys, *args: str) -> tuple[int, list[str]]:
    status = main(["change", "--root", str(root), *args])
    return status, capsys.readouterr().out.splitlines()


@pytest.mark.req("REQ-TRC-9")
def test_a_change_naming_no_record_fails(tmp_path, capsys):
    repo(tmp_path)
    commit(tmp_path, "Fix the rounding")
    commit(tmp_path, "Tidy up")
    status, out = change(tmp_path, capsys, "main", "--description", "Fixes rounding.")
    assert status == 1
    assert len(out) == 1
    assert out[0].startswith("ERROR: ") and "names no record id" in out[0]


@pytest.mark.req("REQ-TRC-9")
def test_a_change_with_no_commits_and_no_description_fails(tmp_path, capsys):
    repo(tmp_path)
    status, out = change(tmp_path, capsys, "main")
    assert status == 1 and "names no record id" in out[0]


@pytest.mark.req("REQ-TRC-9")
def test_a_record_id_in_one_commit_clears_the_other_commits(tmp_path, capsys):
    repo(tmp_path)
    commit(tmp_path, "REQ-TRK-2 — report a record edited after its issue was approved")
    commit(tmp_path, "Tidy up")
    assert change(tmp_path, capsys, "main") == (0, [])


@pytest.mark.req("REQ-TRC-9")
def test_a_record_id_in_the_description_clears_the_change(tmp_path, capsys):
    repo(tmp_path)
    commit(tmp_path, "Tidy up")
    description = "REQ-TRK-2 — report a record edited after its issue was approved"
    assert change(tmp_path, capsys, "main", "--description", description) == (0, [])
    path = tmp_path / "body.md"
    path.write_text("Implements DEC-004: one stack.\n")
    assert change(tmp_path, capsys, "main", "--description-file", str(path)) == (0, [])


@pytest.mark.req("REQ-TRC-9")
def test_an_id_that_resolves_to_no_record_fails_naming_where_it_appears(tmp_path, capsys):
    repo(tmp_path)
    first = commit(tmp_path, "REQ-TRK-2 and REQ-TRK-99")
    second = commit(tmp_path, "REQ-TRK-99 again, and FACT-007")
    status, out = change(tmp_path, capsys, "main", "--description", "See REQ-TRK-99 and DEC-004")
    assert status == 1
    assert len(out) == 2
    assert "REQ-TRK-99 resolves to no record" in out[0]
    assert f"commit {first}, commit {second}, the pull request description" in out[0]
    assert "FACT-007 resolves to no record" in out[1] and f"commit {second}" in out[1]


@pytest.mark.req("REQ-TRC-9")
@pytest.mark.parametrize("message, description", [
    ("NO-REQ — fix a typo in the installation guide", ""),
    ("Fix a typo in the installation guide", "NO-REQ: typo fix."),
])
def test_a_change_naming_no_req_and_no_record_passes(tmp_path, capsys, message, description):
    repo(tmp_path)
    commit(tmp_path, message)
    assert change(tmp_path, capsys, "main", "--description", description) == (0, [])


@pytest.mark.req("REQ-TRC-9")
@pytest.mark.parametrize("message", ["NO-REQS for now", "SEE-NO-REQ", "no-req typo fix"])
def test_no_req_counts_only_as_a_word_of_its_own(tmp_path, capsys, message):
    repo(tmp_path)
    commit(tmp_path, message)
    status, out = change(tmp_path, capsys, "main")
    assert status == 1 and "names no record id and no NO-REQ" in out[0]


@pytest.mark.req("REQ-TRC-9")
def test_an_id_named_next_to_no_req_must_still_resolve(tmp_path, capsys):
    repo(tmp_path)
    commit(tmp_path, "NO-REQ — tidy up the code of REQ-TRK-99")
    status, out = change(tmp_path, capsys, "main")
    assert status == 1 and "REQ-TRK-99 resolves to no record" in out[0]


@pytest.mark.req("REQ-TRC-9")
def test_commits_already_on_the_base_are_not_part_of_the_change(tmp_path, capsys):
    repo(tmp_path)
    git(tmp_path, "checkout", "-q", "main")
    commit(tmp_path, "REQ-TRK-2 on main")
    git(tmp_path, "checkout", "-q", "-b", "other")
    commit(tmp_path, "Tidy up")
    status, out = change(tmp_path, capsys, "main")
    assert status == 1 and "names no record id" in out[0]


@pytest.mark.req("REQ-TRC-9")
def test_an_unknown_base_fails(tmp_path, capsys):
    repo(tmp_path)
    commit(tmp_path, "REQ-TRK-2")
    status, out = change(tmp_path, capsys, "origin/nowhere")
    assert status == 1 and "origin/nowhere" in out[0]
