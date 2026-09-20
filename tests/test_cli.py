from vogon import __version__
from vogon.cli import main


def test_version_is_set():
    assert __version__


def test_version_flag(capsys):
    assert main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_bare_invocation_prints_usage(capsys):
    assert main([]) == 1
    assert "usage: vogon" in capsys.readouterr().err
