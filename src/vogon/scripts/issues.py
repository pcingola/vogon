"""What the issue for a record or a test holds, and how it is found again.

An issue's summary starts with the record id, or, for a test issue, with the
test's node id, and the tracker's search finds the issue by it (REQ-TRK-3,
REQ-TRC-5). The last line of the description is the content hash
(REQ-TRK-2):

    vogon-hash: sha256:<64 hex digits>

A record's content hash covers its frontmatter without `tracked_as`, and its
body, so recording the issue key does not change it. A test's covers the
source of the test function with its decorators, markers included.
"""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import markers
import records

HASH_PREFIX = "vogon-hash: "


def _sha256(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def record_hash(record: records.Record) -> str:
    meta = {str(k): v for k, v in record.meta.items() if k != "tracked_as"}
    return _sha256(json.dumps({"meta": meta, "body": record.body}, sort_keys=True,
                              ensure_ascii=False, default=str))


def hash_line(content_hash: str) -> str:
    return HASH_PREFIX + content_hash


def hash_in(description: str) -> str | None:
    """The content hash on the last non-empty line of a description, or None."""
    lines = [l.strip() for l in description.splitlines() if l.strip()]
    if lines and lines[-1].startswith(HASH_PREFIX):
        return lines[-1][len(HASH_PREFIX):].strip()
    return None


def record_summary(record: records.Record) -> str:
    title = record.meta.get("title")
    title = " ".join(str(title).split()) if title else ""
    return f"{record.id} {title}".strip()


def record_description(record: records.Record) -> str:
    return f"{record.body.strip()}\n\n{hash_line(record_hash(record))}"


@dataclass(frozen=True)
class TestNode:
    node_id: str               # `tests/test_x.py::Class::test_y`, relative to the project root
    path: Path
    line: int
    requirements: tuple[str, ...]
    content_hash: str

    @property
    def summary(self) -> str:
        return self.node_id

    @property
    def description(self) -> str:
        return f"Verifies {', '.join(self.requirements)}.\n\n{hash_line(self.content_hash)}"


def _is_test(node: ast.AST) -> bool:
    return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test")


def test_nodes(root: Path, paths) -> list[TestNode]:
    """Every test function carrying a requirement marker, directly, on its class
    or through `pytestmark`, under the test paths. Files that do not parse are
    left to the marker checks."""
    root = Path(root).resolve()
    found: list[TestNode] = []
    for f in markers.test_files(paths):
        try:
            text = f.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(f))
            marks = markers.collect_file(f)
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        lines = text.splitlines(keepends=True)
        try:
            base = f.resolve().relative_to(root).as_posix()
        except ValueError:
            base = f.as_posix()

        def ids_for(name: str) -> tuple[str, ...]:
            out: list[str] = []
            for m in marks:
                if m.test in ("<module>", name) or name.startswith(m.test + "::"):
                    out.extend(i for i in m.ids if i not in out)
            return tuple(out)

        def visit(body, prefix: str) -> None:
            for node in body:
                if _is_test(node):
                    name = prefix + node.name
                    reqs = ids_for(name)
                    if reqs:
                        first = min([node.lineno] + [d.lineno for d in node.decorator_list])
                        source = "".join(lines[first - 1:node.end_lineno])
                        found.append(TestNode(f"{base}::{name}", f, node.lineno, reqs,
                                              _sha256(source)))
                elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
                    visit(node.body, prefix + node.name + "::")

        visit(tree.body, "")
    return found
