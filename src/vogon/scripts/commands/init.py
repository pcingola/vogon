"""`vogon init`: create the files VOGON needs in a host project.

It writes, where each is missing:

- `vogon.yaml`, holding every setting that has a default and no `systems`
  (`config.default_document()`); setup fills in the rest;
- the records directory with `modules.yaml`, `NO-REQ.md` and the directories
  for each kind of record, held sources, plans and documents;
- `.vogon/` in `.gitignore`;
- the `req` marker in the host project's pytest configuration, so a run
  without the plugin does not fail under `--strict-markers`.

The pytest configuration is the file pytest itself reads: `pytest.ini`,
`.pytest.ini`, `pyproject.toml` with `[tool.pytest.ini_options]`, `tox.ini`
with `[pytest]` or `setup.cfg` with `[tool:pytest]`, first found in that
order. With none, the section is added to `pyproject.toml`, which is created
if absent.

An existing file is changed only to add what is missing, so a second run
changes nothing. Nothing is written under `.claude/`, and no CI file is
written.
"""

from __future__ import annotations

import configparser
import re
import sys
import tomllib
from pathlib import Path

import yaml

import config as config_module
import ids
from markers import MARKER
import records
from checks import rel
from config import Config
from findings import Finding, error

NAME = "init"
HELP = "Create vogon.yaml, the records layout, the .gitignore entry and the req marker."

MARKER_LINE = "req(*ids): the requirement ids the test verifies"
GITIGNORE_ENTRY = ".vogon/"
LAYOUT = (*ids.DIRECTORIES.values(), "sources", "plans", "documents")
MODULES_TEXT = "# Each module the records use, mapped to what it covers, e.g.\n# API: The public API\n"
NO_REQ_FILE = f"{ids.NO_REQ}.md"
NO_REQ_TEXT = """# NO-REQ — Changes that need no requirement

Some changes implement no requirement: typo fixes, refactoring, formatting,
dependency updates, build and CI fixes. Such a change names `NO-REQ` in a
commit message or in the pull request description, followed by a sentence
saying what the change does. `vogon change` accepts a change that names
`NO-REQ` in place of a record id.

A change that adds or changes behaviour does not use `NO-REQ`. It names the
requirement it implements, and if there is none, the requirement is written
first.

Example: "NO-REQ — fix a typo in the installation guide."
"""

# (file, section) in the order pytest looks for its configuration.
INI_FILES = (("pytest.ini", "pytest"), (".pytest.ini", "pytest"), ("pyproject.toml", None),
             ("tox.ini", "pytest"), ("setup.cfg", "tool:pytest"))
TOML_SECTION = "tool.pytest.ini_options"


def add_arguments(parser) -> None:
    pass


def _marker_names(entries) -> set[str]:
    return {re.split(r"[:(]", str(e), maxsplit=1)[0].strip() for e in entries}


def _write(path: Path, text: str, done: list[str], config: Config) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    done.append(rel(config, path))


# The pytest configuration


def _find_pytest_config(root: Path) -> tuple[Path, str | None] | None:
    for name, section in INI_FILES:
        path = root / name
        if not path.is_file():
            continue
        if name in ("pytest.ini", ".pytest.ini"):
            return path, section
        if section is None:
            try:
                data = tomllib.loads(path.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError:
                continue
            if "ini_options" in data.get("tool", {}).get("pytest", {}):
                return path, None
            continue
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read(path, encoding="utf-8")
        except configparser.Error:
            continue
        if parser.has_section(section):
            return path, section
    return None


def _toml_markers(text: str) -> list | None:
    """The markers list in `[tool.pytest.ini_options]`, [] when the key is absent,
    or None when the text does not parse or has no such table."""
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return None
    table = data.get("tool", {}).get("pytest", {}).get("ini_options")
    return None if table is None else list(table.get("markers", []))


def _add_to_toml(text: str) -> str | None:
    """`text` with the req marker added, or None when it cannot be added by
    editing lines: the table or the markers key is written in another form."""
    lines = text.splitlines(keepends=True)
    header = next((n for n, line in enumerate(lines)
                   if re.match(r"\s*\[\s*tool\.pytest\.ini_options\s*\]", line)), None)
    entry = f'"{MARKER_LINE}"'
    if header is None:
        if _toml_markers(text) is not None:
            return None
        sep = "" if not text or text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n")
        return f"{text}{sep}[{TOML_SECTION}]\nmarkers = [{entry}]\n"
    end = next((n for n in range(header + 1, len(lines)) if lines[n].lstrip().startswith("[")
                and not re.match(r"\s*\[\s*[\"']", lines[n])), len(lines))
    for n in range(header + 1, end):
        m = re.match(r"(\s*markers\s*=\s*\[)(.*)", lines[n], re.S)
        if m:
            lines[n] = f"{m.group(1)}{entry}, {m.group(2).lstrip()}" if m.group(2).strip() \
                else f"{m.group(1)}{entry},{m.group(2)}"
            return "".join(lines)
        if re.match(r"\s*markers\s*=", lines[n]):
            return None
    lines.insert(header + 1, f"markers = [{entry}]\n")
    return "".join(lines)


def _add_to_ini(text: str, section: str) -> str | None:
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    header = next((n for n, line in enumerate(lines)
                   if line.strip() == f"[{section}]"), None)
    if header is None:
        sep = "\n" if lines else ""
        return "".join(lines) + f"{sep}[{section}]\nmarkers =\n    {MARKER_LINE}\n"
    end = next((n for n in range(header + 1, len(lines)) if lines[n].startswith("[")), len(lines))
    for n in range(header + 1, end):
        if re.match(r"markers\s*[=:]", lines[n]):
            lines.insert(n + 1, f"    {MARKER_LINE}\n")
            return "".join(lines)
    lines[header + 1:header + 1] = ["markers =\n", f"    {MARKER_LINE}\n"]
    return "".join(lines)


def _ini_markers(text: str, section: str) -> list[str] | None:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(text)
    except configparser.Error:
        return None
    if not parser.has_section(section):
        return None
    return [line for line in parser.get(section, "markers", fallback="").splitlines() if line.strip()]


def register_marker(config: Config, done: list[str]) -> list[Finding]:
    root = config.root
    found = _find_pytest_config(root)
    path, section = found if found else (root / "pyproject.toml", None)
    text = path.read_text(encoding="utf-8") if path.is_file() else ""

    def read(t: str):
        return _toml_markers(t) if section is None else _ini_markers(t, section)

    current = read(text)
    if current is not None and MARKER in _marker_names(current):
        return []
    new = _add_to_toml(text) if section is None else _add_to_ini(text, section)
    after = read(new) if new is not None else None
    if after is None or MARKER not in _marker_names(after):
        return [error(f"cannot add the {MARKER} marker to {rel(config, path)}; add "
                      f"'{MARKER_LINE}' to its markers setting by hand",
                      path=rel(config, path), requirement="REQ-TRC-1")]
    _write(path, new, done, config)
    return []


# The rest


def ignore_state(config: Config, done: list[str]) -> None:
    path = config.root / ".gitignore"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    entries = {line.strip().strip("/") for line in text.splitlines()}
    if GITIGNORE_ENTRY.strip("/") in entries:
        return
    sep = "" if not text or text.endswith("\n") else "\n"
    _write(path, f"{text}{sep}{GITIGNORE_ENTRY}\n", done, config)


def run(args, config: Config) -> list[Finding]:
    done: list[str] = []
    configuration = config.root / config_module.FILENAME
    if not configuration.exists():
        text = yaml.safe_dump(config_module.default_document(), sort_keys=False,
                              default_flow_style=None)
        _write(configuration, text, done, config)

    for name in LAYOUT:
        d = config.records_dir / name
        if not d.is_dir():
            d.mkdir(parents=True)
            done.append(rel(config, d) + "/")
    modules = config.records_dir / records.MODULES_FILE
    if not modules.exists():
        _write(modules, MODULES_TEXT, done, config)
    no_req = config.records_dir / NO_REQ_FILE
    if not no_req.exists():
        _write(no_req, NO_REQ_TEXT, done, config)

    ignore_state(config, done)
    findings = register_marker(config, done)
    for item in done:
        sys.stdout.write(f"{item}\n")
    return findings
