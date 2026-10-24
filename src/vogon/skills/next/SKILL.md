---
name: next
description: Lists the requirements ready to start and the requirements not ready, with the reasons, then assigns the chosen one. TRIGGER when: "what next", "what can I work on", "next requirement", "pick up work", "assign me REQ-".
---

# vogon:next

Lists the requirements that are ready for development, and the requirements
not ready, with the reasons, read from the state files and checked against
the pull requests, commits and tracker items they link. Then assigns the
requirement the developer chooses to that developer in the tracker. Use it
when a developer looks for the next requirement to work on.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- `vogon/project/vogon.yaml`: the tracker and the repository host.
- `vogon/project/requirements.md`: the requirement approver.
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
- The tracker item of each requirement whose `REQ-*.json` has an entry with
  an `issue` field: its approval transitions, priority, assignee and linked
  test procedures.
- The developer's choice: one or more requirement ids, given with the request
  or after the list. The choice is the instruction to assign.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   the Inputs name.
2. Leave out every requirement whose `status` is `withdrawn` or
   `{superseded_by: <id>}`. Report each one that waits for approval
   (`lifecycle.md` "Withdrawal and supersession").
3. For each remaining requirement, decide with the rules in `lifecycle.md`
   whether it is approved, whether its approval is stale, whether it is
   implemented and whether it is in progress. Report each entry those rules
   say to report.
4. Classify each requirement that is not implemented.
   - Ready: all of these hold:
     - it is approved, and the approval is not stale;
     - it is not in progress;
     - every requirement in its `depends_on` is implemented;
     - where `tests.md` requires test procedures before development, the
       procedures exist: a `test_procedures_written` entry links a merged
       pull request or a commit on the default branch, or the tracker item
       links the test procedure items `tracking.md` names;
     - where `tests.md` also requires their approval before development,
       each procedure is approved in the place `tests.md` names.
   - Not ready: any condition of Ready fails. Give each failing condition as
     a reason:
     - not approved;
     - not sent to the tracker: a tracker holds approvals and `REQ-*.json`
       has no entry with an `issue` field;
     - approval stale: `REQ-*.md` changed after the approval of `<date>`;
     - depends on `<id>`, not implemented; or depends on `<id>`, withdrawn or
       superseded;
     - test procedures required by `tests.md` before development not written;
     - test procedure `<id>` not approved, naming the role `tests.md` gives
       and the system where it approves;
     - test procedure approval cannot be read: `tests.md` names no place the
       skill can read;
     - open pull request `<number>` works on it;
     - plan `<path>` on branch `<name>`, not merged;
     - that plan not approved: its `planned` entry has no `approved_by`.
   - Report a fact, constraint or decision in `depends_on` that does not
     exist, is withdrawn or is superseded. The requirement can still be ready.
5. Order each list by tracker priority where the tracker holds one, highest
   first, then by id: module, then number compared numerically. Requirements
   with no priority follow those with one. Without a tracker, order by id.
6. Have the list evaluator check the lists (Loops), then write them in the
   session. State the order used, and that VOGON adds no ranking of its own.
   - Ready: id, title, tracker key, priority, current assignee, and the plan
     path where a `planned` entry names one, marked "not approved" where that
     entry has no `approved_by`.
   - Not ready: id, title, tracker key, priority, and every reason from step
     4. For a missing or stale approval, name the requirement approver
     (`lifecycle.md`) and the system where the approval is given.
   - Then the differences and gaps from steps 1 to 4, with their real dates.
7. Assign each requirement the developer chooses.
   - Where `vogon.yaml` names a tracker and the requirement's `REQ-*.json` has
     an entry with an `issue` field, set the assignee of that tracker item to
     the developer running the skill: the user the tracker connection is
     authenticated as.
   - Where the requirement has no entry with an `issue` field, or no tracker
     is configured, report the choice and write nothing.
   - Where the chosen requirement is not ready, assign it as chosen and
     repeat its reasons from step 4.
   - Where the chosen id is implemented, withdrawn, superseded or does not
     exist, report that and write nothing.
8. Write one main log entry per assignment and per choice reported
   (`loop.md` "Logs").
9. If step 1 derived a process file, push the working branch and open a pull
   request for it (`process-files.md` step 7). Otherwise open no pull
   request.

## Loops

| Writer | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Main agent | The lists of step 6 | List evaluator, before the lists are written | Each classification and each reason follows, by the rules of steps 3 and 4, from the state files and the pull requests, commits and tracker items they link. Where the choice came with the request, it also does the output check for the assignment |
| Main agent | The assignment, where the choice came after the lists | Output check, before the assignee is written | `loop.md` "Output check" |

## Outputs

| Path or system | Format |
| --- | --- |
| The session | The ready and not-ready lists, the order used, the differences and gaps, the assignment made or the choice reported |
| Tracker item of each chosen requirement | The assignee set to the developer running the skill |
| Working branch and pull request on the repository host, only when a process file is derived | The process file |

The skill writes no `REQ-*.md` and no `REQ-*.json`, and adds no step entry.
It writes no field other than the assignee, and performs no transition.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`
- `${CLAUDE_PLUGIN_ROOT}/references/lifecycle.md`
- `${CLAUDE_PLUGIN_ROOT}/references/loop.md`
- `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, to derive a missing or
  outdated process file
