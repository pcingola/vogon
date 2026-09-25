"""`vogon id`: mint the next unused id of a type and module and create its file.

The number is the lowest one no record of that type and module holds, in the
working tree or in the git history, whatever that record's status
(REQ-REC-7). The file is created with the frontmatter VOGON can fill in; the
title and the body are written afterwards.
"""

from __future__ import annotations

import json
import sys

import ids
import records
from checks import rel
from config import Config
from findings import Finding, failure

NAME = "id"
HELP = "Mint the next unused record id and create the record file named for it."

TYPE_NAMES = {**{p: p for p in ids.PREFIXES}, **{t: p for t, p in ids.TYPES.items()}}


def add_arguments(parser) -> None:
    parser.add_argument("type", help="the record type: REQ, FACT, CON, DEC, "
                                     "or requirement, fact, constraint, decision")
    parser.add_argument("--module", "-m", default=None,
                        help="the module the id carries, declared in modules.yaml")
    parser.add_argument("--title", default=None, help="the record's title")


def frontmatter(rid: ids.RecordId, title: str | None) -> str:
    """The frontmatter of a new record: what is known before anyone writes it."""
    lines = ["---", f"id: {rid}", f"type: {rid.type}"]
    if title:
        lines.append(f"title: {_scalar(title)}")
    if rid.module:
        lines.append(f"modules: [{rid.module}]")
    lines += ["status: proposed", "---", ""]
    return "\n".join(lines)


def _scalar(text: str) -> str:
    # A JSON string is a valid YAML scalar.
    return json.dumps(text.strip(), ensure_ascii=False)


def run(args, config: Config) -> list[Finding]:
    prefix = TYPE_NAMES.get(args.type) or TYPE_NAMES.get(args.type.upper())
    if prefix is None:
        return [failure(f"unknown record type {args.type!r}; use one of "
                        f"{', '.join(ids.PREFIXES)}", requirement="REQ-REC-7")]
    module = args.module
    if module is not None:
        if not ids.MODULE_RE.match(module):
            return [failure(f"module {module!r} is not uppercase letters and digits",
                            requirement="REQ-REC-13")]
        try:
            declared = records.load_modules(config.records_dir)
        except records.RecordError as e:
            return [failure(e.message, path=rel(config, e.path), requirement="REQ-REC-14")]
        if declared is None or module not in declared:
            where = rel(config, config.records_dir / records.MODULES_FILE)
            return [failure(f"module {module} is not declared in {where}; add it there first",
                            requirement="REQ-REC-14")]
    rid = ids.mint(config.root, config.records_dir, prefix, module)
    path = ids.record_path(config.records_dir, rid)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as f:
            f.write(frontmatter(rid, args.title))
    except FileExistsError:
        return [failure(f"{rel(config, path)} already exists", path=rel(config, path),
                        requirement="REQ-REC-7")]
    sys.stdout.write(f"{rid} {rel(config, path)}\n")
    return []
