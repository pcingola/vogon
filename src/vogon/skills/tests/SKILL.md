---
name: tests
description: Writes manual test procedures, numbered steps with expected results, for requirements, as tests.md states. TRIGGER when: write test procedures, test protocols or manual test cases; generate test procedures from existing tests.
---

# vogon:tests

Writes the test procedures of requirements, where the project's `tests.md`
requires them, and registers them for approval by the roles `tests.md` names.
A test procedure is a document of numbered steps, each with its expected
result. `tests.md` states whether the procedures are written before
development, from the requirement and its acceptance criteria, or after, from
the existing tests. VOGON imposes no order of its own.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- The requirements the developer names, by id or by module.
- `vogon/project/requirements.md`: the requirement approver.
- `vogon/project/tests.md`.
- `vogon/project/tracking.md`, where `tests.md` keeps procedures in the
  tracker or the test manager, or `vogon.yaml` names a tracker.
- For each requirement: `REQ-*.md`, `REQ-*.json`, and the held sources its
  `source` lists.
- After development: the tests whose `req` marker names the requirement, and
  the code they test.
- The checklist `procedure-checklist.md` (`loop.md` "Project checklists").

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   the Inputs name.
2. If `tests.md` states that the project needs no test procedures, tell the
   developer so, and stop.
3. Read from `tests.md` where procedures are kept (repository, tracker or test
   manager), whether they are written before development or generated after
   it, who approves them, and the formal test environment. If `tests.md`
   keeps procedures in a system `vogon.yaml` does not name, report that the
   system is not configured, tell the developer to run `vogon:init`, and
   stop.
4. Write procedures for every named requirement. Report each one that is not
   approved or whose approval is stale (`lifecycle.md` "Missing approval").
5. Choose the mode per requirement:
   - Before development: the procedure is written from the requirement, its
     acceptance criteria and its sources. If tests or code for the requirement
     already exist, write the procedure the same way. Report that the
     procedure is late, with the dates of the existing tests or code.
   - After development: the procedure is generated from the tests whose `req`
     marker names the requirement. A requirement with no such test gets no
     procedure; report it.
6. Run the review loop in the table below, one writing sub-agent per
   requirement, in parallel. Each writing sub-agent:
   - decides how many procedures the requirement needs, and writes each to
     `vogon/tmp/tests/<requirement id>-<n>.md`, with `n` counting from 1;
   - writes each procedure in the format of `records.md` "Test procedure";
   - writes steps a tester can carry out in the formal test environment
     `tests.md` names;
   - after development, reports in its log each test whose assertion differs
     from the requirement, with the test, the assertion and the sentence of
     the requirement;
   - states its draft paths in its log.
7. Read the draft paths from each writer's log. Allocate an id to each
   checked draft, one at a time, never in parallel.
   - Kept in the repository: run
     `${CLAUDE_PLUGIN_ROOT}/scripts/vogon id TP <module>` with the
     requirement's module, add the `id` field to the draft's frontmatter, and
     move the draft to `vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md`
     before the next call, so the next call sees the id.
   - Kept in the tracker or test manager: create one item per checked draft
     in that system. Give it the item type, fields, name and link to the
     requirement's tracker item that `tracking.md` states. The item key is
     the id. Then delete the draft.
8. After development, add `@pytest.mark.procedure("<procedure id>")` to each
   test the procedure was generated from, unless the test already has that
   marker. Change nothing else in the test.
9. Commit the procedures and the marker changes. Where procedures are kept in
   the repository, run `vogon id --check` and renumber each id it reports
   (`common.md` "Commands"). Push, and open a pull request on the repository
   host. The description lists each procedure with the requirements it
   verifies.
10. Append a `test_procedures_written` entry to each requirement's
    `REQ-*.json` (`lifecycle.md` "State file"). Commit and push to the same
    branch.
11. Find the approver roles in `tests.md` and their holders in `roles` in
    `vogon.yaml`. Tell each holder that the procedures wait for their
    approval, and where: the pull request, or the items in the tracker or
    test manager. Name the same roles in the pull request description.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| One per requirement | The test procedures of that requirement, one draft file each | Checklist evaluator | The procedure checklist, applied to each procedure against its requirement and its sources |
| | | Tests evaluator, after development only | Each procedure against the tests it was generated from: every such test is covered by a step, each step matches what its test does, and every difference between a test's assertion and the requirement is reported |

## Outputs

| Output | Path or system | Format |
| --- | --- | --- |
| Draft of each procedure | `vogon/tmp/tests/<requirement id>-<n>.md`, gitignored; moved or deleted in step 7 | As `records.md` "Test procedure" states, with no `id` field |
| Test procedure, kept in the repository | `vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md` | As `records.md` "Test procedure" states |
| Test procedure, kept in the tracker or test manager | An item in that system, created as `tracking.md` states; its key is the id | The system's item, linked to the requirement's item |
| `procedure` marker, after development | The test files the procedures were generated from | `@pytest.mark.procedure("<procedure id>")` |
| State entry | `REQ-*.json` `steps` | `test_procedures_written` |
| Pull request | Repository host | The procedures, the marker changes and the state entries |

## Reference files

| Read by | Files |
| --- | --- |
| Main agent | `${CLAUDE_PLUGIN_ROOT}/references/common.md`, `${CLAUDE_PLUGIN_ROOT}/references/loop.md`, `${CLAUDE_PLUGIN_ROOT}/references/lifecycle.md`, `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, `${CLAUDE_PLUGIN_ROOT}/references/markers.md` |
| Writing sub-agent | `${CLAUDE_PLUGIN_ROOT}/references/records.md`, `${CLAUDE_PLUGIN_ROOT}/references/sources.md`, `${CLAUDE_PLUGIN_ROOT}/references/writing.md`, `${CLAUDE_PLUGIN_ROOT}/skills/tests/references/procedure-checklist.md` or the project's version |
| Evaluators | The checklist, `${CLAUDE_PLUGIN_ROOT}/references/records.md`, `${CLAUDE_PLUGIN_ROOT}/references/writing.md` |
