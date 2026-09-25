"""Collect the requirement markers from test files without importing them.

A marker is `@pytest.mark.req("REQ-TRK-2", ...)` on a test function or a test
class, or `pytestmark = pytest.mark.req(...)` at module level, which applies
to every test in the file. The files are read with `ast` and never imported
or run (`src/docs/dev/architecture.md`).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

MARKER = "req"


@dataclass(frozen=True)
class Marker:
    path: Path
    line: int
    test: str               # `Class::function`, `function`, or `<module>` for pytestmark
    ids: tuple[str, ...]    # the string arguments, as written
    problems: tuple[str, ...] = ()  # arguments that are not string literals


def test_files(paths) -> list[Path]:
    """The pytest test files under each path: `test_*.py` and `*_test.py`."""
    found: set[Path] = set()
    for p in paths:
        p = Path(p)
        if p.is_file() and p.suffix == ".py":
            found.add(p)
        elif p.is_dir():
            found.update(f for f in p.rglob("*.py")
                         if f.name.startswith("test_") or f.name.endswith("_test.py"))
    return sorted(found)


def _is_req(node: ast.AST) -> bool:
    """`pytest.mark.req(...)` or `mark.req(...)`."""
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    if not (isinstance(f, ast.Attribute) and f.attr == MARKER):
        return False
    owner = f.value
    return (isinstance(owner, ast.Attribute) and owner.attr == "mark") or \
           (isinstance(owner, ast.Name) and owner.id == "mark")


def _marker(path: Path, test: str, call: ast.Call) -> Marker:
    ids: list[str] = []
    problems: list[str] = []
    for arg in call.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            ids.append(arg.value)
        else:
            problems.append(ast.unparse(arg))
    return Marker(path, call.lineno, test, tuple(ids), tuple(problems))


def _calls(value: ast.AST) -> list[ast.Call]:
    items = value.elts if isinstance(value, (ast.List, ast.Tuple)) else [value]
    return [v for v in items if _is_req(v)]


def collect_file(path: Path) -> list[Marker]:
    """Every marker in one file. Raises SyntaxError when the file does not parse."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    found: list[Marker] = []

    def visit(body, prefix: str) -> None:
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + node.name
                found.extend(_marker(path, name, d) for d in node.decorator_list if _is_req(d))
            elif isinstance(node, ast.ClassDef):
                name = prefix + node.name
                found.extend(_marker(path, name, d) for d in node.decorator_list if _is_req(d))
                visit(node.body, name + "::")
            elif isinstance(node, ast.Assign) and not prefix and any(
                    isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets):
                found.extend(_marker(path, "<module>", c) for c in _calls(node.value))

    visit(tree.body, "")
    return found


def collect(paths) -> tuple[list[Marker], list[tuple[Path, SyntaxError]]]:
    """Every marker in the test files under `paths`, and the files that do not
    parse or cannot be read, each with a SyntaxError saying why."""
    found: list[Marker] = []
    errors: list[tuple[Path, SyntaxError]] = []
    for f in test_files(paths):
        try:
            found.extend(collect_file(f))
        except SyntaxError as e:
            errors.append((f, e))
        except (OSError, UnicodeDecodeError) as e:
            errors.append((f, SyntaxError(f"cannot be read as UTF-8 text: {e}")))
    return found, errors
