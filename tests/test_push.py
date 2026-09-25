import json
from pathlib import Path

import pytest

import issues
import records
from cli import main

SETUP = """
systems:
  tracker:
    server: issues
    transition_tools: {transition_issue: transition_id}
    transitions: {"31": Approved}
    approved_states: [Approved]
  test_manager:
    server: tests
    transition_tools: {transition_test: transition}
    transitions: {"6": Approved}
    approved_states: [Approved]
"""

RECORD = """---
id: {id}
type: requirement
title: {title}
modules: [TRK]
status: {status}
verification: test
gxp_risk: data integrity
{extra}---

# {id} — {title}

**Requirement.** VOGON MUST do {id}.
"""

TEST = '''import pytest


@pytest.mark.req("REQ-TRK-1")
def test_one():
    assert 1 + 1 == 2


@pytest.mark.req("REQ-TRK-1", "REQ-TRK-2")
@pytest.mark.parametrize("n", [1, 2])
def test_two(n):
    assert n > 0
'''


def project(root: Path) -> None:
    (root / "vogon.yaml").write_text(SETUP, encoding="utf-8")
    snapshot(root, [], [])


def record(root: Path, rid: str, status: str = "accepted", title: str = "Do the thing",
           extra: str = "") -> Path:
    path = root / "vogon" / "requirements" / "TRK" / f"{rid}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(RECORD.format(id=rid, status=status, title=title, extra=extra), encoding="utf-8")
    return path


def snapshot(root: Path, tracker: list, tests: list) -> None:
    (root / ".vogon").mkdir(exist_ok=True)
    (root / ".vogon" / "tracker.json").write_text(json.dumps({"systems": {
        "tracker": {"server": "issues", "issues": tracker},
        "test_manager": {"server": "tests", "issues": tests}}}), encoding="utf-8")


def read_snapshot(root: Path) -> dict:
    return json.loads((root / ".vogon" / "tracker.json").read_text())


def plan(root: Path, capsys) -> tuple[list[dict], list[str], str, int]:
    """Run `vogon push --plan`: the saved writes, the printed lines, the findings and the exit status."""
    status = main(["push", "--plan", "--root", str(root)])
    out = capsys.readouterr().out.splitlines()
    writes = json.loads((root / ".vogon" / "push_plan.json").read_text())["writes"]
    shown = out[:len(writes)] if writes else out[:1]
    return writes, shown, "\n".join(out[len(shown):]), status


def apply(root: Path, writes: list[dict], at: str = "2026-06-01T12:00:00Z") -> list[dict]:
    """A tracker and test manager that apply the writes to the snapshot, as
    Claude Code does through MCP and then reads back. Returns the created keys."""
    data = read_snapshot(root)
    created = []
    for w in writes:
        held = data["systems"][w["role"]]["issues"]
        by_key = {i["key"]: i for i in held}
        if w["action"] == "create":
            key = ("PROJ-" if w["role"] == "tracker" else "TEST-") + str(len(held) + 1)
            held.append({"key": key, "summary": w["summary"], "description": w["description"],
                         "status": "Open", "links": list(w.get("links", []))})
            created.append({"id": w["id"], "role": w["role"], "key": key})
        elif w["action"] == "update":
            for field, change in w["fields"].items():
                assert by_key[w["key"]][field] == change["from"]
                by_key[w["key"]][field] = change["to"]
        elif w["action"] == "link":
            by_key[w["key"]]["links"].append(w["to"])
        elif w["action"] == "import":
            by_key[w["key"]].setdefault("executions", []).append(
                {"build": w["build"], "at": at, "outcome": w["outcome"]})
        elif w["action"] == "track":
            created.append({"id": w["id"], "role": w["role"], "key": w["key"]})
    (root / ".vogon" / "tracker.json").write_text(json.dumps(data))
    return created


def record_keys(root: Path, created: list[dict], capsys) -> int:
    (root / "created.json").write_text(json.dumps(created))
    status = main(["push", "--record", str(root / "created.json"), "--root", str(root)])
    capsys.readouterr()
    return status


def approve(root: Path, role: str, key: str, at: str = "2026-05-10T09:00:00Z") -> None:
    data = read_snapshot(root)
    for i in data["systems"][role]["issues"]:
        if i["key"] == key:
            i["status"] = "Approved"
            i["transitions"] = [{"to": "Approved", "by": "po@example.com", "at": at}]
    (root / ".vogon" / "tracker.json").write_text(json.dumps(data))


# REQ-CLI-8: a role with no configured server is reported, and nothing is planned for it.


@pytest.mark.req("REQ-CLI-8")
def test_a_role_that_is_not_configured_is_a_warning_and_plans_nothing(tmp_path, capsys):
    project(tmp_path)
    (tmp_path / "vogon.yaml").write_text(SETUP.split("  test_manager:")[0], encoding="utf-8")
    record(tmp_path, "REQ-TRK-1")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text(TEST, encoding="utf-8")
    writes, _, findings, status = plan(tmp_path, capsys)
    assert status == 0
    assert [w["role"] for w in writes] == ["tracker"]
    assert "WARNING: vogon.yaml: Planning the test issues skipped: the test_manager role " \
           "is not configured in vogon.yaml" in findings


# REQ-GEN-2: no tracker write for a proposed record.


@pytest.mark.req("REQ-GEN-2", "REQ-TRK-5")
def test_only_accepted_records_get_an_issue(tmp_path, capsys):
    project(tmp_path)
    record(tmp_path, "REQ-TRK-1", status="proposed")
    record(tmp_path, "REQ-TRK-2", status="accepted")
    record(tmp_path, "REQ-TRK-3", status="withdrawn")
    writes, shown, _, status = plan(tmp_path, capsys)
    assert status == 0
    assert [(w["action"], w["id"]) for w in writes] == [("create", "REQ-TRK-2")]


@pytest.mark.req("REQ-GEN-2")
def test_proposed_record_with_an_issue_gets_no_write(tmp_path, capsys):
    project(tmp_path)
    record(tmp_path, "REQ-TRK-1", status="proposed",
           extra="tracked_as:\n  governs: tracker\n  tracker: PROJ-1\n")
    snapshot(tmp_path, [{"key": "PROJ-1", "summary": "REQ-TRK-1 Old title", "description": "old",
                         "status": "Open"}], [])
    writes, shown, _, _ = plan(tmp_path, capsys)
    assert writes == [] and shown == ["no changes"]


# REQ-TRK-3, REQ-TRK-4, REQ-TRK-5: the full cycle.


@pytest.mark.req("REQ-TRK-3", "REQ-TRK-4", "REQ-TRK-5")
def test_plan_apply_record_and_rerun_gives_no_changes(tmp_path, capsys):
    project(tmp_path)
    paths = [record(tmp_path, f"REQ-TRK-{n}") for n in (1, 2, 3)]
    writes, shown, _, _ = plan(tmp_path, capsys)
    # The lines shown are one per write, in the order saved (REQ-TRK-4).
    assert len(shown) == len(writes) == 3
    for w, text in zip(writes, shown):
        assert text.startswith("create tracker issue") and w["summary"] in text
    # Summary starts with the record id; the description ends with the content hash.
    for w, p in zip(writes, paths):
        r = records.parse(p)
        assert w["summary"].split()[0] == r.id
        assert issues.hash_in(w["description"]) == issues.record_hash(r)
    created = apply(tmp_path, writes)
    assert record_keys(tmp_path, created, capsys) == 0
    # Every accepted record names its issue, and each issue is named by one record.
    keys = [records.parse(p).meta["tracked_as"] for p in paths]
    assert keys == [{"governs": "tracker", "tracker": f"PROJ-{n}"} for n in (1, 2, 3)]
    writes, shown, _, _ = plan(tmp_path, capsys)
    assert writes == [] and shown == ["no changes"]


@pytest.mark.req("REQ-TRK-3")
def test_interrupted_run_creates_only_the_remaining_issues(tmp_path, capsys):
    project(tmp_path)
    for n in range(1, 6):
        record(tmp_path, f"REQ-TRK-{n}")
    writes, _, _, _ = plan(tmp_path, capsys)
    # Two creates were applied, and the run stopped before recording the keys.
    apply(tmp_path, writes[:2])
    writes, _, _, _ = plan(tmp_path, capsys)
    assert [(w["action"], w["id"]) for w in writes] == [
        ("track", "REQ-TRK-1"), ("track", "REQ-TRK-2"),
        ("create", "REQ-TRK-3"), ("create", "REQ-TRK-4"), ("create", "REQ-TRK-5")]
    created = apply(tmp_path, writes)
    record_keys(tmp_path, created, capsys)
    tracker = read_snapshot(tmp_path)["systems"]["tracker"]["issues"]
    assert sorted(i["summary"].split()[0] for i in tracker) == [f"REQ-TRK-{n}" for n in range(1, 6)]
    assert plan(tmp_path, capsys)[0] == []


@pytest.mark.req("REQ-TRK-4")
def test_changed_title_is_a_field_change_showing_both_values(tmp_path, capsys):
    project(tmp_path)
    path = record(tmp_path, "REQ-TRK-1", title="Old title")
    created = apply(tmp_path, plan(tmp_path, capsys)[0])
    record_keys(tmp_path, created, capsys)
    path.write_text(path.read_text().replace("Old title", "New title"))
    writes, shown, _, _ = plan(tmp_path, capsys)
    assert [(w["action"], w["key"], sorted(w["fields"])) for w in writes] == [
        ("update", "PROJ-1", ["description", "summary"])]
    assert writes[0]["fields"]["summary"] == {"from": "REQ-TRK-1 Old title",
                                              "to": "REQ-TRK-1 New title"}
    assert shown[0].startswith("update tracker PROJ-1 (REQ-TRK-1): ")
    apply(tmp_path, writes)
    assert plan(tmp_path, capsys)[0] == []


@pytest.mark.req("REQ-TRK-2")
def test_no_write_to_an_approved_issue_whose_record_changed(tmp_path, capsys):
    project(tmp_path)
    path = record(tmp_path, "REQ-TRK-1")
    record_keys(tmp_path, apply(tmp_path, plan(tmp_path, capsys)[0]), capsys)
    approve(tmp_path, "tracker", "PROJ-1")
    assert plan(tmp_path, capsys)[0] == []
    path.write_text(path.read_text().replace("do REQ-TRK-1.", "do REQ-TRK-1 twice."))
    writes, _, findings, status = plan(tmp_path, capsys)
    assert writes == []
    assert status == 1
    assert "REQ-TRK-1 requires re-approval" in findings


@pytest.mark.req("REQ-TRK-5")
def test_record_adds_the_key_to_an_existing_tracked_as(tmp_path, capsys):
    project(tmp_path)
    path = record(tmp_path, "REQ-TRK-1",
                  extra="tracked_as: {governs: tracker, tracker: PROJ-7}\ntags: [a]\n")
    before = issues.record_hash(records.parse(path))
    assert record_keys(tmp_path, [{"id": "REQ-TRK-1", "role": "test_manager", "key": "TEST-4"}],
                       capsys) == 0
    r = records.parse(path)
    assert r.meta["tracked_as"] == {"governs": "tracker", "tracker": "PROJ-7", "test_manager": "TEST-4"}
    assert r.meta["tags"] == ["a"]
    assert issues.record_hash(r) == before


@pytest.mark.req("REQ-TRK-5")
def test_record_refuses_a_key_another_record_names_or_a_second_key(tmp_path, capsys):
    project(tmp_path)
    record(tmp_path, "REQ-TRK-1", extra="tracked_as:\n  governs: tracker\n  tracker: PROJ-1\n")
    two = record(tmp_path, "REQ-TRK-2")
    text = two.read_text()
    assert record_keys(tmp_path, [{"id": "REQ-TRK-2", "role": "tracker", "key": "PROJ-1"}],
                       capsys) == 1
    assert record_keys(tmp_path, [{"id": "REQ-TRK-1", "role": "tracker", "key": "PROJ-2"}],
                       capsys) == 1
    assert two.read_text() == text
    assert records.parse(tmp_path / "vogon/requirements/TRK/REQ-TRK-1.md").meta["tracked_as"] == {
        "governs": "tracker", "tracker": "PROJ-1"}


# REQ-TRC-5: one test issue per marked test, linked to the requirement issues.


def write_tests(root: Path) -> None:
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests" / "test_x.py").write_text(TEST)


@pytest.mark.req("REQ-TRC-5")
def test_marked_test_gets_one_test_issue_linked_to_its_requirement_issues(tmp_path, capsys):
    project(tmp_path)
    record(tmp_path, "REQ-TRK-1")
    record(tmp_path, "REQ-TRK-2")
    write_tests(tmp_path)
    # No requirement issue yet: no test issue.
    writes, _, _, _ = plan(tmp_path, capsys)
    assert {w["role"] for w in writes} == {"tracker"}
    record_keys(tmp_path, apply(tmp_path, writes), capsys)
    writes, _, _, _ = plan(tmp_path, capsys)
    assert [(w["action"], w["summary"], w["links"]) for w in writes] == [
        ("create", "tests/test_x.py::test_one", ["PROJ-1"]),
        ("create", "tests/test_x.py::test_two", ["PROJ-1", "PROJ-2"]),
    ]
    apply(tmp_path, writes)
    assert plan(tmp_path, capsys)[0] == []


@pytest.mark.req("REQ-TRC-5")
def test_missing_link_on_an_existing_test_issue_is_added(tmp_path, capsys):
    project(tmp_path)
    record(tmp_path, "REQ-TRK-1", extra="tracked_as:\n  governs: tracker\n  tracker: PROJ-1\n")
    record(tmp_path, "REQ-TRK-2", extra="tracked_as:\n  governs: tracker\n  tracker: PROJ-2\n")
    write_tests(tmp_path)
    node = {n.node_id: n for n in issues.test_nodes(tmp_path, [tmp_path / "tests"])}
    one, two = node["tests/test_x.py::test_one"], node["tests/test_x.py::test_two"]
    snapshot(tmp_path,
             [{"key": k, "summary": s, "description": d, "status": "Open"}
              for k, s, d in [("PROJ-1", "REQ-TRK-1 x", "x"), ("PROJ-2", "REQ-TRK-2 x", "x")]],
             [{"key": "TEST-1", "summary": one.summary, "description": one.description,
               "status": "Open", "links": ["PROJ-1"]},
              {"key": "TEST-2", "summary": two.summary, "description": two.description,
               "status": "Open", "links": ["PROJ-1"]}])
    writes = [w for w in plan(tmp_path, capsys)[0] if w["role"] == "test_manager"]
    assert [(w["action"], w["key"], w["to"]) for w in writes] == [("link", "TEST-2", "PROJ-2")]


# REQ-TRC-6: results are imported with the build, and never without one.


def results(root: Path, build) -> None:
    (root / ".vogon" / "results.json").write_text(json.dumps({"format": 1, "build": build, "tests": [
        {"nodeid": "tests/test_x.py::test_one", "requirements": ["REQ-TRK-1"], "outcome": "passed"},
        {"nodeid": "tests/test_x.py::test_two[1]", "requirements": ["REQ-TRK-1"], "outcome": "passed"},
        {"nodeid": "tests/test_x.py::test_two[2]", "requirements": ["REQ-TRK-1"], "outcome": "failed"},
    ]}))


def tracked_tests(root: Path, capsys) -> None:
    project(root)
    record(root, "REQ-TRK-1")
    record(root, "REQ-TRK-2")
    write_tests(root)
    record_keys(root, apply(root, plan(root, capsys)[0]), capsys)
    apply(root, plan(root, capsys)[0])


@pytest.mark.req("REQ-TRC-6")
def test_results_are_imported_once_with_the_build(tmp_path, capsys):
    tracked_tests(tmp_path, capsys)
    build = "a1b2c3d4e5f60718293a4b5c6d7e8f9012345678"
    results(tmp_path, build)
    writes, _, _, _ = plan(tmp_path, capsys)
    assert [(w["action"], w["key"], w["build"], w["outcome"]) for w in writes] == [
        ("import", "TEST-1", build, "passed"),
        ("import", "TEST-2", build, "failed"),
    ]
    apply(tmp_path, writes)
    assert plan(tmp_path, capsys)[0] == []


@pytest.mark.req("REQ-TRC-6")
@pytest.mark.parametrize("build", [None, ""])
def test_results_without_a_build_are_never_imported(tmp_path, capsys, build):
    tracked_tests(tmp_path, capsys)
    results(tmp_path, build)
    writes, _, findings, status = plan(tmp_path, capsys)
    assert writes == []
    assert status == 1
    assert "records no build, so no result is imported" in findings
