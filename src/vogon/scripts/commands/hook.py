"""`vogon hook <name>`: run one Claude Code hook. The hook's JSON input is read
on stdin and its output printed on stdout; the exit status is always zero.
`hooks.py` holds the hooks and `hooks/hooks.json` wires them to the events.
"""

from __future__ import annotations

import sys

import hooks
from config import Config
from findings import Finding

NAME = "hook"
HELP = "Run a Claude Code hook: read its JSON input on stdin and print its output."


def add_arguments(parser) -> None:
    parser.add_argument("name", choices=sorted(hooks.HOOKS), help="the hook to run")


def run(args, config: Config) -> list[Finding]:
    try:
        text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except (OSError, ValueError, AttributeError):
        text = ""
    out = hooks.run(args.name, text)
    if out:
        sys.stdout.write(out + "\n")
    return []
