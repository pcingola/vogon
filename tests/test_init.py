import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import config
from cli import main

LAYOUT = ["requirements", "facts", "constraints", "decisions", "sources", "plans", "documents"]


def init(root: Path, capsys) -> tuple[int, list[str]]:
    status = main(["init", "--root", str(root)])
    return status, capsys.readouterr().out.splitlines()


def snapshot(root: Path) -> dict[str, bytes | None]:
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None)
            for p in sorted(root.rglob("*"))}


@pytest.mark.req("REQ-CLI-3", "REQ-CLI-5", "REQ-CLI-8")
def test_init_writes_the_defaults_and_no_systems(tmp_path, capsys):
    status, out = init(tmp_path, capsys)
    assert status == 0
    assert "systems" not in yaml.safe_load((tmp_path / "vogon.yaml").read_text())
    cfg = config.load(tmp_path)
    assert cfg.findings == ()
    assert cfg.systems == {}
    assert cfg.records_dir == tmp_path / "vogon"
    assert cfg.test_paths == (tmp_path / "tests",)
    assert cfg.test_command == ("python", "-m", "pytest")
    # The default assignment of DEC-018, with the documents of DEC-023.
    assert {n: (a.roles, a.system, a.configured) for n, a in cfg.approvals.items()} == {
        "requirements": (("product_owner",), "tracker", True),
        "test_cases": (("test_lead",), "test_manager", True),
        "test_specification": (("test_lead",), "document_system", True),
        "change": (("engineer",), "repository_host", True),
        "risk_assessment": (("system_owner", "it_quality_manager"), "document_system", True),
        "release": (("system_owner", "it_quality_manager"), "document_system", True),
    }
    for name in LAYOUT:
        assert (tmp_path / "vogon" / name).is_dir()
    assert yaml.safe_load((tmp_path / "vogon" / "modules.yaml").read_text()) is None
    assert (tmp_path / ".gitignore").read_text() == ".vogon/\n"
    assert "vogon.yaml" in out and ".gitignore" in out and "pyproject.toml" in out


@pytest.mark.req("REQ-GEN-1")
def test_init_writes_nothing_under_claude_and_no_ci_file(tmp_path, capsys):
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text('{"enabledPlugins": {"vogon@vogon": true}}\n')
    before = snapshot(tmp_path / ".claude")
    init(tmp_path, capsys)
    assert snapshot(tmp_path / ".claude") == before
    assert not (tmp_path / ".github").exists()
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        ".claude", ".gitignore", "pyproject.toml", "vogon", "vogon.yaml"]


# The req marker is registered in whichever file holds the host's pytest configuration.
MARKED_TEST = 'import pytest\n\n\n@pytest.mark.req("REQ-TRC-1")\ndef test_x():\n    pass\n'

CONFIGS = {
    "none": {},
    "pyproject without pytest": {"pyproject.toml": '[project]\nname = "host"\n'},
    "pyproject section, no markers": {
        "pyproject.toml": '[project]\nname = "host"\n\n[tool.pytest.ini_options]\n'
                          'testpaths = ["tests"]\n\n[tool.other]\nx = 1\n'},
    "pyproject markers on one line": {
        "pyproject.toml": '[tool.pytest.ini_options]\nmarkers = ["slow: slow tests"]\n'},
    "pyproject markers on several lines": {
        "pyproject.toml": '[tool.pytest.ini_options]\nmarkers = [\n    "slow: slow tests",\n]\n'},
    "pyproject empty markers": {"pyproject.toml": "[tool.pytest.ini_options]\nmarkers = []\n"},
    "pytest.ini": {"pytest.ini": "[pytest]\nmarkers =\n    slow: slow tests\n",
                   "pyproject.toml": '[tool.pytest.ini_options]\nmarkers = []\n'},
    "tox.ini": {"tox.ini": "[tox]\nenvlist = py311\n\n[pytest]\ntestpaths = tests\n"},
    "setup.cfg": {"setup.cfg": "[metadata]\nname = host\n\n[tool:pytest]\n"
                               "markers = slow: slow tests\naddopts = -q"},
}
WHERE = {"none": "pyproject.toml", "pytest.ini": "pytest.ini", "tox.ini": "tox.ini",
         "setup.cfg": "setup.cfg"}


@pytest.mark.req("REQ-TRC-1")
@pytest.mark.parametrize("case", list(CONFIGS))
def test_init_registers_the_req_marker_so_strict_markers_passes_without_the_plugin(
        tmp_path, capsys, case):
    for name, text in CONFIGS[case].items():
        (tmp_path / name).write_text(text)
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_host.py").write_text(MARKED_TEST)
    before = {name: (tmp_path / name).read_text() for name in CONFIGS[case]}

    strict = [sys.executable, "-m", "pytest", "-q", "--strict-markers", "-p", "no:cacheprovider",
              "tests"]
    assert subprocess.run(strict, cwd=tmp_path, capture_output=True).returncode != 0
    status, out = init(tmp_path, capsys)
    assert status == 0
    changed = WHERE.get(case, "pyproject.toml")
    assert changed in out
    # Only the file pytest reads is changed, and what it held is kept.
    for name, text in before.items():
        after = (tmp_path / name).read_text()
        if name == changed:
            assert all(line in after.splitlines() for line in text.splitlines()
                       if "markers" not in line)
        else:
            assert after == text
    run = subprocess.run(strict, cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    if "slow" in before.get(changed, ""):
        listed = subprocess.run([sys.executable, "-m", "pytest", "--markers", "-p",
                                 "no:cacheprovider"], cwd=tmp_path, capture_output=True, text=True)
        assert "@pytest.mark.slow: slow tests" in listed.stdout
        assert "@pytest.mark.req(*ids): the requirement ids the test verifies" in listed.stdout


@pytest.mark.req("REQ-CLI-8")
def test_a_second_run_changes_nothing_and_keeps_the_configured_setup(tmp_path, capsys):
    (tmp_path / ".gitignore").write_text("__pycache__/")
    init(tmp_path, capsys)
    assert (tmp_path / ".gitignore").read_text() == "__pycache__/\n.vogon/\n"
    configured = "systems:\n  repository_host: {server: git}\nroles:\n  engineer: [alice@example.com]\n"
    (tmp_path / "vogon.yaml").write_text(configured)
    before = snapshot(tmp_path)
    assert init(tmp_path, capsys) == (0, [])
    assert snapshot(tmp_path) == before
    assert config.load(tmp_path).system("repository_host").server == "git"
