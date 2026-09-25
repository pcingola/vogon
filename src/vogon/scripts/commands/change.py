"""`vogon change`: check that a change names the records it implements (REQ-TRC-9).

A change is the commits on HEAD that are not on the base branch, read with
`git log <base>..HEAD`, together with the pull request description. It fails
when neither names a record id nor FAKE-REQ, and for each id that resolves to no
record, naming where the id appears. A commit with no id passes when another
commit or the description names one. FAKE-REQ marks a change that implements no
record, such as a typo fix; ids named next to it must still resolve.
"""

from __future__ import annotations

import sys
from pathlib import Path

import history
import ids
import records
from config import Config
from findings import Finding, error

NAME = "change"
HELP = "Check that the commits and pull request description of a change name existing records."

DESCRIPTION = "the pull request description"


def add_arguments(parser) -> None:
    parser.add_argument("base", help="the branch the change merges into, such as origin/main")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--description", default=None, help="the pull request description")
    group.add_argument("--description-file", type=Path, default=None,
                       help="a file holding the pull request description; - reads standard input")


def _description(args) -> str:
    if args.description is not None:
        return args.description
    if args.description_file is None:
        return ""
    if str(args.description_file) == "-":
        return sys.stdin.read()
    return args.description_file.read_text(encoding="utf-8")


def check_change(config: Config, base: str, description: str) -> list[Finding]:
    commits = history.messages(config.root, f"{base}..HEAD")
    if commits is None:
        return [error(f"cannot read the commits between {base} and HEAD; the base must be a "
                      "branch or commit git can resolve, in a clone with full history",
                      requirement="REQ-TRC-9")]
    sources = [(f"commit {history.short(c)}", m) for c, m in reversed(commits)]
    sources.append((DESCRIPTION, description))

    named: dict[str, list[str]] = {}
    for where, text in sources:
        for rid in ids.find_in_text(text):
            places = named.setdefault(rid, [])
            if where not in places:
                places.append(where)
    fake_req = any(ids.names_fake_req(text) for _, text in sources)
    if not named and not fake_req:
        return [error(f"the change from {base} to HEAD names no record id and no "
                      f"{ids.FAKE_REQ} in its commit messages or {DESCRIPTION}",
                      requirement="REQ-TRC-9")]
    if not named:
        return []

    found, _ = records.load_all(config.records_dir)
    return [error(f"{rid} resolves to no record; it appears in {', '.join(places)}",
                  requirement="REQ-TRC-9")
            for rid, places in named.items() if records.find(found, rid) is None]


def run(args, config: Config) -> list[Finding]:
    try:
        description = _description(args)
    except OSError as e:
        return [error(f"cannot read {args.description_file}: {e.strerror}",
                      requirement="REQ-TRC-9")]
    return check_change(config, args.base, description)
