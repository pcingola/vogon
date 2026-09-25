from pathlib import Path

import pytest

import markers
from checks import markers as marker_checks
from config import load


def requirement(rid: str, status: str = "accepted", verification: str = "test",
                gxp_risk: str = "data integrity", accepted: bool = True, block: bool = True) -> str:
    acceptance = "acceptance_by: alice@example.com\nacceptance_on: 2026-03-01\n" if accepted else ""
    body = "\n**Acceptance.** For any input, the output is 1.24.\n" if block else "\n"
    return (f"---\nid: {rid}\ntype: requirement\ntitle: T\nmodules: [TRC]\nstatus: {status}\n"
            f"verification: {verification}\ngxp_risk: {gxp_risk}\n{acceptance}---\n{body}")


def put(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def req(root: Path, rid: str, **kw) -> None:
    put(root, f"vogon/requirements/TRC/{rid}.md", requirement(rid, **kw))


def write_test(root: Path, body: str, name: str = "test_rounding.py") -> str:
    put(root, f"tests/{name}", "import pytest\n\n\n" + body)
    return f"tests/{name}"


def check(root: Path, fn):
    return list(fn(load(root)))


# Markers are read with ast, never by importing the test file.


@pytest.mark.req("REQ-TRC-2")
def test_markers_are_read_without_importing_the_file(tmp_path):
    rel = write_test(tmp_path, """
import module_that_does_not_exist
raise SystemExit("imported")

pytestmark = [pytest.mark.req("REQ-TRC-1"), pytest.mark.slow]


@pytest.mark.req("REQ-TRC-2", "REQ-TRC-3")
def test_a():
    pass


@pytest.mark.req("REQ-TRC-4")
class TestB:
    @pytest.mark.req("REQ-TRC-5")
    async def test_c(self):
        pass
""")
    found, errors = markers.collect([tmp_path / "tests"])
    assert errors == []
    assert [(m.path.name, m.test, m.ids) for m in found] == [
        ("test_rounding.py", "<module>", ("REQ-TRC-1",)),
        ("test_rounding.py", "test_a", ("REQ-TRC-2", "REQ-TRC-3")),
        ("test_rounding.py", "TestB", ("REQ-TRC-4",)),
        ("test_rounding.py", "TestB::test_c", ("REQ-TRC-5",)),
    ]
    assert Path(rel).name == found[0].path.name


# REQ-TRC-2: a marker naming an id with no requirement fails, naming the test and the id.


@pytest.mark.req("REQ-TRC-2")
@pytest.mark.parametrize("named", ["REQ-TRC-40", "REQ_TRC_4", "FACT-001"])
def test_marker_naming_no_requirement_fails(tmp_path, named):
    for n in range(1, 9):
        req(tmp_path, f"REQ-TRC-{n}")
    put(tmp_path, "vogon/facts/FACT-001.md", "---\nid: FACT-001\ntype: fact\n---\n")
    rel = write_test(tmp_path, f'@pytest.mark.req("REQ-TRC-1", "{named}")\ndef test_x():\n    pass\n')
    found = check(tmp_path, marker_checks.resolution)
    assert [(f.path, f.line, f.requirement, f.is_error) for f in found] == [
        (rel, 4, "REQ-TRC-2", True)]
    assert f"{rel}::test_x" in found[0].message and named in found[0].message


@pytest.mark.req("REQ-TRC-2")
def test_a_test_file_that_is_not_utf8_fails_naming_the_file(tmp_path):
    req(tmp_path, "REQ-TRC-1")
    path = tmp_path / "tests" / "test_latin1.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'# caf\xe9\n@pytest.mark.req("REQ-TRC-1")\ndef test_x():\n    pass\n')
    found = check(tmp_path, marker_checks.resolution)
    assert [(f.path, f.requirement, f.is_error) for f in found] == [
        ("tests/test_latin1.py", "REQ-TRC-2", True)]
    assert "UTF-8" in found[0].message


@pytest.mark.req("REQ-TRC-2")
def test_marker_argument_that_is_not_a_literal_fails(tmp_path):
    req(tmp_path, "REQ-TRC-1")
    rel = write_test(tmp_path, 'ID = "REQ-TRC-1"\n\n@pytest.mark.req(ID)\ndef test_x():\n    pass\n')
    found = check(tmp_path, marker_checks.resolution)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-TRC-2")]
    assert "ID" in found[0].message


# REQ-TRC-3: a marker naming a withdrawn or superseded requirement fails, naming the status.


@pytest.mark.req("REQ-TRC-3")
@pytest.mark.parametrize("status, words", [
    ("withdrawn", ["withdrawn"]),
    ("{superseded_by: REQ-TRC-9}", ["superseded_by", "REQ-TRC-9"]),
])
def test_marker_naming_a_retired_requirement_fails(tmp_path, status, words):
    req(tmp_path, "REQ-TRC-3", status=status)
    req(tmp_path, "REQ-TRC-9")
    rel = write_test(tmp_path, '@pytest.mark.req("REQ-TRC-3")\ndef test_x():\n    pass\n')
    found = check(tmp_path, marker_checks.resolution)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-TRC-3")]
    assert f"{rel}::test_x" in found[0].message and "REQ-TRC-3" in found[0].message
    assert all(w in found[0].message for w in words)


@pytest.mark.req("REQ-TRC-3", "REQ-TRC-8")
def test_marker_naming_a_proposed_or_accepted_requirement_with_accepted_block_passes(tmp_path):
    req(tmp_path, "REQ-TRC-1")
    req(tmp_path, "REQ-TRC-2", status="proposed")
    write_test(tmp_path, '@pytest.mark.req("REQ-TRC-1", "REQ-TRC-02")\ndef test_x():\n    pass\n')
    assert check(tmp_path, marker_checks.resolution) == []


# REQ-TRC-8: a marker naming a requirement whose acceptance block is absent or unaccepted fails.


@pytest.mark.req("REQ-TRC-8")
@pytest.mark.parametrize("kw, words", [
    ({"accepted": False}, ["acceptance_by"]),
    ({"block": False}, ["no acceptance block"]),
    ({"accepted": False, "gxp_risk": "none", "verification": "inspection"}, ["acceptance_by"]),
])
def test_marker_naming_a_requirement_without_accepted_block_fails(tmp_path, kw, words):
    req(tmp_path, "REQ-TRC-5", status="proposed", **kw)
    rel = write_test(tmp_path, '\n@pytest.mark.req("REQ-TRC-5")\ndef test_x():\n    pass\n')
    found = check(tmp_path, marker_checks.resolution)
    assert [(f.path, f.line, f.requirement) for f in found] == [(rel, 5, "REQ-TRC-8")]
    assert f"{rel}::test_x" in found[0].message and "REQ-TRC-5" in found[0].message
    assert all(w in found[0].message for w in words)


# REQ-TRC-4: every accepted requirement verified by test is named by a marker.


@pytest.mark.req("REQ-TRC-4")
@pytest.mark.parametrize("gxp_risk", ["none", "data integrity"])
def test_accepted_requirement_verified_by_test_that_no_marker_names_fails(tmp_path, gxp_risk):
    req(tmp_path, "REQ-TRC-1")
    req(tmp_path, "REQ-TRC-2", gxp_risk=gxp_risk)
    write_test(tmp_path, '@pytest.mark.req("REQ-TRC-1")\ndef test_x():\n    pass\n')
    found = check(tmp_path, marker_checks.coverage)
    assert [(f.path, f.requirement, f.is_error) for f in found] == [
        ("vogon/requirements/TRC/REQ-TRC-2.md", "REQ-TRC-4", True)]
    assert "REQ-TRC-2" in found[0].message


@pytest.mark.req("REQ-TRC-4")
@pytest.mark.parametrize("kw", [
    {"verification": "inspection"},
    {"verification": "analysis"},
    {"verification": "demonstration"},
    {"status": "proposed"},
    {"status": "withdrawn"},
])
def test_requirement_not_accepted_or_not_verified_by_test_needs_no_marker(tmp_path, kw):
    req(tmp_path, "REQ-TRC-2", **kw)
    assert check(tmp_path, marker_checks.coverage) == []


@pytest.mark.req("REQ-TRC-4")
def test_requirement_named_by_a_class_or_module_marker_is_covered(tmp_path):
    req(tmp_path, "REQ-TRC-1")
    req(tmp_path, "REQ-TRC-2")
    write_test(tmp_path, 'pytestmark = pytest.mark.req("REQ-TRC-1")\n\n\n'
                        '@pytest.mark.req("REQ-TRC-2")\nclass TestX:\n    def test_y(self):\n'
                        '        pass\n')
    assert check(tmp_path, marker_checks.coverage) == []
