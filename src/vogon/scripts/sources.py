"""Read the held documents in `<records>/sources/` (`src/docs/dev/sources.md`).

A held document is named `YYYY-MM-DD_slug.ext`. A markdown document carries
frontmatter with `title`, `date`, `kind` and `authority`, and optionally
`original`, `derived_from`, `participants` and `retrieved_from`.
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from pathlib import Path

import records

DIRECTORY = "sources"

KINDS = ("transcript", "summary", "procedure", "standard", "regulation", "deck", "email", "note")
# Strongest first. A `source` list is ordered by this.
AUTHORITIES = ("regulation", "standard", "procedure", "project", "informal")
REQUIRED = ("title", "date", "kind", "authority")
OPTIONAL = ("original", "derived_from", "participants", "retrieved_from")

# Date, underscore, a lowercase slug of words joined by underscores, then one or
# more extensions (`.md`, `.pdf`, `.summary.md`).
NAME_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})_(?P<slug>[a-z0-9]+(?:_[a-z0-9]+)*)"
                     r"(?P<ext>(?:\.[A-Za-z0-9]+)+)$")


def directory(records_dir: Path) -> Path:
    return Path(records_dir) / DIRECTORY


def valid_date(text) -> bool:
    if not isinstance(text, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return False
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def rank(authority: str | None) -> int | None:
    """0 for the strongest authority, None for an unknown one."""
    return AUTHORITIES.index(authority) if authority in AUTHORITIES else None


@dataclass(frozen=True)
class Held:
    path: Path
    meta: dict | None   # None for a file that is not markdown or has no readable frontmatter

    @property
    def authority(self) -> str | None:
        value = (self.meta or {}).get("authority")
        return value if value in AUTHORITIES else None

    @property
    def derived_from(self) -> str | None:
        value = (self.meta or {}).get("derived_from")
        return value if isinstance(value, str) else None


def files(records_dir: Path) -> list[Path]:
    """Every file under the sources directory, at any depth, except dotfiles."""
    d = directory(records_dir)
    if not d.is_dir():
        return []
    return sorted(p for p in d.rglob("*")
                  if p.is_file() and not any(part.startswith(".") for part in p.relative_to(d).parts))


def read(path: Path) -> Held:
    """Read a held document's frontmatter where it is markdown and has one."""
    if path.suffix != ".md":
        return Held(path, None)
    try:
        return Held(path, records.parse(path).meta)
    except records.RecordError:
        return Held(path, None)


def resolve(root: Path, value: str, relative_to: Path | None = None) -> Path | None:
    """The file a path written in a record or held document names, or None.

    A path resolves from the project root. A bare name written in a held
    document also resolves beside that document.
    """
    if not isinstance(value, str) or not value.strip():
        return None
    candidates = [Path(root) / value]
    if relative_to is not None:
        candidates.append(Path(relative_to).parent / value)
    for c in candidates:
        if c.is_file():
            return c.resolve()
    return None
