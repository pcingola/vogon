"""What a check reports: a failure or a notice, where, and under which requirement.

A failure makes the run exit non-zero. A notice is reported and does not change
the exit status (REQ-CLI-1).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import IO, Iterable

FAILURE = "failure"
NOTICE = "notice"
SEVERITIES = (FAILURE, NOTICE)


@dataclass(frozen=True)
class Finding:
    """One reported problem.

    `path` is relative to the project root where the finding concerns a file.
    `requirement` is the id of the requirement the check implements, if any.
    """

    severity: str
    message: str
    path: str | None = None
    line: int | None = None
    requirement: str | None = None

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}, not {self.severity!r}")
        if self.line is not None and self.path is None:
            raise ValueError("a line number needs a path")

    @property
    def is_failure(self) -> bool:
        return self.severity == FAILURE

    @property
    def location(self) -> str | None:
        """`path:line`, `path`, or None."""
        if self.path is None:
            return None
        return self.path if self.line is None else f"{self.path}:{self.line}"

    def format(self) -> str:
        """One line: `location: severity: REQ-ID: message`, omitting absent parts."""
        parts = [p for p in (self.location, self.severity, self.requirement) if p]
        return ": ".join([*parts, self.message])

    def to_dict(self) -> dict:
        return asdict(self)


def failure(message: str, path: str | None = None, line: int | None = None,
            requirement: str | None = None) -> Finding:
    return Finding(FAILURE, message, path, line, requirement)


def notice(message: str, path: str | None = None, line: int | None = None,
           requirement: str | None = None) -> Finding:
    return Finding(NOTICE, message, path, line, requirement)


def exit_status(findings: Iterable[Finding]) -> int:
    """1 if any finding is a failure, else 0 (REQ-CLI-1)."""
    return 1 if any(f.is_failure for f in findings) else 0


def write(findings: list[Finding], fmt: str, stream: IO[str]) -> None:
    """Write findings as text, one per line, or as a JSON object."""
    if fmt == "json":
        json.dump({"findings": [f.to_dict() for f in findings]}, stream, indent=2)
        stream.write("\n")
        return
    for f in findings:
        stream.write(f.format() + "\n")
