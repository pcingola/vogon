---
name: implement
description: Plans approved requirements, then writes and checks their code, tests and docs, and opens the pull request. TRIGGER when: user says implement REQ-*, plan REQ-*, write the automated tests for REQ-*, or names vogon/plans/plan_*.md.
---

# vogon:implement

Turns one or more approved requirements into code, tests and documentation. A
writing sub-agent writes a plan, the developers approve it, and the main agent
then has each part of the plan written and checked, runs the project's test
suite, and opens the pull request. Use it when a developer asks to implement or
plan requirements, or names an existing plan.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the start-of-skill reads, the loop, sub-agent prompts, systems by role, actions never taken, stops and commands.

## Inputs

- One or more requirement ids, or the path of an existing plan in
  `vogon/plans/`. A plan names its requirements.
- `vogon/project/tests.md`, for test procedures and its topic "Running the
  test suite". Derive it first if it is missing, as `common.md` states.
- `vogon/project/tracking.md`, where `common.md` "Approval of a requirement"
  requires it.
- The test procedures of the requirements, where `tests.md` keeps them.
- The host project's code, tests and documentation.
- The checklists `test-checklist.md` and `code-checklist.md`, read as
  `common.md` "Project checklists" states.

## Steps

1. If requirement ids were given and a pushed branch that is not merged
   holds a `planned` entry for one of them, report it and take that branch
   and its plan as if the plan had been given. If a plan was given and the
   plan or its `planned` entries are on a pushed branch that is not merged,
   check out that branch as the working branch. Otherwise create a working
   branch from the default branch. Every later commit is on it. Do the start-of-skill reads in `common.md`. A requirement that is not
   approved, as `common.md` "Approval of a requirement" defines it, is not
   planned: report it, name the Product Owner as the role that approves it, and continue
   with the others. If none remain, stop. Where `tests.md` says test
   procedures are written before the tests and a requirement has none, report
   the gap.
2. If no plan was given, go to step 3. If a plan was given and each
   requirement's state file has a `planned` entry for that plan whose commit
   holds the plan as it is now, go to step 6. Otherwise the plan is stale or
   not approved: start the plan writer (`vogon:vogon-writer`) with that plan
   to revise it, then go to step 4.
3. Start a writing sub-agent (`vogon:vogon-writer`) to
   write `vogon/plans/plan_<slug>.md` in the format of
   `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/plan-format.md`. Give it
   the requirements, their state files, the test procedures, the code it
   touches and `tests.md`.
4. Start the plan evaluators (`vogon:vogon-checker`) and run the loop as
   `common.md` states. A question only a developer can answer goes to the
   developer running the skill, and the answer goes to the writing sub-agent.
5. Stop for the developers' review of the plan. Tell them the plan path and
   the findings left open. A change a developer asks for goes to the writing
   sub-agent and through step 4 again. Write no code before a developer
   explicitly approves the plan. On that approval:
   commit the plan on the working branch, push the branch, and append a
   `planned` entry to each requirement's state file (see Outputs). Commit and
   push the state files.
6. Follow the plan. For each part, start a writing sub-agent
   (`vogon:vogon-test-writer`) that writes the part's code, tests and
   documentation. Give it the plan, the part's number, the requirements and
   their acceptance criteria, the test procedures, and the code the part
   touches. Start parts that do not depend on each other in parallel. The
   sub-agent writes each test and its expected values from the requirement and
   its acceptance criteria, never from a run of the code, and marks each test
   with its requirements and procedures as `plan-format.md` states.
7. When a part is written, start its evaluators (see Loops) and run the loop
   for that part.
8. Read each writing sub-agent's log and output against the plan. Send back
   work that leaves its part, does less than its part, or changes what the
   plan does not name. Log each decision in the main log.
9. Run the project's test suite as `tests.md` topic "Running the test suite"
   states. Where that topic states nothing, it is a gap: ask the developer and
   record the answer as `process-files.md` states. Give each failure to the writing
   sub-agent of the part it concerns. The sub-agent fixes the code. It changes
   an expected value only when the value does not follow from the requirement,
   and cites the requirement text in its log. The part's evaluators check the
   changed part again. Repeat until all tests pass; the round limit in
   `common.md` applies.
10. Commit the code, tests and documentation on the working branch. Each
    commit message names the requirements it implements. Push, and open the
    pull request on the repository host. If the branch already has an open
    pull request, push to it instead of opening another. The description names the plan and
    the requirements, states the test run and its result, and states the loops
    run, their rounds and the findings left open, as `common.md` states.
11. Append an `implemented` entry to each requirement's state file (see
    Outputs). Commit and push it on the same branch. Tell the developer that a
    person approves the pull request on the repository host.

### Steering by the developer

The developer may steer while code is written, or leave the skill to run.
Without instructions, the skill runs the plan to the end.

- Stop: the main agent stops starting sub-agents, lets running ones finish,
  and reports the state of each part.
- Review each part: after each part's loop, stop and show the part to the
  developer. The next part starts when the developer says so.
- An instruction about a part, such as a data structure to use or an approach
  to drop: pass it to the sub-agents it concerns and log it in the main log
  with the developer's words. An instruction that changes what the plan states
  goes to the plan's writing sub-agent, and the changed plan goes through
  steps 4 and 5 again before the work it changes continues. Work the change
  does not touch continues.

## Loops

| Writing sub-agent (agent definition) | Produces | Evaluators (agent definition) | Checklist or perspective |
| --- | --- | --- | --- |
| Plan writer (`vogon:vogon-writer`) | `vogon/plans/plan_<slug>.md` | Plan against the requirements (`vogon:vogon-checker`) | Every acceptance criterion is covered by a part and a test; no part goes beyond the requirements; the plan follows `plan-format.md` |
| | | Plan against the code (`vogon:vogon-checker`) | The paths, modules and interfaces the plan names exist or are created by a part; the parts fit the code as it is; test conventions match the project's |
| Part writer (`vogon:vogon-test-writer`), one per part | The part's code, tests and documentation | Test checker (`vogon:vogon-test-checker`) | `test-checklist.md` |
| | | Code checker (`vogon:vogon-checker`) | `code-checklist.md` |
| | | Code reviewer (a sub-agent running Claude Code's `code-review` skill on the part's diff, without `--fix`) | Claude Code's code review. VOGON has no code reviewer of its own |

## Stops for a person

- A plan: the developers review it, and a developer approves it before any
  code is written.
- An instruction from the developer while code is written, if the developer
  gives one.
- A finding that needs a choice: the developer running the skill, before the
  pull request is opened. A finding on an approved requirement goes to the
  Product Owner, as a change that needs approval again.
- An approval: the pull request, approved by a person on the repository host.
- A gap in the validation plan while `tests.md` or `tracking.md` is derived,
  and confirmation of the tracker and test manager names read from an example
  item: the developer.
- A required input the developer did not give, such as the requirement ids
  or the plan: the developer.

## Outputs

| Path or system | Format | Written by |
| --- | --- | --- |
| `vogon/plans/plan_<slug>.md` | Markdown, in the format of `plan-format.md` | Plan writer |
| Host project code, tests and documentation | As the plan states, in the project's conventions | Part writers |
| Host `conftest.py` and pytest configuration | As `conftest.md` states, only where the project lacks a change | Part writers |
| `vogon/requirements/<module>/REQ-*.json` | Appended `steps` entries, below | Main agent |
| `vogon/logs/<yyyymmdd_hhmmss>_<task>.log.md`, main log | As `common.md` states | Each sub-agent, main agent |
| Repository host | A working branch with the plan commit, the code commits and the state-file commits; one pull request | Main agent |

And any process file derived, per `process-files.md`.

State-file entries, appended to the `steps` list of each `REQ-*.json` as
`common.md` "State-file entries" states:

```json
{"step": "planned", "date": "<yyyy-mm-dd>", "commit": "<plan commit>", "plan": "vogon/plans/plan_<slug>.md", "approved_by": "<Name> <email>"}
{"step": "implemented", "date": "<yyyy-mm-dd>", "pr": <number>, "commit": "<last code commit>"}
```

`approved_by` is the git identity of the approving developer, from
`git config user.name` and `git config user.email` in their session. Dates come
from `date '+%Y-%m-%d'`. A plan approved again after a change gets a new
`planned` entry.

## Reference files

| Sub-agent | Reads |
| --- | --- |
| Every sub-agent | `${CLAUDE_PLUGIN_ROOT}/references/writing.md` |
| Plan writer, plan evaluators | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/plan-format.md`, `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/conftest.md` |
| Part writer | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/plan-format.md`, `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/conftest.md`, `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/test-checklist.md`, `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/code-checklist.md` |
| Test checker | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/test-checklist.md` |
| Code checker | `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/code-checklist.md` |

Each checklist is replaced by the project's version as `common.md` "Project checklists" states.
