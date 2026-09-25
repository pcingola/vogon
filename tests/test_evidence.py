from pathlib import Path

import pytest

from cli import main

BUILD = "a1b2c3d"
REPORT = b"Traceability report\nBuild: a1b2c3d\nREQ-TRK-1 -> TEST-1 passed\n"
RESULTS = b'{"build": "a1b2c3d", "tests": [{"key": "TEST-1", "status": "PASS"}]}\n'


def put(root: Path, build: str, part: str, name: str, data: bytes) -> None:
    path = root / ".vogon" / "evidence" / build / part / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def exported(root: Path, build: str = BUILD, report: bytes = REPORT, results: bytes = RESULTS) -> None:
    put(root, build, "export", "traceability.txt", report)
    put(root, build, "export", "results.json", results)


def evidence(root: Path, capsys, build: str = BUILD) -> tuple[int, list[str]]:
    status = main(["evidence", build, "--root", str(root)])
    return status, capsys.readouterr().out.splitlines()


@pytest.mark.req("REQ-TRK-10")
def test_filed_copies_identical_to_the_export_pass(tmp_path, capsys):
    exported(tmp_path)
    put(tmp_path, BUILD, "filed", "traceability.txt", REPORT)
    put(tmp_path, BUILD, "filed", "results.json", RESULTS)
    assert evidence(tmp_path, capsys) == (0, ["every filed copy for build a1b2c3d matches the export"])


@pytest.mark.req("REQ-TRK-10")
def test_a_changed_byte_is_reported(tmp_path, capsys):
    exported(tmp_path)
    put(tmp_path, BUILD, "filed", "traceability.txt", REPORT.replace(b"\n", b"\r\n"))
    put(tmp_path, BUILD, "filed", "results.json", RESULTS)
    status, out = evidence(tmp_path, capsys)
    assert status == 1
    assert out == [".vogon/evidence/a1b2c3d/filed/traceability.txt: failure: REQ-TRK-10: "
                   "traceability.txt differs from the exported file"]


@pytest.mark.req("REQ-TRK-10")
def test_an_export_not_filed_is_reported(tmp_path, capsys):
    exported(tmp_path)
    put(tmp_path, BUILD, "filed", "results.json", RESULTS)
    status, out = evidence(tmp_path, capsys)
    assert status == 1
    assert out == [".vogon/evidence/a1b2c3d/export/traceability.txt: failure: REQ-TRK-10: "
                   "traceability.txt was exported for build a1b2c3d and has no filed copy"]


@pytest.mark.req("REQ-TRK-10")
def test_a_file_that_does_not_name_the_build_is_reported(tmp_path, capsys):
    report = b"Traceability report\nREQ-TRK-1 -> TEST-1 passed\n"
    exported(tmp_path, report=report)
    put(tmp_path, BUILD, "filed", "traceability.txt", report)
    put(tmp_path, BUILD, "filed", "results.json", RESULTS)
    status, out = evidence(tmp_path, capsys)
    assert status == 1
    assert out == [".vogon/evidence/a1b2c3d/filed/traceability.txt: failure: REQ-TRK-10: "
                   "traceability.txt does not name build a1b2c3d"]


@pytest.mark.req("REQ-TRK-10")
def test_a_result_from_another_build_is_reported(tmp_path, capsys):
    old = b'{"build": "0f9e8d7", "tests": [{"key": "TEST-1", "status": "PASS"}]}\n'
    exported(tmp_path, build="0f9e8d7", report=REPORT.replace(b"a1b2c3d", b"0f9e8d7"), results=old)
    exported(tmp_path)
    put(tmp_path, BUILD, "filed", "traceability.txt", REPORT)
    put(tmp_path, BUILD, "filed", "results.json", old)
    status, out = evidence(tmp_path, capsys)
    assert status == 1
    assert out == [".vogon/evidence/a1b2c3d/filed/results.json: failure: REQ-TRK-10: "
                   "results.json is the export of build 0f9e8d7, not a1b2c3d"]


@pytest.mark.req("REQ-TRK-10")
def test_a_filed_file_that_is_not_in_the_export_is_reported(tmp_path, capsys):
    exported(tmp_path)
    put(tmp_path, BUILD, "filed", "traceability.txt", REPORT)
    put(tmp_path, BUILD, "filed", "results.json", RESULTS)
    put(tmp_path, BUILD, "filed", "extra.txt", b"Build a1b2c3d notes\n")
    status, out = evidence(tmp_path, capsys)
    assert status == 1
    assert out == [".vogon/evidence/a1b2c3d/filed/extra.txt: failure: REQ-TRK-10: "
                   "extra.txt is filed and is not in the export for build a1b2c3d"]


@pytest.mark.req("REQ-TRK-10")
@pytest.mark.parametrize("filed", [False, True])
def test_nothing_exported_or_nothing_read_back_fails(tmp_path, capsys, filed):
    if filed:
        exported(tmp_path)
    status, out = evidence(tmp_path, capsys)
    assert status == 1
    assert len(out) == 1
    assert ("nothing read back" if filed else "nothing exported") in out[0]


@pytest.mark.req("REQ-TRK-10")
def test_an_export_whose_bytes_another_build_also_exported_passes(tmp_path, capsys):
    # The report names its build in the file name only, so two builds can export the same bytes.
    report = b"Traceability report\nREQ-TRK-1 -> TEST-1 passed\n"
    put(tmp_path, "e5f6a7b", "export", "e5f6a7b_traceability.txt", report)
    put(tmp_path, BUILD, "export", f"{BUILD}_traceability.txt", report)
    put(tmp_path, BUILD, "filed", f"{BUILD}_traceability.txt", report)
    assert evidence(tmp_path, capsys) == (0, ["every filed copy for build a1b2c3d matches the export"])
