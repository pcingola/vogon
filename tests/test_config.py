from pathlib import Path

import pytest

import config
from config import load


def write(root: Path, text: str) -> None:
    (root / "vogon.yaml").write_text(text, encoding="utf-8")


def failures(cfg):
    return [f for f in cfg.findings if f.is_failure]


# REQ-CLI-3: defaults and overrides


@pytest.mark.req("REQ-CLI-3")
def test_no_file_resolves_the_default_layout(tmp_path):
    cfg = load(tmp_path)
    assert cfg.file is None
    assert cfg.records_dir == tmp_path.resolve() / "vogon"
    assert cfg.test_paths == (tmp_path.resolve() / "tests",)
    assert cfg.test_command == ("python", "-m", "pytest")
    assert cfg.findings == ()


@pytest.mark.req("REQ-CLI-3")
@pytest.mark.parametrize("text, field, expected", [
    ("paths:\n  records: records\n", "records_dir", "records"),
    ("paths:\n  tests: [tests/unit, tests/api]\n", "test_paths", ("tests/unit", "tests/api")),
    ("paths:\n  tests: spec\n", "test_paths", ("spec",)),
    ("test_command: uv run pytest -q\n", "test_command", ("uv", "run", "pytest", "-q")),
])
def test_each_setting_overrides_exactly_one_default(tmp_path, text, field, expected):
    default = load(tmp_path)
    write(tmp_path, text)
    cfg = load(tmp_path)
    assert cfg.findings == ()
    root = tmp_path.resolve()
    if field == "records_dir":
        expected = root / expected
    elif field == "test_paths":
        expected = tuple(root / p for p in expected)
    assert getattr(cfg, field) == expected
    for other in ("records_dir", "test_paths", "test_command", "systems", "approvals", "roles"):
        if other != field:
            assert getattr(cfg, other) == getattr(default, other), other


@pytest.mark.req("REQ-CLI-3")
def test_file_is_read_again_on_every_call(tmp_path):
    write(tmp_path, "test_command: pytest\n")
    assert load(tmp_path).test_command == ("pytest",)
    write(tmp_path, "test_command: tox\n")
    assert load(tmp_path).test_command == ("tox",)


@pytest.mark.req("REQ-CLI-3")
@pytest.mark.parametrize("text, words", [
    ("pathz:\n  records: x\n", ["pathz"]),
    ("paths:\n  record: x\n", ["record"]),
    ("paths: [\n", ["not valid YAML"]),
    ("- a\n- b\n", ["mapping"]),
    ("test_command: 3.5\n", ["test_command"]),
])
def test_an_invalid_file_is_a_failure_naming_the_problem(tmp_path, text, words):
    write(tmp_path, text)
    found = failures(load(tmp_path))
    assert found
    assert all(f.path == "vogon.yaml" for f in found)
    assert all(w in found[0].message for w in words)


@pytest.mark.req("REQ-CLI-3", "REQ-TRK-1")
def test_a_file_that_is_not_utf8_is_a_failure_and_leaves_the_systems_unknown(tmp_path):
    (tmp_path / "vogon.yaml").write_bytes(b"systems: \xff\n")
    cfg = load(tmp_path)
    found = failures(cfg)
    assert [f.path for f in found] == ["vogon.yaml"]
    assert "UTF-8" in found[0].message
    assert cfg.systems_unreadable


@pytest.mark.req("REQ-CLI-3")
def test_an_error_outside_systems_leaves_the_systems_readable(tmp_path):
    write(tmp_path, "systems:\n  document_system: {server: docs}\n"
                    "approvals:\n  release: {roles: [system_owner], system: nowhere}\n")
    cfg = load(tmp_path)
    assert failures(cfg)
    assert not cfg.systems_unreadable
    assert cfg.system("document_system").server == "docs"


# REQ-CLI-5: approvals and role holders


@pytest.mark.req("REQ-CLI-5")
def test_no_file_gives_the_shipped_approval_assignment(tmp_path):
    cfg = load(tmp_path)
    approvals = {n: (a.roles, a.system, a.configured) for n, a in cfg.approvals.items()}
    assert approvals == {
        "requirements": (("product_owner",), "tracker", False),
        "test_cases": (("test_lead",), "test_manager", False),
        "test_specification": (("test_lead",), "document_system", False),
        "change": (("engineer",), "repository_host", False),
        "risk_assessment": (("system_owner", "it_quality_manager"), "document_system", False),
        "release": (("system_owner", "it_quality_manager"), "document_system", False),
    }


@pytest.mark.req("REQ-CLI-5")
def test_configured_approval_resolves_to_its_roles_system_and_holders(tmp_path):
    write(tmp_path, """
approvals:
  test_cases: {roles: [validation_lead], system: test_manager}
roles:
  validation_lead: [vera@example.com]
  product_owner: [alice@example.com]
""")
    cfg = load(tmp_path)
    assert failures(cfg) == []
    test_cases = cfg.approvals["test_cases"]
    assert (test_cases.roles, test_cases.system, test_cases.configured) == (
        ("validation_lead",), "test_manager", True)
    assert cfg.holders("validation_lead") == ("vera@example.com",)
    requirements = cfg.approvals["requirements"]
    assert (requirements.roles, requirements.system, requirements.configured) == (
        ("product_owner",), "tracker", False)
    assert cfg.holders("product_owner") == ("alice@example.com",)
    assert cfg.holders("test_lead") == ()


@pytest.mark.req("REQ-CLI-5")
def test_approval_naming_an_undefined_role_fails_naming_both(tmp_path):
    write(tmp_path, """
approvals:
  test_cases: {roles: [validation_lead], system: test_manager}
roles:
  test_lead: [bob@example.com]
""")
    found = failures(load(tmp_path))
    assert len(found) == 1
    assert found[0].requirement == "REQ-CLI-5"
    assert "test_cases" in found[0].message
    assert "validation_lead" in found[0].message


@pytest.mark.req("REQ-CLI-5")
def test_approval_given_in_an_unknown_system_fails(tmp_path):
    write(tmp_path, "approvals:\n  requirements: {roles: [product_owner], system: wiki}\n")
    found = failures(load(tmp_path))
    assert len(found) == 1
    assert "approvals.requirements.system" in found[0].message


# Systems, transitions and approved states have no default.


@pytest.mark.req("REQ-CLI-8")
def test_no_file_configures_no_system(tmp_path):
    cfg = load(tmp_path)
    assert cfg.systems == {}
    assert all(cfg.system(role) is None for role in config.SYSTEM_ROLES)


@pytest.mark.req("REQ-CLI-8")
def test_default_document_names_no_system(tmp_path):
    assert "systems" not in config.default_document()


@pytest.mark.req("REQ-CLI-8")
def test_server_without_transition_settings_leaves_them_unset(tmp_path):
    write(tmp_path, "systems:\n  tracker: {server: issues}\n  document_system: {server: dms}\n")
    cfg = load(tmp_path)
    assert failures(cfg) == []
    tracker = cfg.system("tracker")
    assert tracker.server == "issues"
    assert (tracker.transition_tools, tracker.transitions, tracker.approved_states) == (None, None, None)
    assert tracker.missing_transition_keys() == ["transition_tools", "transitions", "approved_states"]
    assert cfg.system("document_system").missing_transition_keys() == []
    assert cfg.system("test_manager") is None


@pytest.mark.req("REQ-CLI-8")
def test_full_transition_setup_is_read(tmp_path):
    write(tmp_path, """
systems:
  tracker:
    server: issues
    transition_tools: {transition_issue: transition_id}
    transitions: {11: In Review, 31: Approved}
    approved_states: [Approved]
""")
    cfg = load(tmp_path)
    assert failures(cfg) == []
    tracker = cfg.system("tracker")
    assert tracker.transition_tools == {"transition_issue": "transition_id"}
    assert tracker.transitions == {"11": "In Review", "31": "Approved"}
    assert tracker.approved_states == ("Approved",)
    assert tracker.missing_transition_keys() == []


@pytest.mark.req("REQ-CLI-8")
@pytest.mark.parametrize("text, words", [
    ("systems:\n  wiki: {server: w}\n", ["wiki"]),
    ("systems:\n  tracker: {transitions: {1: Done}}\n", ["server"]),
    ("systems:\n  repository_host: {server: git, approved_states: [Merged]}\n", ["approved_states"]),
    ("systems:\n  tracker: {server: t, transitions: {}}\n", ["transitions"]),
])
def test_invalid_system_entry_fails(tmp_path, text, words):
    write(tmp_path, text)
    found = failures(load(tmp_path))
    assert found
    assert all(w in found[0].message for w in words)


# REQ-CLI-6: an approval whose role has no holder


def setup_findings(cfg, requirement):
    return [f for f in config.check(cfg) if f.requirement == requirement]


@pytest.mark.req("REQ-CLI-6")
def test_approval_whose_role_has_no_holder_is_reported_naming_both(tmp_path):
    write(tmp_path, """
approvals:
  release: {roles: [system_owner, it_quality_manager], system: document_system}
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
  engineer: [alice@example.com]
  system_owner: [dave@example.com]
  it_quality_manager: []
""")
    found = setup_findings(load(tmp_path), "REQ-CLI-6")
    reported = {(a, r) for f in found for a in config.DEFAULT_APPROVALS
                for r in ("system_owner", "it_quality_manager")
                if repr(a) in f.message and repr(r) in f.message}
    assert reported == {("release", "it_quality_manager"), ("risk_assessment", "it_quality_manager")}
    assert len(found) == 2
    assert all(not f.is_failure and f.path == "vogon.yaml" for f in found)


@pytest.mark.req("REQ-CLI-6")
def test_every_role_with_a_holder_reports_nothing(tmp_path):
    write(tmp_path, """
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
  engineer: [alice@example.com]
  system_owner: [dave@example.com]
  it_quality_manager: [erin@example.com]
""")
    assert setup_findings(load(tmp_path), "REQ-CLI-6") == []


@pytest.mark.req("REQ-CLI-6")
def test_default_setup_reports_every_approval_and_role(tmp_path):
    found = setup_findings(load(tmp_path), "REQ-CLI-6")
    expected = {("requirements", "product_owner"), ("test_cases", "test_lead"),
                ("test_specification", "test_lead"), ("change", "engineer"),
                ("risk_assessment", "system_owner"), ("risk_assessment", "it_quality_manager"),
                ("release", "system_owner"), ("release", "it_quality_manager")}
    assert {(a, r) for a, r in expected
            if any(repr(a) in f.message and repr(r) in f.message for f in found)} == expected
    assert len(found) == len(expected)


# REQ-CLI-8: roles and transition settings come from setup


@pytest.mark.req("REQ-CLI-8")
def test_no_systems_entry_reports_each_needed_role_as_not_configured(tmp_path):
    write(tmp_path, "test_command: pytest\n")
    found = setup_findings(load(tmp_path), "REQ-CLI-8")
    assert all(not f.is_failure for f in found)
    for role in config.SYSTEM_ROLES:
        assert sum(f"the {role} role is not configured" in f.message for f in found) == 1


@pytest.mark.req("REQ-CLI-8")
def test_configured_role_is_not_reported_as_not_configured(tmp_path):
    write(tmp_path, "systems:\n  document_system: {server: dms}\n  repository_host: {server: git}\n")
    found = setup_findings(load(tmp_path), "REQ-CLI-8")
    messages = " ".join(f.message for f in found)
    assert "tracker role is not configured" in messages
    assert "test_manager role is not configured" in messages
    assert "document_system role" not in messages
    assert "repository_host role" not in messages


@pytest.mark.req("REQ-CLI-8")
@pytest.mark.parametrize("role", ["tracker", "test_manager"])
@pytest.mark.parametrize("present, missing", [
    ({}, ["transition_tools", "transitions", "approved_states"]),
    ({"transition_tools": "{move: id}"}, ["transitions", "approved_states"]),
    ({"transition_tools": "{move: id}", "transitions": "{1: Approved}"}, ["approved_states"]),
])
def test_incomplete_transition_setup_is_a_failure_naming_the_missing_keys(tmp_path, role, present,
                                                                         missing):
    entry = "".join(f"\n    {k}: {v}" for k, v in present.items())
    write(tmp_path, f"systems:\n  {role}:\n    server: srv{entry}\n")
    cfg = load(tmp_path)
    assert failures(cfg) == []
    found = [f for f in setup_findings(cfg, "REQ-CLI-8") if f.is_failure]
    assert len(found) == 1
    assert role in found[0].message and "srv" in found[0].message
    for key in ("transition_tools", "transitions", "approved_states"):
        assert (key in found[0].message) == (key in missing), key


@pytest.mark.req("REQ-CLI-8")
def test_complete_transition_setup_is_not_a_failure(tmp_path):
    write(tmp_path, """
systems:
  tracker:
    server: issues
    transition_tools: {transition_issue: transition_id}
    transitions: {11: In Review, 31: Approved}
    approved_states: [Approved]
  repository_host: {server: git}
""")
    assert [f for f in config.check(load(tmp_path)) if f.is_failure] == []


@pytest.mark.req("REQ-CLI-8")
def test_invalid_transition_setting_is_reported_once(tmp_path):
    write(tmp_path, """
systems:
  tracker:
    server: issues
    transition_tools: {transition_issue: transition_id}
    transitions: {}
    approved_states: [Approved]
""")
    cfg = load(tmp_path)
    reported = [f.message for f in cfg.findings] + [f.message for f in config.check(cfg)]
    assert sum("transitions" in m for m in reported) == 1
