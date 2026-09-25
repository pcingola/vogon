"""Read the git history of the project the checks run on.

Every function returns an empty result, or None, when the root is not inside a
git repository or git is not installed, so a caller can tell a project with no
history from one whose history is clean by calling `is_repo` first.

History is read along the first-parent line of HEAD, with each merge compared
against its first parent. That is the sequence of trees the checked-out
branch went through, which is the history reachable from the working tree.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

# Separates the commit header from the file list in `git log` output.
_MARK = "\x1ecommit "


@dataclass(frozen=True)
class Change:
    commit: str   # full hash
    status: str   # A, M or D
    path: str     # relative to the repository top level


def git(root: Path, *args: str, stdin: str | None = None) -> str | None:
    """The standard output of `git -C root <args>`, or None when git fails or is absent."""
    try:
        return subprocess.run(["git", "-C", str(root), *args], input=stdin,
                              capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_repo(root: Path) -> bool:
    return git(root, "rev-parse", "--is-inside-work-tree") is not None


def has_commits(root: Path) -> bool:
    return git(root, "rev-parse", "--verify", "-q", "HEAD") is not None


def toplevel(root: Path) -> Path | None:
    out = git(root, "rev-parse", "--show-toplevel")
    return Path(out.strip()).resolve() if out else None


def short(commit: str) -> str:
    return commit[:10]


def changes(root: Path, pathspec: Path, grep: str | None = None) -> list[Change]:
    """Every file added, modified or deleted under `pathspec`, oldest first.

    With `grep`, only commits whose diff adds or removes a line matching that
    regular expression (`git log -G`) are listed.
    """
    if not has_commits(root):
        return []
    args = ["log", "HEAD", "--first-parent", "-m", "--reverse", "--no-renames",
            "--name-status", f"--format={_MARK}%H"]
    if grep is not None:
        args.append(f"-G{grep}")
    out = git(root, *args, "--", str(Path(pathspec).resolve()))
    if out is None:
        return []
    found: list[Change] = []
    for block in out.split(_MARK)[1:]:
        lines = block.splitlines()
        commit = lines[0].strip()
        for line in lines[1:]:
            parts = line.split("\t")
            if len(parts) == 2 and parts[0][:1] in "AMD":
                found.append(Change(commit, parts[0][:1], parts[1]))
    return found


def show(root: Path, commit: str, path: str) -> str | None:
    """The content of `path` (relative to the top level) at `commit`, or None."""
    top = toplevel(root)
    if top is None:
        return None
    return git(top, "show", f"{commit}:{path}")


def blob_ids(root: Path, specs: list[str]) -> dict[str, str | None]:
    """The blob id of each `<commit>:<path>`, or None where it does not exist."""
    if not specs:
        return {}
    top = toplevel(root)
    out = git(top, "cat-file", "--batch-check", stdin="\n".join(specs) + "\n") if top else None
    if out is None:
        return {s: None for s in specs}
    result: dict[str, str | None] = {}
    for spec, line in zip(specs, out.splitlines()):
        parts = line.split()
        result[spec] = parts[0] if len(parts) == 3 and parts[1] == "blob" else None
    return result


def working_blob_ids(root: Path, paths: list[Path]) -> dict[Path, str | None]:
    """The blob id git would store for each file as it is in the working tree."""
    if not paths:
        return {}
    top = toplevel(root)
    out = git(top, "hash-object", "--", *[str(p) for p in paths]) if top else None
    if out is None:
        return {p: None for p in paths}
    return dict(zip(paths, out.split()))


def head(root: Path) -> str | None:
    """The full hash of the commit checked out, or None with no commit."""
    out = git(root, "rev-parse", "--verify", "-q", "HEAD")
    return out.strip() if out else None


def uncommitted(root: Path, untracked: bool = True) -> list[str] | None:
    """The paths `git status` reports as changed, with untracked files unless
    `untracked` is False, or None outside a repository. Ignored files are not listed."""
    args = ["status", "--porcelain", f"--untracked-files={'all' if untracked else 'no'}"]
    out = git(root, *args)
    if out is None:
        return None
    return [line[3:] for line in out.splitlines() if line.strip()]


def messages(root: Path, rev_range: str) -> list[tuple[str, str]] | None:
    """(hash, full message) of each commit in `rev_range`, newest first, or None
    when git cannot resolve the range."""
    out = git(root, "log", "--format=%H%x1f%B%x1e", rev_range, "--")
    if out is None:
        return None
    found: list[tuple[str, str]] = []
    for entry in out.split("\x1e"):
        if "\x1f" in entry:
            commit, message = entry.split("\x1f", 1)
            found.append((commit.strip(), message.strip()))
    return found
