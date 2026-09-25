"""Checks comparing the records with what Claude Code read from the external
systems and saved under `.vogon/` (formats in `snapshots.py`).

A check whose snapshot is absent reports one warning that it was skipped
(REQ-CLI-2), and only when the role it reads is configured: an unconfigured
role is already reported by the configuration check.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

import history
import ids
import issues
import records
import snapshots
from checks import rel
from config import Config
from findings import Finding, error, warning

ISSUE_ROLES = ("tracker", "test_manager")
# The approval an issue in each role's approved state stands for.
ISSUE_APPROVAL = {"tracker": "requirements", "test_manager": "test_cases"}


def _time(t: datetime) -> str:
    return t.isoformat().replace("+00:00", "Z")


def _approved_states(config: Config, role: str) -> tuple[str, ...]:
    s = config.system(role)
    return tuple(s.approved_states or ()) if s is not None else ()


def tracker_snapshot(config: Config) -> Iterable[Finding]:
    """What reading `.vogon/tracker.json` reported, once for every check that
    reads it: a warning when it is absent and the tracker or the test manager is
    configured, and an error when it is malformed or read from another server."""
    snap, found = snapshots.load_tracker(config)
    if snap is None and not found and any(config.system(r) for r in ISSUE_ROLES):
        found = [snapshots.skipped(snapshots.TRACKER_FILE,
                                   "Tracker checks")]
    return found


def _tracker(config: Config) -> snapshots.TrackerSnapshot | None:
    return snapshots.load_tracker(config)[0]


def _governing(record: records.Record) -> tuple[str, str] | None:
    """(role, key) of the issue whose approval state counts for the record."""
    tracked = record.meta.get("tracked_as")
    if not isinstance(tracked, dict):
        return None
    role = tracked.get("governs")
    key = tracked.get(role) if isinstance(role, str) else None
    return (role, key) if isinstance(key, str) and key.strip() else None


def approved_records(config: Config, snap: snapshots.TrackerSnapshot):
    """Each record whose governing issue is in an approved state, with the issue
    and the approving transition."""
    found, _ = records.load_all(config.records_dir)
    for r in found:
        gov = _governing(r)
        if gov is None or gov[0] not in snap.systems:
            continue
        issue = snap.systems[gov[0]].issues.get(gov[1])
        if issue is None:
            continue
        approval = issue.approval(_approved_states(config, gov[0]))
        if approval is not None:
            yield r, issue, approval


def edited_after_approval(config: Config) -> Iterable[Finding]:
    """REQ-TRK-2: a record, or a marked test, whose content hash differs from
    the one on the last line of its issue's description at approval."""
    snap = _tracker(config)
    if snap is None:
        return
    for r, issue, approval in approved_records(config, snap):
        approved = issues.hash_in(issue.description_at(approval))
        current = issues.record_hash(r)
        if approved != current:
            why = ("its description at approval carries no content hash"
                   if approved is None else "it has changed since")
            yield error(f"{r.id} requires re-approval: {issue.role} issue {issue.key} was "
                        f"approved at {_time(approval.at)} and {why}; nothing is written to "
                        f"that issue", path=rel(config, r.path), requirement="REQ-TRK-2")
    tests = snap.systems.get("test_manager")
    if tests is None:
        return
    states = _approved_states(config, "test_manager")
    for node in issues.test_nodes(config.root, config.test_paths):
        for issue in tests.find(node.node_id):
            approval = issue.approval(states)
            if approval is not None and issues.hash_in(issue.description_at(approval)) != node.content_hash:
                yield error(f"{node.node_id} requires re-approval: test issue {issue.key} was "
                            f"approved at {_time(approval.at)} and the test has changed since",
                            path=rel(config, node.path), line=node.line, requirement="REQ-TRK-2")


def unresolved_keys(config: Config) -> Iterable[Finding]:
    """REQ-TRK-6: a `tracked_as` key, under any role, naming no issue in the snapshot."""
    snap = _tracker(config)
    if snap is None:
        return
    recs, _ = records.load_all(config.records_dir)
    for r in recs:
        tracked = r.meta.get("tracked_as")
        if not isinstance(tracked, dict):
            continue
        for role, key in tracked.items():
            if role == "governs" or not isinstance(key, str):
                continue
            system = snap.systems.get(role)
            if system is None:
                yield warning(f"{r.id}: tracked_as.{role} {key} was not checked; "
                              f"{snapshots.rel(snapshots.TRACKER_FILE)} holds no {role}",
                              path=rel(config, r.path), requirement="REQ-TRK-6")
            elif key not in system.issues:
                reason = system.missing.get(key, f"not found in {snapshots.rel(snapshots.TRACKER_FILE)}")
                yield error(f"{r.id}: tracked_as.{role} {key} does not resolve: {reason}",
                            path=rel(config, r.path), requirement="REQ-TRK-6")


def record_authors(config: Config, record: records.Record, until: datetime) -> set[str] | None:
    """The author emails of the commits that changed the record's file up to
    `until`, or None when the history cannot tell."""
    out = history.git(config.root, "log", "HEAD", "--format=%ae%x09%aI", "--",
                       str(record.path.resolve()))
    if not out:
        return None
    authors = set()
    for line in out.splitlines():
        email, _, when = line.partition("\t")
        t = snapshots.parse_time(when)
        if t is not None and t <= until:
            authors.add(email.strip().lower())
    return authors or None


def approved_by_author(config: Config) -> Iterable[Finding]:
    """REQ-TRK-8: a record approved by one of its authors."""
    snap = _tracker(config)
    if snap is None:
        return
    for r, issue, approval in approved_records(config, snap):
        if approval.by is None:
            continue
        authors = record_authors(config, r, approval.at)
        if authors and approval.by in authors:
            yield error(f"{r.id}: {issue.role} issue {issue.key} was approved by "
                        f"{approval.by}, who is an author of the record "
                        f"(authors: {', '.join(sorted(authors))})",
                        path=rel(config, r.path), requirement="REQ-TRK-8")


def approver_holds_role(config: Config) -> Iterable[Finding]:
    """REQ-TRK-9: an approved issue whose approver holds none of the roles
    configured for that approval."""
    snap = _tracker(config)
    if snap is None:
        return
    for role, name in ISSUE_APPROVAL.items():
        system = snap.systems.get(role)
        approval = config.approvals.get(name)
        if system is None or approval is None:
            continue
        holders = {h.strip().lower() for r in approval.roles for h in config.holders(r)}
        states = _approved_states(config, role)
        for issue in system.issues.values():
            t = issue.approval(states)
            if t is None or t.by is None or t.by in holders:
                continue
            yield error(f"{role} issue {issue.key} ({issue.identity}) was approved by {t.by}, "
                        f"who does not hold the role {' or '.join(approval.roles)} configured "
                        f"for the {name!r} approval", requirement="REQ-TRK-9")


def server_operations(config: Config) -> Iterable[Finding]:
    """REQ-CLI-4: each operation VOGON needs that a configured server lacks."""
    if not config.systems:
        return
    servers, found = snapshots.load_servers(config)
    yield from found
    if servers is None:
        if not found:
            yield snapshots.skipped(snapshots.SERVERS_FILE, "Server operation check")
        return
    for role in snapshots.OPERATIONS:
        system = config.system(role)
        if system is None:
            continue
        for op in snapshots.missing_operations(role, system.server, servers):
            yield error(f"the {role} server {system.server!r} does not provide the "
                        f"operation {op!r}", path=snapshots.rel(snapshots.SERVERS_FILE),
                        requirement="REQ-CLI-4")


def branch_rules(config: Config) -> Iterable[Finding]:
    """REQ-CLI-7: a default branch that allows a merge without an independent review."""
    host = config.system("repository_host")
    if host is None:
        return
    rules, found = snapshots.load_branch_rules(config)
    yield from found
    if rules is None:
        if not found:
            yield snapshots.skipped(snapshots.BRANCH_RULES_FILE, "Branch rule check")
        return
    if rules.server != host.server:
        yield error(f"{snapshots.rel(snapshots.BRANCH_RULES_FILE)} was read from server "
                    f"{rules.server!r}, but vogon.yaml names {host.server!r}; read it again",
                    path=snapshots.rel(snapshots.BRANCH_RULES_FILE), requirement="REQ-CLI-7")
        return
    for missing in rules.missing_rules():
        yield error(f"branch {rules.default_branch!r} allows a merge without an independent "
                    f"review: missing rule: {missing}",
                    path=snapshots.rel(snapshots.BRANCH_RULES_FILE), requirement="REQ-CLI-7")


def risk_assessment(config: Config) -> Iterable[Finding]:
    """REQ-GEN-9: a requirement whose risk level is absent from the approved risk
    assessment or differs from it."""
    if config.system("document_system") is None:
        return
    levels, found = snapshots.load_risk_assessment(config)
    yield from found
    if levels is None:
        yield snapshots.skipped(snapshots.RISK_FILE, "Risk assessment check")
        return
    by_key = {ids.parse(k).key: v for k, v in levels.items()}
    recs, _ = records.load_all(config.records_dir, "requirement")
    for r in recs:
        level = r.meta.get("gxp_risk")
        rid = r.parsed_id
        if rid is None or level in (None, "none") or r.status not in ("proposed", "accepted"):
            continue
        approved = by_key.get(rid.key)
        if approved is None:
            yield error(f"{r.id} carries risk {level!r}, which the approved risk assessment "
                        f"does not list", path=rel(config, r.path), requirement="REQ-GEN-9")
        elif approved != level:
            yield error(f"{r.id} carries risk {level!r}; the approved risk assessment gives "
                        f"{approved!r}", path=rel(config, r.path), requirement="REQ-GEN-9")


def default_branch_ref(config: Config) -> str | None:
    """The ref of the default branch: the one the branch rules name, else the
    remote's HEAD. Remote-tracking refs are preferred to local branches."""
    rules, _ = snapshots.load_branch_rules(config)
    names = [rules.default_branch] if rules else []
    head = history.git(config.root, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD")
    if head and head.strip():
        names.append(head.strip().split("/", 1)[-1])
    for name in names:
        for ref in (f"refs/remotes/origin/{name}", f"refs/heads/{name}"):
            if history.git(config.root, "rev-parse", "--verify", "-q", ref) is not None:
                return ref
    return None


def first_naming_commits(config: Config, ref: str) -> dict[tuple, tuple[str, datetime]]:
    """For each record id named in a commit message reachable from `ref`, the
    earliest such commit and its committer date."""
    out = history.git(config.root, "log", ref, "--format=%x1e%H%x09%cI%n%B")
    first: dict[tuple, tuple[str, datetime]] = {}
    for block in (out or "").split("\x1e")[1:]:
        head, _, message = block.partition("\n")
        commit, _, when = head.partition("\t")
        t = snapshots.parse_time(when)
        if t is None:
            continue
        for text in ids.find_in_text(message):
            rid = ids.parse(text)
            if rid is not None and (rid.key not in first or t < first[rid.key][1]):
                first[rid.key] = (commit, t)
    return first


def approved_after_use(config: Config) -> Iterable[Finding]:
    """REQ-TRK-11: a requirement issue approved after the first commit on the
    default branch naming its record, and a test issue approved after the
    earliest result imported against it."""
    snap = _tracker(config)
    if snap is None:
        return
    approved = [(r, i, a) for r, i, a in approved_records(config, snap)
                if r.type == "requirement" and r.parsed_id is not None]
    ref = default_branch_ref(config) if approved and history.has_commits(config.root) else None
    if not approved:
        pass
    elif ref is None:
        yield warning("Approval order check for requirement issues skipped: the "
                      "default branch is not known; it is read from "
                      f"{snapshots.rel(snapshots.BRANCH_RULES_FILE)} or origin/HEAD",
                      requirement="REQ-CLI-2")
    else:
        commits = first_naming_commits(config, ref)
        for r, issue, approval in approved:
            first = commits.get(r.parsed_id.key)
            if first is not None and approval.at > first[1]:
                yield error(f"{issue.role} issue {issue.key} ({r.id}) was approved at "
                            f"{_time(approval.at)}, after commit {history.short(first[0])} "
                            f"on the default branch named it at {_time(first[1])}",
                            path=rel(config, r.path), requirement="REQ-TRK-11")
    tests = snap.systems.get("test_manager")
    if tests is None:
        return
    states = _approved_states(config, "test_manager")
    for issue in tests.issues.values():
        approval = issue.approval(states)
        if approval is None or not issue.executions:
            continue
        earliest = min(x.at for x in issue.executions)
        if approval.at > earliest:
            yield error(f"test issue {issue.key} ({issue.identity}) was approved at "
                        f"{_time(approval.at)}, after the earliest result imported against it "
                        f"at {_time(earliest)}", requirement="REQ-TRK-11")


CHECKS = [
    tracker_snapshot,
    edited_after_approval,
    unresolved_keys,
    approved_by_author,
    approver_holds_role,
    approved_after_use,
    server_operations,
    branch_rules,
    risk_assessment,
]
