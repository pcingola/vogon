"""Read `vogon.yaml` from the project root.

The file is read on every call, so what a script or hook checks never depends
on what the agent was told. With no file, the default layout applies
(REQ-CLI-3). The paths, `test_command` and the approval assignment have
defaults. `systems` has none: a role with no entry is not configured, and the
transition settings of the tracker and the test manager are never filled in
by VOGON.

Schema:

    paths:
      records: vogon            # the records directory
      tests: [tests]            # test paths, a string or a list
    test_command: python -m pytest
    systems:
      tracker:
        server: <MCP server name>
        transition_tools: {<tool name>: <argument holding the transition id>}
        transitions: {<transition id>: <target state>}
        approved_states: [<state>, ...]
      test_manager: {same keys as tracker}
      repository_host: {server: <MCP server name>}
      document_system: {server: <MCP server name>}
    approvals:
      <approval>: {roles: [<role>, ...], system: <system role>}
    roles:
      <role>: [<holder email>, ...]
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from findings import Finding, failure, notice

FILENAME = "vogon.yaml"

DEFAULT_RECORDS = "vogon"
DEFAULT_TESTS = ("tests",)
DEFAULT_TEST_COMMAND = "python -m pytest"

SYSTEM_ROLES = ("tracker", "test_manager", "repository_host", "document_system")
# Roles whose workflow has transitions VOGON must never perform into an approved state.
TRANSITION_ROLES = ("tracker", "test_manager")
TRANSITION_KEYS = ("transition_tools", "transitions", "approved_states")

# The shipped approval assignment (DEC-018), plus the drafted documents
# approved in the document system (DEC-023).
DEFAULT_APPROVALS: dict[str, dict] = {
    "requirements": {"roles": ["product_owner"], "system": "tracker"},
    "test_cases": {"roles": ["test_lead"], "system": "test_manager"},
    "test_specification": {"roles": ["test_lead"], "system": "document_system"},
    "change": {"roles": ["engineer"], "system": "repository_host"},
    "risk_assessment": {"roles": ["system_owner", "it_quality_manager"], "system": "document_system"},
    "release": {"roles": ["system_owner", "it_quality_manager"], "system": "document_system"},
}

TOP_LEVEL_KEYS = ("paths", "test_command", "systems", "approvals", "roles")
PATH_KEYS = ("records", "tests")


@dataclass(frozen=True)
class SystemConfig:
    """The server filling one role and, for the tracker and the test manager,
    its transition settings. A transition setting is None when not configured."""

    role: str
    server: str
    transition_tools: dict[str, str] | None = None
    transitions: dict[str, str] | None = None
    approved_states: tuple[str, ...] | None = None

    def missing_transition_keys(self) -> list[str]:
        """The transition settings this role needs and does not have."""
        if self.role not in TRANSITION_ROLES:
            return []
        return [k for k in TRANSITION_KEYS if getattr(self, k) is None]


@dataclass(frozen=True)
class Approval:
    name: str
    roles: tuple[str, ...]
    system: str
    configured: bool  # False when the shipped default applies


@dataclass(frozen=True)
class Config:
    root: Path
    file: Path | None  # the vogon.yaml read, or None when absent
    records_dir: Path
    test_paths: tuple[Path, ...]
    test_command: tuple[str, ...]
    systems: dict[str, SystemConfig]
    approvals: dict[str, Approval]
    roles: dict[str, tuple[str, ...]]
    findings: tuple[Finding, ...] = field(default=())
    # True when the file could not be parsed, has a top-level key VOGON does not
    # know, or holds an error under `systems`: which server fills each role is
    # then unknown, and the transition hook refuses every MCP call.
    systems_unreadable: bool = False

    def system(self, role: str) -> SystemConfig | None:
        """The configured system for a role, or None when the role is not configured."""
        return self.systems.get(role)

    def holders(self, role: str) -> tuple[str, ...]:
        return self.roles.get(role, ())


def not_configured(role: str, needed_by: str) -> Finding:
    """The notice a step or check reports when the role it needs has no server."""
    return notice(f"{needed_by} skipped: the {role} role is not configured in {FILENAME}",
                  path=FILENAME, requirement="REQ-CLI-8")


def default_document() -> dict:
    """What `vogon init` writes: every setting that has a default, and no systems."""
    return {
        "paths": {"records": DEFAULT_RECORDS, "tests": list(DEFAULT_TESTS)},
        "test_command": DEFAULT_TEST_COMMAND,
        "approvals": {k: dict(v) for k, v in DEFAULT_APPROVALS.items()},
        "roles": {r: [] for r in _default_roles()},
    }


def _default_roles() -> list[str]:
    seen: dict[str, None] = {}
    for a in DEFAULT_APPROVALS.values():
        for r in a["roles"]:
            seen[r] = None
    return list(seen)


class _Reader:
    """Validates the parsed document, collecting failures instead of raising."""

    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def fail(self, message: str) -> None:
        self.findings.append(failure(message, path=FILENAME, requirement="REQ-CLI-3"))

    def mapping(self, value, where: str) -> dict:
        if value is None:
            return {}
        if not isinstance(value, dict):
            self.fail(f"{where} must be a mapping")
            return {}
        return value

    def string(self, value, where: str) -> str | None:
        if isinstance(value, str) and value.strip():
            return value
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)
        self.fail(f"{where} must be a non-empty string")
        return None

    def strings(self, value, where: str, allow_single: bool = False) -> tuple[str, ...] | None:
        if allow_single and isinstance(value, str):
            value = [value]
        if not isinstance(value, list):
            self.fail(f"{where} must be a list")
            return None
        out = [self.string(v, f"an entry of {where}") for v in value]
        return None if None in out else tuple(out)

    def unknown_keys(self, data: dict, allowed, where: str) -> None:
        for key in data:
            if key not in allowed:
                self.fail(f"unknown key {key!r} in {where}")


def load(root: Path) -> Config:
    """Read `vogon.yaml` under `root`, apply the defaults, and report what is invalid.

    Always returns a Config. Invalid parts are reported in `Config.findings` as
    failures and the default is used in their place.
    """
    root = Path(root).resolve()
    path = root / FILENAME
    r = _Reader()
    data: dict = {}
    file = None
    if path.is_file():
        file = path
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            r.fail(f"not valid YAML: {e}")
            loaded = None
        except (OSError, UnicodeDecodeError) as e:
            r.fail(f"cannot be read as UTF-8 text: {e}")
            loaded = None
        data = r.mapping(loaded, FILENAME)
    r.unknown_keys(data, TOP_LEVEL_KEYS, FILENAME)
    systems = _read_systems(r, r.mapping(data.get("systems"), "systems"))
    # Every failure so far concerns parsing, the top-level keys or `systems`.
    systems_unreadable = bool(r.findings)

    paths = r.mapping(data.get("paths"), "paths")
    r.unknown_keys(paths, PATH_KEYS, "paths")
    records = DEFAULT_RECORDS
    if "records" in paths:
        records = r.string(paths["records"], "paths.records") or DEFAULT_RECORDS
    tests: tuple[str, ...] = DEFAULT_TESTS
    if "tests" in paths:
        tests = r.strings(paths["tests"], "paths.tests", allow_single=True) or DEFAULT_TESTS

    test_command = shlex.split(DEFAULT_TEST_COMMAND)
    if "test_command" in data:
        value = data["test_command"]
        if isinstance(value, str) and value.strip():
            test_command = shlex.split(value)
        elif isinstance(value, list) and value:
            test_command = list(r.strings(value, "test_command") or test_command)
        else:
            r.fail("test_command must be a non-empty string or list")

    roles = _read_roles(r, data)
    approvals = _read_approvals(r, r.mapping(data.get("approvals"), "approvals"), roles)

    return Config(
        root=root,
        file=file,
        records_dir=root / records,
        test_paths=tuple(root / t for t in tests),
        test_command=tuple(test_command),
        systems=systems,
        approvals=approvals,
        roles=roles,
        findings=tuple(r.findings),
        systems_unreadable=systems_unreadable,
    )


def _read_systems(r: _Reader, data: dict) -> dict[str, SystemConfig]:
    systems: dict[str, SystemConfig] = {}
    for role, entry in data.items():
        where = f"systems.{role}"
        if role not in SYSTEM_ROLES:
            r.fail(f"unknown system role {role!r}; the roles are {', '.join(SYSTEM_ROLES)}")
            continue
        entry = r.mapping(entry, where)
        allowed = ("server", *TRANSITION_KEYS) if role in TRANSITION_ROLES else ("server",)
        r.unknown_keys(entry, allowed, where)
        if "server" not in entry:
            r.fail(f"{where}.server is missing")
            continue
        server = r.string(entry["server"], f"{where}.server")
        if server is None:
            continue
        tools = transitions = states = None
        if "transition_tools" in entry:
            tools = _string_map(r, entry["transition_tools"], f"{where}.transition_tools")
        if "transitions" in entry:
            transitions = _string_map(r, entry["transitions"], f"{where}.transitions")
        if "approved_states" in entry:
            states = r.strings(entry["approved_states"], f"{where}.approved_states")
        systems[role] = SystemConfig(role, server, tools, transitions, states)
    return systems


def _string_map(r: _Reader, value, where: str) -> dict[str, str] | None:
    """A mapping of strings to strings. Keys YAML read as numbers become strings."""
    if not isinstance(value, dict) or not value:
        r.fail(f"{where} must be a non-empty mapping")
        return None
    out: dict[str, str] = {}
    for k, v in value.items():
        key = r.string(k, f"a key of {where}")
        val = r.string(v, f"{where}.{k}")
        if key is None or val is None:
            return None
        out[key] = val
    return out


def _read_roles(r: _Reader, data: dict) -> dict[str, tuple[str, ...]]:
    # Roles the default assignment uses exist with no holder until configured.
    roles: dict[str, tuple[str, ...]] = {role: () for role in _default_roles()}
    for role, holders in r.mapping(data.get("roles"), "roles").items():
        if holders is None:
            roles[str(role)] = ()
            continue
        value = r.strings(holders, f"roles.{role}")
        roles[str(role)] = value if value is not None else ()
    return roles


def _read_approvals(r: _Reader, data: dict, roles: dict) -> dict[str, Approval]:
    approvals = {
        name: Approval(name, tuple(d["roles"]), d["system"], configured=False)
        for name, d in DEFAULT_APPROVALS.items()
    }
    for name, entry in data.items():
        where = f"approvals.{name}"
        entry = r.mapping(entry, where)
        r.unknown_keys(entry, ("roles", "system"), where)
        default = DEFAULT_APPROVALS.get(name, {})
        if "roles" in entry:
            names = r.strings(entry["roles"], f"{where}.roles", allow_single=True)
        elif default:
            names = tuple(default["roles"])
        else:
            r.fail(f"{where}.roles is missing")
            names = None
        if "system" in entry:
            system = r.string(entry["system"], f"{where}.system")
        elif default:
            system = default["system"]
        else:
            r.fail(f"{where}.system is missing")
            system = None
        if system is not None and system not in SYSTEM_ROLES:
            r.fail(f"{where}.system is {system!r}; it must be one of {', '.join(SYSTEM_ROLES)}")
            system = None
        if names is not None:
            for role in names:
                if role not in roles:
                    r.findings.append(failure(
                        f"approval {name!r} names role {role!r}, which is not defined in roles",
                        path=FILENAME, requirement="REQ-CLI-5"))
        if names is None or system is None:
            continue
        approvals[name] = Approval(name, names, system, configured=True)
    return approvals


def check(cfg: Config) -> list[Finding]:
    """What the configuration leaves unset, beyond what `load` reported as invalid.

    - An approval whose role has no holder is a notice naming both (REQ-CLI-6).
    - A configured tracker or test manager without `transition_tools`,
      `transitions` or `approved_states` is a failure, because the transition
      hook then blocks every call to its server (REQ-CLI-8, REQ-TRK-1). A key
      whose value `load` already reported as invalid is not reported again.
    - A system role that an approval is given in and that has no entry in
      `systems` is a notice naming the role and the approvals (REQ-CLI-8).
    """
    found: list[Finding] = []
    for name, approval in cfg.approvals.items():
        for role in approval.roles:
            if role in cfg.roles and not cfg.holders(role):
                found.append(notice(
                    f"approval {name!r}: role {role!r} has no holder in roles",
                    path=FILENAME, requirement="REQ-CLI-6"))

    reported = [f.message for f in cfg.findings]
    for role in TRANSITION_ROLES:
        system = cfg.system(role)
        if system is None:
            continue
        missing = [k for k in system.missing_transition_keys()
                   if not any(f"systems.{role}.{k}" in m for m in reported)]
        if missing:
            found.append(failure(
                f"systems.{role} (server {system.server!r}) has no {', '.join(missing)}; "
                f"every call to that server is blocked until setup writes them",
                path=FILENAME, requirement="REQ-CLI-8"))

    needed: dict[str, list[str]] = {}
    for name, approval in cfg.approvals.items():
        if approval.system not in cfg.systems:
            needed.setdefault(approval.system, []).append(name)
    for role in SYSTEM_ROLES:
        if role in needed:
            names = ", ".join(repr(n) for n in needed[role])
            found.append(notice(
                f"the {role} role is not configured in {FILENAME}; "
                f"the approvals given in it are {names}",
                path=FILENAME, requirement="REQ-CLI-8"))
    return found
