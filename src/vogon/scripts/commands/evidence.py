"""`vogon evidence <build>`: compare the test manager's export for a build with
the copies filed in the document system (REQ-TRK-10).

Claude Code saves the files it exports from the test manager for the build,
the traceability report and the results, under
`.vogon/evidence/<build>/export/`, files them in the document system, reads
each filed document back, and saves the copies under
`.vogon/evidence/<build>/filed/` with the same relative paths. This command
reports:

- an exported file with no filed copy, and a filed copy with no exported file;
- a filed copy whose bytes differ from the exported file;
- a filed copy that does not name the build, in its file name or its content;
- a filed copy byte-identical to a file exported for another build under
  `.vogon/evidence/`.

The build is given as the test manager records it, normally the full commit
hash `vogon trace` recorded.
"""

from __future__ import annotations

import sys
from pathlib import Path

import snapshots
from config import Config
from findings import Finding, failure

NAME = "evidence"
HELP = "Compare the test manager's export for a build with the copies filed in the document system."

EVIDENCE_DIR = "evidence"
EXPORT = "export"
FILED = "filed"
REQ = "REQ-TRK-10"


def add_arguments(parser) -> None:
    parser.add_argument("build", help="the build the evidence is for")


def build_dir(config: Config, build: str) -> Path:
    return config.root / snapshots.STATE_DIR / EVIDENCE_DIR / build


def _files(base: Path) -> dict[str, Path]:
    if not base.is_dir():
        return {}
    return {p.relative_to(base).as_posix(): p for p in sorted(base.rglob("*")) if p.is_file()}


def run(args, config: Config) -> list[Finding]:
    build = args.build.strip()
    if not build or "/" in build or "\\" in build or build in (".", ".."):
        return [failure(f"{args.build!r} is not a build identifier", requirement=REQ)]
    base = build_dir(config, build)
    shown = f"{snapshots.STATE_DIR}/{EVIDENCE_DIR}/{build}"
    exported, filed = _files(base / EXPORT), _files(base / FILED)
    if not exported:
        return [failure(f"nothing exported for build {build}: {shown}/{EXPORT}/ is empty or absent",
                        requirement=REQ)]
    if not filed:
        return [failure(f"nothing read back from the document system for build {build}: "
                        f"{shown}/{FILED}/ is empty or absent", requirement=REQ)]
    other_builds = {}
    for d in sorted((config.root / snapshots.STATE_DIR / EVIDENCE_DIR).iterdir()):
        if d.is_dir() and d.name != build:
            for name, p in _files(d / EXPORT).items():
                other_builds.setdefault(p.read_bytes(), d.name)

    found: list[Finding] = []
    token = build.encode("utf-8")
    for name in sorted(set(exported) | set(filed)):
        where = f"{shown}/{FILED}/{name}"
        if name not in filed:
            found.append(failure(f"{name} was exported for build {build} and has no filed copy",
                                 path=f"{shown}/{EXPORT}/{name}", requirement=REQ))
            continue
        data = filed[name].read_bytes()
        same = name in exported and data == exported[name].read_bytes()
        # A copy equal to this build's export is this build's, even when another
        # build exported the same bytes.
        if not same and data in other_builds:
            found.append(failure(f"{name} is the export of build {other_builds[data]}, "
                                 f"not {build}", path=where, requirement=REQ))
            continue
        if name not in exported:
            found.append(failure(f"{name} is filed and is not in the export for build {build}",
                                 path=where, requirement=REQ))
            continue
        if not same:
            found.append(failure(f"{name} differs from the exported file", path=where,
                                 requirement=REQ))
        if build not in name and token not in data:
            found.append(failure(f"{name} does not name build {build}", path=where,
                                 requirement=REQ))
    if not found:
        sys.stdout.write(f"every filed copy for build {build} matches the export\n")
    return found
