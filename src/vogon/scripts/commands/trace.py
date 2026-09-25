"""`vogon trace`: run the tests and record the outcome of each marked test,
with the build it ran on (REQ-TRC-1, REQ-TRC-6).

It runs the configured `test_command` with `-p vogon_pytest`, the plugin's
`scripts/pytest_plugin/` directory on `PYTHONPATH`, and any further arguments
given. That directory holds `vogon_pytest.py` alone, because every module on
`PYTHONPATH` is importable by the host project's tests and would shadow a
module of the same name installed in the host's environment. The results go to
`.vogon/results.json` in the format `vogon_pytest.py` documents.

The test command runs in the host project's environment, not in the one `uv`
made for the scripts. When the scripts run under `uv run`, which puts that
environment's `bin` first on `PATH` and sets `VIRTUAL_ENV` to it, both are
removed before the test command starts, so `python` in `test_command` is the
host's `python`.

The build is the output of `git rev-parse HEAD`. It is recorded only when the
working tree has no uncommitted change, tracked or untracked, before the run,
and the commit and the tracked files are the same after it. Otherwise the
results are written with no build, so they cannot be imported, and a notice
names the reason.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import history
import snapshots
from checks import rel
from config import Config
from findings import Finding, failure, notice

NAME = "trace"
HELP = "Run the tests and record each marked test's outcome with the build it ran on."

# Holds vogon_pytest.py and nothing else; the only directory put on PYTHONPATH.
PLUGIN_DIR = Path(__file__).resolve().parent.parent / "pytest_plugin"
# The environment variables vogon_pytest.py reads. It is not imported here,
# because it imports pytest, which the scripts' own environment does not hold.
RESULTS_ENV = "VOGON_RESULTS"
BUILD_ENV = "VOGON_BUILD"


def host_environment(environ: dict, prefix: str) -> dict:
    """The environment for the test command: `environ` without the scripts'
    own environment at `prefix`, when `uv run` activated it for this run."""
    env = dict(environ)
    active = env.get("VIRTUAL_ENV")
    if "UV_RUN_RECURSION_DEPTH" not in env or not active \
            or os.path.realpath(active) != os.path.realpath(prefix):
        return env
    del env["VIRTUAL_ENV"]
    own = {os.path.realpath(os.path.join(prefix, d)) for d in ("bin", "Scripts")}
    path = [p for p in env.get("PATH", "").split(os.pathsep)
            if p and os.path.realpath(p) not in own]
    env["PATH"] = os.pathsep.join(path)
    return env


def add_arguments(parser) -> None:
    parser.add_argument("test_args", nargs=argparse.REMAINDER,
                        help="further arguments for the test command, after --")


def results_path(config: Config) -> Path:
    return snapshots.path(config, snapshots.RESULTS_FILE)


def build_before(root: Path) -> tuple[str | None, str | None]:
    """The commit to record as the build, or None and the reason there is none."""
    if not history.is_repo(root):
        return None, "the project is not a git repository"
    commit = history.head(root)
    if commit is None:
        return None, "the repository has no commit"
    changed = history.uncommitted(root)
    if changed:
        return None, f"the working tree has uncommitted changes: {', '.join(changed)}"
    return commit, None


def _run(command: list[str], cwd: Path, env: dict) -> int:
    """Run the test command with its output on this process's standard error,
    so standard output holds only the findings."""
    try:
        err = sys.stderr.fileno()
    except (AttributeError, io.UnsupportedOperation):
        err = None
    if err is not None:
        return subprocess.run(command, cwd=cwd, env=env, stdout=err, stderr=err).returncode
    done = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    sys.stderr.write(done.stdout + done.stderr)
    return done.returncode


def run(args, config: Config) -> list[Finding]:
    root = config.root
    out = results_path(config)
    shown = rel(config, out)
    build, reason = build_before(root)

    extra = list(args.test_args)
    if extra[:1] == ["--"]:
        extra = extra[1:]
    command = [*config.test_command, "-p", "vogon_pytest", *extra]
    env = host_environment(dict(os.environ), sys.prefix)
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(PLUGIN_DIR), env.get("PYTHONPATH")) if p)
    env[RESULTS_ENV] = str(out)
    env[BUILD_ENV] = build or ""

    if out.exists():
        out.unlink()
    try:
        status = _run(command, root, env)
    except OSError as e:
        return [failure(f"test command {' '.join(command)!r} could not be run: {e}",
                        requirement="REQ-TRC-1")]

    if not out.is_file():
        return [failure(f"test command {' '.join(command)!r} exited with status {status} "
                        f"and wrote no {shown}", requirement="REQ-TRC-1")]

    if build is not None:
        after = history.head(root)
        changed = history.uncommitted(root, untracked=False)
        if after != build or changed:
            reason = ("the commit or a tracked file changed during the run: "
                      + ", ".join(changed or [f"HEAD is now {after}"]))
            build = None
            document = json.loads(out.read_text(encoding="utf-8"))
            document["build"] = None
            out.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    found: list[Finding] = []
    if build is None:
        found.append(notice(f"no build recorded in {shown}, so these results cannot be "
                            f"imported: {reason}", path=shown, requirement="REQ-TRC-6"))
    if status != 0:
        found.append(failure(f"test command exited with status {status}", path=shown,
                             requirement="REQ-TRC-1"))
    sys.stdout.write(f"{shown} build {build or 'none'}\n")
    return found
