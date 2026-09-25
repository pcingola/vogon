"""Read the files Claude Code writes under `.vogon/` from what it read through MCP.

The scripts reach no external system. Claude Code reads the tracker, the test
manager, the repository host and the document system through the servers
`vogon.yaml` names, and saves what it read in the files below. The checks and
`vogon push` compare them with the records. Every timestamp is ISO 8601 with a
UTC offset, such as `2026-05-10T09:00:00Z`.

`.vogon/tracker.json`: the issues of the tracker and the test manager.

    {
      "read_at": "2026-05-10T12:00:00Z",
      "systems": {
        "<role>": {                       tracker, test_manager, or another tracked_as role
          "server": "<MCP server the issues were read from>",
          "issues": [
            {
              "key": "PROJ-412",
              "summary": "REQ-TRK-2 Report a record edited after ...",
              "description": "<the full description; its last line is the content hash>",
              "status": "Approved",
              "links": ["PROJ-7"],        a test issue: the requirement issues it is linked to
              "transitions": [            every status change, oldest first
                {"to": "Approved", "by": "bob@example.com", "at": "2026-05-10T09:00:00Z",
                 "description": "<the description when the transition was made;
                                  absent when it has not changed since>"}
              ],
              "executions": [             a test issue: every result imported against it
                {"build": "a1b2c3d...", "at": "2026-06-01T12:00:00Z", "outcome": "passed"}
              ]
            }
          ],
          "missing": [                    keys named in a tracked_as that were read and not found
            {"key": "PROJ-9", "reason": "deleted"}
          ]
        }
      }
    }

For each role it holds, the file lists every issue whose summary starts with a
record id or a test node id, and every key a record's `tracked_as` names for
that role. `links`, `transitions`, `executions` and `missing` may be omitted
when empty. `by` is the email the system reports for the person who made the
transition.

`.vogon/servers.json`: the tools of each configured server, written at setup.

    {
      "servers": {
        "<server>": {
          "tools": ["get_issue", "search_issues", ...],
          "operations": {"<operation>": "<tool>", ...}
        }
      }
    }

`operations` maps each operation VOGON needs (`OPERATIONS`) to the tool Claude
Code found for it. An operation with no entry, or mapped to a tool not in
`tools`, is missing (REQ-CLI-4).

`.vogon/branch_rules.json`: the repository host's rules for the default branch.

    {
      "server": "<MCP server>",
      "repository": "acme/app",
      "default_branch": "main",
      "required_approving_reviews": 1,
      "author_approval_excluded": true
    }

`required_approving_reviews` is the number of approving reviews a merge into
the default branch needs, 0 when none. `author_approval_excluded` is true when
the author's own approval does not count towards it (REQ-CLI-7).

`.vogon/risk_assessment.md`: the approved risk assessment, as read back from
the document system. The draft in `vogon/documents/risk_assessment.md` has the
same format: markdown holding one table whose first two columns are
`Requirement` and `Risk`, one row per requirement, the risk level being a
`gxp_risk` value (REQ-GEN-9):

    | Requirement | Risk | Failure would damage | Basis |
    | --- | --- | --- | --- |
    | REQ-TRK-2 | data integrity | An unapproved edit would ... | CON-001, FACT-004 |

A file that is absent returns None and no finding; the caller reports the
check it could not run as skipped (REQ-CLI-2). A file that is present and
malformed is a failure.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import ids
from config import Config
from findings import Finding, failure, notice

STATE_DIR = ".vogon"
TRACKER_FILE = "tracker.json"
SERVERS_FILE = "servers.json"
BRANCH_RULES_FILE = "branch_rules.json"
RISK_FILE = "risk_assessment.md"
# Written by `vogon trace` in the format `pytest_plugin/vogon_pytest.py` documents.
RESULTS_FILE = "results.json"

GXP_RISKS = ("safety", "product quality", "data integrity", "none")

# The operations VOGON needs from the server filling each role (REQ-CLI-4).
OPERATIONS: dict[str, tuple[str, ...]] = {
    "tracker": (
        "search_issues", "read_issue", "read_issue_history", "read_transitions",
        "create_issue", "update_issue", "link_issues",
    ),
    "test_manager": (
        "search_tests", "read_test", "read_test_history", "read_transitions",
        "create_test", "update_test", "link_test_to_requirement", "import_results",
        "export_traceability_report", "export_results",
    ),
    "repository_host": ("read_repository", "read_branch_rules"),
    "document_system": ("upload_document", "download_document"),
}


def path(config: Config, name: str) -> Path:
    return config.root / STATE_DIR / name


def rel(name: str) -> str:
    return f"{STATE_DIR}/{name}"


def skipped(name: str, what: str) -> Finding:
    """The notice for a check that did not run because a snapshot is absent."""
    return notice(f"{what} skipped: {rel(name)} is absent; Claude Code writes it from what "
                  f"it reads through MCP", path=rel(name), requirement="REQ-CLI-2")


def parse_time(value) -> datetime | None:
    """An ISO 8601 timestamp with a UTC offset, or None."""
    if not isinstance(value, str):
        return None
    try:
        t = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo is not None else None


class SnapshotError(Exception):
    def __init__(self, name: str, message: str) -> None:
        super().__init__(message)
        self.finding = failure(f"{rel(name)} {message}", path=rel(name))


def _read_json(config: Config, name: str):
    p = path(config, name)
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise SnapshotError(name, f"is not valid JSON: {e}") from e


def _mapping(name: str, value, where: str) -> dict:
    if not isinstance(value, dict):
        raise SnapshotError(name, f"{where} must be an object")
    return value


def _list(name: str, value, where: str) -> list:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SnapshotError(name, f"{where} must be a list")
    return value


def _string(name: str, value, where: str, optional: bool = False) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    if optional and value is None:
        return None
    raise SnapshotError(name, f"{where} must be a non-empty string")


def _time(name: str, value, where: str) -> datetime:
    t = parse_time(value)
    if t is None:
        raise SnapshotError(name, f"{where} must be an ISO 8601 time with a UTC offset, "
                                  f"not {value!r}")
    return t


# .vogon/tracker.json


@dataclass(frozen=True)
class Transition:
    to: str
    by: str | None
    at: datetime
    description: str | None  # the description at that time, None when unchanged since


@dataclass(frozen=True)
class Execution:
    build: str
    at: datetime
    outcome: str | None


@dataclass(frozen=True)
class Issue:
    role: str
    key: str
    summary: str
    description: str
    status: str
    links: tuple[str, ...] = ()
    transitions: tuple[Transition, ...] = ()
    executions: tuple[Execution, ...] = ()

    @property
    def identity(self) -> str:
        """The first word of the summary: a record id or a test node id."""
        words = self.summary.split(maxsplit=1)
        return words[0] if words else ""

    def approval(self, approved_states) -> Transition | None:
        """The transition the current approved state rests on: the last one into an
        approved state, when the issue is in one. None when it is not approved, or
        when no transition into its state was read."""
        if self.status not in approved_states:
            return None
        for t in reversed(self.transitions):
            if t.to in approved_states:
                return t
        return None

    def description_at(self, transition: Transition) -> str:
        return transition.description if transition.description is not None else self.description


@dataclass
class SystemIssues:
    role: str
    server: str
    issues: dict[str, Issue] = field(default_factory=dict)
    missing: dict[str, str] = field(default_factory=dict)  # key -> reason

    def find(self, identity: str) -> list[Issue]:
        """The issues whose summary starts with `identity`. A record id is compared
        numerically, so `REQ-TRK-02` finds `REQ-TRK-2`."""
        target = ids.parse(identity)
        found = []
        for issue in self.issues.values():
            if target is not None:
                got = ids.parse(issue.identity)
                if got is not None and got.key == target.key:
                    found.append(issue)
            elif issue.identity == identity:
                found.append(issue)
        return found


@dataclass
class TrackerSnapshot:
    read_at: datetime | None
    systems: dict[str, SystemIssues]


def load_tracker(config: Config) -> tuple[TrackerSnapshot | None, list[Finding]]:
    """Read `.vogon/tracker.json`. A role whose server differs from the one
    `vogon.yaml` names is dropped and reported, because it was read from a
    system the configuration does not use."""
    name = TRACKER_FILE
    try:
        data = _read_json(config, name)
        if data is None:
            return None, []
        data = _mapping(name, data, "the file")
        read_at = parse_time(data.get("read_at"))
        systems: dict[str, SystemIssues] = {}
        for role, entry in _mapping(name, data.get("systems", {}), "systems").items():
            systems[role] = _system(name, role, entry)
    except SnapshotError as e:
        return None, [e.finding]
    findings: list[Finding] = []
    for role, s in list(systems.items()):
        configured = config.system(role)
        if configured is not None and configured.server != s.server:
            findings.append(failure(
                f"{rel(name)} holds the {role} as read from server {s.server!r}, but "
                f"vogon.yaml names {configured.server!r}; read it again", path=rel(name)))
            del systems[role]
    return TrackerSnapshot(read_at, systems), findings


def _system(name: str, role: str, entry) -> SystemIssues:
    where = f"systems.{role}"
    entry = _mapping(name, entry, where)
    s = SystemIssues(role, _string(name, entry.get("server"), f"{where}.server"))
    for n, item in enumerate(_list(name, entry.get("issues"), f"{where}.issues")):
        issue = _issue(name, role, item, f"{where}.issues[{n}]")
        s.issues[issue.key] = issue
    for n, item in enumerate(_list(name, entry.get("missing"), f"{where}.missing")):
        w = f"{where}.missing[{n}]"
        item = _mapping(name, item, w)
        key = _string(name, item.get("key"), f"{w}.key")
        s.missing[key] = _string(name, item.get("reason"), f"{w}.reason", optional=True) or "not found"
    return s


def _issue(name: str, role: str, item, where: str) -> Issue:
    item = _mapping(name, item, where)
    description = item.get("description") or ""
    if not isinstance(description, str):
        raise SnapshotError(name, f"{where}.description must be a string")
    links = tuple(_string(name, k, f"{where}.links[]")
                  for k in _list(name, item.get("links"), f"{where}.links"))
    transitions = []
    for n, t in enumerate(_list(name, item.get("transitions"), f"{where}.transitions")):
        w = f"{where}.transitions[{n}]"
        t = _mapping(name, t, w)
        desc = t.get("description")
        if desc is not None and not isinstance(desc, str):
            raise SnapshotError(name, f"{w}.description must be a string")
        by = _string(name, t.get("by"), f"{w}.by", optional=True)
        transitions.append(Transition(_string(name, t.get("to"), f"{w}.to"),
                                      by.strip().lower() if by else None,
                                      _time(name, t.get("at"), f"{w}.at"), desc))
    executions = []
    for n, x in enumerate(_list(name, item.get("executions"), f"{where}.executions")):
        w = f"{where}.executions[{n}]"
        x = _mapping(name, x, w)
        executions.append(Execution(_string(name, x.get("build"), f"{w}.build"),
                                    _time(name, x.get("at"), f"{w}.at"),
                                    _string(name, x.get("outcome"), f"{w}.outcome", optional=True)))
    return Issue(role, _string(name, item.get("key"), f"{where}.key"),
                 _string(name, item.get("summary"), f"{where}.summary"), description,
                 _string(name, item.get("status"), f"{where}.status"), links,
                 tuple(transitions), tuple(executions))


# .vogon/servers.json


def load_servers(config: Config) -> tuple[dict[str, dict] | None, list[Finding]]:
    """Read `.vogon/servers.json` as {server: {"tools": set, "operations": dict}}."""
    name = SERVERS_FILE
    try:
        data = _read_json(config, name)
        if data is None:
            return None, []
        data = _mapping(name, data, "the file")
        out: dict[str, dict] = {}
        for server, entry in _mapping(name, data.get("servers", {}), "servers").items():
            where = f"servers.{server}"
            entry = _mapping(name, entry, where)
            tools = {_string(name, t, f"{where}.tools[]")
                     for t in _list(name, entry.get("tools"), f"{where}.tools")}
            ops = {str(op): _string(name, tool, f"{where}.operations.{op}")
                   for op, tool in _mapping(name, entry.get("operations", {}),
                                            f"{where}.operations").items()}
            out[server] = {"tools": tools, "operations": ops}
    except SnapshotError as e:
        return None, [e.finding]
    return out, []


def missing_operations(role: str, server: str, servers: dict[str, dict]) -> list[str]:
    """The operations VOGON needs from `role` that `server` does not provide."""
    entry = servers.get(server, {"tools": set(), "operations": {}})
    return [op for op in OPERATIONS.get(role, ())
            if entry["operations"].get(op) not in entry["tools"]]


# .vogon/branch_rules.json


@dataclass(frozen=True)
class BranchRules:
    server: str
    repository: str | None
    default_branch: str
    required_approving_reviews: int
    author_approval_excluded: bool

    def missing_rules(self) -> list[str]:
        """Each rule a merge without an independent review needs and the branch lacks."""
        missing = []
        if self.required_approving_reviews < 1:
            missing.append("at least one approving review is required")
        if not self.author_approval_excluded:
            missing.append("the author's own approval is excluded")
        return missing


def load_branch_rules(config: Config) -> tuple[BranchRules | None, list[Finding]]:
    name = BRANCH_RULES_FILE
    try:
        data = _read_json(config, name)
        if data is None:
            return None, []
        data = _mapping(name, data, "the file")
        reviews = data.get("required_approving_reviews", 0)
        if isinstance(reviews, bool) or not isinstance(reviews, int) or reviews < 0:
            raise SnapshotError(name, "required_approving_reviews must be a whole number")
        excluded = data.get("author_approval_excluded", False)
        if not isinstance(excluded, bool):
            raise SnapshotError(name, "author_approval_excluded must be true or false")
        rules = BranchRules(_string(name, data.get("server"), "server"),
                            _string(name, data.get("repository"), "repository", optional=True),
                            _string(name, data.get("default_branch"), "default_branch"),
                            reviews, excluded)
    except SnapshotError as e:
        return None, [e.finding]
    return rules, []


# The risk assessment

_ROW_RE = re.compile(r"^\s*\|(.*)\|\s*$")


def _cells(line: str) -> list[str] | None:
    m = _ROW_RE.match(line)
    return [c.strip() for c in m.group(1).split("|")] if m else None


def parse_risk_assessment(text: str) -> tuple[dict[str, str], list[str]]:
    """The levels in a risk assessment, keyed by requirement id as written, and
    the problems found reading it. The table is the first one whose header
    starts with `Requirement | Risk`."""
    lines = text.splitlines()
    levels: dict[str, str] = {}
    problems: list[str] = []
    for n, line in enumerate(lines):
        head = _cells(line)
        if head and len(head) >= 2 and [h.lower() for h in head[:2]] == ["requirement", "risk"]:
            break
    else:
        return levels, ["has no table whose first columns are 'Requirement' and 'Risk'"]
    for line in lines[n + 2:]:
        row = _cells(line)
        if row is None:
            break
        rid, level = row[0].strip("` "), (row[1] if len(row) > 1 else "").strip("` ")
        if ids.parse(rid) is None:
            problems.append(f"row {row[0]!r} does not name a requirement id")
        elif level not in GXP_RISKS:
            problems.append(f"{rid}: risk {level!r} is not one of {', '.join(GXP_RISKS)}")
        elif rid in levels:
            problems.append(f"{rid} appears twice")
        else:
            levels[rid] = level
    return levels, problems


def load_risk_assessment(config: Config) -> tuple[dict[str, str] | None, list[Finding]]:
    """The approved risk assessment's levels, keyed by requirement id."""
    p = path(config, RISK_FILE)
    if not p.is_file():
        return None, []
    try:
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {}, [failure(f"{rel(RISK_FILE)} cannot be read as UTF-8 text: {e}",
                            path=rel(RISK_FILE), requirement="REQ-GEN-9")]
    levels, problems = parse_risk_assessment(text)
    return levels, [failure(f"{rel(RISK_FILE)} {m}", path=rel(RISK_FILE), requirement="REQ-GEN-9")
                    for m in problems]
