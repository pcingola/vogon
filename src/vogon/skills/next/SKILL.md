---
name: next
description: Lists the approved requirements ready to start and the blocked ones with what blocks each, then assigns the chosen one. TRIGGER when: "what next", "what can I work on", "next requirement", "pick up work", "assign me REQ-".
---

# vogon:next

Lists the approved requirements that are ready for development, and the
requirements that are blocked, each with what blocks it, read from the state
files and checked against the pull requests, commits and tracker items they
link. Then assigns the requirement the developer chooses to that developer in
the tracker. Use it when a developer looks for the next requirement to work on.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the start-of-skill reads, the loop, sub-agent prompts, systems by role, actions never taken, stops and commands.

## Inputs

- `vogon/project/vogon.yaml`: the tracker and the repository host.
- `vogon/project/tests.md`: whether test procedures are written before
  development, and whether their approval is required before development.
- `vogon/project/tracking.md`, when `vogon.yaml` names a tracker: the item
  types, the approval transitions and the links.
- Every `vogon/requirements/<module>/REQ-*.md` and `REQ-*.json` on the default
  branch, after `git fetch`.
- The open pull requests on the repository host, with their titles,
  descriptions and commits.
- The `REQ-*.json` files on each pushed branch that is not merged, after
  `git fetch`, for their `planned` entries.
- The tracker item of each requirement whose `REQ-*.json` has an `issue`
  field: its approval transitions, priority, assignee and linked test
  procedures.
- The developer's choice: one or more requirement ids, given with the request
  or after the list. The choice is the input. Do not ask for a confirmation.

## Steps

1. Do the start-of-skill reads in `common.md`. Read `tests.md`, and
   `tracking.md` only when `vogon.yaml` names a tracker. If a process file is
   missing or older than the held plan, create a working branch from the
   default branch before anything is derived, then derive the file as
   `${CLAUDE_PLUGIN_ROOT}/references/process-files.md` states. Every later
   commit of the run goes on that branch.
2. Leave out every requirement whose `status` is `withdrawn` or
   `superseded_by`, or whose `REQ-*.json` has a `withdrawn` step.
3. Check each remaining requirement against the sources it links, as
   `common.md` states.
   - Approval. Decide whether the requirement is approved, has a tracker
     approval not yet synced, or needs approval again because its text
     changed, as `common.md` "Approval of a requirement" states. The approval
     is stale in the last case.
   - Implemented. The requirement is implemented when an `implemented` step
     links a merged pull request or a commit on the default branch, and the
     step is dated on or after the latest approval. An `implemented` step
     whose pull request is not merged, or whose commit is not on the default
     branch, does not count; report it. An `implemented` step dated before
     the latest approval means the approved change is not implemented; report
     it.
   - Work in progress. An open pull request works on the requirement when
     its title, its description or one of its commits names the requirement
     id. A pushed branch that is not merged works on the requirement when it
     holds a `planned` entry for it. A `planned` entry names no pull request.
4. Classify each requirement that is not implemented.
   - Ready: approved, the approval not stale, no open pull request or
     pushed branch works on it, and every record in `depends_on` is satisfied. A requirement in
     `depends_on` is satisfied when it is implemented. Where `tests.md`
     requires test procedures before development, a `test_procedures_written`
     step links a merged pull request or commit, or the tracker item links the
     test procedure items `tracking.md` names. Where `tests.md` also requires
     their approval before development, each procedure is approved in the
     place `tests.md` names.
   - Blocked: any condition of ready fails. Give each failing condition as a
     reason, from the data:
     - no approval;
     - approval not synced; run `vogon:approve`; or, where an open pull
       request holds the sync, sync pull request `<number>` not merged;
     - approval stale: `REQ-*.md` changed after the approval of `<date>`;
     - depends on `<id>`, not implemented; or depends on `<id>`, withdrawn or
       superseded;
     - test procedures required by `tests.md` before development not written;
     - test procedure `<id>` not approved, naming the role `tests.md` gives
       and the system where it approves;
     - test procedure approval cannot be read, where `tests.md` names no
       place the skill can read;
     - open pull request `<number>` works on it;
     - approved plan `<path>` on branch `<name>`, not merged.
   - Report a fact, constraint or decision in `depends_on` that does not
     exist, is withdrawn or is superseded. It does not block.
5. Order each list by tracker priority where the tracker holds one, highest
   first, then by id: module, then number compared numerically. Requirements
   with no priority follow those with one. Without a tracker, order by id.
6. Write the list in the session. State the order used, and that VOGON adds
   no ranking of its own.
   - Ready: id, title, tracker key, priority, current assignee, and the
     approved plan path where a `planned` step names one.
   - Blocked: id, title, tracker key, priority, and every reason from step 4.
     For a missing or stale approval, name the role that gives the approval
     and the system where it is given.
   - Then the differences and gaps from steps 1 to 4, with their real dates.
7. Assign each requirement the developer chooses.
   - Where `vogon.yaml` names a tracker and the requirement's `REQ-*.json` has
     an `issue` field, set the assignee of that tracker item to the developer
     running the skill: the user the tracker connection is authenticated as.
     Read the item back and report its assignee.
   - Where the requirement has no `issue` field, or no tracker is configured,
     report the choice and write nothing.
   - Where the chosen requirement is blocked, assign it as chosen and repeat
     its reasons from step 4.
   - Where the chosen id is implemented, withdrawn, superseded or does not
     exist, report that and write nothing.
8. Write one main log entry per assignment and per choice reported, as
   `common.md` states.
9. If step 1 derived a process file, push the working branch and open a pull
   request for it, as `process-files.md` step 7 states. Otherwise open no
   pull request.

## Loops

This skill produces no work, so it runs no loop of its own. A process file
derived in step 1 goes through the loop in `process-files.md`.

| Writing sub-agent (agent definition) | Produces | Evaluators (agent definition) | Checklist or perspective |
| --- | --- | --- | --- |
| `vogon:vogon-writer`, only to derive a missing or outdated process file | `vogon/project/tests.md` or `vogon/project/tracking.md` | `vogon:vogon-checker` | Support and completeness, as `process-files.md` states |

## Stops for a person

- A gap in the validation plan, or tracker or test manager names read from an
  example item, while `tests.md` or `tracking.md` is derived: the developer
  running the skill answers or confirms, as `process-files.md` states.

The list does not wait for anyone. The developer's choice is the input to
step 7, not a confirmation.

## Outputs

| Path or system | Format |
| --- | --- |
| The session | The ready and blocked lists, the order used, the differences and gaps, the assignment made or the choice reported |
| Tracker item of each chosen requirement | The assignee set to the developer running the skill |
| `vogon/logs/` main log | Entries as `common.md` states |
| Working branch and pull request on the repository host, only when a process file is derived | The process file, per `process-files.md` |

The skill writes no `REQ-*.md` and no `REQ-*.json`, and adds no step entry.
It writes no field other than the assignee, and performs no transition.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`
- `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, to derive a missing or
  outdated process file
- `${CLAUDE_PLUGIN_ROOT}/templates/tests.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/tracking.md`
