"""Command-line entry point: wires the subcommands in `commands/` together.

To add a subcommand, write `commands/<name>.py` following the contract in
`commands/__init__.py` and add one line to COMMANDS.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import config as config_module
import findings as findings_module
from commands import check, id as id_command, index
from commands import change, init, trace
from commands import hook
from commands import evidence, push

PLUGIN_JSON = Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"

# The version is kept in plugin.json only.
__version__ = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]

COMMANDS = [
    check,
    id_command,
    index,
    trace,
    change,
    init,
    hook,
    push,
    evidence,
]

DESCRIPTION = """VOGON maintains the requirements, traceability and validation evidence for a
GxP software project. Findings are failures or notices; the exit status is
non-zero only when there is a failure."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vogon", description=DESCRIPTION)
    parser.add_argument("-V", "--version", action="store_true", help="print the version and exit")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", type=Path, default=None,
                        help="the project root holding vogon.yaml (default: the current directory)")
    common.add_argument("--format", choices=("text", "json"), default="text",
                        help="how findings are printed (default: text)")
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    for module in COMMANDS:
        p = sub.add_parser(module.NAME, help=module.HELP, description=module.HELP, parents=[common])
        module.add_arguments(p)
        p.set_defaults(run=module.run)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the VOGON command-line interface and return the exit status."""
    argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:  # argparse reports usage errors and --help this way
        return int(e.code or 0)
    if args.version:
        print(f"vogon {__version__}")
        return 0
    if args.command is None:
        parser.print_help(sys.stderr)
        return 1
    root = args.root if args.root is not None else Path.cwd()
    config = config_module.load(root)
    found = list(args.run(args, config) or [])
    findings_module.write(found, args.format, sys.stdout)
    return findings_module.exit_status(found)
