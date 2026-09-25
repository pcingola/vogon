import subprocess
from pathlib import Path

import pytest

import records

REQ = """---
id: REQ-TRK-2
type: requirement
modules: [TRK, REC]
status: accepted
acceptance_on: 2026-03-01
---

# REQ-TRK-2 — Title

Body.
"""


def put(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.req("REQ-REC-1")
def test_parse_splits_frontmatter_and_body(tmp_path):
    path = put(tmp_path, "vogon/requirements/TRK/REQ-TRK-2.md", REQ)
    r = records.parse(path)
    assert r.id == "REQ-TRK-2"
    assert r.type == "requirement"
    assert r.status == "accepted"
    assert r.meta["acceptance_on"] == "2026-03-01"
    assert r.body.startswith("\n# REQ-TRK-2")
    assert r.body_line == 8
    assert r.line_of("status") == 5


@pytest.mark.req("REQ-REC-1")
@pytest.mark.parametrize("text, line", [
    ("# no frontmatter\n", 1),
    ("---\nid: DEC-001\n", 1),
    ("---\nid: DEC-001\ntitle: [unclosed\n---\n", 3),
    ("---\n- a list\n---\n", 2),
])
def test_unreadable_frontmatter_is_an_error_naming_the_file(tmp_path, text, line):
    path = put(tmp_path, "vogon/decisions/DEC-001.md", text)
    with pytest.raises(records.RecordError) as e:
        records.parse(path)
    assert e.value.path == path
    assert e.value.line == line


@pytest.mark.req("REQ-REC-2")
def test_superseded_status_names_the_successor(tmp_path):
    path = put(tmp_path, "vogon/decisions/DEC-012.md",
               "---\nid: DEC-012\nstatus:\n  superseded_by: DEC-021\n---\n")
    r = records.parse(path)
    assert (r.status, r.superseded_by) == ("superseded_by", "DEC-021")


@pytest.mark.req("REQ-REC-3")
def test_load_all_enumerates_each_kind_and_reports_unparsable_files(tmp_path):
    root = tmp_path / "vogon"
    put(root, "requirements/TRK/REQ-TRK-2.md", REQ)
    put(root, "facts/FACT-001.md", "---\nid: FACT-001\ntype: fact\n---\n")
    put(root, "decisions/DEC-001.md", "no frontmatter\n")
    put(root, "sources/2026-01-01_notes.md", "---\ndate: 2026-01-01\n---\n")
    found, errors = records.load_all(root)
    assert [r.id for r in found] == ["FACT-001", "REQ-TRK-2"]
    assert [e.path.name for e in errors] == ["DEC-001.md"]
    assert [p.name for p in records.record_files(root, "requirement")] == ["REQ-TRK-2.md"]
    assert records.find(found, "REQ-TRK-02").id == "REQ-TRK-2"


@pytest.mark.req("REQ-REC-14")
def test_modules_come_from_the_id_and_the_frontmatter(tmp_path):
    root = tmp_path / "vogon"
    put(root, "modules.yaml", "TRK: Tracker\nREC: Records\n")
    r = records.parse(put(root, "requirements/TRK/REQ-TRK-2.md", REQ))
    assert records.load_modules(root) == {"TRK": "Tracker", "REC": "Records"}
    assert records.record_modules(r) == ["TRK", "REC"]
    assert records.load_modules(tmp_path / "absent") is None


# The record checks. Each builds a project in tmp_path and runs the checks on it.

from checks import records as record_checks  # noqa: E402
from config import load  # noqa: E402

TRK_2 = """---
id: REQ-TRK-2
type: requirement
title: Report a record edited after its issue was approved
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
acceptance_by: alice@example.com
acceptance_on: 2026-03-01
depends_on: [FACT-004]
---

# REQ-TRK-2 — Report a record edited after its issue was approved

**Requirement.** Where a record has changed since the tracker approved the
issue it is tracked as, VOGON MUST report it.

**Acceptance.** For any record whose content hash differs from the hash
recorded at approval, the record appears in the report.
"""

FACT_4 = """---
id: FACT-004
type: fact
title: An auditor compares approval dates with first use
modules: [TRK]
status: accepted
as_of: 2026-09-19
---

# FACT-004 — An auditor compares approval dates with first use

Body.
"""

CON_1 = """---
id: CON-001
type: constraint
title: Approval cannot be performed by a machine account
modules: [TRK, REC]
status: accepted
imposed_by: 21 CFR Part 11 §11.200
lifts_when: permanent
depends_on: [FACT-004]
references:
  - docs/architecture.md
---

Body.
"""

DEC_1 = """---
id: DEC-001
type: decision
title: Records are plain text in git
modules: [REC]
status: {superseded_by: DEC-002}
---

Body.
"""

DEC_2 = """---
id: DEC-002
type: decision
title: Records are markdown with YAML frontmatter
modules: [REC]
status: proposed
depends_on: [DEC-001]
tracked_as:
  governs: tracker
  tracker: PROJ-412
---

Body.
"""

TRK_2_PATH = "vogon/requirements/TRK/REQ-TRK-2.md"


def project(root: Path) -> Path:
    """A project whose records satisfy every rule."""
    put(root, "vogon/modules.yaml", "TRK: Tracker\nREC: Records\n")
    put(root, TRK_2_PATH, TRK_2)
    put(root, "vogon/facts/FACT-004.md", FACT_4)
    put(root, "vogon/constraints/CON-001.md", CON_1)
    put(root, "vogon/decisions/DEC-001.md", DEC_1)
    put(root, "vogon/decisions/DEC-002.md", DEC_2)
    put(root, "docs/architecture.md", "# Architecture\n")
    return root


def check(root: Path, *fns):
    config = load(root)
    return [f for fn in (fns or record_checks.CHECKS) for f in fn(config)]


def edit(root: Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", message)
    return git(root, "rev-parse", "HEAD")[:10]


def init_repo(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.email", "alice@example.com")
    git(root, "config", "user.name", "Alice")
    git(root, "config", "commit.gpgsign", "false")


@pytest.mark.req("REQ-REC-1", "REQ-REC-2", "REQ-REC-3", "REQ-REC-4", "REQ-REC-12", "REQ-REC-13",
                 "REQ-REC-14", "REQ-TRK-7")
def test_records_satisfying_every_rule_produce_no_output(tmp_path):
    init_repo(tmp_path)
    project(tmp_path)
    commit(tmp_path, "add")
    assert check(tmp_path) == []


# REQ-REC-1: the report names the file, the field and the rule it fails.


@pytest.mark.req("REQ-REC-1")
@pytest.mark.parametrize("rel, old, new, field, rule, line", [
    (TRK_2_PATH, "verification: test\n", "", "verification", "missing", None),
    (TRK_2_PATH, "status: accepted", "status: done", "status", "one of proposed, accepted", 6),
    (TRK_2_PATH, "gxp_risk: data integrity", "gxp_risk: high", "gxp_risk", "one of safety", 8),
    (TRK_2_PATH, "verification: test", "verification: review", "verification", "one of", 7),
    (TRK_2_PATH, "status: accepted\n", "status: accepted\npriority: high\n", "priority",
     "not defined for a requirement", 7),
    (TRK_2_PATH, "acceptance_on: 2026-03-01", "acceptance_on: 1 March", "acceptance_on",
     "YYYY-MM-DD", 10),
    (TRK_2_PATH, "modules: [TRK]", "modules: [REC]", "modules", "does not list TRK", 5),
    (TRK_2_PATH, "modules: [TRK]", "modules: []", "modules", "non-empty list", 5),
    (TRK_2_PATH, "type: requirement", "type: decision", "type", "names a requirement", 3),
    (TRK_2_PATH, "type: requirement", "type: rule", "type", "one of requirement", 3),
    (TRK_2_PATH, "type: requirement", "type: [requirement]", "type", "one of requirement", 3),
    (TRK_2_PATH, "type: requirement", "type: {kind: requirement}", "type", "one of requirement", 3),
    ("vogon/facts/FACT-004.md", "as_of: 2026-09-19\n", "as_of: 2026-09-19\ndepends_on: [CON-001]\n",
     "depends_on", "not defined for a fact", 8),
    ("vogon/facts/FACT-004.md", "as_of: 2026-09-19\n", "", "as_of", "missing", None),
    ("vogon/constraints/CON-001.md", "lifts_when: permanent\n", "", "lifts_when", "missing", None),
    ("vogon/decisions/DEC-002.md", "status: proposed\n", "status: proposed\nreviewed_by: bob\n",
     "reviewed_by", "without 'reviewed_on'", 7),
    ("vogon/decisions/DEC-002.md", "  governs: tracker\n", "", "tracked_as", "governs", 8),
    ("vogon/decisions/DEC-002.md", "governs: tracker", "governs: test_manager", "tracked_as.governs",
     "test_manager", 8),
])
def test_schema_violation_names_file_field_and_rule(tmp_path, rel, old, new, field, rule, line):
    project(tmp_path)
    edit(tmp_path, rel, old, new)
    found = check(tmp_path, record_checks.schema)
    assert len(found) == 1, found
    f = found[0]
    assert (f.path, f.line, f.requirement, f.is_failure) == (rel, line, "REQ-REC-1", True)
    assert f"'{field}'" in f.message
    assert rule in f.message


@pytest.mark.req("REQ-REC-1")
def test_unreadable_record_is_reported_naming_the_file(tmp_path):
    project(tmp_path)
    put(tmp_path, "vogon/decisions/DEC-003.md", "---\nid: DEC-003\ntitle: [unclosed\n---\n")
    found = check(tmp_path, record_checks.schema)
    assert [(f.path, f.line, f.requirement) for f in found] == [
        ("vogon/decisions/DEC-003.md", 3, "REQ-REC-1")]


# REQ-REC-2: every id referenced in frontmatter resolves to a file.


@pytest.mark.req("REQ-REC-2")
@pytest.mark.parametrize("rel, old, new, missing", [
    (TRK_2_PATH, "depends_on: [FACT-004]", "depends_on: [FACT-004, FACT-099]", "FACT-099"),
    ("vogon/decisions/DEC-001.md", "superseded_by: DEC-002", "superseded_by: DEC-099", "DEC-099"),
    (TRK_2_PATH, "depends_on: [FACT-004]", "depends_on: [FACT_4]", "FACT_4"),
])
def test_reference_to_a_missing_id_names_the_record_and_the_id(tmp_path, rel, old, new, missing):
    project(tmp_path)
    edit(tmp_path, rel, old, new)
    found = check(tmp_path, record_checks.links)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-2")]
    assert missing in found[0].message


@pytest.mark.req("REQ-REC-2")
def test_reference_to_a_withdrawn_record_resolves(tmp_path):
    project(tmp_path)
    edit(tmp_path, "vogon/facts/FACT-004.md", "status: accepted", "status: withdrawn")
    assert check(tmp_path, record_checks.links) == []


# REQ-REC-3: every id appears exactly once and equals the filename stem.


@pytest.mark.req("REQ-REC-3")
def test_two_files_declaring_one_id_are_both_reported(tmp_path):
    project(tmp_path)
    put(tmp_path, "vogon/requirements/TRK/REQ-TRK-3.md", TRK_2)
    found = check(tmp_path, record_checks.identifiers)
    dup = [f for f in found if "held by 2 files" in f.message]
    assert sorted(f.path for f in dup) == [TRK_2_PATH, "vogon/requirements/TRK/REQ-TRK-3.md"]
    assert all(TRK_2_PATH in f.message and "REQ-TRK-3.md" in f.message for f in dup)
    mismatch = [f for f in found if f not in dup]
    assert [(f.path, f.requirement) for f in mismatch] == [
        ("vogon/requirements/TRK/REQ-TRK-3.md", "REQ-REC-3")]


@pytest.mark.req("REQ-REC-3")
def test_id_differing_from_the_filename_is_reported(tmp_path):
    project(tmp_path)
    put(tmp_path, "vogon/requirements/REC/REQ-REC-4.md",
        TRK_2.replace("REQ-TRK-2", "REQ-REC-5").replace("[TRK]", "[REC]"))
    found = check(tmp_path, record_checks.identifiers)
    assert [(f.path, f.line, f.requirement) for f in found] == [
        ("vogon/requirements/REC/REQ-REC-4.md", 2, "REQ-REC-3")]
    assert "REQ-REC-5" in found[0].message and "REQ-REC-4.md" in found[0].message


@pytest.mark.req("REQ-REC-3")
def test_ids_differing_only_in_leading_zeros_are_one_id(tmp_path):
    project(tmp_path)
    put(tmp_path, "vogon/requirements/TRK/REQ-TRK-02.md", TRK_2.replace("REQ-TRK-2", "REQ-TRK-02"))
    found = check(tmp_path, record_checks.identifiers)
    assert sorted(f.path for f in found) == sorted([TRK_2_PATH, "vogon/requirements/TRK/REQ-TRK-02.md"])


# REQ-REC-4: every source and references entry resolves to a file.


@pytest.mark.req("REQ-REC-4")
@pytest.mark.parametrize("field", ["source", "references"])
def test_path_that_does_not_resolve_names_record_and_field(tmp_path, field):
    project(tmp_path)
    edit(tmp_path, TRK_2_PATH, "depends_on:",
         f"{field}:\n  - vogon/sources/2026-04-02_procedure.md\ndepends_on:")
    found = check(tmp_path, record_checks.paths)
    assert [(f.path, f.line, f.requirement) for f in found] == [(TRK_2_PATH, 11, "REQ-REC-4")]
    assert field in found[0].message
    assert "vogon/sources/2026-04-02_procedure.md" in found[0].message
    put(tmp_path, "vogon/sources/2026-04-02_procedure.md", "held\n")
    assert check(tmp_path, record_checks.paths) == []


# REQ-REC-5: an id that has ever existed appears in at most one live record.


@pytest.mark.req("REQ-REC-5")
def test_deleting_a_withdrawn_record_and_minting_its_id_again_are_reported(tmp_path):
    init_repo(tmp_path)
    project(tmp_path)
    rel = "vogon/requirements/REC/REQ-REC-9.md"
    rec_9 = TRK_2.replace("REQ-TRK-2", "REQ-REC-9").replace("[TRK]", "[REC]")
    put(tmp_path, rel, rec_9.replace("status: accepted", "status: withdrawn"))
    commit(tmp_path, "withdraw")
    assert check(tmp_path, record_checks.reuse) == []

    (tmp_path / rel).unlink()
    deleted = commit(tmp_path, "delete")
    found = check(tmp_path, record_checks.reuse)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-5")]
    assert deleted in found[0].message

    put(tmp_path, rel, rec_9)
    readded = commit(tmp_path, "mint REQ-REC-9 again")
    found = check(tmp_path, record_checks.reuse)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-5")]
    assert deleted in found[0].message and readded in found[0].message


@pytest.mark.req("REQ-REC-5")
def test_withdrawn_record_made_live_again_is_reported(tmp_path):
    init_repo(tmp_path)
    project(tmp_path)
    commit(tmp_path, "add")
    edit(tmp_path, "vogon/facts/FACT-004.md", "status: accepted", "status: withdrawn")
    withdrawn = commit(tmp_path, "withdraw")
    edit(tmp_path, "vogon/facts/FACT-004.md", "status: withdrawn", "status: accepted")
    commit(tmp_path, "revive")
    found = check(tmp_path, record_checks.reuse)
    assert [(f.path, f.requirement) for f in found] == [("vogon/facts/FACT-004.md", "REQ-REC-5")]
    assert withdrawn in found[0].message and "'accepted'" in found[0].message


@pytest.mark.req("REQ-REC-5")
def test_uncommitted_deletion_is_reported(tmp_path):
    init_repo(tmp_path)
    project(tmp_path)
    commit(tmp_path, "add")
    (tmp_path / "vogon/facts/FACT-004.md").unlink()
    found = check(tmp_path, record_checks.reuse)
    assert [(f.path, f.requirement) for f in found] == [("vogon/facts/FACT-004.md", "REQ-REC-5")]


@pytest.mark.req("REQ-REC-5")
def test_moving_a_record_and_keeping_withdrawn_records_is_not_reported(tmp_path):
    init_repo(tmp_path)
    project(tmp_path)
    commit(tmp_path, "add")
    edit(tmp_path, "vogon/facts/FACT-004.md", "status: accepted", "status: withdrawn")
    commit(tmp_path, "withdraw")
    git(tmp_path, "mv", TRK_2_PATH, "vogon/requirements/REQ-TRK-2.md")
    commit(tmp_path, "move")
    assert check(tmp_path, record_checks.reuse) == []


# REQ-REC-12: an accepted acceptance block on a requirement carrying risk or verified by test.


@pytest.mark.req("REQ-REC-12")
@pytest.mark.parametrize("old, new", [
    ("acceptance_by: alice@example.com\n", ""),
    ("acceptance_on: 2026-03-01\n", ""),
    ("**Acceptance.**", "**Criteria.**"),
])
def test_accepted_requirement_without_accepted_block_fails(tmp_path, old, new):
    project(tmp_path)
    edit(tmp_path, TRK_2_PATH, "verification: test", "verification: inspection")
    edit(tmp_path, TRK_2_PATH, "gxp_risk: data integrity", "gxp_risk: safety")
    edit(tmp_path, TRK_2_PATH, old, new)
    found = check(tmp_path, record_checks.acceptance)
    assert [(f.path, f.line, f.requirement, f.is_failure) for f in found] == [
        (TRK_2_PATH, 6, "REQ-REC-12", True)]
    assert "'safety'" in found[0].message and "proposed" in found[0].message


@pytest.mark.req("REQ-REC-12")
def test_proposed_requirement_without_acceptance_is_reported_and_does_not_fail(tmp_path):
    project(tmp_path)
    edit(tmp_path, TRK_2_PATH, "status: accepted", "status: proposed")
    edit(tmp_path, TRK_2_PATH, "acceptance_by: alice@example.com\nacceptance_on: 2026-03-01\n", "")
    found = check(tmp_path, record_checks.acceptance)
    assert [(f.path, f.requirement, f.is_failure) for f in found] == [
        (TRK_2_PATH, "REQ-REC-12", False)]


@pytest.mark.req("REQ-REC-12")
def test_requirement_with_no_risk_verified_by_inspection_needs_no_acceptance(tmp_path):
    project(tmp_path)
    edit(tmp_path, TRK_2_PATH, "verification: test", "verification: inspection")
    edit(tmp_path, TRK_2_PATH, "gxp_risk: data integrity", "gxp_risk: none")
    edit(tmp_path, TRK_2_PATH, "acceptance_by: alice@example.com\nacceptance_on: 2026-03-01\n", "")
    assert check(tmp_path, record_checks.acceptance) == []


# REQ-REC-13: the id matches the grammar.


@pytest.mark.req("REQ-REC-13")
@pytest.mark.parametrize("bad", ["REQ_TRK_2", "REQ-trk-2", "RQ-TRK-2", "TODO-TRK-2"])
def test_id_not_matching_the_grammar_is_reported_with_id_and_path(tmp_path, bad):
    project(tmp_path)
    rel = f"vogon/requirements/TRK/{bad}.md"
    (tmp_path / TRK_2_PATH).unlink()
    put(tmp_path, rel, TRK_2.replace("id: REQ-TRK-2", f"id: {bad}"))
    found = check(tmp_path, record_checks.identifiers)
    assert [(f.path, f.line, f.requirement) for f in found] == [(rel, 2, "REQ-REC-13")]
    assert bad in found[0].message


@pytest.mark.req("REQ-REC-13")
def test_valid_id_in_a_module_no_other_record_uses_passes(tmp_path):
    project(tmp_path)
    assert check(tmp_path, record_checks.identifiers) == []


# REQ-REC-14: every module named is declared in modules.yaml.


@pytest.mark.req("REQ-REC-14")
def test_undeclared_module_in_the_id_is_reported(tmp_path):
    project(tmp_path)
    rel = "vogon/requirements/TRCK/REQ-TRCK-3.md"
    put(tmp_path, rel, TRK_2.replace("REQ-TRK-2", "REQ-TRCK-3").replace("[TRK]", "[TRCK]"))
    found = check(tmp_path, record_checks.modules)
    assert [(f.path, f.requirement) for f in found] == [(rel, "REQ-REC-14")]
    assert "TRCK" in found[0].message


@pytest.mark.req("REQ-REC-14")
def test_undeclared_module_in_frontmatter_is_reported(tmp_path):
    project(tmp_path)
    edit(tmp_path, "vogon/facts/FACT-004.md", "modules: [TRK]", "modules: [TRK, RSK]")
    found = check(tmp_path, record_checks.modules)
    assert [(f.path, f.line, f.requirement) for f in found] == [
        ("vogon/facts/FACT-004.md", 5, "REQ-REC-14")]
    assert "RSK" in found[0].message


@pytest.mark.req("REQ-REC-14")
def test_project_using_no_modules_needs_no_modules_file(tmp_path):
    put(tmp_path, "vogon/facts/FACT-001.md", FACT_4.replace("FACT-004", "FACT-001")
        .replace("modules: [TRK]\n", ""))
    assert check(tmp_path, record_checks.modules) == []


# REQ-TRK-7: no record asserts that it was approved or signed.


@pytest.mark.req("REQ-TRK-7")
@pytest.mark.parametrize("old, new, line", [
    ("status: accepted\n", "status: accepted\napproved_by: jsmith\n", 7),
    ("status: accepted\n", "status: accepted\nsignature: J. Smith\n", 7),
    ("status: accepted", "status: approved", 6),
    ("**Acceptance.**", "Approved by J. Smith on 2026-03-02.\n\n**Acceptance.**", 19),
    ("**Acceptance.**", "**Signed off by:** J. Smith\n\n**Acceptance.**", 19),
])
def test_record_asserting_approval_is_invalid(tmp_path, old, new, line):
    project(tmp_path)
    edit(tmp_path, TRK_2_PATH, old, new)
    found = check(tmp_path, record_checks.approval_claims)
    assert [(f.path, f.line, f.requirement, f.is_failure) for f in found] == [
        (TRK_2_PATH, line, "REQ-TRK-7", True)]
    assert check(tmp_path, record_checks.schema) == []


@pytest.mark.req("REQ-TRK-7", "REQ-REC-1")
def test_a_key_containing_sign_inside_a_word_is_not_an_approval_claim(tmp_path):
    project(tmp_path)
    edit(tmp_path, TRK_2_PATH, "status: accepted\n", "status: accepted\ndesign_notes: none\n")
    assert check(tmp_path, record_checks.approval_claims) == []
    found = check(tmp_path, record_checks.schema)
    assert [(f.line, f.requirement) for f in found] == [(7, "REQ-REC-1")]
    assert "design_notes" in found[0].message


@pytest.mark.req("REQ-TRK-7")
def test_prose_about_approval_in_the_tracker_is_not_a_claim(tmp_path):
    project(tmp_path)
    edit(tmp_path, TRK_2_PATH, "**Acceptance.**",
         "The Product Owner approves the issue in the tracker, and the approval is read\n"
         "from there.\n\n**Acceptance.**")
    assert check(tmp_path, record_checks.approval_claims) == []
