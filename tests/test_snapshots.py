import json
import os
import subprocess
from pathlib import Path

import pytest

import config
import issues
import records
import snapshots
from checks import snapshots as checks

SETUP = """
systems:
  tracker:
    server: issues
    transition_tools: {transition_issue: transition_id}
    transitions: {"21": In Review, "31": Approved}
    approved_states: [Approved]
  test_manager:
    server: tests
    transition_tools: {transition_test: transition}
    transitions: {"6": Approved}
    approved_states: [Approved]
  repository_host: {server: git}
  document_system: {server: dms}
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
  engineer: [alice@example.com, bob@example.com, carol@example.com]
  system_owner: [dave@example.com]
  it_quality_manager: [erin@example.com]
"""

REQ = """---
id: {id}
type: requirement
title: Report the thing
modules: [TRK]
status: accepted
verification: test
gxp_risk: {risk}
{tracked}---

# {id} — Report the thing

**Requirement.** VOGON MUST report the thing.

**Acceptance.** The thing is reported.
"""


def project(root: Path) -> None:
    (root / "vogon.yaml").write_text(SETUP, encoding="utf-8")


def cfg(root: Path):
    return config.load(root)


def write_record(root: Path, rid: str, key: str | None = "PROJ-1", risk: str = "data integrity",
                 extra: str = "") -> Path:
    tracked = f"tracked_as:\n  governs: tracker\n  tracker: {key}\n{extra}" if key else ""
    path = root / "vogon" / "requirements" / "TRK" / f"{rid}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(REQ.format(id=rid, risk=risk, tracked=tracked), encoding="utf-8")
    return path


def issue(key: str, summary: str, description: str, status: str = "Approved",
          by: str | None = "alice@example.com", at: str = "2026-05-10T09:00:00Z", **more) -> dict:
    d = {"key": key, "summary": summary, "description": description, "status": status, **more}
    if status == "Approved":
        d["transitions"] = [{"to": "In Review", "by": "carol@example.com", "at": "2026-05-01T09:00:00Z"},
                            {"to": "Approved", "by": by, "at": at}]
    return d


def approved_issue(path: Path, key: str = "PROJ-1", **kw) -> dict:
    """The issue as `vogon push` wrote it for the record, then approved."""
    r = records.parse(path)
    return issue(key, issues.record_summary(r), issues.record_description(r), **kw)


def snapshot(root: Path, tracker=(), tests=(), missing=()) -> None:
    data = {"read_at": "2026-06-10T00:00:00Z", "systems": {
        "tracker": {"server": "issues", "issues": list(tracker), "missing": list(missing)},
        "test_manager": {"server": "tests", "issues": list(tests)},
    }}
    state = root / ".vogon"
    state.mkdir(exist_ok=True)
    (state / "tracker.json").write_text(json.dumps(data), encoding="utf-8")


def run(check, root: Path):
    return list(check(cfg(root)))


def errors(found):
    return [f for f in found if f.is_error]


def git(root: Path, *args: str, date: str | None = None, email: str = "alice@example.com") -> None:
    env = {**os.environ, "GIT_AUTHOR_EMAIL": email, "GIT_AUTHOR_NAME": email,
           "GIT_COMMITTER_EMAIL": email, "GIT_COMMITTER_NAME": email}
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=env)


def repo(root: Path) -> None:
    git(root, "init", "-q", "-b", "main")


def commit(root: Path, message: str, date: str, email: str = "alice@example.com") -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "--allow-empty", "-m", message, date=date, email=email)


# REQ-CLI-2: a missing snapshot skips the checks that read it, as a warning.


@pytest.mark.req("REQ-CLI-2")
def test_missing_snapshots_are_warnings_and_no_error(tmp_path):
    project(tmp_path)
    write_record(tmp_path, "REQ-TRK-1")
    found = [f for c in checks.CHECKS for f in c(cfg(tmp_path))]
    assert errors(found) == []
    paths = sorted(f.path for f in found)
    assert paths == [".vogon/branch_rules.json", ".vogon/risk_assessment.md",
                     ".vogon/servers.json", ".vogon/tracker.json"]
    assert all(f.requirement == "REQ-CLI-2" for f in found)


@pytest.mark.req("REQ-CLI-2")
def test_no_snapshot_warning_for_a_project_with_no_systems(tmp_path):
    write_record(tmp_path, "REQ-TRK-1")
    assert [f for c in checks.CHECKS for f in c(cfg(tmp_path))] == []


@pytest.mark.req("REQ-CLI-8")
def test_snapshot_read_from_another_server_is_an_error(tmp_path):
    project(tmp_path)
    (tmp_path / "vogon.yaml").write_text(SETUP.replace("server: issues", "server: other"))
    snapshot(tmp_path)
    found = run(checks.tracker_snapshot, tmp_path)
    assert len(found) == 1 and found[0].is_error
    assert "'issues'" in found[0].message and "'other'" in found[0].message


# REQ-TRK-2: a record edited after its issue was approved.


@pytest.mark.req("REQ-TRK-2")
def test_record_unchanged_since_approval_is_not_reported(tmp_path):
    project(tmp_path)
    path = write_record(tmp_path, "REQ-TRK-1")
    snapshot(tmp_path, [approved_issue(path)])
    assert run(checks.edited_after_approval, tmp_path) == []


@pytest.mark.req("REQ-TRK-2")
def test_record_edited_after_approval_requires_re_approval(tmp_path):
    project(tmp_path)
    path = write_record(tmp_path, "REQ-TRK-1")
    snapshot(tmp_path, [approved_issue(path)])
    path.write_text(path.read_text().replace("The thing is reported.",
                                             "The thing is reported. A second clause."))
    found = run(checks.edited_after_approval, tmp_path)
    assert [(f.severity, f.requirement, f.path) for f in found] == [
        ("error", "REQ-TRK-2", "vogon/requirements/TRK/REQ-TRK-1.md")]
    assert "REQ-TRK-1 requires re-approval" in found[0].message
    assert "PROJ-1" in found[0].message


@pytest.mark.req("REQ-TRK-2")
def test_approval_covers_the_description_at_the_time_of_approval(tmp_path):
    # The description was brought in line with the record after approval;
    # what was approved is the older description.
    project(tmp_path)
    path = write_record(tmp_path, "REQ-TRK-1")
    current = approved_issue(path)
    current["transitions"][-1]["description"] = "Older text.\n\nvogon-hash: sha256:" + "0" * 64
    snapshot(tmp_path, [current])
    found = run(checks.edited_after_approval, tmp_path)
    assert [f.requirement for f in found] == ["REQ-TRK-2"]


@pytest.mark.req("REQ-TRK-2")
def test_issue_not_in_an_approved_state_is_not_reported(tmp_path):
    project(tmp_path)
    write_record(tmp_path, "REQ-TRK-1")
    snapshot(tmp_path, [issue("PROJ-1", "REQ-TRK-1 Old", "Old.\n\nvogon-hash: sha256:00",
                              status="In Review")])
    assert run(checks.edited_after_approval, tmp_path) == []


@pytest.mark.req("REQ-TRK-2")
def test_recording_the_key_does_not_change_the_content_hash(tmp_path):
    a = records.parse(write_record(tmp_path, "REQ-TRK-1", key=None))
    b = records.parse(write_record(tmp_path, "REQ-TRK-1", key="PROJ-1"))
    assert issues.record_hash(a) == issues.record_hash(b)


@pytest.mark.req("REQ-TRK-2")
def test_test_changed_after_its_test_issue_was_approved(tmp_path):
    project(tmp_path)
    test = tmp_path / "tests" / "test_a.py"
    test.parent.mkdir()
    test.write_text('import pytest\n\n\n@pytest.mark.req("REQ-TRK-1")\ndef test_a():\n    assert 1 == 1\n')
    node = issues.test_nodes(tmp_path, [tmp_path / "tests"])[0]
    assert node.node_id == "tests/test_a.py::test_a"
    snapshot(tmp_path, tests=[issue("TEST-1", node.summary, node.description, by="bob@example.com")])
    assert run(checks.edited_after_approval, tmp_path) == []
    test.write_text(test.read_text().replace("1 == 1", "2 == 2"))
    found = run(checks.edited_after_approval, tmp_path)
    assert [(f.requirement, f.path) for f in found] == [("REQ-TRK-2", "tests/test_a.py")]
    assert "TEST-1" in found[0].message


# REQ-TRK-6: a tracked_as key that does not resolve.


@pytest.mark.req("REQ-TRK-6")
def test_key_under_every_role_resolves_or_is_reported_with_the_reason(tmp_path):
    project(tmp_path)
    write_record(tmp_path, "REQ-TRK-1", key="PROJ-1")
    write_record(tmp_path, "REQ-TRK-2", key="PROJ-9")
    write_record(tmp_path, "REQ-TRK-3", key="PROJ-3", extra="  test_manager: TEST-7\n")
    write_record(tmp_path, "REQ-TRK-4", key="PROJ-4")
    snapshot(tmp_path,
             [issue("PROJ-1", "REQ-TRK-1 a", "x", status="Open"),
              issue("PROJ-3", "REQ-TRK-3 a", "x", status="Open")],
             missing=[{"key": "PROJ-9", "reason": "deleted"}])
    found = run(checks.unresolved_keys, tmp_path)
    got = sorted((f.path.rsplit("/", 1)[-1], f.message) for f in found)
    assert all(f.is_error and f.requirement == "REQ-TRK-6" for f in found)
    assert got == [
        ("REQ-TRK-2.md", "REQ-TRK-2: tracked_as.tracker PROJ-9 does not resolve: deleted"),
        ("REQ-TRK-3.md", "REQ-TRK-3: tracked_as.test_manager TEST-7 does not resolve: "
                         "not found in .vogon/tracker.json"),
        ("REQ-TRK-4.md", "REQ-TRK-4: tracked_as.tracker PROJ-4 does not resolve: "
                         "not found in .vogon/tracker.json"),
    ]


# REQ-TRK-8: an approval applied by the record's author.


@pytest.mark.req("REQ-TRK-8")
@pytest.mark.parametrize("approver, reported", [
    ("alice@example.com", True),
    ("ALICE@example.com", True),
    ("bob@example.com", False),
])
def test_approval_by_an_author_of_the_record_is_reported(tmp_path, approver, reported):
    project(tmp_path)
    repo(tmp_path)
    path = write_record(tmp_path, "REQ-TRK-1")
    commit(tmp_path, "Add REQ-TRK-1", "2026-05-01T10:00:00Z", email="alice@example.com")
    snapshot(tmp_path, [approved_issue(path, by=approver)])
    found = run(checks.approved_by_author, tmp_path)
    if reported:
        assert [f.requirement for f in found] == ["REQ-TRK-8"]
        assert "alice@example.com" in found[0].message and "PROJ-1" in found[0].message
    else:
        assert found == []


@pytest.mark.req("REQ-TRK-8")
def test_every_author_of_the_record_counts(tmp_path):
    project(tmp_path)
    repo(tmp_path)
    path = write_record(tmp_path, "REQ-TRK-1")
    commit(tmp_path, "Add REQ-TRK-1", "2026-05-01T10:00:00Z", email="alice@example.com")
    path.write_text(path.read_text() + "\nMore.\n")
    commit(tmp_path, "Edit REQ-TRK-1", "2026-05-02T10:00:00Z", email="bob@example.com")
    snapshot(tmp_path, [approved_issue(path, by="bob@example.com")])
    found = run(checks.approved_by_author, tmp_path)
    assert [f.requirement for f in found] == ["REQ-TRK-8"]
    assert "bob@example.com" in found[0].message


@pytest.mark.req("REQ-TRK-8")
def test_authorship_not_determinable_is_not_reported(tmp_path):
    project(tmp_path)
    path = write_record(tmp_path, "REQ-TRK-1")  # no git repository
    snapshot(tmp_path, [approved_issue(path)])
    assert run(checks.approved_by_author, tmp_path) == []


# REQ-TRK-9: an approval by a person who does not hold the configured role.


@pytest.mark.req("REQ-TRK-9")
def test_approver_outside_the_configured_role_is_reported(tmp_path):
    project(tmp_path)
    snapshot(tmp_path,
             [issue("PROJ-1", "REQ-TRK-1 a", "x", by="alice@example.com"),
              issue("PROJ-2", "REQ-TRK-2 b", "x", by="carol@example.com"),
              issue("PROJ-3", "REQ-TRK-3 c", "x", status="In Review")],
             tests=[issue("TEST-1", "tests/test_a.py::test_a", "x", by="bob@example.com"),
                    issue("TEST-2", "tests/test_a.py::test_b", "x", by="alice@example.com")])
    found = run(checks.approver_holds_role, tmp_path)
    assert all(f.is_error and f.requirement == "REQ-TRK-9" for f in found)
    assert len(found) == 2
    assert "PROJ-2" in found[0].message and "carol@example.com" in found[0].message
    assert "product_owner" in found[0].message
    assert "TEST-2" in found[1].message and "alice@example.com" in found[1].message
    assert "test_lead" in found[1].message


# REQ-CLI-4: the operations each configured server must provide.


def servers(root: Path, tracker_ops: dict) -> None:
    def full(role):
        return {op: op for op in snapshots.OPERATIONS[role]}
    data = {"servers": {
        "issues": {"tools": sorted(set(tracker_ops.values()) - {"absent"}), "operations": tracker_ops},
        "tests": {"tools": sorted(full("test_manager")), "operations": full("test_manager")},
        "git": {"tools": sorted(full("repository_host")), "operations": full("repository_host")},
        "dms": {"tools": sorted(full("document_system")), "operations": full("document_system")},
    }}
    (root / ".vogon").mkdir(exist_ok=True)
    (root / ".vogon" / "servers.json").write_text(json.dumps(data))


@pytest.mark.req("REQ-CLI-4")
def test_every_operation_present_passes(tmp_path):
    project(tmp_path)
    servers(tmp_path, {op: op for op in snapshots.OPERATIONS["tracker"]})
    assert run(checks.server_operations, tmp_path) == []


@pytest.mark.req("REQ-CLI-4")
def test_each_missing_operation_is_reported_with_role_and_server(tmp_path):
    project(tmp_path)
    ops = {op: op for op in snapshots.OPERATIONS["tracker"]}
    del ops["link_issues"]            # no tool found for it
    ops["update_issue"] = "absent"    # mapped to a tool the server does not list
    servers(tmp_path, ops)
    found = run(checks.server_operations, tmp_path)
    assert [f.message for f in found] == [
        "the tracker server 'issues' does not provide the operation 'update_issue'",
        "the tracker server 'issues' does not provide the operation 'link_issues'",
    ]
    assert all(f.is_error and f.requirement == "REQ-CLI-4" for f in found)


@pytest.mark.req("REQ-CLI-4")
def test_configured_server_absent_from_the_tool_list_lacks_every_operation(tmp_path):
    project(tmp_path)
    (tmp_path / "vogon.yaml").write_text(SETUP.replace("server: dms", "server: other-dms"))
    servers(tmp_path, {op: op for op in snapshots.OPERATIONS["tracker"]})
    found = run(checks.server_operations, tmp_path)
    assert [f.message for f in found] == [
        f"the document_system server 'other-dms' does not provide the operation {op!r}"
        for op in snapshots.OPERATIONS["document_system"]]


# REQ-CLI-7: the default branch requires an independent review.


def branch_rules(root: Path, reviews: int, excluded: bool) -> None:
    (root / ".vogon").mkdir(exist_ok=True)
    (root / ".vogon" / "branch_rules.json").write_text(json.dumps({
        "server": "git", "repository": "acme/app", "default_branch": "main",
        "required_approving_reviews": reviews, "author_approval_excluded": excluded}))


@pytest.mark.req("REQ-CLI-7")
@pytest.mark.parametrize("reviews, excluded, missing", [
    (1, True, []),
    (2, True, []),
    (0, True, ["at least one approving review is required"]),
    (1, False, ["the author's own approval is excluded"]),
    (0, False, ["at least one approving review is required", "the author's own approval is excluded"]),
])
def test_branch_passes_only_with_an_independent_review(tmp_path, reviews, excluded, missing):
    project(tmp_path)
    branch_rules(tmp_path, reviews, excluded)
    found = run(checks.branch_rules, tmp_path)
    assert all(f.is_error and f.requirement == "REQ-CLI-7" for f in found)
    assert [f.message for f in found] == [
        f"branch 'main' allows a merge without an independent review: missing rule: {m}"
        for m in missing]


# REQ-GEN-9: the risk assessment matches the records.


def risk(root: Path, rows: list[tuple[str, str]]) -> None:
    (root / ".vogon").mkdir(exist_ok=True)
    table = "\n".join(f"| {r} | {l} | Reason. |" for r, l in rows)
    (root / ".vogon" / "risk_assessment.md").write_text(
        f"# Risk assessment\n\n| Requirement | Risk | Reasoning |\n| --- | --- | --- |\n{table}\n")


@pytest.mark.req("REQ-GEN-9")
def test_risk_level_absent_or_different_is_reported_with_both_levels(tmp_path):
    project(tmp_path)
    write_record(tmp_path, "REQ-TRK-1", risk="product quality")
    write_record(tmp_path, "REQ-TRK-2", risk="safety")
    write_record(tmp_path, "REQ-TRK-3", risk="data integrity")
    write_record(tmp_path, "REQ-TRK-4", risk="none")
    risk(tmp_path, [("REQ-TRK-1", "product quality"), ("REQ-TRK-2", "product quality")])
    found = run(checks.risk_assessment, tmp_path)
    assert all(f.is_error and f.requirement == "REQ-GEN-9" for f in found)
    assert [f.message for f in found] == [
        "REQ-TRK-2 carries risk 'safety'; the approved risk assessment gives 'product quality'",
        "REQ-TRK-3 carries risk 'data integrity', which the approved risk assessment does not list",
    ]


@pytest.mark.req("REQ-GEN-9")
def test_a_risk_assessment_that_is_not_utf8_is_an_error(tmp_path):
    project(tmp_path)
    (tmp_path / ".vogon").mkdir(exist_ok=True)
    (tmp_path / ".vogon" / "risk_assessment.md").write_bytes(b"| Requirement | Risk |\n\xff\n")
    found = run(checks.risk_assessment, tmp_path)
    assert [(f.path, f.requirement, f.is_error) for f in found] == [
        (".vogon/risk_assessment.md", "REQ-GEN-9", True)]


@pytest.mark.req("REQ-GEN-9")
def test_risk_assessment_row_with_an_unknown_level_is_reported(tmp_path):
    project(tmp_path)
    risk(tmp_path, [("REQ-TRK-1", "high")])
    found = run(checks.risk_assessment, tmp_path)
    assert [f.requirement for f in found] == ["REQ-GEN-9"]
    assert "'high'" in found[0].message


# REQ-TRK-11: an approval given after what it governs was used.


def tracked_repo(root: Path, commit_date: str) -> Path:
    project(root)
    repo(root)
    branch_rules(root, 1, True)
    path = write_record(root, "REQ-TRK-1")
    commit(root, "Add the record", "2026-05-01T09:00:00Z")
    (root / "src.py").write_text("x = 1\n")
    commit(root, "Implement REQ-TRK-1", commit_date)
    return path


@pytest.mark.req("REQ-TRK-11")
@pytest.mark.parametrize("approved_at, reported", [
    ("2026-05-10T09:00:00Z", True),
    ("2026-05-08T15:00:00Z", False),
])
def test_requirement_issue_approved_after_the_first_commit_naming_it(tmp_path, approved_at, reported):
    path = tracked_repo(tmp_path, "2026-05-08T16:00:00Z")
    snapshot(tmp_path, [approved_issue(path, by="bob@example.com", at=approved_at)])
    found = run(checks.approved_after_use, tmp_path)
    if reported:
        assert [f.requirement for f in found] == ["REQ-TRK-11"]
        assert "PROJ-1" in found[0].message
        assert "2026-05-10T09:00:00Z" in found[0].message
        assert "2026-05-08T16:00:00Z" in found[0].message
    else:
        assert found == []


@pytest.mark.req("REQ-TRK-11")
def test_commit_on_another_branch_does_not_count(tmp_path):
    path = tracked_repo(tmp_path, "2026-05-11T16:00:00Z")
    git(tmp_path, "checkout", "-q", "-b", "feature")
    commit(tmp_path, "Start REQ-TRK-1 early", "2026-05-08T16:00:00Z")
    snapshot(tmp_path, [approved_issue(path, by="bob@example.com", at="2026-05-10T09:00:00Z")])
    assert run(checks.approved_after_use, tmp_path) == []


@pytest.mark.req("REQ-TRK-11")
@pytest.mark.parametrize("executions, status, reported", [
    ([{"build": "b1", "at": "2026-06-01T12:00:00Z", "outcome": "passed"},
      {"build": "b2", "at": "2026-06-03T12:00:00Z", "outcome": "passed"}], "Approved", True),
    ([], "Approved", False),
    ([{"build": "b1", "at": "2026-06-01T12:00:00Z", "outcome": "passed"}], "In Review", False),
])
def test_test_issue_approved_after_its_earliest_result(tmp_path, executions, status, reported):
    tracked_repo(tmp_path, "2026-05-08T16:00:00Z")
    snapshot(tmp_path, tests=[issue("TEST-1", "tests/test_a.py::test_a", "x", status=status,
                                    by="bob@example.com", at="2026-06-02T10:00:00Z",
                                    executions=executions)])
    found = run(checks.approved_after_use, tmp_path)
    if reported:
        assert [f.requirement for f in found] == ["REQ-TRK-11"]
        assert "TEST-1" in found[0].message
        assert "2026-06-02T10:00:00Z" in found[0].message
        assert "2026-06-01T12:00:00Z" in found[0].message
    else:
        assert found == []


@pytest.mark.req("REQ-TRK-11")
def test_requirement_issue_with_no_approval_is_not_reported(tmp_path):
    tracked_repo(tmp_path, "2026-05-08T16:00:00Z")
    snapshot(tmp_path, [issue("PROJ-1", "REQ-TRK-1 a", "x", status="In Review")])
    assert run(checks.approved_after_use, tmp_path) == []
