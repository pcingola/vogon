"""Checks on the requirement markers in the test files, read with `ast`."""

from __future__ import annotations

from typing import Iterable

import ids
import markers as markers_module
import records
from checks import rel
from checks.records import has_acceptance_block
from config import Config
from findings import Finding, failure


def _collect(config: Config):
    return markers_module.collect(config.test_paths)


def _test(config: Config, m: markers_module.Marker) -> str:
    return f"{rel(config, m.path)}::{m.test}"


def resolution(config: Config) -> Iterable[Finding]:
    """REQ-TRC-2, REQ-TRC-3 and REQ-TRC-8: every id a marker names resolves to
    a requirement that is proposed or accepted and whose acceptance block
    carries `acceptance_by`."""
    found, errors = _collect(config)
    for path, e in errors:
        yield failure(f"test file does not parse, so its markers cannot be read: {e.msg}",
                      path=rel(config, path), line=e.lineno, requirement="REQ-TRC-2")
    if not found:
        return
    recs, _ = records.load_all(config.records_dir)
    for m in found:
        test = _test(config, m)

        def fail(message: str, requirement: str) -> Finding:
            return failure(message, path=rel(config, m.path), line=m.line, requirement=requirement)

        for arg in m.problems:
            yield fail(f"test {test} has a marker argument {arg} that is not a string literal, so "
                       "the requirement it names cannot be read", "REQ-TRC-2")
        if not m.ids and not m.problems:
            yield fail(f"test {test} has a req marker naming no requirement", "REQ-TRC-2")
        for rid in m.ids:
            r = records.find(recs, rid) if ids.is_valid(rid) else None
            if r is None or r.type != "requirement":
                yield fail(f"test {test} names {rid}, for which no requirement record exists",
                           "REQ-TRC-2")
                continue
            if r.status == "superseded_by":
                yield fail(f"test {test} names {rid}, whose status is superseded_by "
                           f"{r.superseded_by}", "REQ-TRC-3")
            elif r.status not in ("proposed", "accepted"):
                yield fail(f"test {test} names {rid}, whose status is {r.status}", "REQ-TRC-3")
            if not has_acceptance_block(r):
                yield fail(f"test {test} names {rid}, which has no acceptance block", "REQ-TRC-8")
            elif not r.meta.get("acceptance_by"):
                yield fail(f"test {test} names {rid}, whose acceptance block carries no "
                           "acceptance_by", "REQ-TRC-8")


def coverage(config: Config) -> Iterable[Finding]:
    """REQ-TRC-4: every accepted requirement whose verification is `test` is
    named by at least one marker."""
    found, _ = _collect(config)
    named = set()
    for m in found:
        for rid in m.ids:
            parsed = ids.parse(rid)
            if parsed is not None:
                named.add(parsed.key)
    recs, _ = records.load_all(config.records_dir)
    for r in recs:
        if (r.type == "requirement" and r.status == "accepted"
                and r.meta.get("verification") == "test"
                and r.parsed_id is not None and r.parsed_id.key not in named):
            yield failure(f"requirement {r.id} is accepted and verified by test, and no test "
                          "marker names it", path=rel(config, r.path),
                          line=r.line_of("verification"), requirement="REQ-TRC-4")


CHECKS = [resolution, coverage]
