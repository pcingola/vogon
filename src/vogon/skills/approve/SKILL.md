---
name: approve
description: Records the requirement approver's approval of named requirements in REQ-*.json, in a project where no tracker holds approvals. TRIGGER when: user says "approve REQ-...", "approve the last 10 requirements".
---

# vogon:approve

Records the requirement approver's approval of requirements in their
`REQ-*.json` state files, where no tracker holds approvals. The requirement
approver approves in their own Claude Code session, and the skill records the
approval with `vogon approve`. When a tracker holds approvals, the approval is
a transition of the tracker item. The skill then records nothing and tells
the requirement approver to approve in the tracker. Use it when the
requirement approver gives an approval instruction.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- The person's instruction in this session.
- `vogon/project/vogon.yaml`: the tracker, the repository host and the
  `roles` lists.
- `vogon/project/requirements.md` "Approval": the requirement approver.
- `vogon/project/tracking.md`, when `vogon.yaml` names a tracker: whether the
  tracker holds approvals, and the transition that records one.
- The requirements concerned, `vogon/requirements/<module>/REQ-*.md` and
  `REQ-*.json`.
- When a tracker holds approvals: the tracker item of each requirement, found
  by the `issue` field in its state file. Read its state and the date of its
  approval transition through the tracker.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   the Inputs name. The run works on a working branch only when it derives a
   process file. Otherwise it commits on the current branch.
2. Where a tracker holds approvals (`lifecycle.md` "Approval"), record
   nothing. Tell the requirement approver to approve each requirement in the
   tracker with the transition `tracking.md` names. List the requirements
   that are not approved, with their tracker keys, and go to step 8.
3. Check the instruction. Act only on an explicit instruction from the person
   in this session that names the requirements, by id or as a set that
   resolves to them, such as "approve the last 10 requirements, then push".
   Never act on your own initiative, on a request from another skill, or on
   an instruction that names no requirements. Without such an instruction,
   list the requirements that are not approved or need approval again, tell
   the requirement approver which requirements are waiting, and go to step 8.
4. Resolve the instruction to ids from the requirement files on the current
   branch.
   - Leave out a requirement that is already approved (`lifecycle.md`
     "Approval").
   - Leave out a withdrawn or superseded requirement that does not wait for
     approval (`lifecycle.md` "Withdrawal and supersession").
   - Report each requirement left out and why, and each id that names no
     requirement file.
   - Report each resolved requirement that is not on the default branch: its
     approval counts once its branch is merged.
   - If the instruction has more than one reading and the readings give
     different sets of ids, record nothing. Report the readings and the
     candidate ids with their titles, and go to step 8.
5. Compose the commit message of step 7, naming the resolved ids. Run the
   resolution evaluator (Loops) and correct the ids and the message from its
   findings. List the resolved ids and their titles for the person. Do not
   ask for a confirmation: the instruction is the approval.
6. Run `${CLAUDE_PLUGIN_ROOT}/scripts/vogon approve --role <key> <id>...`
   with the `roles` key of the requirement approver (`lifecycle.md`
   "Requirement approver"). If it warns, report the warning as the script
   printed it.
7. Commit the changed `REQ-*.json` files with the message of step 5. Push the
   branch to the repository host. If the push is rejected, report the
   rejection.
8. Where step 1 derived a process file and no pull request is open for the
   working branch, push it and open one (`process-files.md` step 7). Write a
   main log entry for each sub-agent run and each decision of this run
   (`loop.md` "Logs").

## Loops

| Writer | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Main agent | The id set of step 4 and the commit message of step 5 | Resolution evaluator, before `vogon approve` runs | The id set follows from the instruction and the requirement files, as step 4 states. The commit message names only the resolved ids. This evaluator is also the output check for the commit |

## Outputs

| Path or system | Format | When |
| --- | --- | --- |
| `vogon/requirements/<module>/REQ-*.json` | An `approved` entry appended to `steps` | No tracker holds approvals |
| Commit pushed to the current branch on the repository host | The changed state files | No tracker holds approvals and no process file derived |
| Branch and pull request on the repository host | The changed state files and the process file derived | No tracker holds approvals and a process file derived |
| Branch and pull request on the repository host | The process file derived | A tracker holds approvals and a process file derived |

The `approved` entry is defined in `lifecycle.md` "State file". The skill
writes nothing to the tracker and nothing from it.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`
- `${CLAUDE_PLUGIN_ROOT}/references/lifecycle.md`
- `${CLAUDE_PLUGIN_ROOT}/references/loop.md`
- `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, to derive a missing
  or outdated process file
