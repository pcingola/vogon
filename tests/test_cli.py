import ast
import io
import json
import re
import subprocess
from pathlib import Path

import pytest

from cli import main
from findings import exit_status, failure, notice, write

SCRIPTS = Path(__file__).resolve().parent.parent / "src" / "vogon" / "scripts"
ENTRY = SCRIPTS / "vogon"


# REQ-CLI-1: the exit status is non-zero if and only if a failure was reported.


@pytest.mark.req("REQ-CLI-1")
@pytest.mark.parametrize("findings, status", [
    ([], 0),
    ([notice("role has no holder", path="vogon.yaml")], 0),
    ([notice("a"), notice("b")], 0),
    ([failure("dangling depends_on", path="vogon/decisions/DEC-001.md", line=7)], 1),
    ([notice("a"), failure("b")], 1),
])
def test_exit_status_is_nonzero_only_for_a_failure(findings, status):
    assert exit_status(findings) == status


# Every role configured and every approval role held, so `check` has nothing to report.
COMPLETE_SETUP = """
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
  repository_host: {server: git}
  document_system: {server: dms}
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
  engineer: [alice@example.com]
  system_owner: [dave@example.com]
  it_quality_manager: [erin@example.com]
"""


def complete_snapshots(root: Path) -> None:
    """What Claude Code saves under .vogon/ for the setup above, with nothing to report."""
    import snapshots
    state = root / ".vogon"
    state.mkdir()
    (state / "tracker.json").write_text(json.dumps({"systems": {
        "tracker": {"server": "issues", "issues": []},
        "test_manager": {"server": "tests", "issues": []}}}))
    servers = {"issues": "tracker", "tests": "test_manager", "git": "repository_host",
               "dms": "document_system"}
    (state / "servers.json").write_text(json.dumps({"servers": {
        server: {"tools": list(snapshots.OPERATIONS[role]),
                 "operations": {op: op for op in snapshots.OPERATIONS[role]}}
        for server, role in servers.items()}}))
    (state / "branch_rules.json").write_text(json.dumps({
        "server": "git", "default_branch": "main", "required_approving_reviews": 1,
        "author_approval_excluded": True}))
    (state / "risk_assessment.md").write_text("| Requirement | Risk | Reasoning |\n| --- | --- | --- |\n")


@pytest.mark.req("REQ-CLI-1")
def test_check_on_a_valid_project_exits_zero_with_no_output(tmp_path, capsys):
    (tmp_path / "vogon.yaml").write_text(COMPLETE_SETUP)
    complete_snapshots(tmp_path)
    assert main(["check", "--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out == ""


@pytest.mark.req("REQ-CLI-1")
def test_check_reporting_a_failure_exits_nonzero(tmp_path, capsys):
    (tmp_path / "vogon.yaml").write_text(
        "approvals:\n  test_cases: {roles: [validation_lead], system: test_manager}\n")
    assert main(["check", "--root", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert re.search(r"^vogon\.yaml: failure: REQ-CLI-5: .*test_cases.*validation_lead", out, re.M)


@pytest.mark.req("REQ-CLI-1")
def test_check_through_the_entry_script_exits_nonzero_on_failure(tmp_path):
    (tmp_path / "vogon.yaml").write_text("unknown_setting: 1\n")
    run = subprocess.run([str(ENTRY), "check", "--root", str(tmp_path)], capture_output=True, text=True)
    assert run.returncode != 0
    assert "unknown_setting" in run.stdout


@pytest.mark.req("REQ-CLI-1")
def test_notice_alone_is_printed_and_exits_zero():
    stream = io.StringIO()
    found = [notice("approval release: role it_quality_manager has no holder", path="vogon.yaml",
                    requirement="REQ-CLI-6")]
    write(found, "text", stream)
    assert stream.getvalue() == (
        "vogon.yaml: notice: REQ-CLI-6: approval release: role it_quality_manager has no holder\n")
    assert exit_status(found) == 0


@pytest.mark.req("REQ-REC-1", "REQ-REC-8")
def test_text_output_names_file_line_severity_and_requirement():
    stream = io.StringIO()
    write([failure("status 'done' is not allowed", path="vogon/facts/FACT-001.md", line=6,
                   requirement="REQ-REC-1"), failure("no location")], "text", stream)
    assert stream.getvalue().splitlines() == [
        "vogon/facts/FACT-001.md:6: failure: REQ-REC-1: status 'done' is not allowed",
        "failure: no location",
    ]


@pytest.mark.req("REQ-CLI-1", "REQ-CLI-3")
def test_json_output_holds_every_field(tmp_path, capsys):
    (tmp_path / "vogon.yaml").write_text("pathz: {}\n")
    assert main(["check", "--root", str(tmp_path), "--format", "json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert [f for f in data["findings"] if f["severity"] == "failure"] == [{
        "severity": "failure",
        "message": "unknown key 'pathz' in vogon.yaml",
        "path": "vogon.yaml",
        "line": None,
        "requirement": "REQ-CLI-3",
    }]


# REQ-GEN-3: no model client library and no network call.

MODEL_OR_NETWORK_MODULES = {
    "anthropic", "openai", "google", "cohere", "mistralai", "ollama", "litellm", "langchain",
    "requests", "httpx", "aiohttp", "urllib", "urllib3", "http", "socket", "ssl", "ftplib",
    "smtplib",
}


@pytest.mark.req("REQ-GEN-3")
def test_entry_script_depends_on_no_model_client_library():
    header = re.search(r"^# /// script\n(.*?)^# ///$", ENTRY.read_text(), re.S | re.M).group(1)
    deps = re.search(r"dependencies = (\[.*?\])", header).group(1)
    names = {re.split(r"[<>=!~ \[]", d, maxsplit=1)[0].lower() for d in json.loads(deps)}
    assert names <= {"pyyaml"}


@pytest.mark.req("REQ-GEN-3")
def test_no_script_imports_a_model_or_network_module():
    offenders = []
    for path in sorted(SCRIPTS.rglob("*.py")):
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module or ""]
            else:
                continue
            offenders += [(path.name, n) for n in names if n.split(".")[0] in MODEL_OR_NETWORK_MODULES]
    assert offenders == []
