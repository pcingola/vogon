import subprocess
from pathlib import Path

from cli import __version__, main

ENTRY = Path(__file__).resolve().parent.parent / "src" / "vogon" / "scripts" / "vogon"


def test_version_is_set():
    assert __version__


def test_version_flag(capsys):
    assert main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_bare_invocation_prints_usage(capsys):
    assert main([]) == 1
    assert "usage: vogon" in capsys.readouterr().err


def test_entry_script_runs():
    out = subprocess.run([str(ENTRY), "--version"], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == f"vogon {__version__}"
