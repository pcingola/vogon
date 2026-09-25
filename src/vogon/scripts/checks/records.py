"""Checks on the record files: schema, identifiers, links, paths, modules,
acceptance, approval claims and id reuse (`src/docs/dev/records.md`)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import history
import ids
import records
import sources
from checks import rel
from config import Config
from findings import Finding, error, warning

COMMON_FIELDS = ("id", "type", "title", "modules", "status", "source", "reviewed_by",
                 "reviewed_on", "tags", "tracked_as", "depends_on", "references")
TYPE_FIELDS = {
    "requirement": ("verification", "gxp_risk", "acceptance_by", "acceptance_on"),
    "fact": ("as_of",),
    "constraint": ("imposed_by", "lifts_when"),
    "decision": (),
}
REQUIRED_FIELDS = ("id", "type", "title", "status")
TYPE_REQUIRED = {
    "requirement": ("verification", "gxp_risk"),
    "fact": ("as_of",),
    "constraint": ("imposed_by", "lifts_when"),
    "decision": (),
}
# A fact rests on nothing (records.md).
TYPE_FORBIDDEN = {"fact": ("depends_on",)}
# Fields given together or not at all.
PAIRS = (("reviewed_by", "reviewed_on"), ("acceptance_by", "acceptance_on"))

STATUSES = ("proposed", "accepted", "withdrawn")
LIVE = ("proposed", "accepted")
VERIFICATIONS = ("inspection", "analysis", "demonstration", "test")
GXP_RISKS = ("safety", "product quality", "data integrity", "none")
DATE_FIELDS = ("reviewed_on", "acceptance_on", "as_of")
LIST_FIELDS = ("modules", "source", "tags", "depends_on", "references")
STRING_FIELDS = ("title", "imposed_by", "lifts_when")
PERSON_FIELDS = ("reviewed_by", "acceptance_by")

# REQ-TRK-7: a frontmatter key naming an approver or a signature, and a body
# line asserting that the record was approved or signed.
# A key word starting with `approv` or `sign`: `approved_by`, `signature`,
# `sign_off`, but not `design`.
APPROVAL_KEY_RE = re.compile(r"(?:^|_)(?:approv|sign)", re.I)
APPROVAL_STATUS_RE = re.compile(r"approved|signed", re.I)
APPROVAL_LINE_RE = re.compile(
    r"^[\s>*_#-]*(?:approved|signed(?:\s+off)?)\s+(?:by|on)\b"
    r"|^[\s>*_#-]*(?:approval|signature|approver|signed)(?:\s+\w+)?[*_]*\s*:",
    re.I)

ACCEPTANCE_RE = re.compile(r"^(?:\*\*Acceptance\.?\*\*|#+\s*Acceptance\b)", re.M)


def _load(config: Config):
    return records.load_all(config.records_dir)


def _f(config: Config, message: str, record: records.Record, key: str | None = None,
       requirement: str | None = None, line: int | None = None) -> Finding:
    if line is None and key is not None:
        line = record.line_of(key)
    return error(message, path=rel(config, record.path), line=line, requirement=requirement)


def has_acceptance_block(record: records.Record) -> bool:
    return ACCEPTANCE_RE.search(record.body) is not None


def acceptance_accepted(record: records.Record) -> bool:
    """The acceptance block is present and `acceptance_by` and `acceptance_on` are set."""
    return (has_acceptance_block(record) and _present(record.meta.get("acceptance_by"))
            and sources.valid_date(record.meta.get("acceptance_on")))


def _present(value) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(isinstance(v, str) and v.strip() for v in value)
    return False


# REQ-REC-1 schema, REQ-TRK-7 approval claims


def schema(config: Config) -> Iterable[Finding]:
    """REQ-REC-1: every record file parses, and its frontmatter has the fields
    its type requires, no field its type does not define, and allowed values."""
    found, errors = _load(config)
    for e in errors:
        yield error(f"record {e.message}", path=rel(config, e.path), line=e.line,
                    requirement="REQ-REC-1")
    for r in found:
        yield from _schema(config, r)


def _schema(config: Config, r: records.Record) -> Iterable[Finding]:
    req = "REQ-REC-1"
    meta = r.meta
    # The id names the type where it can; a wrong `type` is then one finding
    # rather than one per field the wrong type does not define.
    kind = r.parsed_id.type if r.parsed_id and r.parsed_id.type else None
    if kind is None and r.type in TYPE_FIELDS:
        kind = r.type
    for key in REQUIRED_FIELDS + (TYPE_REQUIRED[kind] if kind else ()):
        if key not in meta:
            yield _f(config, f"field '{key}' is missing; a {kind or 'record'} requires it", r,
                     requirement=req)
    allowed = COMMON_FIELDS + (TYPE_FIELDS[kind] if kind else ())
    forbidden = TYPE_FORBIDDEN.get(kind, ())
    for key in meta:
        k = str(key)
        if APPROVAL_KEY_RE.search(k):
            continue  # reported by approval_claims
        if k not in allowed or k in forbidden:
            yield _f(config, f"field '{k}' is not defined for a {kind or 'record'}", r, k,
                     requirement=req)
    for a, b in PAIRS:
        if (a in meta) != (b in meta) and (a in allowed or b in allowed):
            present, absent = (a, b) if a in meta else (b, a)
            yield _f(config, f"field '{present}' is set without '{absent}'; the two are given together",
                     r, present, requirement=req)

    def bad(key: str, rule: str) -> Finding:
        return _f(config, f"field '{key}' {rule}", r, key, requirement=req)

    if "type" in meta:
        if not isinstance(meta["type"], str) or meta["type"] not in TYPE_FIELDS:
            yield bad("type", f"is {meta['type']!r}; it must be one of {', '.join(TYPE_FIELDS)}")
        elif r.parsed_id is not None and r.parsed_id.type not in (None, meta["type"]):
            yield bad("type", f"is {meta['type']!r} but the id {r.id} names a {r.parsed_id.type}")
    if "id" in meta and not isinstance(meta["id"], str):
        yield bad("id", "must be a string")
    if "status" in meta:
        status = meta["status"]
        if isinstance(status, dict):
            if list(status) != ["superseded_by"] or not isinstance(status["superseded_by"], str):
                yield bad("status", "must be a value or a mapping holding only 'superseded_by: <id>'")
        elif isinstance(status, str) and APPROVAL_STATUS_RE.fullmatch(status):
            pass  # reported by approval_claims
        elif status not in STATUSES:
            yield bad("status", f"is {status!r}; it must be one of {', '.join(STATUSES)} "
                                "or a mapping 'superseded_by: <id>'")
    for key in STRING_FIELDS:
        if key in meta and not (isinstance(meta[key], str) and meta[key].strip()
                                and "\n" not in meta[key].strip()):
            yield bad(key, "must be a non-empty single-line string")
    for key in LIST_FIELDS:
        if key in meta and not (isinstance(meta[key], list) and _present(meta[key])):
            yield bad(key, "must be a non-empty list of strings")
    if isinstance(meta.get("modules"), list):
        for m in meta["modules"]:
            if isinstance(m, str) and not ids.MODULE_RE.match(m):
                yield bad("modules", f"entry {m!r} is not uppercase letters and digits")
    rid = r.parsed_id
    if rid is not None and rid.module and _present(meta.get("modules")) \
            and isinstance(meta["modules"], list) and rid.module not in r.modules:
        yield bad("modules", f"does not list {rid.module}, the module in the id {r.id}")
    for key in PERSON_FIELDS:
        if key in meta and not _present(meta[key]):
            yield bad(key, "must name a person, as a string or a list of strings")
    for key in DATE_FIELDS:
        if key in meta and not sources.valid_date(meta[key]):
            yield bad(key, f"is {meta[key]!r}; it must be a date written YYYY-MM-DD")
    if kind == "requirement":
        if "verification" in meta and meta["verification"] not in VERIFICATIONS:
            yield bad("verification", f"is {meta['verification']!r}; it must be one of "
                                      f"{', '.join(VERIFICATIONS)}")
        if "gxp_risk" in meta and meta["gxp_risk"] not in GXP_RISKS:
            yield bad("gxp_risk", f"is {meta['gxp_risk']!r}; it must be one of {', '.join(GXP_RISKS)}")
    if "tracked_as" in meta:
        yield from _tracked_as(config, r)


def _tracked_as(config: Config, r: records.Record) -> Iterable[Finding]:
    value = r.meta["tracked_as"]
    where = dict(record=r, key="tracked_as", requirement="REQ-REC-1")
    if not isinstance(value, dict) or not value:
        yield _f(config, "field 'tracked_as' must be a mapping from system role to key", **where)
        return
    for role, key in value.items():
        if not isinstance(key, str) or not key.strip():
            yield _f(config, f"field 'tracked_as.{role}' must be a non-empty key", **where)
    governs = value.get("governs")
    if governs is None:
        yield _f(config, "field 'tracked_as' has no 'governs' entry naming the role whose "
                         "approval state counts", **where)
    elif governs == "governs" or governs not in value:
        yield _f(config, f"field 'tracked_as.governs' names {governs!r}, which has no entry "
                         "in tracked_as", **where)


def approval_claims(config: Config) -> Iterable[Finding]:
    """REQ-TRK-7: a record asserting in its frontmatter or body that it was
    approved or signed. Approval state is read from the tracker only."""
    found, _ = _load(config)
    for r in found:
        for key in r.meta:
            if APPROVAL_KEY_RE.search(str(key)):
                yield _f(config, f"field '{key}' records an approval or a signature; approval "
                                 "state is read from the tracker, never from a record",
                         r, str(key), requirement="REQ-TRK-7")
        status = r.meta.get("status")
        if isinstance(status, str) and APPROVAL_STATUS_RE.fullmatch(status):
            yield _f(config, f"status {status!r} asserts an approval; approval state is read "
                             "from the tracker, never from a record", r, "status",
                     requirement="REQ-TRK-7")
        for n, line in enumerate(r.body.splitlines(), start=r.body_line):
            if APPROVAL_LINE_RE.match(line):
                yield _f(config, f"the body asserts an approval or a signature: {line.strip()!r}; "
                                 "approval state is read from the tracker, never from a record",
                         r, line=n, requirement="REQ-TRK-7")


# REQ-REC-3 and REQ-REC-13: identifiers


def identifiers(config: Config) -> Iterable[Finding]:
    """REQ-REC-13: every id matches the grammar. REQ-REC-3: every id is held by
    one file and equals that file's name."""
    found, _ = _load(config)
    for r in found:
        if r.id is None:
            continue  # a missing or non-string id is reported by schema
        if not ids.is_valid(r.id):
            yield _f(config, f"id {r.id!r} does not match <TYPE>-<NUMBER> or "
                             "<TYPE>-<MODULE>-<NUMBER> with TYPE one of "
                             f"{', '.join(ids.PREFIXES)}", r, "id", requirement="REQ-REC-13")
        if r.id != r.path.stem:
            yield _f(config, f"id {r.id} does not match the file name {r.path.name}", r, "id",
                     requirement="REQ-REC-3")
    for rid, group in records.by_id(found).items():
        if len(group) > 1:
            names = ", ".join(rel(config, g.path) for g in group)
            for g in group:
                yield _f(config, f"id {rid} is held by {len(group)} files: {names}", g, "id",
                         requirement="REQ-REC-3")


# REQ-REC-2 and REQ-REC-4: links


def links(config: Config) -> Iterable[Finding]:
    """REQ-REC-2: every `depends_on` entry and `superseded_by` value names an
    id for which a record file exists."""
    found, _ = _load(config)
    existing = records.existing_keys(config.records_dir) | {r.parsed_id.key for r in found if r.parsed_id}
    for r in found:
        refs: list[tuple[str, str]] = []
        deps = r.meta.get("depends_on")
        if isinstance(deps, list):
            refs += [("depends_on", d) for d in deps]
        if r.superseded_by is not None:
            refs.append(("status", r.superseded_by))
        for key, target in refs:
            rid = ids.parse(target) if isinstance(target, str) else None
            if rid is None or rid.type is None or rid.key not in existing:
                field = "superseded_by" if key == "status" else key
                yield _f(config, f"{field} names {target}, for which no record file exists", r, key,
                         requirement="REQ-REC-2")


def paths(config: Config) -> Iterable[Finding]:
    """REQ-REC-4: every `source` and `references` entry resolves to a file in
    the repository."""
    found, _ = _load(config)
    for r in found:
        for key in ("source", "references"):
            value = r.meta.get(key)
            if not isinstance(value, list):
                continue
            for entry in value:
                if not isinstance(entry, str) or sources.resolve(config.root, entry) is None:
                    yield _f(config, f"{key} entry {entry!r} does not resolve to a file", r, key,
                             requirement="REQ-REC-4")


# REQ-REC-14: modules


def modules(config: Config) -> Iterable[Finding]:
    """REQ-REC-14: every module a record names is declared in modules.yaml."""
    found, _ = _load(config)
    modules_path = Path(config.records_dir) / records.MODULES_FILE
    try:
        declared = records.load_modules(config.records_dir)
    except records.RecordError as e:
        yield error(e.message, path=rel(config, e.path), requirement="REQ-REC-14")
        return
    if declared is not None:
        for name in declared:
            if not ids.MODULE_RE.match(name):
                yield error(f"module {name!r} is not uppercase letters and digits",
                            path=rel(config, modules_path), requirement="REQ-REC-14")
    for r in found:
        undeclared = [m for m in records.record_modules(r) if declared is None or m not in declared]
        for m in undeclared:
            where = f"is not declared in {rel(config, modules_path)}"
            if declared is None:
                where = f"is named, and {rel(config, modules_path)}, which declares the modules, is absent"
            key = "modules" if m in r.modules else "id"
            yield _f(config, f"module {m} {where}", r, key, requirement="REQ-REC-14")


# REQ-REC-12: acceptance


def acceptance(config: Config) -> Iterable[Finding]:
    """REQ-REC-12: a requirement carrying risk or verified by test has an
    acceptance block with `acceptance_by` and `acceptance_on`, and stays
    `proposed` until it has. On a proposed requirement the gap is a warning."""
    found, _ = _load(config)
    for r in found:
        if r.type != "requirement":
            continue
        risk = r.meta.get("gxp_risk")
        needs = (risk is not None and risk != "none") or r.meta.get("verification") == "test"
        if not needs or acceptance_accepted(r):
            continue
        missing = []
        if not has_acceptance_block(r):
            missing.append("an acceptance block")
        for key in ("acceptance_by", "acceptance_on"):
            if key not in r.meta:
                missing.append(f"'{key}'")
        if not missing:
            continue  # the values are set but malformed: reported by schema
        why = f"gxp_risk {risk!r}" if risk not in (None, "none") else "verification 'test'"
        message = f"a requirement with {why} needs {' and '.join(missing)}"
        path = rel(config, r.path)
        if r.status == "proposed":
            yield warning(message + " before it leaves proposed", path=path,
                          line=r.line_of("status"), requirement="REQ-REC-12")
        else:
            yield error(message + f"; its status is {r.status!r} and must stay proposed until "
                                    "it has them", path=path, line=r.line_of("status"),
                          requirement="REQ-REC-12")


# REQ-REC-5: id reuse and deletion, from the git history


def reuse(config: Config) -> Iterable[Finding]:
    """REQ-REC-5: an id held by a withdrawn or superseded record and now by a
    live one, and a record file deleted rather than withdrawn."""
    root, rdir = config.root, config.records_dir
    if not history.is_repo(root):
        if records.record_files(rdir):
            yield warning("id reuse check skipped: the project is not a git repository",
                          requirement="REQ-REC-5")
        return
    top = history.toplevel(root)
    if top is None or not history.has_commits(root):
        return
    found, _ = _load(config)
    current: dict[tuple, records.Record] = {}
    for r in found:
        if r.parsed_id is not None:
            current.setdefault(r.parsed_id.key, r)
    present = records.existing_keys(config.records_dir)
    kind_dirs = [records.kind_dir(rdir, k).resolve() for k in records.KINDS]

    def key_of(path: str):
        """The id key of a record file path relative to the top level, or None."""
        if not path.endswith(".md"):
            return None
        full = (top / path).resolve()
        if not any(full.is_relative_to(d) for d in kind_dirs):
            return None
        rid = ids.parse(full.stem)
        return rid.key if rid is not None else None

    def shown(path: str) -> str:
        return rel(config, top / path)

    # Replay the mainline commit by commit: which paths hold each id. A file
    # moved within one commit is a deletion and an addition in that commit and
    # is neither a deletion nor a reuse.
    held: dict[tuple, set[str]] = {}
    deleted: dict[tuple, tuple[str, str]] = {}      # key -> (commit, path) of the deletion
    retaken: dict[tuple, tuple[str, str]] = {}      # key -> (deleting commit, re-adding commit)
    by_commit: dict[str, list[history.Change]] = {}
    for c in history.changes(root, rdir):
        by_commit.setdefault(c.commit, []).append(c)
    for commit, group in by_commit.items():
        touched = {}
        for c in group:
            key = key_of(c.path)
            if key is None:
                continue
            paths_now = held.setdefault(key, set())
            touched.setdefault(key, (bool(paths_now), c.path))
            (paths_now.discard if c.status == "D" else paths_now.add)(c.path)
        for key, (before, path) in touched.items():
            after = bool(held[key])
            if before and not after:
                deleted[key] = (commit, path)
            elif not before and after and key in deleted:
                retaken[key] = (deleted.pop(key)[0], commit)

    for key, (commit, path) in deleted.items():
        stem = Path(path).stem
        if key in present:
            r = current.get(key)
            where = shown(path) if r is None else rel(config, r.path)
            yield error(f"id {stem} was held by a record deleted in {history.short(commit)} and "
                        "is taken again in the working tree; an id is never reused",
                        path=where, requirement="REQ-REC-5")
        else:
            yield error(f"record {stem} was deleted in {history.short(commit)}; a record is "
                        "withdrawn and keeps its file, never deleted",
                        path=shown(path), requirement="REQ-REC-5")
    for key, (gone, back) in retaken.items():
        r = current.get(key)
        if r is not None:
            yield _f(config, f"id {r.id} was held by a record deleted in {history.short(gone)} and "
                             f"was taken again in {history.short(back)}; an id is never reused",
                     r, "id", requirement="REQ-REC-5")
    for key, paths_now in held.items():
        if paths_now and key not in present:
            path = sorted(paths_now)[0]
            yield error(f"record {Path(path).stem} is committed and has been deleted from the "
                        "working tree; a record is withdrawn and keeps its file, never deleted",
                        path=shown(path), requirement="REQ-REC-5")

    # The first revision in which each id was withdrawn or superseded.
    retired: dict[tuple, tuple[str, str]] = {}
    for c in history.changes(root, rdir, grep=r"withdrawn|superseded_by"):
        key = key_of(c.path)
        if key is None or c.status == "D" or key in retired:
            continue
        status = _status_of(history.show(root, c.commit, c.path))
        if status in ("withdrawn", "superseded_by"):
            retired[key] = (c.commit, status)
    for key, (commit, status) in retired.items():
        r = current.get(key)
        if r is not None and r.status in LIVE and key not in retaken:
            yield _f(config, f"id {r.id} had status {status!r} in {history.short(commit)} and is "
                             f"now held by a record with status {r.status!r}; an id is never reused",
                     r, "status", requirement="REQ-REC-5")


def _status_of(text: str | None) -> str | None:
    parts = records.split(text) if text is not None else None
    if parts is None:
        return None
    try:
        meta = records.load_yaml(parts[0])
    except Exception:  # noqa: BLE001 - an unreadable old revision has no status
        return None
    if not isinstance(meta, dict):
        return None
    status = meta.get("status")
    if isinstance(status, dict) and "superseded_by" in status:
        return "superseded_by"
    return status if isinstance(status, str) else None


CHECKS = [schema, identifiers, links, paths, modules, acceptance, approval_claims, reuse]
