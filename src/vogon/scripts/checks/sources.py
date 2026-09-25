"""Checks on the held documents in `<records>/sources/` and on the `source`
lists that cite them (`src/docs/dev/sources.md`)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import history
import records
import sources
from checks import rel
from config import Config
from findings import Finding, failure, notice


def naming(config: Config) -> Iterable[Finding]:
    """REQ-REC-9: every held file is named `YYYY-MM-DD_slug.ext` and sits
    directly in the sources directory, and every markdown document there has
    complete frontmatter whose `date` matches its name."""
    base = sources.directory(config.records_dir)
    for path in sources.files(config.records_dir):
        shown = rel(config, path)

        def fail(message: str, key: str | None = None) -> Finding:
            line = None
            if key is not None:
                try:
                    line = records.parse(path).line_of(key)
                except records.RecordError:
                    pass
            return failure(message, path=shown, line=line, requirement="REQ-REC-9")

        if path.parent.resolve() != base.resolve():
            yield fail(f"held documents sit directly in {rel(config, base)}, with no subdirectories")
        m = sources.NAME_RE.match(path.name)
        if m is None:
            yield fail("the name must be the document's date as YYYY-MM-DD, an underscore, and a "
                       "lowercase slug of words joined by underscores")
        elif not sources.valid_date(m["date"]):
            yield fail(f"the name starts with {m['date']}, which is not a calendar date")
        if path.suffix != ".md":
            continue
        try:
            meta = records.parse(path).meta
        except records.RecordError as e:
            yield failure(f"a markdown held document needs frontmatter: {e.message}", path=shown,
                          line=e.line, requirement="REQ-REC-9")
            continue
        for key in sources.REQUIRED:
            if key not in meta:
                yield fail(f"field '{key}' is missing")
        for key in meta:
            if key not in sources.REQUIRED + sources.OPTIONAL:
                yield fail(f"field '{key}' is not defined for a held document", str(key))
        if "title" in meta and not (isinstance(meta["title"], str) and meta["title"].strip()):
            yield fail("field 'title' must be a non-empty string", "title")
        date = meta.get("date")
        if "date" in meta:
            if not sources.valid_date(date):
                yield fail(f"field 'date' is {date!r}; it must be a date written YYYY-MM-DD", "date")
            elif m is not None and date != m["date"]:
                yield fail(f"field 'date' is {date} and the name starts with {m['date']}; the two "
                           "must agree", "date")
        if "kind" in meta and meta["kind"] not in sources.KINDS:
            yield fail(f"field 'kind' is {meta['kind']!r}; it must be one of "
                       f"{', '.join(sources.KINDS)}", "kind")
        if "authority" in meta and meta["authority"] not in sources.AUTHORITIES:
            yield fail(f"field 'authority' is {meta['authority']!r}; it must be one of "
                       f"{', '.join(sources.AUTHORITIES)}", "authority")
        if meta.get("kind") == "summary" and "derived_from" not in meta:
            yield fail("a summary needs 'derived_from' naming the document it was produced from",
                       "kind")
        for key in ("original", "derived_from"):
            if key in meta and sources.resolve(config.root, meta[key], path) is None:
                yield fail(f"field '{key}' is {meta[key]!r}, which does not resolve to a file", key)


def unchanged(config: Config) -> Iterable[Finding]:
    """REQ-REC-10: every held file's content equals the content of the commit
    that added it."""
    root = config.root
    held = sources.files(config.records_dir)
    if not held:
        return
    if not history.is_repo(root):
        yield notice("held document check skipped: the project is not a git repository",
                     requirement="REQ-REC-10")
        return
    top = history.toplevel(root)
    added: dict[str, str] = {}      # path -> the commit that last added it
    modified: dict[str, str] = {}   # path -> the last commit that changed it after that
    for c in history.changes(root, sources.directory(config.records_dir)):
        if c.status == "A":
            added[c.path] = c.commit
            modified.pop(c.path, None)
        elif c.status == "M":
            modified[c.path] = c.commit
    tracked = {p: (top / p).resolve() for p in added}
    on_disk = {p.resolve() for p in held}
    paths = [rp for rp, full in tracked.items() if full in on_disk]
    original = history.blob_ids(root, [f"{added[rp]}:{rp}" for rp in paths])
    now = history.working_blob_ids(root, [tracked[rp] for rp in paths])
    for rp in paths:
        before, after = original[f"{added[rp]}:{rp}"], now[tracked[rp]]
        if before is None or after is None or before == after:
            continue
        changed = history.short(modified[rp]) if rp in modified else None
        where = f"in {changed}" if changed else "in the working tree"
        if changed and history.blob_ids(root, [f"HEAD:{rp}"])[f"HEAD:{rp}"] != after:
            where += " and again in the working tree"
        yield failure(f"held document added in {history.short(added[rp])} was changed {where}; a "
                      "held document is never edited, a new version is filed as a new dated file",
                      path=rel(config, tracked[rp]), requirement="REQ-REC-10")


def citations(config: Config) -> Iterable[Finding]:
    """REQ-REC-11: a `source` list is ordered by authority, strongest first; a
    fact has a source stronger than informal; and a cited summary comes after
    the document it derives from."""
    found, _ = records.load_all(config.records_dir)
    cache: dict[Path, sources.Held] = {}

    def held(entry) -> tuple[Path | None, sources.Held | None]:
        path = sources.resolve(config.root, entry) if isinstance(entry, str) else None
        if path is None:
            return None, None
        if path not in cache:
            cache[path] = sources.read(path)
        return path, cache[path]

    for r in found:
        entries = r.meta.get("source")
        if not isinstance(entries, list) or not entries:
            continue
        shown, line = rel(config, r.path), r.line_of("source")

        def fail(message: str) -> Finding:
            return failure(message, path=shown, line=line, requirement="REQ-REC-11")

        resolved = [held(e) for e in entries]
        previous: tuple[str, str] | None = None   # (entry, authority) of the last entry with one
        for entry, (_, doc) in zip(entries, resolved):
            authority = doc.authority if doc else None
            if authority is None:
                continue
            if previous is not None and sources.rank(authority) < sources.rank(previous[1]):
                yield fail(f"source {entry} ({authority}) is listed after {previous[0]} "
                           f"({previous[1]}); a source list is ordered by authority, strongest first")
            previous = (entry, authority)
        if r.type == "fact":
            known = [doc.authority for _, doc in resolved if doc and doc.authority]
            if not any(a != "informal" for a in known):
                yield fail("a fact needs a source stronger than informal; every source it cites is "
                           "informal or declares no authority")
        seen: list[Path] = []
        for entry, (path, doc) in zip(entries, resolved):
            if doc is not None and doc.derived_from is not None:
                parent = sources.resolve(config.root, doc.derived_from, doc.path)
                if parent is None or parent not in seen:
                    yield fail(f"source {entry} is derived from {doc.derived_from}, which must be "
                               "listed before it")
            if path is not None:
                seen.append(path)


CHECKS = [naming, unchanged, citations]
