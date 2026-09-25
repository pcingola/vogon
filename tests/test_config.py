from pathlib import Path

import pytest

import config
from config import load


def write(root: Path, text: str) -> None:
    (root / "vogon.yaml").write_text(text, encoding="utf-8")


def errors(cfg):
    return [f for f in cfg.findings if f.is_error]


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
def test_an_invalid_file_is_an_error_naming_the_problem(tmp_path, text, words):
    write(tmp_path, text)
    found = errors(load(tmp_path))
    assert found
    assert all(f.path == "vogon.yaml" for f in found)
    assert all(w in found[0].message for w in words)


@pytest.mark.req("REQ-CLI-3")
def test_a_file_that_is_not_utf8_is_an_error(tmp_path):
    (tmp_path / "vogon.yaml").write_bytes(b"systems: \xff\n")
    cfg = load(tmp_path)
    found = errors(cfg)
    assert [f.path for f in found] == ["vogon.yaml"]
    assert "UTF-8" in found[0].message


@pytest.mark.req("REQ-CLI-3")
def test_an_error_outside_systems_leaves_the_systems_readable(tmp_path):
    write(tmp_path, "systems:\n  document_system: {server: docs}\n"
                    "approvals:\n  release: {roles: [system_owner], system: nowhere}\n")
    cfg = load(tmp_path)
    assert errors(cfg)
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
    assert errors(cfg) == []
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
    found = errors(load(tmp_path))
    assert len(found) == 1
    assert found[0].requirement == "REQ-CLI-5"
    assert "test_cases" in found[0].message
    assert "validation_lead" in found[0].message


@pytest.mark.req("REQ-CLI-5")
def test_approval_given_in_an_unknown_system_fails(tmp_path):
    write(tmp_path, "approvals:\n  requirements: {roles: [product_owner], system: wiki}\n")
    found = errors(load(tmp_path))
    assert len(found) == 1
    assert "approvals.requirements.system" in found[0].message


# Systems and approved states have no default.


@pytest.mark.req("REQ-CLI-8")
def test_no_file_configures_no_system(tmp_path):
    cfg = load(tmp_path)
    assert cfg.systems == {}
    assert all(cfg.system(role) is None for role in config.SYSTEM_ROLES)


@pytest.mark.req("REQ-CLI-8")
def test_default_document_names_no_system(tmp_path):
    assert "systems" not in config.default_document()


@pytest.mark.req("REQ-CLI-8")
def test_server_without_approved_states_leaves_them_unset(tmp_path):
    write(tmp_path, "systems:\n  tracker: {server: issues}\n  document_system: {server: dms}\n")
    cfg = load(tmp_path)
    assert errors(cfg) == []
    tracker = cfg.system("tracker")
    assert tracker.server == "issues"
    assert tracker.approved_states is None
    assert cfg.system("test_manager") is None


@pytest.mark.req("REQ-CLI-8")
def test_approved_states_are_read(tmp_path):
    write(tmp_path, """
systems:
  tracker:
    server: issues
    approved_states: [Approved]
""")
    cfg = load(tmp_path)
    assert errors(cfg) == []
    tracker = cfg.system("tracker")
    assert tracker.approved_states == ("Approved",)


@pytest.mark.req("REQ-CLI-8")
@pytest.mark.parametrize("text, words", [
    ("systems:\n  wiki: {server: w}\n", ["wiki"]),
    ("systems:\n  tracker: {approved_states: [Done]}\n", ["server"]),
    ("systems:\n  repository_host: {server: git, approved_states: [Merged]}\n", ["approved_states"]),
    ("systems:\n  tracker: {server: t, transitions: {1: Done}}\n", ["transitions"]),
    ("systems:\n  tracker: {server: t, approved_states: Approved}\n", ["approved_states"]),
])
def test_invalid_system_entry_fails(tmp_path, text, words):
    write(tmp_path, text)
    found = errors(load(tmp_path))
    assert found
    assert all(w in found[0].message for w in words)


# REQ-CLI-6: an approval whose role has no holder


def setup_findings(cfg, requirement):
    return [f for f in config.check(cfg) if f.requirement == requirement]


HOLDERS = """
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
  engineer: [carol@example.com]
  system_owner: [dave@example.com]
  it_quality_manager: [erin@example.com]
"""

SERVERS = """
systems:
  tracker:
    server: issues
    approved_states: [Approved]
  test_manager:
    server: tests
    approved_states: [Approved]
  repository_host: {server: git}
  document_system: {server: dms}
"""


@pytest.mark.req("REQ-CLI-6")
def test_each_role_with_no_holder_is_one_error_naming_its_approvals(tmp_path):
    write(tmp_path, SERVERS + HOLDERS.replace("[erin@example.com]", "[]")
          .replace("[bob@example.com]", "[]"))
    found = setup_findings(load(tmp_path), "REQ-CLI-6")
    assert [(f.severity, f.path, f.message) for f in found] == [
        ("error", "vogon.yaml", "no holder for the role test_lead, which gives the test_cases "
                                "and test_specification approvals"),
        ("error", "vogon.yaml", "no holder for the role it_quality_manager, which gives the "
                                "risk_assessment and release approvals"),
    ]


@pytest.mark.req("REQ-CLI-6")
def test_a_role_giving_one_approval_names_it_in_the_singular(tmp_path):
    write(tmp_path, SERVERS + HOLDERS.replace("[alice@example.com]", "[]"))
    assert [f.message for f in setup_findings(load(tmp_path), "REQ-CLI-6")] == [
        "no holder for the role product_owner, which gives the requirements approval"]


@pytest.mark.req("REQ-CLI-6")
def test_every_role_with_a_holder_reports_nothing(tmp_path):
    write(tmp_path, HOLDERS)
    assert setup_findings(load(tmp_path), "REQ-CLI-6") == []


@pytest.mark.req("REQ-CLI-6")
def test_a_role_no_approval_uses_is_not_reported(tmp_path):
    write(tmp_path, SERVERS + HOLDERS + "  auditor: []\n")
    assert config.check(load(tmp_path)) == []


@pytest.mark.req("REQ-CLI-6")
def test_default_setup_reports_every_role_once(tmp_path):
    found = setup_findings(load(tmp_path), "REQ-CLI-6")
    assert all(f.is_error for f in found)
    assert [f.message.split(",")[0] for f in found] == [
        f"no holder for the role {r}" for r in
        ("product_owner", "test_lead", "engineer", "system_owner", "it_quality_manager")]


# REQ-CLI-8: roles and approved states come from setup


@pytest.mark.req("REQ-CLI-8")
def test_no_systems_entry_is_one_error_per_role_naming_its_approvals(tmp_path):
    write(tmp_path, "test_command: pytest\n" + HOLDERS)
    found = setup_findings(load(tmp_path), "REQ-CLI-8")
    assert [(f.severity, f.path, f.message) for f in found] == [
        ("error", "vogon.yaml", "no server for the tracker; the requirements approval cannot be given"),
        ("error", "vogon.yaml", "no server for the test_manager; the test_cases approval cannot "
                                "be given"),
        ("error", "vogon.yaml", "no server for the repository_host; the change approval cannot "
                                "be given"),
        ("error", "vogon.yaml", "no server for the document_system; the test_specification, "
                                "risk_assessment and release approvals cannot be given"),
    ]


@pytest.mark.req("REQ-CLI-8")
def test_configured_role_is_not_reported_as_having_no_server(tmp_path):
    write(tmp_path, "systems:\n  document_system: {server: dms}\n  repository_host: {server: git}\n")
    messages = [f.message for f in setup_findings(load(tmp_path), "REQ-CLI-8")]
    assert [m.split(";")[0] for m in messages] == ["no server for the tracker",
                                                   "no server for the test_manager"]


@pytest.mark.req("REQ-CLI-8")
def test_a_system_role_no_approval_is_given_in_is_not_reported(tmp_path):
    write(tmp_path, SERVERS.split("  repository_host:")[0] + HOLDERS + """
approvals:
  change: {roles: [engineer], system: tracker}
  test_specification: {roles: [test_lead], system: tracker}
  risk_assessment: {roles: [system_owner, it_quality_manager], system: tracker}
  release: {roles: [system_owner, it_quality_manager], system: tracker}
""")
    assert config.check(load(tmp_path)) == []


@pytest.mark.req("REQ-CLI-6", "REQ-CLI-8")
def test_a_complete_setup_reports_nothing(tmp_path):
    write(tmp_path, SERVERS + HOLDERS)
    cfg = load(tmp_path)
    assert cfg.findings == ()
    assert config.check(cfg) == []


@pytest.mark.req("REQ-CLI-8")
@pytest.mark.parametrize("role", ["tracker", "test_manager"])
def test_missing_approved_states_is_an_error(tmp_path, role):
    write(tmp_path, f"systems:\n  {role}:\n    server: srv\n")
    cfg = load(tmp_path)
    assert errors(cfg) == []
    found = [f for f in setup_findings(cfg, "REQ-CLI-8") if f.message.startswith("systems.")]
    assert len(found) == 1 and found[0].is_error
    assert role in found[0].message and "srv" in found[0].message
    assert "approved_states" in found[0].message


@pytest.mark.req("REQ-CLI-8")
def test_configured_approved_states_are_not_an_error(tmp_path):
    write(tmp_path, """
systems:
  tracker:
    server: issues
    approved_states: [Approved]
  repository_host: {server: git}
""")
    assert [f for f in config.check(load(tmp_path)) if f.message.startswith("systems.")] == []


@pytest.mark.req("REQ-CLI-8")
def test_invalid_approved_states_are_reported_once(tmp_path):
    write(tmp_path, """
systems:
  tracker:
    server: issues
    approved_states: Approved
""")
    cfg = load(tmp_path)
    reported = [f.message for f in cfg.findings] + [f.message for f in config.check(cfg)]
    assert sum("approved_states" in m for m in reported) == 1
