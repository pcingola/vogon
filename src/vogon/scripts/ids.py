"""Record identifiers: the grammar, parsing, and minting the next free id.

An id is `<TYPE>-<NUMBER>` or `<TYPE>-<MODULE>-<NUMBER>`. The number is
compared numerically, so `REQ-TRK-2` and `REQ-TRK-02` are the same id. An id
is never reused: an id held by any record file in the working tree or in the
git history counts as used, whatever that record's status.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import history

# Type prefix -> record type, and record type -> directory under the records root.
PREFIXES = {"REQ": "requirement", "FACT": "fact", "CON": "constraint", "DEC": "decision"}
TYPES = {v: k for k, v in PREFIXES.items()}
DIRECTORIES = {"requirement": "requirements", "fact": "facts",
               "constraint": "constraints", "decision": "decisions"}

ID_RE = re.compile(r"^(?P<prefix>[A-Z]{3,})(?:-(?P<module>[A-Z0-9]+))?-(?P<number>[0-9]+)$")
# An id of one of the four types inside free text, such as a commit message.
ID_IN_TEXT_RE = re.compile(r"\b(?:REQ|FACT|CON|DEC)(?:-[A-Z0-9]+)?-[0-9]+\b")
MODULE_RE = re.compile(r"^[A-Z0-9]+$")

# Width new ids are padded to in a namespace that has no id yet.
UNMODULED_WIDTH = 3


@dataclass(frozen=True)
class RecordId:
    prefix: str
    module: str | None
    number: str  # as written, with any leading zeros

    @property
    def value(self) -> int:
        return int(self.number)

    @property
    def type(self) -> str | None:
        """The record type the prefix names, or None for an unknown prefix."""
        return PREFIXES.get(self.prefix)

    @property
    def namespace(self) -> tuple[str, str | None]:
        return (self.prefix, self.module)

    @property
    def key(self) -> tuple[str, str | None, int]:
        """Identity: two ids with the same key are the same id."""
        return (self.prefix, self.module, self.value)

    def __str__(self) -> str:
        parts = [self.prefix, self.module, self.number] if self.module else [self.prefix, self.number]
        return "-".join(parts)


def parse(text: str) -> RecordId | None:
    """Parse an id matching the grammar, or return None. The prefix is not checked
    against the four types; `RecordId.type` is None for an unknown one."""
    m = ID_RE.match(text) if isinstance(text, str) else None
    if not m:
        return None
    return RecordId(m["prefix"], m["module"], m["number"])


def is_valid(text: str) -> bool:
    """The id matches the grammar and names one of the four record types (REQ-REC-13)."""
    rid = parse(text)
    return rid is not None and rid.type is not None


def find_in_text(text: str) -> list[str]:
    """Every id of the four types appearing in `text`, in order of appearance."""
    return ID_IN_TEXT_RE.findall(text)


def history_ids(root: Path, records_dir: Path) -> set[str]:
    """The stems of every `.md` file that has existed under `records_dir` in any
    commit of the repository at `root`. Empty when `root` is not a git repository."""
    try:
        rel = records_dir.resolve().relative_to(root.resolve())
    except ValueError:
        rel = records_dir
    out = history.git(root, "log", "--all", "--no-renames", "--name-only", "--pretty=format:",
                      "--", str(rel))
    if out is None:
        return set()
    return {Path(line).stem for line in out.splitlines() if line.endswith(".md")}


def next_number(namespace: tuple[str, str | None], used: Iterable[str]) -> str:
    """The lowest number not used in the namespace, as a string padded to the
    width the namespace already uses (REQ-REC-7)."""
    taken: set[int] = set()
    widths: list[int] = []
    for text in used:
        rid = parse(text)
        if rid is None or rid.namespace != namespace:
            continue
        taken.add(rid.value)
        if rid.number.startswith("0"):
            widths.append(len(rid.number))
    n = 1
    while n in taken:
        n += 1
    if widths:
        width = max(widths)
    elif not taken and namespace[1] is None:
        width = UNMODULED_WIDTH
    else:
        width = 0
    return str(n).zfill(width)


def next_id(prefix: str, module: str | None, used: Iterable[str]) -> RecordId:
    """The next free id of a type and module, given every id already used."""
    if prefix not in PREFIXES:
        raise ValueError(f"unknown record type prefix {prefix!r}")
    if module is not None and not MODULE_RE.match(module):
        raise ValueError(f"module {module!r} is not uppercase letters and digits")
    return RecordId(prefix, module, next_number((prefix, module), used))


def mint(root: Path, records_dir: Path, prefix: str, module: str | None) -> RecordId:
    """The next free id, counting the record files in the working tree and in the
    git history as used. Does not create the file."""
    used = {p.stem for p in records_dir.rglob("*.md")} | history_ids(root, records_dir)
    return next_id(prefix, module, used)


def record_path(records_dir: Path, rid: RecordId) -> Path:
    """Where the record file for an id belongs."""
    kind = rid.type
    if kind is None:
        raise ValueError(f"{rid} does not name a record type")
    base = records_dir / DIRECTORIES[kind]
    if kind == "requirement" and rid.module:
        base = base / rid.module
    return base / f"{rid}.md"
