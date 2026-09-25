"""`vogon push`: work out what the tracker and the test manager should hold, and
record the keys of the issues Claude Code created.

`vogon push --plan` compares the records, the marked tests and the results of
the last `vogon trace` with `.vogon/tracker.json`, prints one line per write,
and saves the same writes to `.vogon/push_plan.json`. Claude Code shows the
lines to the person and, once they confirm, applies exactly the writes in the
file (REQ-TRK-4). It writes nothing itself.

    {"writes": [
      {"action": "create", "role": "tracker", "server": "acme-tracker",
       "id": "REQ-TRK-2", "record": "vogon/requirements/TRK/REQ-TRK-2.md",
       "summary": "REQ-TRK-2 Report ...", "description": "...\\n\\nvogon-hash: sha256:..."},
      {"action": "create", "role": "test_manager", "server": "acme-tests",
       "id": "tests/test_x.py::test_y", "summary": "...", "description": "...",
       "links": ["PROJ-412"]},
      {"action": "update", "role": "tracker", "server": "acme-tracker", "key": "PROJ-412",
       "id": "REQ-TRK-2", "fields": {"description": {"from": "...", "to": "..."}}},
      {"action": "link", "role": "test_manager", "server": "acme-tests", "key": "TEST-5",
       "id": "tests/test_x.py::test_y", "to": "PROJ-412"},
      {"action": "import", "role": "test_manager", "server": "acme-tests", "key": "TEST-5",
       "id": "tests/test_x.py::test_y", "build": "<commit>", "outcome": "passed"},
      {"action": "track", "role": "tracker", "key": "PROJ-412", "id": "REQ-TRK-2",
       "record": "vogon/requirements/TRK/REQ-TRK-2.md"}
    ]}

`track` needs no call to any system: the issue exists and the record does not
name it yet. Claude Code passes it to `vogon push --record` with the keys it
created.

Rules:

- Only an `accepted` record gets an issue or a write, so a `proposed` one gets
  none (REQ-GEN-2, REQ-TRK-5). Its issue goes to the role its
  `tracked_as.governs` names, the tracker by default.
- An issue is found by the `tracked_as` key, or else by the record id or test
  node id its summary starts with, so a second run creates nothing (REQ-TRK-3).
- Nothing is written to an issue in an approved state. A record or test that
  changed since its issue was approved is reported instead (REQ-TRK-2).
- A marked test gets one test issue, linked to the issue of each requirement
  it names that has one (REQ-TRC-5). A test with no such requirement issue
  gets none yet.
- A test's result is imported against its test issue with the build
  `vogon trace` recorded, once per build. Results with no build are never
  imported (REQ-TRC-6). Parametrised items of one test function are one
  result: the first of `error`, `failed`, `passed`, `xpassed`, `xfailed`,
  `skipped` among their outcomes.

`vogon push --record FILE` reads the keys Claude Code saved after applying
the plan, as a JSON list `[{"id": "REQ-TRK-2", "role": "tracker", "key": "PROJ-412"}]`
or an object `{"created": [...]}` holding one (the plan's `track` entries have
the same fields), and writes each key into its
record's `tracked_as`, adding `governs` when the record had no `tracked_as`
(REQ-TRK-5). Entries whose id is a test node id are skipped, because a test
issue is found by its summary. A record that already names another key for
that role is reported and left unchanged.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import issues
import records
import snapshots
from checks import rel
from config import Config, not_configured
from findings import Finding, failure

NAME = "push"
HELP = "Plan the writes to the tracker and the test manager, or record the keys created."

PLAN_FILE = "push_plan.json"
OUTCOME_ORDER = ("error", "failed", "passed", "xpassed", "xfailed", "skipped")
_PARAM_RE = re.compile(r"\[.*\]$")


def add_arguments(parser) -> None:
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true",
                      help="print the creates and field changes, and save them to "
                           f".vogon/{PLAN_FILE}")
    mode.add_argument("--record", type=Path, metavar="FILE",
                      help="write the issue keys in FILE into the records' tracked_as")


def run(args, config: Config) -> list[Finding]:
    if args.record is not None:
        return record_keys(config, args.record)
    writes, found = plan(config)
    target = snapshots.path(config, PLAN_FILE)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"writes": writes}, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    if args.format == "text":
        sys.stdout.write("".join(line(w) + "\n" for w in writes) or "no changes\n")
    return found


def line(w: dict) -> str:
    """The line a write is shown to the person as."""
    a = w["action"]
    if a == "create":
        links = f", linked to {', '.join(w['links'])}" if w.get("links") else ""
        return f"create {w['role']} issue {w['summary']!r}{links}"
    if a == "update":
        return f"update {w['role']} {w['key']} ({w['id']}): " + "; ".join(
            f"{k} {v['from']!r} -> {v['to']!r}" for k, v in w["fields"].items())
    if a == "link":
        return f"link {w['role']} {w['key']} ({w['id']}) to {w['to']}"
    if a == "import":
        return f"import {w['outcome']} for {w['role']} {w['key']} ({w['id']}) build {w['build']}"
    return f"track {w['id']} as {w['role']} {w['key']}"


def plan(config: Config) -> tuple[list[dict], list[Finding]]:
    """The writes that bring the tracker and the test manager in line with the
    records, the marked tests and the last results, and what prevents others."""
    snap, found = snapshots.load_tracker(config)
    found = list(found)
    if snap is None:
        return [], found or [failure(
            f"{snapshots.rel(snapshots.TRACKER_FILE)} is absent; Claude Code reads the tracker "
            f"and the test manager into it before planning", requirement="REQ-TRK-3")]
    recs, _ = records.load_all(config.records_dir)
    writes: list[dict] = []
    for r in recs:
        writes.extend(_record_writes(config, snap, r, found))
    writes.extend(_test_writes(config, snap, recs, found))
    return writes, found


def _system(config: Config, snap, role: str, found: list[Finding], what: str):
    system = config.system(role)
    held = snap.systems.get(role) if system is not None else None
    if system is None:
        f = not_configured(role, what)
    elif held is None:
        f = failure(f"{what}: {snapshots.rel(snapshots.TRACKER_FILE)} holds no {role}; "
                    f"read it before planning", requirement="REQ-TRK-3")
    else:
        return system, held
    if f not in found:
        found.append(f)
    return None, None


def _approved_changed(issue: snapshots.Issue, states, content_hash: str):
    """(approved, changed): whether the issue is approved, and whether the
    content hash differs from the one at approval."""
    approval = issue.approval(states)
    if issue.status in states:
        at = issue.description_at(approval) if approval else issue.description
        return True, issues.hash_in(at) != content_hash
    return False, False


def _fields(issue: snapshots.Issue, summary: str, description: str) -> dict:
    fields = {}
    if issue.summary != summary:
        fields["summary"] = {"from": issue.summary, "to": summary}
    if issue.description != description:
        fields["description"] = {"from": issue.description, "to": description}
    return fields


def _record_writes(config: Config, snap, r: records.Record, found: list[Finding]) -> list[dict]:
    if r.status != "accepted" or r.parsed_id is None:
        return []  # REQ-GEN-2, REQ-TRK-5
    path = rel(config, r.path)
    tracked = r.meta.get("tracked_as") if isinstance(r.meta.get("tracked_as"), dict) else {}
    role = tracked.get("governs") or "tracker"
    system, held = _system(config, snap, role, found, f"Planning the {role} issues")
    if system is None or held is None:
        return []
    base = {"role": role, "server": system.server, "id": r.id}
    summary, description = issues.record_summary(r), issues.record_description(r)
    key = tracked.get(role)
    track: list[dict] = []
    if key:
        issue = held.issues.get(key)
        if issue is None:
            reason = held.missing.get(key, "not found in the snapshot")
            found.append(failure(f"{r.id}: tracked_as.{role} {key} does not resolve: {reason}; "
                                 f"nothing is planned for it", path=path, requirement="REQ-TRK-6"))
            return []
    else:
        matches = held.find(r.id)
        if len(matches) > 1:
            found.append(failure(f"{r.id}: {len(matches)} {role} issues carry its id "
                                 f"({', '.join(sorted(i.key for i in matches))}); nothing is planned "
                                 f"for it", path=path, requirement="REQ-TRK-3"))
            return []
        if not matches:
            return [{"action": "create", **base, "record": path, "summary": summary,
                     "description": description}]
        issue = matches[0]
        track = [{"action": "track", "role": role, "key": issue.key, "id": r.id, "record": path}]
    approved, changed = _approved_changed(issue, system.approved_states or (),
                                          issues.record_hash(r))
    if approved:
        if changed:
            found.append(failure(f"{r.id} requires re-approval: {role} issue {issue.key} is "
                                 f"approved and the record has changed since; nothing is written "
                                 f"to it", path=path, requirement="REQ-TRK-2"))
        return track
    fields = _fields(issue, summary, description)
    update = [{"action": "update", **base, "key": issue.key, "fields": fields}] if fields else []
    return update + track


def _requirement_issue(recs: list[records.Record], rid: str) -> str | None:
    r = records.find(recs, rid)
    if r is None or r.status != "accepted":
        return None
    tracked = r.meta.get("tracked_as")
    if not isinstance(tracked, dict):
        return None
    key = tracked.get(tracked.get("governs"))
    return key if isinstance(key, str) and key.strip() else None


def load_results(config: Config) -> tuple[str | None, dict[str, str], list[Finding]]:
    """The build and the outcome of each test function in `.vogon/results.json`,
    written by `vogon trace` in the format `vogon_pytest.py` documents."""
    p = snapshots.path(config, snapshots.RESULTS_FILE)
    if not p.is_file():
        return None, {}, []
    shown = rel(config, p)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        tests = data["tests"]
        build = data.get("build") or None
        outcomes: dict[str, list[str]] = {}
        for t in tests:
            outcomes.setdefault(_PARAM_RE.sub("", t["nodeid"]), []).append(t["outcome"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        return None, {}, [failure(f"{shown} cannot be read: {e}", path=shown,
                                  requirement="REQ-TRC-6")]
    combined = {n: next((o for o in OUTCOME_ORDER if o in outs), outs[0])
                for n, outs in outcomes.items()}
    if build is None and combined:
        return None, {}, [failure(f"{shown} records no build, so no result is imported; run "
                                  f"`vogon trace` on a committed working tree",
                                  path=shown, requirement="REQ-TRC-6")]
    return build, combined, []


def _test_writes(config: Config, snap, recs: list[records.Record],
                 found: list[Finding]) -> list[dict]:
    nodes = issues.test_nodes(config.root, config.test_paths)
    build, outcomes, result_findings = load_results(config)
    if not nodes and not outcomes:
        return []
    system, held = _system(config, snap, "test_manager", found, "Planning the test issues")
    if system is None or held is None:
        return []
    found.extend(result_findings)
    writes: list[dict] = []
    states = system.approved_states or ()
    for node in nodes:
        base = {"role": "test_manager", "server": system.server, "id": node.node_id}
        links = sorted({k for rid in node.requirements
                        if (k := _requirement_issue(recs, rid)) is not None})
        if not links:
            continue
        matches = held.find(node.node_id)
        if len(matches) > 1:
            found.append(failure(f"{node.node_id}: {len(matches)} test issues carry its node id "
                                 f"({', '.join(sorted(i.key for i in matches))}); nothing is planned "
                                 f"for it", path=rel(config, node.path), line=node.line,
                                 requirement="REQ-TRC-5"))
            continue
        if not matches:
            writes.append({"action": "create", **base, "summary": node.summary,
                           "description": node.description, "links": links})
            continue
        issue = matches[0]
        approved, changed = _approved_changed(issue, states, node.content_hash)
        if approved and changed:
            found.append(failure(f"{node.node_id} requires re-approval: test issue {issue.key} is "
                                 f"approved and the test has changed since; nothing is written "
                                 f"to it", path=rel(config, node.path), line=node.line,
                                 requirement="REQ-TRK-2"))
        if not approved:
            fields = _fields(issue, node.summary, node.description)
            if fields:
                writes.append({"action": "update", **base, "key": issue.key, "fields": fields})
            writes.extend({"action": "link", **base, "key": issue.key, "to": k}
                          for k in links if k not in issue.links)
        outcome = outcomes.get(node.node_id)
        if build and outcome and all(x.build != build for x in issue.executions):
            writes.append({"action": "import", **base, "key": issue.key, "build": build,
                           "outcome": outcome})
    return writes


# vogon push --record

_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")


def _yaml_scalar(value: str) -> str:
    return value if _KEY_RE.match(value) else json.dumps(value)


def _tracked_block(tracked: dict) -> list[str]:
    return ["tracked_as:"] + [f"  {role}: {_yaml_scalar(str(key))}" for role, key in tracked.items()]


def write_tracked_as(record: records.Record, tracked: dict) -> None:
    """Replace the record's `tracked_as` with `tracked`, leaving every other line
    of the file as it was. A new `tracked_as` goes at the end of the frontmatter."""
    lines = record.path.read_text(encoding="utf-8").splitlines(keepends=True)
    end = record.body_line - 2  # index of the closing `---`
    start = next((i for i in range(1, end) if lines[i].startswith("tracked_as:")), None)
    if start is None:
        start = stop = end
    else:
        stop = start + 1
        while stop < end and (lines[stop].startswith((" ", "\t")) or not lines[stop].strip()):
            stop += 1
    block = [l + "\n" for l in _tracked_block(tracked)]
    record.path.write_text("".join(lines[:start] + block + lines[stop:]), encoding="utf-8")


def record_keys(config: Config, file: Path) -> list[Finding]:
    """Write each created key in `file` into its record's `tracked_as` (REQ-TRK-5)."""
    try:
        data = json.loads(Path(file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [failure(f"{file} cannot be read: {e}", requirement="REQ-TRK-5")]
    entries = data.get("created") if isinstance(data, dict) else data
    if not isinstance(entries, list):
        return [failure(f"{file} must hold a list of {{id, role, key}} entries",
                        requirement="REQ-TRK-5")]
    recs, _ = records.load_all(config.records_dir)
    found: list[Finding] = []
    for e in entries:
        if not (isinstance(e, dict) and all(isinstance(e.get(k), str) and e[k].strip()
                                            for k in ("id", "role", "key"))):
            found.append(failure(f"{file}: entry {e!r} needs id, role and key",
                                 requirement="REQ-TRK-5"))
            continue
        if "::" in e["id"]:
            continue  # a test issue is found by its summary
        r = records.find(recs, e["id"])
        if r is None:
            found.append(failure(f"{file}: no record has the id {e['id']}", requirement="REQ-TRK-5"))
            continue
        role, key = e["role"], e["key"].strip()
        others = [o.id for o in recs if o is not r and isinstance(o.meta.get("tracked_as"), dict)
                  and o.meta["tracked_as"].get(role) == key]
        if others:
            found.append(failure(f"{e['id']}: {role} issue {key} is already named by "
                                 f"{', '.join(others)}; not recorded", path=rel(config, r.path),
                                 requirement="REQ-TRK-5"))
            continue
        tracked = r.meta.get("tracked_as")
        tracked = dict(tracked) if isinstance(tracked, dict) else {"governs": role}
        if tracked.get(role) == key:
            continue
        if tracked.get(role):
            found.append(failure(f"{e['id']}: tracked_as.{role} is already {tracked[role]}; "
                                 f"{key} is not recorded", path=rel(config, r.path),
                                 requirement="REQ-TRK-5"))
            continue
        tracked[role] = key
        write_tracked_as(r, tracked)
        r = records.parse(r.path)
        recs = [r if o.path == r.path else o for o in recs]
        sys.stdout.write(f"{e['id']} tracked_as.{role}: {key}\n")
    return found
