---
name: tests
description: Writes manual test procedures, numbered steps with expected results, for requirements, as tests.md states. TRIGGER when: write test procedures, test protocols or manual test cases; generate test procedures from existing tests.
---

# vogon:tests

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   `requirements.md` and `tests.md`. Add `tracking.md` where `vogon.yaml`
   names a tracker or `tests.md` keeps procedures in the tracker or the test
   manager.
2. If `tests.md` states that the project needs no test procedures, tell the
   developer so, and stop.
3. If `tests.md` keeps procedures in a system `vogon.yaml` does not name,
   report that the system is not configured, tell the developer to run
   `vogon:init`, and stop.
4. Write procedures for every named requirement. Report each one that is not
   approved or whose approval is stale (`lifecycle.md` "Missing approval").
5. For each requirement, follow the order `tests.md` states. VOGON imposes no
   order of its own. The orders are:
   - Before development: the procedure is written from the requirement, its
     acceptance criteria and its sources. If tests or code for the requirement
     already exist, write the procedure the same way. Report that the
     procedure is late, with the dates of the existing tests or code.
   - After development: the procedure is generated from the tests whose `req`
     marker names the requirement. A requirement with no such test gets no
     procedure; report it.
6. A sub-agent per requirement writes its procedures to `vogon/tmp/tests/`, in
   the format of `records.md` "Test procedure", with steps a tester can carry
   out in the formal test environment `tests.md` names. After development, it
   reports each test whose assertion differs from the requirement, with the
   test, the assertion and the sentence of the requirement.
7. Allocate an id to each reviewed draft, one at a time, never in parallel.
   - Kept in the repository: run `vogon id TP <module>` with the
     requirement's module, add the `id` field to the draft's frontmatter, and
     move the draft to `vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md`
     before the next call, so the next call sees the id.
   - Kept in the tracker or test manager: create one item per reviewed draft
     in that system. Give it the item type, fields, name and link to the
     requirement's tracker item that `tracking.md` states. The item key is
     the id.
8. After development, add `@pytest.mark.procedure("<procedure id>")` to each
   test the procedure was generated from, unless the test already has that
   marker. Change nothing else in the test.
9. Commit the procedures and the marker changes. Where procedures are kept in
   the repository, run `vogon id --check` and renumber each id it reports.
   Push, and open a pull request.
10. Append a `test_procedures_written` entry to each requirement's
    `REQ-*.json` (`lifecycle.md` "State file"). Commit and push to the same
    branch.
11. Tell each holder of an approver role `tests.md` names, from `roles` in
    `vogon.yaml`, that the procedures wait for their approval, and where: the
    pull request, or the items in the tracker or test manager.
