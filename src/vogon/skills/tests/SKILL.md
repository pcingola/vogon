---
name: tests
description: Writes manual test procedures, numbered steps with expected results, for approved requirements, as tests.md states. TRIGGER when: write test procedures, test protocols or manual test cases; generate test procedures from existing tests.
---

# vogon:tests

Writes the test procedures of approved requirements, where the project's
`tests.md` requires them, and registers them for approval by the roles
`tests.md` names. A test procedure is a document of numbered steps, each with
its expected result. Depending on `tests.md`, the procedures are written before
development from the requirement and its acceptance criteria, or after, from
the existing tests. VOGON imposes no order of its own. Use it after the Product
Owner has approved the requirements, or after their tests exist.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the start-of-skill reads, the loop, sub-agent prompts, systems by role, actions never taken, stops and commands.

## Inputs

- The requirements the developer names, by id or by module.
- `vogon/project/tests.md`, and `vogon/project/tracking.md` where `tests.md`
  keeps procedures in the tracker or test manager or where `common.md`
  "Approval of a requirement" requires it. Derive or regenerate either as `${CLAUDE_PLUGIN_ROOT}/references/process-files.md` states.
- For each requirement: `REQ-*.md`, `REQ-*.json`, and the held sources its
  `source` lists.
- After development: the tests whose `req` marker names the requirement, and
  the code they test.
- The checklist `procedure-checklist.md`, read as `common.md` "Project
  checklists" states.

## Steps

1. Create a working branch from the default branch.
2. Do the start-of-skill reads in `common.md`. A process file derived here is
   committed on the working branch, as `process-files.md` states.
3. If `tests.md` states that the project needs no test procedures, tell the
   developer so, and stop.
4. Read from `tests.md` where procedures are kept (repository, tracker or test
   manager), whether they are written before development or generated after
   it, who approves them, and the formal test environment. If the role that
   holds the procedures has no system in `vogon.yaml`, act as `common.md`
   "Systems by role" states; the skill then has no task left and stops.
5. Take only the requirements that are approved as `common.md` "Approval of a
   requirement" states. Report each other named requirement and leave it out.
6. Choose the mode per requirement:
   - Before development: the procedure is written from the requirement, its
     acceptance criteria and its sources. If tests or code for the requirement
     already exist, write the procedure the same way and report the gap with
     the real dates, as `common.md` states.
   - After development: the procedure is generated from the tests whose `req`
     marker names the requirement. A requirement with no such test gets no
     procedure; report it.
7. Run the loop in the table below, one writing sub-agent per requirement, in
   parallel. Each writing sub-agent:
   - decides how many procedures the requirement needs, and writes each to
     `vogon/tmp/tests/<requirement id>-<n>.md`, with `n` counting from 1;
   - writes each procedure with frontmatter `id` (left empty),
     `type: test_procedure`, `title`, `modules`, `status: active` and
     `verifies` (the requirement ids), and a body of numbered steps, each with
     one action and its expected result;
   - takes each expected result from the requirement and its sources, never
     from the code, a test or a run of the code;
   - writes steps a tester can carry out in the formal test environment
     `tests.md` names;
   - after development, reports in its log each test whose assertion differs
     from the requirement, with the test, the assertion and the sentence of
     the requirement;
   - states in its log the number of procedures it wrote and their draft
     paths.
8. Read from each writer's log the number of procedures it wrote. Allocate an
   id to each checked draft, one procedure at a time, never in parallel.
   - Kept in the repository: run
     `${CLAUDE_PLUGIN_ROOT}/scripts/vogon id TP <module>` with the
     requirement's module, set the id in the draft's frontmatter, and move the
     draft to `vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md` before the
     next call, so the next call sees the id.
   - Kept in the tracker or test manager: create one item per draft through
     the system `vogon.yaml` names, with the item type, fields, link to the
     requirement's item and naming that `tracking.md` states for that system:
     its tracker topics for the tracker, its test-manager topics for the test
     manager. The item key is the id. Set the item's text from the draft, read
     it back, report any difference, and delete the draft.
9. After development, add `@pytest.mark.procedure("<procedure id>")` to each
   test a procedure was generated from that does not name it. Change nothing
   else in the test. Where the host project lacks a change
   `${CLAUDE_PLUGIN_ROOT}/references/conftest.md` states, report it as that
   file states.
10. Commit the procedures and the marker changes. Where procedures are kept
    in the repository, run `vogon id --check`; for each id it reports, take a
    new id from `vogon id`, rename the procedure, and change every reference
    to the old id on the branch. Push, and open a pull request on the
    repository host. If the branch has no commit yet, make an empty
    commit that names the requirements. The description lists
    each procedure with the requirements it verifies and states the loops,
    rounds and open findings as `common.md` states.
11. Append a `test_procedures_written` entry to each requirement's
    `REQ-*.json`, commit and push to the same branch.
12. Tell the roles `tests.md` names for approval, from `vogon.yaml`, that the
    procedures wait for their approval, and where: the pull request, or the
    items in the tracker or test manager. Name the same roles in the pull
    request description.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| One per requirement | The test procedures of that requirement, one draft file each | Checklist evaluator | The procedure checklist, applied to each procedure against its requirement and its sources |
| | | Tests evaluator, after development only | Each procedure against the tests it was generated from: every such test is covered by a step, each step matches what its test does, and every difference between a test's assertion and the requirement is reported |

## Stops for a person

- Approval of the procedures: the roles `tests.md` names, in the system where
  the procedures are kept.
- A finding that needs a choice, such as a test whose assertion contradicts
  the requirement: the developer running the skill, before the pull request
  is opened. A finding that the approved requirement itself is wrong or cannot
  be tested goes to the Product Owner, as a change that needs approval again.
- A required input the developer did not give, such as the requirements: the
  developer.
- A gap in the validation plan while `tests.md` or `tracking.md` is derived,
  and confirmation of the tracker and test manager names read from an example
  item: the developer.

## Outputs

| Output | Path or system | Format |
| --- | --- | --- |
| Draft of each procedure | `vogon/tmp/tests/<requirement id>-<n>.md`, gitignored; moved or deleted in step 8 | Markdown with YAML frontmatter, as step 7 states |
| Test procedure, kept in the repository | `vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md` | Markdown with YAML frontmatter, as step 7 states |
| Test procedure, kept in the tracker or test manager | An item in that system, created as `tracking.md` states; its key is the id | The system's item, linked to the requirement's item |
| `procedure` marker, after development | The test files the procedures were generated from | `@pytest.mark.procedure("<procedure id>")` |
| State entry | `REQ-*.json` `steps` | `{"step": "test_procedures_written", "date": "<yyyy-mm-dd>", "pr": <number>}` |
| Pull request | Repository host | The procedures, the marker changes and the state entries |
| Sub-agent logs and main log | `vogon/logs/` | As `common.md` states |

And any process file derived, per `process-files.md`.

## Reference files

| Read by | Files |
| --- | --- |
| Main agent | `${CLAUDE_PLUGIN_ROOT}/references/common.md`, `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, `${CLAUDE_PLUGIN_ROOT}/references/conftest.md` |
| Writing sub-agent | `${CLAUDE_PLUGIN_ROOT}/references/records.md`, `${CLAUDE_PLUGIN_ROOT}/references/sources.md`, `${CLAUDE_PLUGIN_ROOT}/references/writing.md`, `${CLAUDE_PLUGIN_ROOT}/skills/tests/references/procedure-checklist.md` or the project's version |
| Evaluators | The checklist, `${CLAUDE_PLUGIN_ROOT}/references/records.md`, `${CLAUDE_PLUGIN_ROOT}/references/writing.md` |
