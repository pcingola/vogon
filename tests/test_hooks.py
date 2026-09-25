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
    transition_tools: {transition_issue: transition_id}
    transitions: {"11": In Review, "21": Approved, "31": Rejected}
    approved_states: [Approved]
  test_manager:
    server: acme-tests
    transition_tools: {transition_test: transition}
    transitions: {"5": Ready for Review, "6": Approved}
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


def pre(root: Path, tool: str, tool_input: dict, agent_type: str | None = None) -> str:
    fields = {"tool_name": tool, "tool_input": tool_input, "tool_use_id": "toolu_01"}
    if agent_type is not None:
        fields.update(agent_id="agent-1", agent_type=agent_type)
    return json.dumps(payload(root, "PreToolUse", **fields))


def decision(out: str) -> str | None:
    """`deny` when the hook refused the call, None when it said nothing."""
    if not out.strip():
        return None
    data = json.loads(out)["hookSpecificOutput"]
    assert data["hookEventName"] == "PreToolUse"
    return data["permissionDecision"]


def reason(out: str) -> str:
    return json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]


# hooks.json


def matches(matcher: str, value: str) -> bool:
    """A matcher as Claude Code evaluates it: an exact list of names, or an
    unanchored regular expression when it holds any other character."""
    if matcher in ("", "*"):
        return True
    if re.fullmatch(r"[A-Za-z0-9_\-, |]+", matcher):
        return value in [m.strip() for m in re.split(r"[|,]", matcher)]
    return re.search(matcher, value) is not None


def wired() -> dict[str, list[str]]:
    """hook name -> the matchers of the entries that run it, per event."""
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    out: dict[str, list[tuple[str, str]]] = {}
    for event, entries in data["hooks"].items():
        for e in entries:
            for h in e["hooks"]:
                m = re.fullmatch(r'"\$\{CLAUDE_PLUGIN_ROOT\}"/scripts/vogon hook ([a-z-]+)', h["command"])
                assert m, h["command"]
                out.setdefault(m[1], []).append((event, e.get("matcher", "")))
    return out


@pytest.mark.req("REQ-TRK-1", "REQ-GEN-11", "REQ-REC-1", "REQ-CLI-8")
def test_hooks_json_runs_each_hook_on_its_event_and_tools():
    w = wired()
    assert set(w) == set(hooks.HOOKS)
    assert [e for e, _ in w["session-start"]] == ["SessionStart"]

    def fires(name, event, tool):
        return any(e == event and matches(m, tool) for e, m in w[name])

    for tool in ("mcp__acme-tracker__transition_issue", "mcp__plugin_acme_tests__get_test"):
        assert fires("transition", "PreToolUse", tool)
    assert not fires("transition", "PreToolUse", "Bash")
    for tool in ("Read", "Grep", "Glob", "Write", "Edit", "NotebookEdit", "Bash",
                 "mcp__filesystem__read_file"):
        assert fires("test-read", "PreToolUse", tool)
    for tool in ("TodoWrite", "Agent", "SubagentHandback"):
        assert not fires("test-read", "PreToolUse", tool)


# Without vogon.yaml and with no project directory from Claude Code, every hook
# is silent.


@pytest.mark.req("REQ-TRK-1", "REQ-GEN-11", "REQ-REC-1", "REQ-CLI-8", "REQ-CLI-10")
@pytest.mark.parametrize("name, event, fields", [
    ("session-start", "SessionStart", {"source": "startup"}),
    ("transition", "PreToolUse", {"tool_name": "mcp__acme-tracker__transition_issue",
                                  "tool_input": {"transition_id": "21"}}),
    ("test-read", "PreToolUse", {"tool_name": "Read", "agent_type": "vogon:vogon-test-writer",
                                 "tool_input": {"file_path": "src/a.py"}}),
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


@pytest.mark.req("REQ-CLI-10")
def test_setup_request_comes_only_from_session_start(tmp_path):
    env = {"CLAUDE_PROJECT_DIR": str(tmp_path)}
    text = json.dumps(payload(tmp_path, "PreToolUse", tool_name="mcp__acme-tracker__transition_issue",
                              tool_input={"transition_id": "21"}))
    assert hooks.run("transition", text, env=env) == ""


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


# transition


def call(root: Path, tool: str, tool_input: dict | None = None) -> str:
    return run_hook("transition", pre(root, tool, tool_input or {}))


@pytest.mark.req("REQ-TRK-1")
@pytest.mark.parametrize("tool, tool_input", [
    ("mcp__acme-tracker__transition_issue", {"issue": "ACME-1", "transition_id": "21"}),
    ("mcp__acme-tracker__transition_issue", {"issue": "ACME-1", "transition_id": 21}),
    ("mcp__acme-tracker__transition_issue", {"issue": "ACME-1", "transition_id": {"id": "21"}}),
    ("mcp__acme-tests__transition_test", {"key": "T-1", "transition": "6"}),
])
def test_transition_into_an_approved_state_is_refused(project, tool, tool_input):
    out = call(project, tool, tool_input)
    assert decision(out) == "deny"
    assert "Approved" in reason(out)


@pytest.mark.req("REQ-TRK-1")
@pytest.mark.parametrize("tool_input", [
    {"issue": "ACME-1", "transition_id": "99"},
    {"issue": "ACME-1"},
    {"issue": "ACME-1", "transition_id": None},
    {"issue": "ACME-1", "transition_id": ["21"]},
])
def test_transition_with_an_unknown_or_missing_id_is_refused(project, tool_input):
    assert decision(call(project, "mcp__acme-tracker__transition_issue", tool_input)) == "deny"


@pytest.mark.req("REQ-TRK-1")
@pytest.mark.parametrize("tool, tool_input", [
    ("mcp__acme-tracker__transition_issue", {"issue": "ACME-1", "transition_id": "11"}),
    ("mcp__acme-tracker__transition_issue", {"issue": "ACME-1", "transition_id": "31"}),
    ("mcp__acme-tracker__get_issue", {"issue": "ACME-1"}),
    ("mcp__acme-tracker__create_issue", {"summary": "REQ-TRK-1 x"}),
    ("mcp__github__merge_pull_request", {"number": 1}),
    # servers not in systems pass, whatever the call
    ("mcp__other__transition_issue", {"transition_id": "21"}),
    ("mcp__acme-tracker-2__transition_issue", {"transition_id": "21"}),
])
def test_other_calls_pass(project, tool, tool_input):
    assert decision(call(project, tool, tool_input)) is None


@pytest.mark.req("REQ-TRK-1")
@pytest.mark.parametrize("missing", ["transition_tools", "transitions", "approved_states"])
@pytest.mark.parametrize("tool", ["mcp__acme-tracker__get_issue",
                                  "mcp__acme-tracker__transition_issue"])
def test_every_call_to_a_server_with_incomplete_transition_setup_is_refused(project, missing, tool):
    lines = CONFIG.splitlines()
    # the first occurrence is the tracker's
    lines.remove(next(line for line in lines if line.strip().startswith(f"{missing}:")))
    (project / "vogon.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    out = call(project, tool, {"issue": "ACME-1", "transition_id": "11"})
    assert decision(out) == "deny"
    assert missing in reason(out)
    # the test manager's setup is complete, so its calls still pass
    assert decision(call(project, "mcp__acme-tests__get_test", {"key": "T-1"})) is None


@pytest.mark.req("REQ-TRK-1")
def test_a_configured_server_with_no_transition_keys_is_blocked_entirely(project):
    (project / "vogon.yaml").write_text("systems:\n  tracker: {server: acme-tracker}\n",
                                        encoding="utf-8")
    assert decision(call(project, "mcp__acme-tracker__search_issues", {"jql": "x"})) == "deny"
    assert decision(call(project, "mcp__other__search", {})) is None


@pytest.mark.req("REQ-TRK-1")
@pytest.mark.parametrize("server, tool", [
    # a plugin-bundled server, configured by its own key
    ("acme-tests", "mcp__plugin_acme-plugin_acme-tests__transition_test"),
    # the same server, configured by its scoped name
    ("plugin:acme-plugin:acme-tests", "mcp__plugin_acme-plugin_acme-tests__transition_test"),
    # a name with characters Claude Code replaces by `_`
    ("claude.ai Acme Tests", "mcp__claude_ai_Acme_Tests__transition_test"),
])
def test_server_names_match_the_way_claude_code_names_tools(project, server, tool):
    text = CONFIG.replace("server: acme-tests", f"server: {server}")
    (project / "vogon.yaml").write_text(text, encoding="utf-8")
    assert decision(call(project, tool, {"transition": "6"})) == "deny"
    assert decision(call(project, tool, {"transition": "5"})) is None


@pytest.mark.req("REQ-TRK-1")
def test_transition_tool_named_in_full_is_recognised(project):
    text = CONFIG.replace("{transition_issue: transition_id}",
                          "{mcp__acme-tracker__transition_issue: transition_id}")
    (project / "vogon.yaml").write_text(text, encoding="utf-8")
    assert decision(call(project, "mcp__acme-tracker__transition_issue",
                         {"transition_id": "21"})) == "deny"


@pytest.mark.req("REQ-TRK-1")
@pytest.mark.parametrize("text", [
    "systems: [not, a, mapping]\n",
    "systems:\n  tracker: {server: acme-tracker\n",
    "systems:\n  trackr: {server: acme-tracker}\n",
])
def test_unreadable_systems_refuse_every_mcp_call(project, text):
    (project / "vogon.yaml").write_text(text, encoding="utf-8")
    assert decision(call(project, "mcp__anything__read", {})) == "deny"


@pytest.mark.req("REQ-TRK-1")
@pytest.mark.parametrize("text", [
    "approvals:\n  release: {roles: [system_owner], system: nowhere}\n",
    "approvals:\n  audit: {roles: [auditor]}\n",
    "roles: [a, b]\n",
])
def test_an_error_outside_systems_does_not_refuse_unrelated_mcp_calls(project, text):
    (project / "vogon.yaml").write_text(CONFIG + text, encoding="utf-8")
    assert decision(call(project, "mcp__other__read_file", {"path": "x"})) is None
    assert decision(call(project, "mcp__acme-tracker__transition_issue",
                         {"transition_id": "21"})) == "deny"


@pytest.mark.req("REQ-TRK-1")
def test_a_transition_id_object_with_more_fields_is_judged_by_its_id(project):
    tool = "mcp__acme-tracker__transition_issue"
    assert decision(call(project, tool, {"transition_id": {"id": "21", "name": "Approve"}})) == "deny"
    assert decision(call(project, tool, {"transition_id": {"id": "11", "name": "Review"}})) is None


@pytest.mark.req("REQ-TRK-1")
def test_the_project_is_found_from_claude_project_dir(project, tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    text = pre(elsewhere, "mcp__acme-tracker__transition_issue", {"transition_id": "21"})
    assert decision(hooks.run("transition", text, env={})) is None
    assert decision(hooks.run("transition", text, env={"CLAUDE_PROJECT_DIR": str(project)})) == "deny"


@pytest.mark.req("REQ-TRK-1")
def test_transition_hook_through_the_entry_script_fails_closed(project):
    result = entry("transition", pre(project, "mcp__acme-tracker__transition_issue",
                                     {"transition_id": "21"}), project)
    assert result.returncode == 0
    assert decision(result.stdout) == "deny"
    for stdin in ("", "not json", "[1, 2]"):
        result = entry("transition", stdin, project)
        assert result.returncode == 0
        assert decision(result.stdout) == "deny"


# test-read


def read(root: Path, agent: str | None, tool: str, tool_input: dict, cwd: Path | None = None) -> str:
    text = pre(cwd or root, tool, tool_input, agent_type=agent)
    return run_hook("test-read", text)


TEST_AGENTS = ["vogon-test-writer", "vogon-test-checker",
               "vogon:vogon-test-writer", "vogon:vogon-test-checker"]


@pytest.mark.req("REQ-GEN-11")
@pytest.mark.parametrize("agent", TEST_AGENTS)
def test_test_agent_reading_the_source_is_refused(project, agent):
    out = read(project, agent, "Read", {"file_path": str(project / "src" / "a.py")})
    assert decision(out) == "deny"
    assert "vogon/" in reason(out) and "tests/" in reason(out)


@pytest.mark.req("REQ-GEN-11")
@pytest.mark.parametrize("agent", TEST_AGENTS)
@pytest.mark.parametrize("tool, tool_input", [
    ("Read", {"file_path": "vogon/requirements/TRK/REQ-TRK-1.md"}),
    ("Read", {"file_path": "tests/test_a.py", "offset": 1, "limit": 10}),
    ("Grep", {"pattern": "MUST", "path": "vogon"}),
    ("Grep", {"pattern": "def test", "path": "tests", "glob": "*.py"}),
    ("Glob", {"pattern": "**/*.md", "path": "vogon"}),
    ("Glob", {"pattern": "unit/*.py", "path": "tests"}),
    ("Write", {"file_path": "tests/test_b.py", "content": "def test_b():\n    pass\n"}),
    ("Edit", {"file_path": "tests/test_a.py", "old_string": "pass", "new_string": "assert 1"}),
])
def test_test_agent_reading_the_records_and_tests_is_allowed(project, agent, tool, tool_input):
    tool_input = {k: (str(project / v) if k in ("file_path", "path") else v)
                  for k, v in tool_input.items()}
    assert decision(read(project, agent, tool, tool_input)) is None


@pytest.mark.req("REQ-GEN-11")
@pytest.mark.parametrize("tool, tool_input", [
    ("Grep", {"pattern": "X"}),                                   # no path: the project root
    ("Grep", {"pattern": "X", "path": "src"}),
    ("Grep", {"pattern": "X", "path": "."}),
    ("Glob", {"pattern": "**/*.py"}),                             # no path: the project root
    ("Glob", {"pattern": "../src/*.py", "path": "tests"}),
    ("Glob", {"pattern": "{..,unit}/src/*.py", "path": "tests"}),
    ("Grep", {"pattern": "X", "path": "tests", "glob": "{..,x}/src/*.py"}),
    ("Glob", {"pattern": "src/**/*.py"}),
    ("Glob", {"pattern": "tests/**/*.py"}),                       # no path: the project root
    ("Read", {"file_path": "tests/../src/a.py"}),
    ("Read", {"file_path": "vogon.yaml"}),
    ("Write", {"file_path": "src/a.py", "content": "X = 3\n"}),
    ("Edit", {"file_path": "src/a.py", "old_string": "1", "new_string": "2"}),
    ("Read", {}),
    ("Bash", {"command": "cat src/a.py"}),
    ("mcp__filesystem__read_file", {"path": "src/a.py"}),
])
def test_test_agent_reading_anything_else_is_refused(project, tool, tool_input):
    tool_input = {k: (str(project / v) if k in ("file_path",) else v) for k, v in tool_input.items()}
    assert decision(read(project, "vogon:vogon-test-writer", tool, tool_input)) == "deny"


@pytest.mark.req("REQ-GEN-11")
def test_a_search_of_the_project_root_is_refused_naming_the_root(project):
    out = read(project, "vogon-test-writer", "Grep", {"pattern": "X"})
    assert decision(out) == "deny"
    assert "The project root is outside them" in reason(out)


@pytest.mark.req("REQ-GEN-11")
def test_a_relative_path_resolves_against_the_agent_cwd(project):
    out = read(project, "vogon-test-checker", "Grep", {"pattern": "X", "path": "../src"},
               cwd=project / "tests")
    assert decision(out) == "deny"
    out = read(project, "vogon-test-checker", "Grep", {"pattern": "X", "path": "."},
               cwd=project / "tests")
    assert decision(out) is None


@pytest.mark.req("REQ-GEN-11")
def test_a_link_from_the_tests_to_the_source_is_refused(project):
    (project / "tests" / "link").symlink_to(project / "src", target_is_directory=True)
    out = read(project, "vogon-test-writer", "Read",
               {"file_path": str(project / "tests" / "link" / "a.py")})
    assert decision(out) == "deny"


@pytest.mark.req("REQ-GEN-11")
def test_the_configured_test_paths_are_the_allowed_ones(project):
    (project / "spec").mkdir()
    (project / "vogon.yaml").write_text(CONFIG + "paths:\n  tests: [spec]\n", encoding="utf-8")
    agent = "vogon:vogon-test-checker"
    assert decision(read(project, agent, "Read", {"file_path": str(project / "spec" / "x.py")})) is None
    assert decision(read(project, agent, "Read", {"file_path": str(project / "tests" / "test_a.py")})) == "deny"


@pytest.mark.req("REQ-GEN-11")
@pytest.mark.parametrize("agent", [None, "Explore", "general-purpose", "vogon:vogon-writer",
                                   "vogon:vogon-checker", "other:vogon-test-writer"])
def test_other_agents_pass(project, agent):
    for tool, tool_input in [("Read", {"file_path": str(project / "src" / "a.py")}),
                             ("Grep", {"pattern": "X"}), ("Bash", {"command": "ls"})]:
        assert decision(read(project, agent, tool, tool_input)) is None


@pytest.mark.req("REQ-GEN-11")
def test_test_read_hook_through_the_entry_script_fails_closed(project):
    result = entry("test-read", pre(project, "Read", {"file_path": str(project / "src" / "a.py")},
                                    agent_type="vogon:vogon-test-writer"), project)
    assert result.returncode == 0
    assert decision(result.stdout) == "deny"
    result = entry("test-read", "{broken", project)
    assert result.returncode == 0
    assert decision(result.stdout) == "deny"
