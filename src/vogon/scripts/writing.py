"""The writing checks: the mechanical part of `src/docs/dev/writing.md`.

`check_record` applies to one record the banned words and phrases, the
placeholder values, the question and open-item headings, the counts and the
body length limit (REQ-REC-8). `check_brand` reports a fixed string from the
brand guide in any file under the records directory other than a held
document (REQ-GEN-5). The word lists are in `writing_rules.py`.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

import records
import writing_rules as rules
from checks import relative
from config import Config
from findings import Finding, error

REQ_WRITING = "REQ-REC-8"
REQ_BRAND = "REQ-GEN-5"
# Held documents are copies of what others wrote and are never edited (sources.md).
SOURCES_DIR = "sources"


def _phrase_re(phrase: str) -> re.Pattern:
    """Whole-word, case-insensitive match; a phrase may break across lines."""
    body = r"\s+".join(re.escape(w) for w in phrase.split())
    return re.compile(rf"(?<![\w-]){body}(?![\w-])", re.IGNORECASE)


BANNED_RES = [(rule, phrase, _phrase_re(phrase))
              for rule, phrases in rules.BANNED.items() for phrase in phrases]

_NUMBER = r"\d+|(?:" + "|".join(rules.NUMBER_WORDS) + r")(?:-(?:" + "|".join(rules.NUMBER_WORDS) + r"))?"
COUNT_RE = re.compile(
    rf"(?<![\w.\-])({_NUMBER})\s+({'|'.join(rules.COUNTED_NOUNS)})(?![\w-])", re.IGNORECASE)

OPEN_ITEM_RE = re.compile(
    r"(?<![\w-])(?:" + "|".join(re.escape(x) for x in rules.OPEN_ITEM_LABELS) + r")(?![\w-])",
    re.IGNORECASE)

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
LABEL_RE = re.compile(r"^\s*\*\*(.+?)\*\*")
CODE_SPAN_RE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)


def _blank(text: str) -> str:
    """Spaces in place of every character but newlines, so offsets and lines hold."""
    return re.sub(r"[^\n]", " ", text)


def _code_lines(lines: list[str]) -> set[int]:
    """0-based indexes of the lines inside a fenced code block, fences included."""
    inside: set[int] = set()
    fence: str | None = None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[0] * len(m.group(1))
                inside.add(i)
        else:
            inside.add(i)
            if m and m.group(1).startswith(fence) and line.strip() == m.group(1):
                fence = None
    return inside


def mask_code(text: str) -> str:
    """The text with fenced code blocks and code spans blanked."""
    lines = text.split("\n")
    code = _code_lines(lines)
    lines = [_blank(l) if i in code else l for i, l in enumerate(lines)]
    return CODE_SPAN_RE.sub(lambda m: _blank(m.group(0)), "\n".join(lines))


def _label(line: str) -> str | None:
    m = LABEL_RE.match(line)
    return m.group(1).strip() if m else None


def mask_example(text: str) -> str:
    """The text with the example block blanked: from a bold `Example` label to
    the next bold label or heading outside a code block."""
    lines = text.split("\n")
    code = _code_lines(lines)
    out: list[str] = []
    in_example = False
    for i, line in enumerate(lines):
        if i not in code:
            label = _label(line)
            if label is not None:
                in_example = label.rstrip(".:").strip().lower() in rules.EXAMPLE_LABELS
            elif HEADING_RE.match(line):
                in_example = False
        out.append(_blank(line) if in_example else line)
    return "\n".join(out)


def _line(text: str, offset: int) -> int:
    """0-based line of an offset in text."""
    return text.count("\n", 0, offset)


def _banned(text: str) -> Iterable[tuple[int, str]]:
    for rule, phrase, rx in BANNED_RES:
        for m in rx.finditer(text):
            yield _line(text, m.start()), f"{rule}: {m.group(0)!r} is on the banned list"


def _counts(text: str) -> Iterable[tuple[int, str]]:
    for m in COUNT_RE.finditer(text):
        yield _line(text, m.start()), (
            f"count of something that can change: {' '.join(m.group(0).split())!r}; "
            "name them or refer to the set without sizing it")


def _headings(body: str) -> Iterable[tuple[int, str]]:
    lines = body.split("\n")
    code = _code_lines(lines)
    for i, line in enumerate(lines):
        if i in code:
            continue
        m = HEADING_RE.match(line)
        text, kind = (m.group(1), "heading") if m else (_label(line), "bold block label")
        if text is None:
            continue
        if text.rstrip().endswith("?"):
            yield i, f"{kind} phrased as a question: {text!r}"
        if OPEN_ITEM_RE.search(text):
            yield i, (f"{kind} names an open item: {text!r}; a record states what is "
                      "settled, and an open question is raised with a person")


def _placeholder(value) -> str | None:
    """The placeholder a frontmatter value is, or None. `none` is handled by the caller."""
    if value is None:
        return "null"
    if isinstance(value, str) and value.strip().casefold() in rules.PLACEHOLDERS:
        return value
    if isinstance(value, (list, dict)) and not value:
        return "an empty list" if isinstance(value, list) else "an empty mapping"
    return None


def _placeholders(key: str, value) -> Iterable[str]:
    found = _placeholder(value)
    if found is not None:
        yield found
        return
    if (isinstance(value, str) and value.strip().casefold() == rules.NONE_PLACEHOLDER
            and key not in rules.NONE_ALLOWED_IN):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _placeholders(key, item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _placeholders(key, item)


def check_record(record: records.Record, root: Path) -> list[Finding]:
    """Every mechanical writing violation in one record (REQ-REC-8)."""
    path = relative(root, record.path)
    found: list[Finding] = []

    def add(line: int | None, message: str) -> None:
        found.append(error(message, path=path, line=line, requirement=REQ_WRITING))

    for key, value in record.meta.items():
        for p in _placeholders(str(key), value):
            add(record.line_of(str(key)), f"{key}: placeholder {p!r} where the field should "
                                          "be absent")

    title = record.meta.get("title")
    if isinstance(title, str):
        title_line = record.line_of("title")
        masked = mask_code(title)
        for _, message in (*_banned(masked), *_counts(title)):
            add(title_line, f"title: {message}")
        if title.rstrip().endswith("?"):
            add(title_line, f"title phrased as a question: {title!r}")

    body = record.body
    for i, message in _banned(mask_code(body)):
        add(record.body_line + i, message)
    for i, message in _headings(body):
        add(record.body_line + i, message)
    for i, message in _counts(mask_example(body)):
        add(record.body_line + i, message)

    limit = rules.BODY_WORD_LIMITS.get(record.type or "")
    words = len(body.split())
    if limit is not None and words > limit:
        add(record.body_line, f"body is {words} words; the limit for a {record.type} is {limit}")

    return sorted(found, key=lambda f: (f.line or 0, f.message))


def _brand_re(s: str) -> re.Pattern:
    start = r"(?<!\w)" if s[0].isalnum() else ""
    end = r"(?!\w)" if s[-1].isalnum() else ""
    return re.compile(start + r"\s+".join(re.escape(w) for w in s.split()) + end)


BRAND_RES = [(s, _brand_re(s)) for s in sorted(rules.BRAND_STRINGS, key=len, reverse=True)]


def brand_findings(text: str, path: str, first_line: int = 1) -> list[Finding]:
    """A finding for each fixed string of the brand guide in the text (REQ-GEN-5)."""
    found: list[Finding] = []
    spans: list[tuple[int, int]] = []
    for s, rx in BRAND_RES:  # longest first, so a string inside another is reported once
        for m in rx.finditer(text):
            if any(a <= m.start() and m.end() <= b for a, b in spans):
                continue
            spans.append(m.span())
            found.append(error(
                f"brand fixed string {s!r}: the satirical voice belongs on the marketing "
                "page only", path=path, line=first_line + _line(text, m.start()),
                requirement=REQ_BRAND))
    return found


def _brand_files(records_dir: Path) -> list[Path]:
    if not records_dir.is_dir():
        return []
    sources = records_dir / SOURCES_DIR
    return sorted(p for p in records_dir.rglob("*")
                  if p.is_file() and sources not in p.parents)


def check_brand(config: Config) -> list[Finding]:
    """Every brand fixed string in a file under the records directory,
    held documents excepted (REQ-GEN-5)."""
    found: list[Finding] = []
    for path in _brand_files(config.records_dir):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        found.extend(brand_findings(text, relative(config.root, path)))
    return found


def check(config: Config) -> list[Finding]:
    """The writing checks over every readable record, and the brand check."""
    loaded, _ = records.load_all(config.records_dir)  # unreadable files are reported elsewhere
    found: list[Finding] = []
    for record in loaded:
        found.extend(check_record(record, config.root))
    found.extend(check_brand(config))
    return found
