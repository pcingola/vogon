"""`vogon hook <name>`: real hook JSON piped into the entry script, and into
`hooks.run` where a case needs many inputs."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import hooks
from findings import Finding

SCRIPTS = Path(__file__).resolve().parent.parent / "src" / "vogon" / "scripts"
ENTRY = SCRIPTS / "vogon"
HOOKS_JSON = SCRIPTS.parent / "hooks" / "hooks.json"

CONFIG = """\
systems:
  tracker:
    server: acme-tracker
    approved_states: [Approved]
  test_manager:
    server: acme-tests
    approved_states: [Approved]
  repository_host: {server: github}
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
"""

REQUIREMENT = """\
---
id: REQ-TRK-1
type: requirement
title: Never transition an issue into an approved state
modules: [TRK]
status: proposed
verification: inspection
gxp_risk: data integrity
---

# REQ-TRK-1 — Never transition an issue into an approved state

**Requirement.** VOGON MUST NOT transition an issue into an approved state.
"""

DECISION = """\
---
id: DEC-001
type: decision
title: Keep one record per file
modules: [REC]
status: accepted
---

# DEC-001 — Keep one record per file

**Decision.** Each record is one file named for its id.
"""


def run_hook(name: str, text: str) -> str:
    """`hooks.run` with no CLAUDE_PROJECT_DIR, so the project is found through `cwd`."""
    return hooks.run(name, text, env={})


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "project"
    (root / "vogon" / "requirements" / "TRK").mkdir(parents=True)
    (root / "vogon" / "decisions").mkdir()
    (root / "vogon" / "modules.yaml").write_text("TRK: tracker\nREC: records\n", encoding="utf-8")
    (root / "vogon" / "requirements" / "TRK" / "REQ-TRK-1.md").write_text(REQUIREMENT, encoding="utf-8")
    (root / "vogon" / "decisions" / "DEC-001.md").write_text(DECISION, encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "test_a.py").write_text("def test_a():\n    pass\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("X = 1\n", encoding="utf-8")
    (root / "vogon.yaml").write_text(CONFIG, encoding="utf-8")
    return root.resolve()


def entry(name: str, stdin: str, cwd: Path) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    return subprocess.run([sys.executable, str(ENTRY), "hook", name], input=stdin,
                          capture_output=True, text=True, cwd=cwd, env=env)


def payload(root: Path, event: str, **fields) -> dict:
    return {"session_id": "abc123", "transcript_path": "/dev/null", "cwd": str(root),
            "permission_mode": "default", "hook_event_name": event, **fields}


# hooks.json


def wired() -> dict[str, list[str]]:
    """hook name -> the events of the entries that run it."""
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    out: dict[str, list[str]] = {}
    for event, entries in data["hooks"].items():
        for e in entries:
            for h in e["hooks"]:
                m = re.fullmatch(r'"\$\{CLAUDE_PLUGIN_ROOT\}"/scripts/vogon hook ([a-z-]+)', h["command"])
                assert m, h["command"]
                out.setdefault(m[1], []).append(event)
    return out


@pytest.mark.req("REQ-REC-1", "REQ-CLI-8")
def test_hooks_json_runs_each_hook_on_its_event():
    w = wired()
    assert set(w) == set(hooks.HOOKS)
    assert w["session-start"] == ["SessionStart"]


# Without vogon.yaml and with no project directory from Claude Code, every hook
# is silent.


@pytest.mark.req("REQ-REC-1", "REQ-CLI-8", "REQ-CLI-10")
@pytest.mark.parametrize("name, event, fields", [
    ("session-start", "SessionStart", {"source": "startup"}),
])
def test_every_hook_prints_nothing_in_a_project_without_vogon_yaml(tmp_path, name, event, fields):
    (tmp_path / "vogon" / "decisions").mkdir(parents=True)
    (tmp_path / "vogon" / "decisions" / "DEC-001.md").write_text("no frontmatter\n")
    result = entry(name, json.dumps(payload(tmp_path, event, **fields)), tmp_path)
    assert result.returncode == 0
    assert result.stdout == ""


# session-start


@pytest.mark.req("REQ-CLI-10")
def test_the_project_directory_from_claude_code_is_the_only_place_looked_at(tmp_path, project):
    # A project with no vogon.yaml, whose hook input names a cwd inside a set-up project.
    bare = tmp_path / "bare"
    bare.mkdir()
    text = json.dumps(payload(project, "SessionStart", source="startup"))
    out = hooks.run("session-start", text, env={"CLAUDE_PROJECT_DIR": str(bare)})
    assert f"{bare / 'vogon.yaml'} does not exist" in out


@pytest.mark.req("REQ-CLI-10")
def test_session_start_without_vogon_yaml_asks_for_setup(tmp_path):
    text = json.dumps(payload(tmp_path, "SessionStart", source="startup"))
    out = hooks.run("session-start", text, env={"CLAUDE_PROJECT_DIR": str(tmp_path)})
    assert f"{tmp_path / 'vogon.yaml'} does not exist" in out
    assert "`vogon` skill" in out and "`references/config.md`" in out and "`vogon init`" in out


@pytest.mark.req("REQ-CLI-8")
def test_session_start_prints_the_server_for_each_role_the_approvals_and_the_holders(project):
    result = entry("session-start", json.dumps(payload(project, "SessionStart", source="startup")),
                   project)
    assert result.returncode == 0
    out = result.stdout
    assert not out.lstrip().startswith("{")  # plain text is added to the context
    assert "- tracker: acme-tracker" in out
    assert "- test_manager: acme-tests" in out
    assert "- repository_host: github" in out
    assert "- document_system: not configured" in out
    assert "- requirements: by product_owner, in the tracker" in out
    assert "- release: by system_owner, it_quality_manager, in the document_system" in out
    assert "- product_owner: alice@example.com" in out
    assert "- system_owner: no holder" in out


@pytest.mark.req("REQ-CLI-6", "REQ-CLI-8")
def test_session_start_lists_each_configuration_error_then_asks_to_complete_setup(project):
    out = run_hook("session-start", json.dumps(payload(project, "SessionStart", source="startup")))
    lines = out.splitlines()
    errors = lines[lines.index("Errors:") + 1:-1]
    assert errors == [
        "- ERROR: vogon.yaml: no holder for the role engineer, which gives the change approval",
        "- ERROR: vogon.yaml: no holder for the role system_owner, which gives the "
        "risk_assessment and release approvals",
        "- ERROR: vogon.yaml: no holder for the role it_quality_manager, which gives the "
        "risk_assessment and release approvals",
        "- ERROR: vogon.yaml: no server for the document_system; the test_specification, "
        "risk_assessment and release approvals cannot be given",
    ]
    assert lines[-1] == hooks.SETUP_INCOMPLETE
    assert "Warnings:" not in lines


@pytest.mark.req("REQ-CLI-8")
@pytest.mark.parametrize("severities, sections", [
    ((), []),
    (("warning",), ["Warnings:"]),
    (("error",), ["Errors:", "setup"]),
    (("warning", "error"), ["Errors:", "Warnings:", "setup"]),
])
def test_session_start_prints_a_section_only_for_a_severity_it_has(severities, sections):
    found = [Finding(s, f"a {s}", path="vogon.yaml") for s in severities]
    lines = hooks.finding_sections(found)
    shown = [line for line in lines if line in ("Errors:", "Warnings:")]
    if hooks.SETUP_INCOMPLETE in lines:
        shown.append("setup")
    assert shown == sections
    assert [line for line in lines if line.startswith("- ")] == (
        [f"- {s.upper()}: vogon.yaml: a {s}" for s in ("error", "warning") if s in severities])


@pytest.mark.req("REQ-CLI-8")
def test_session_start_reads_the_project_from_a_subdirectory(project):
    out = run_hook("session-start",
                    json.dumps(payload(project / "src", "SessionStart", source="resume")))
    assert "- tracker: acme-tracker" in out

