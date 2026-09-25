import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from cli import main
from commands import trace as trace_command

# A host project: pytest runs under --strict-markers and does not declare the req marker,
# so the run passes only if vogon_pytest registers it.
PYTEST_INI = "[pytest]\naddopts = --strict-markers\n"

VOGON_YAML = json.dumps({"test_command": [sys.executable, "-m", "pytest", "-q"]})

TESTS = '''
import pytest

pytestmark = pytest.mark.req("REQ-TRC-4")


def test_unmarked_module_level_only():
    pass


@pytest.mark.req("REQ-TRC-1", "REQ-TRC-6")
def test_passes():
    assert 1 + 1 == 2


@pytest.mark.req("REQ-TRC-1")
def test_fails():
    assert 1 == 2


@pytest.mark.req("REQ-TRC-2")
@pytest.mark.skip(reason="not yet")
def test_skipped():
    pass


@pytest.fixture
def broken():
    raise RuntimeError("setup")


@pytest.mark.req("REQ-TRC-3")
def test_setup_error(broken):
    pass


@pytest.mark.req("REQ-TRC-8")
@pytest.mark.xfail(reason="known")
def test_expected_failure():
    assert False


@pytest.mark.req("REQ-TRC-9")
class TestGroup:
    @pytest.mark.req("REQ-TRC-5")
    @pytest.mark.parametrize("n", [1, 2])
    def test_param(self, n):
        assert n == 1
'''

PLAIN = "def test_plain():\n    pass\n"


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def project(root: Path, tests: str = TESTS, commit: bool = True) -> None:
    (root / "tests").mkdir()
    (root / "tests" / "test_host.py").write_text(tests)
    (root / "tests" / "test_plain.py").write_text(PLAIN)
    (root / "pytest.ini").write_text(PYTEST_INI)
    (root / "vogon.yaml").write_text(VOGON_YAML)
    (root / ".gitignore").write_text(".vogon/\n")
    if commit:
        git(root, "init", "-q")
        git(root, "config", "user.email", "alice@example.com")
        git(root, "config", "user.name", "Alice")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "tests")


def trace(root: Path, capsys, *extra: str) -> tuple[int, dict, str]:
    status = main(["trace", "--root", str(root), *extra])
    out = capsys.readouterr().out
    return status, json.loads((root / ".vogon" / "results.json").read_text()), out


@pytest.mark.req("REQ-TRC-1")
def test_every_marked_test_is_recorded_with_its_ids_and_outcome(tmp_path, capsys):
    project(tmp_path)
    status, results, _ = trace(tmp_path, capsys)
    assert results["format"] == 1
    assert {t["nodeid"]: (t["requirements"], t["outcome"]) for t in results["tests"]} == {
        "tests/test_host.py::test_unmarked_module_level_only": (["REQ-TRC-4"], "passed"),
        "tests/test_host.py::test_passes": (["REQ-TRC-4", "REQ-TRC-1", "REQ-TRC-6"], "passed"),
        "tests/test_host.py::test_fails": (["REQ-TRC-4", "REQ-TRC-1"], "failed"),
        "tests/test_host.py::test_skipped": (["REQ-TRC-4", "REQ-TRC-2"], "skipped"),
        "tests/test_host.py::test_setup_error": (["REQ-TRC-4", "REQ-TRC-3"], "error"),
        "tests/test_host.py::test_expected_failure": (["REQ-TRC-4", "REQ-TRC-8"], "xfailed"),
        "tests/test_host.py::TestGroup::test_param[1]":
            (["REQ-TRC-4", "REQ-TRC-9", "REQ-TRC-5"], "passed"),
        "tests/test_host.py::TestGroup::test_param[2]":
            (["REQ-TRC-4", "REQ-TRC-9", "REQ-TRC-5"], "failed"),
    }
    # Failing tests make the run fail.
    assert status == 1


@pytest.mark.req("REQ-TRC-1")
def test_unmarked_tests_are_not_recorded_and_a_passing_run_exits_zero(tmp_path, capsys):
    project(tmp_path)
    status, results, _ = trace(tmp_path, capsys, "--", "tests/test_plain.py")
    assert results["tests"] == []
    assert status == 0


@pytest.mark.req("REQ-TRC-6")
def test_a_clean_working_tree_records_head_as_the_build(tmp_path, capsys):
    project(tmp_path)
    head = git(tmp_path, "rev-parse", "HEAD")
    status, results, out = trace(tmp_path, capsys, "--", "-k", "test_passes")
    assert status == 0
    assert results["build"] == head
    assert out.strip() == f".vogon/results.json build {head}"


@pytest.mark.req("REQ-TRC-6")
@pytest.mark.parametrize("change", ["modified", "untracked", "staged"])
def test_a_run_with_uncommitted_changes_records_no_build(tmp_path, capsys, change):
    project(tmp_path)
    if change == "modified":
        (tmp_path / "tests" / "test_plain.py").write_text(PLAIN + "\n# edited\n")
    elif change == "untracked":
        (tmp_path / "tests" / "test_new.py").write_text(PLAIN)
    else:
        (tmp_path / "notes.txt").write_text("x\n")
        git(tmp_path, "add", "notes.txt")
    status, results, out = trace(tmp_path, capsys, "--", "-k", "test_passes")
    assert results["build"] is None
    assert [t["outcome"] for t in results["tests"]] == ["passed"]
    assert status == 0
    assert "build none" in out
    assert re.search(r"^WARNING: \S+: no build recorded", out, re.M) and "uncommitted" in out


@pytest.mark.req("REQ-TRC-6")
def test_a_run_that_changes_a_tracked_file_records_no_build(tmp_path, capsys):
    tests = ('import pathlib\nimport pytest\n\n\n@pytest.mark.req("REQ-TRC-6")\n'
             'def test_edits():\n    pathlib.Path("pytest.ini").write_text("[pytest]\\n")\n')
    project(tmp_path, tests=tests)
    status, results, out = trace(tmp_path, capsys)
    assert results["build"] is None
    assert "changed during the run" in out and "pytest.ini" in out


@pytest.mark.req("REQ-TRC-6")
def test_a_project_outside_git_records_no_build(tmp_path, capsys):
    project(tmp_path, commit=False)
    status, results, out = trace(tmp_path, capsys, "--", "-k", "test_passes")
    assert results["build"] is None
    assert "not a git repository" in out


# A host whose environment installs its own top-level `config` and `records`
# modules. site-packages follows PYTHONPATH on sys.path, so the runner appends
# the install directory to the end of sys.path, where site-packages sits.
HOST_RUNNER = '''
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "site-packages"))

import pytest

sys.exit(pytest.main(sys.argv[1:]))
'''

HOST_TESTS = '''
import pytest

import config
import records


@pytest.mark.req("REQ-TRC-1")
def test_host_modules_are_imported():
    assert config.OWNER == "host"
    assert records.OWNER == "host"
'''


@pytest.mark.req("REQ-TRC-1")
def test_the_plugin_does_not_shadow_modules_installed_in_the_host(tmp_path, capsys):
    project(tmp_path, tests=HOST_TESTS, commit=False)
    installed = tmp_path / "site-packages"
    installed.mkdir()
    for name in ("config", "records"):
        (installed / f"{name}.py").write_text('OWNER = "host"\n')
    (tmp_path / "run_tests.py").write_text(HOST_RUNNER)
    (tmp_path / "vogon.yaml").write_text(
        json.dumps({"test_command": [sys.executable, "run_tests.py", "-q"]}))
    status, results, _ = trace(tmp_path, capsys, "--", "tests/test_host.py")
    assert [(t["nodeid"], t["outcome"]) for t in results["tests"]] == [
        ("tests/test_host.py::test_host_modules_are_imported", "passed")]
    assert status == 0


ENTRY = Path(__file__).resolve().parent.parent / "src" / "vogon" / "scripts" / "vogon"


@pytest.mark.req("REQ-TRC-1")
def test_under_uv_the_test_command_runs_in_the_host_environment(tmp_path):
    """The entry script runs under `uv run --script`, and `python` in the test
    command is the host's `python`, not the one of the scripts' environment."""
    project(tmp_path)
    (tmp_path / "vogon.yaml").write_text(json.dumps({"test_command": ["python", "-m", "pytest", "-q"]}))
    git(tmp_path, "commit", "-q", "-am", "python from PATH")
    host_bin = tmp_path.parent / f"{tmp_path.name}-bin"
    host_bin.mkdir()
    (host_bin / "python").write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
    (host_bin / "python").chmod(0o755)
    env = {k: v for k, v in os.environ.items() if k not in ("VIRTUAL_ENV", "UV_RUN_RECURSION_DEPTH")}
    env["PATH"] = os.pathsep.join([str(host_bin), env.get("PATH", "")])
    done = subprocess.run(["uv", "run", "--script", str(ENTRY), "trace"], cwd=tmp_path, env=env,
                          capture_output=True, text=True)
    assert "No module named pytest" not in done.stderr
    results = json.loads((tmp_path / ".vogon" / "results.json").read_text())
    assert results["build"] == git(tmp_path, "rev-parse", "HEAD")
    assert results["tests"]


@pytest.mark.req("REQ-TRC-1")
def test_the_uv_environment_is_removed_from_the_test_command_environment(tmp_path):
    prefix = tmp_path / "env"
    (prefix / "bin").mkdir(parents=True)
    environ = {"PATH": os.pathsep.join([str(prefix / "bin"), "/usr/bin"]),
               "VIRTUAL_ENV": str(prefix), "UV_RUN_RECURSION_DEPTH": "1", "HOME": "/home/alice"}
    env = trace_command.host_environment(environ, str(prefix))
    assert env["PATH"] == "/usr/bin"
    assert "VIRTUAL_ENV" not in env
    assert env["HOME"] == "/home/alice"


@pytest.mark.req("REQ-TRC-1")
def test_an_environment_uv_did_not_activate_is_kept(tmp_path):
    prefix = tmp_path / "env"
    environ = {"PATH": os.pathsep.join([str(prefix / "bin"), "/usr/bin"]), "VIRTUAL_ENV": str(prefix)}
    assert trace_command.host_environment(environ, str(prefix)) == environ
    other = {**environ, "UV_RUN_RECURSION_DEPTH": "1", "VIRTUAL_ENV": str(tmp_path / "other")}
    assert trace_command.host_environment(other, str(prefix)) == other
