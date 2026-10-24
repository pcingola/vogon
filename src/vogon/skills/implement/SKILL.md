---
name: implement
description: Plans requirements, then writes and checks their code, tests and docs, and opens the pull request. TRIGGER when: user says implement REQ-*, plan REQ-*, write the automated tests for REQ-*, or names vogon/plans/plan_*.md.
---

# vogon:implement

Turns one or more requirements into code, tests and documentation. A writing
sub-agent writes a plan, the developers are asked to approve it, and the main
agent then has each part of the plan written and checked, runs the project's
test suite, and opens the pull request. Use it when a developer asks to
implement or plan requirements, or names an existing plan.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- One or more requirement ids, or the path of an existing plan in
  `vogon/plans/`. A plan names its requirements.
- `vogon/project/requirements.md`: the requirement approver.
- `vogon/project/tests.md`, for test procedures and its topic "Running the
  test suite".
- `vogon/project/tracking.md`, where `vogon.yaml` names a tracker.
- The test procedures of the requirements, where `tests.md` keeps them.
- The host project's code, tests and documentation.
- The checklists `test-checklist.md` and `code-checklist.md` (`loop.md`
  "Project checklists").

## Steps

1. Choose the working branch:
   - Requirement ids given, and a pushed branch that is not merged holds a
     `planned` entry for one of them: report that branch, and take it and its
     plan as if the plan had been given.
   - Plan given, and the plan or its `planned` entries are on a pushed branch
     that is not merged: check out that branch as the working branch.
   - Otherwise: create a working branch (`common.md` "Working branch").
2. Do the steps of `common.md` "Start of every skill", with the process files
   the Inputs name. Report each requirement that is not approved or whose
   approval is stale, in the session and in the plan's Summary
   (`lifecycle.md` "Missing approval"). Plan it with the others. When `tests.md` requires test
   procedures before the tests, report each requirement that has none.
3. If no plan was given, start a writing sub-agent, the plan writer, to write
   `vogon/plans/plan_<slug>.md` in the format of
   `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/plan-format.md`. Give it
   the requirements, their state files, the test procedures, the code it
   touches and `tests.md`. If a plan was given, compare it with the plan in
   the commit of each requirement's `planned` entry:
   - every requirement has such an entry and the plan is unchanged: report
     each entry with no `approved_by`, and go to step 6;
   - otherwise the plan has changed: give it to the plan writer to revise.
4. Start the plan evaluators (Loops) and run the review loop (`loop.md`). Ask
   the developer each question only a developer can answer before the plan
   is presented; the plan writer records the answer under Decisions.
5. Present the plan to the developers and ask them to approve it. Tell them
   the plan path and the findings left open. Write no code before a
   developer answers. A developer approves the plan, asks for a change, or
   tells the skill to continue without approval.
   - A change goes to the plan writer and through step 4 again.
   - On approval, or on the instruction to continue: commit the plan on the
     working branch, push the branch, and append a `planned` entry to each
     requirement's state file (`lifecycle.md` "State file"). Commit and push
     the state files.
6. Follow the plan. For each part, start a writing sub-agent that writes the
   part's code, tests and documentation. Give it the plan, the part's number,
   the requirements and their acceptance criteria, the test procedures, and
   the code the part touches. Start parts that do not depend on each other in
   parallel. The sub-agent works out each expected value (`records.md`
   "Expected values") and marks each test (`markers.md`). It
   calls only the interfaces the plan names. Where the part needs an
   interface the plan does not name, the sub-agent reports it and does not
   invent one; the plan is changed through steps 4 and 5.
7. When a part is written, start its evaluators (Loops) and run the review
   loop for that part.
8. Read each writing sub-agent's log and output against the plan. Return work
   to its writer when it changes files outside its part, omits something its
   part lists, or changes something the plan does not name. Log each
   decision in the main log.
9. Run the test suite with the command in `tests.md` "Running the test
   suite". When that topic is empty, ask the developer and record the answer
   (`process-files.md` step 6). Give each failure to the writing sub-agent of
   the part it concerns. The sub-agent fixes the code, and changes a test only
   where `test-checklist.md` allows it. Where the requirement
   itself is wrong, the sub-agent reports it.
   - With the developer's agreement, the requirement is changed
     (`lifecycle.md` "Change to an approved requirement"). The test follows
     the changed text. Report that the requirement needs approval again.
   - Without that agreement, the test stays on the current text, and the
     finding is reported.
   The part's evaluators check the changed part again. Repeat until all tests
   pass or the round limit is reached (`loop.md` "Levels and stop rules").
10. Commit the code, tests and documentation on the working branch, with
    commit messages that name the requirements (`markers.md`). Push, and
    open the pull request on the repository host. The description names the
    plan and the requirements, states the test run and its result, and
    reports a plan that is not approved.
11. Append an `implemented` entry to each requirement's state file
    (`lifecycle.md` "State file"). Commit and push it on the same branch.

### Instructions from the developer

An instruction that changes what the plan states goes to the plan writer, and
the changed plan goes through steps 4 and 5 again before the work it changes
continues.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Plan writer | `vogon/plans/plan_<slug>.md` | Plan against the requirements | The format of `plan-format.md`, and its rules on criterion coverage and on nothing beyond the requirements |
| | | Plan against the code | The rules of `plan-format.md` on paths and interfaces, the fit with the code as it is, reuse, broken tests, stored data, data integrity and security risks, and test conventions |
| Part writer, one per part | The part's code, tests and documentation | Test checker | `test-checklist.md` |
| | | Code reviewer (a sub-agent running Claude Code's `code-review` skill on the part's diff, without `--fix`) | Claude Code's code review, then `code-checklist.md`. VOGON has no code reviewer of its own |

## Outputs

| Path or system | Format |
| --- | --- |
| `vogon/plans/plan_<slug>.md` | Markdown, in the format of `plan-format.md` |
| Host project code, tests and documentation | As the plan states, in the project's conventions |
| `vogon/requirements/<module>/REQ-*.json` | `planned` and `implemented` entries |
| Repository host | A working branch with the plan commit, the code commits and the state-file commits; one pull request |

## Reference files

| Sub-agent | Reads |
| --- | --- |
| Main agent | `${CLAUDE_PLUGIN_ROOT}/references/common.md`, `${CLAUDE_PLUGIN_ROOT}/references/loop.md`, `${CLAUDE_PLUGIN_ROOT}/references/lifecycle.md`, `${CLAUDE_PLUGIN_ROOT}/references/process-files.md` |
| Every sub-agent | `${CLAUDE_PLUGIN_ROOT}/references/writing.md` |
| Plan writer, plan evaluators | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/plan-format.md`, `${CLAUDE_PLUGIN_ROOT}/references/markers.md` |
| Part writer | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/plan-format.md`, `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/test-checklist.md`, `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/code-checklist.md`, `${CLAUDE_PLUGIN_ROOT}/references/records.md`, `${CLAUDE_PLUGIN_ROOT}/references/markers.md` |
| Test checker | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/test-checklist.md`, `${CLAUDE_PLUGIN_ROOT}/references/records.md`, `${CLAUDE_PLUGIN_ROOT}/references/markers.md` |
| Code reviewer | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/code-checklist.md`, `${CLAUDE_PLUGIN_ROOT}/references/markers.md` |
