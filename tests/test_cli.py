from vogon import __version__
from vogon.cli import main


def test_version_is_set():
    assert __version__


def test_version_flag(capsys):
    assert main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_bare_invocation_is_rejected(capsys):
    assert main([]) == 1
    assert "REJECTED" in capsys.readouterr().out
