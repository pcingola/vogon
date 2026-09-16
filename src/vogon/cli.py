"""Command-line entry point."""

from __future__ import annotations

import sys

from . import __version__

REJECTED = """
        ┌─────────────────┐
        │    REJECTED     │
        │      VOGON      │
        └─────────────────┘
"""


def main(argv: list[str] | None = None) -> int:
    """Run the VOGON command-line interface."""
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in {"-V", "--version"}:
        print(f"vogon {__version__}")
        return 0
    print(REJECTED)
    print("No change request on file. Per SOP.")
    return 1
