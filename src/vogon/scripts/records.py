"""Read record files: YAML frontmatter followed by a markdown body.

A record file lives under one of the four kind directories of the records
root (`src/docs/dev/records.md`). Frontmatter values are read as YAML with
dates kept as the strings written in the file, so a value read back is the
value written.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ids import DIRECTORIES, RecordId, parse as parse_id

KINDS = tuple(DIRECTORIES)  # requirement, fact, constraint, decision
MODULES_FILE = "modules.yaml"


class _Loader(yaml.SafeLoader):
    """SafeLoader that leaves dates and timestamps as strings."""


_Loader.yaml_implicit_resolvers = {
    ch: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(text: str):
    """Parse YAML as record frontmatter is parsed."""
    return yaml.load(text, Loader=_Loader)


class RecordError(Exception):
    """A record file that cannot be read as frontmatter and body."""

    def __init__(self, path: Path, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.path = path
        self.message = message
        self.line = line


@dataclass(frozen=True)
class Record:
    path: Path
    meta: dict            # the frontmatter
    body: str             # everything after the closing `---`
    body_line: int        # 1-based line number of the first body line

    @property
    def id(self) -> str | None:
        value = self.meta.get("id")
        return value if isinstance(value, str) else None

    @property
    def parsed_id(self) -> RecordId | None:
        return parse_id(self.id) if self.id else None

    @property
    def type(self) -> str | None:
        value = self.meta.get("type")
        return value if isinstance(value, str) else None

    @property
    def status(self) -> str | None:
        """`proposed`, `accepted`, `withdrawn`, or `superseded_by` for a superseded record."""
        value = self.meta.get("status")
        if isinstance(value, dict) and list(value) == ["superseded_by"]:
            return "superseded_by"
        return value if isinstance(value, str) else None

    @property
    def superseded_by(self) -> str | None:
        value = self.meta.get("status")
        if isinstance(value, dict):
            target = value.get("superseded_by")
            return target if isinstance(target, str) else None
        return None

    @property
    def modules(self) -> list[str]:
        value = self.meta.get("modules")
        return [m for m in value if isinstance(m, str)] if isinstance(value, list) else []

    def line_of(self, key: str) -> int | None:
        """1-based line of a top-level frontmatter key in the file, or None."""
        lines = self.path.read_text(encoding="utf-8").splitlines()
        for n, text in enumerate(lines[1:self.body_line - 2], start=2):
            if text.startswith(f"{key}:"):
                return n
        return None


def split(text: str) -> tuple[str, str, int] | None:
    """Split a file's text into (frontmatter, body, body_line), or None when the
    text does not open with a `---` line closed by another `---` line."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r\n") == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1:]), i + 2
    return None


def parse(path: Path) -> Record:
    """Read one record file. Raises RecordError when it has no frontmatter, the
    frontmatter is not valid YAML, or it is not a mapping."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise RecordError(path, f"cannot be read: {e}") from e
    parts = split(text)
    if parts is None:
        raise RecordError(path, "has no frontmatter: the file must open with a '---' line "
                                "and the frontmatter must end with another", line=1)
    front, body, body_line = parts
    try:
        meta = load_yaml(front)
    except yaml.YAMLError as e:
        mark = getattr(e, "context_mark", None) or getattr(e, "problem_mark", None)
        line = mark.line + 2 if mark is not None else 1
        raise RecordError(path, f"frontmatter is not valid YAML: {e}", line=line) from e
    if not isinstance(meta, dict):
        raise RecordError(path, "frontmatter is not a mapping", line=2)
    return Record(path, meta, body, body_line)


def kind_dir(records_dir: Path, kind: str) -> Path:
    return Path(records_dir) / DIRECTORIES[kind]


def record_files(records_dir: Path, kind: str | None = None) -> list[Path]:
    """Every `.md` file under the kind directories, or under one kind's, sorted.
    Requirements are searched recursively, since they sit in module directories."""
    kinds = KINDS if kind is None else (kind,)
    files: list[Path] = []
    for k in kinds:
        d = kind_dir(records_dir, k)
        if d.is_dir():
            files.extend(d.rglob("*.md") if k == "requirement" else d.glob("*.md"))
    return sorted(files)


def existing_keys(records_dir: Path) -> set[tuple]:
    """The id key of every record file named for an id, whether or not it parses."""
    keys = set()
    for p in record_files(records_dir):
        rid = parse_id(p.stem)
        if rid is not None:
            keys.add(rid.key)
    return keys


def load_all(records_dir: Path, kind: str | None = None) -> tuple[list[Record], list[RecordError]]:
    """Parse every record file. Files that cannot be parsed are returned as errors."""
    records: list[Record] = []
    errors: list[RecordError] = []
    for path in record_files(records_dir, kind):
        try:
            records.append(parse(path))
        except RecordError as e:
            errors.append(e)
    return records, errors


def by_id(records: list[Record]) -> dict[str, list[Record]]:
    """Records grouped by the key of their id, keyed by the id as first written.
    More than one record under a key is a duplicate id."""
    groups: dict[tuple, list[Record]] = {}
    for r in records:
        rid = r.parsed_id
        if rid is not None:
            groups.setdefault(rid.key, []).append(r)
    return {str(g[0].parsed_id): g for g in groups.values()}


def find(records: list[Record], record_id: str) -> Record | None:
    """The record with this id, compared numerically, or None."""
    target = parse_id(record_id)
    if target is None:
        return None
    for r in records:
        rid = r.parsed_id
        if rid is not None and rid.key == target.key:
            return r
    return None


def load_modules(records_dir: Path) -> dict[str, str] | None:
    """The module names declared in `modules.yaml`, mapped to their description,
    or None when the file is absent. Raises RecordError when it is not a mapping."""
    path = Path(records_dir) / MODULES_FILE
    if not path.is_file():
        return None
    try:
        data = load_yaml(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise RecordError(path, f"not valid YAML: {e}") from e
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise RecordError(path, "must map each module name to a description")
    return {str(k): "" if v is None else str(v) for k, v in data.items()}


def record_modules(record: Record) -> list[str]:
    """Every module a record names, in its id and in its `modules` frontmatter."""
    names: list[str] = []
    rid = record.parsed_id
    if rid is not None and rid.module:
        names.append(rid.module)
    for m in record.modules:
        if m not in names:
            names.append(m)
    return names
