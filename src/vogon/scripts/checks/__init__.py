"""The checks `vogon check` runs, grouped by what they read.

Each check is a function `check(config) -> Iterable[Finding]` and is listed in
`commands/check.py:CHECKS`. A check reads what it needs itself, so any one of
them can run alone.
"""

from __future__ import annotations

from pathlib import Path

from config import Config


def relative(root: Path, path: Path) -> str:
    """A path as findings print it: relative to `root` where possible."""
    try:
        return Path(path).resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path)


def rel(config: Config, path: Path) -> str:
    """A path relative to the project root, as findings print it."""
    return relative(config.root, path)
