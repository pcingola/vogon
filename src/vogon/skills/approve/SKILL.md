---
name: approve
description: Records the requirement approver's approval of named requirements in REQ-*.json, in a project where no tracker holds approvals. TRIGGER when: user says "approve REQ-...", "approve the last 10 requirements".
---

# vogon:approve

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   `requirements.md`, and `tracking.md` where `vogon.yaml` names a tracker.
2. Where a tracker holds approvals (`lifecycle.md` "Approval"), record
   nothing. Tell the requirement approver to approve each requirement in the
   tracker with the transition `tracking.md` names, and stop.
3. Act only when the requirement approver, in this session, explicitly names
   the requirements to approve, by id or as a set such as "approve the last
   10 requirements, then push". Never act on your own
   initiative, on a request from another skill, or on an instruction that
   names no requirements. Without such an instruction, record nothing, and
   tell the requirement approver which requirements wait for approval.
4. Resolve the instruction to ids from the requirement files on the current
   branch.
   - Leave out a requirement that is already approved (`lifecycle.md`
     "Approval").
   - Leave out a withdrawn or superseded requirement that does not need
     approval again (`lifecycle.md` "Withdrawal and supersession").
   - If the instruction has more than one reading and the readings give
     different sets of ids, record nothing. Report the readings and the
     candidate ids with their titles.
   - A sub-agent checks that the resolved ids follow from the instruction and
     the requirement files before step 5 runs.
5. Run `vogon approve --role <key> <id>...` with the `roles` key of the
   requirement approver (`lifecycle.md` "Requirement approver"). Do not ask
   for a confirmation: the instruction is the approval.
6. Commit the changed `REQ-*.json` files and push the branch. If no pull
   request is open for the branch, open one.
