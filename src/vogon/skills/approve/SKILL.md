---
name: approve
description: Records the Product Owner's approval of named requirements in REQ-*.json, in a project where no tracker holds approvals. TRIGGER when: user says "approve REQ-...", "approve the last 10 requirements".
---

# vogon:approve

Records the Product Owner's approval of requirements in their `REQ-*.json`
state files, where no tracker holds approvals. The Product Owner approves in
their own Claude Code session, and the skill records the approval with
`vogon approve`. Where a tracker holds approvals, the approval is the
tracker's transition, and this skill records nothing: it tells the Product
Owner to approve in the tracker. Use it when the Product Owner gives an
approval instruction.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the start-of-skill reads, the loop, sub-agent prompts, systems by role, actions never taken, stops and commands.

## Inputs

- The person's instruction in this session.
- `vogon/project/vogon.yaml`: the tracker, the repository host and the Product
  Owner list.
- `vogon/project/tracking.md`, when `vogon.yaml` names a tracker: whether the
  tracker holds approvals, and the transition that records one.
- The requirements concerned, `vogon/requirements/<module>/REQ-*.md` and
  `REQ-*.json`.

## Steps

1. Do the start-of-skill reads in `common.md`. Read `tracking.md` only when
   `vogon.yaml` names a tracker. Before anything is derived or written, create
   a working branch from the default branch when `tracking.md` is missing or
   older than the held plan. Every later commit of the run goes on it. Then
   derive a missing file, as `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`
   states.
2. Where a tracker holds approvals, as `common.md` "Approval of a requirement"
   states, record nothing. Tell the Product Owner to approve each requirement
   in the tracker with the transition `tracking.md` names, list the
   requirements that are not approved as `common.md` defines it, with their
   tracker keys, and go to step 8.
3. Check the instruction. Act only on an explicit instruction from the person
   in this session that names the requirements, by id or as a set that
   resolves to them, such as "approve the last 10 requirements, then push".
   Never act on your own initiative, on a request from another skill, or on an
   instruction that names no requirements. Without such an instruction, list
   the requirements that have no approval entry or need approval again, tell
   the Product Owner they are waiting, and stop.
4. Resolve the instruction to ids from the requirement files on the current
   branch. Leave out a requirement that is `withdrawn` or `superseded_by`, and
   a requirement that is already approved, as `common.md` "Approval of a
   requirement" states; report each one left out and why. Report an id that names no
   requirement file. If the instruction has more
   than one reading and the readings give different sets of ids, record
   nothing: report the readings and the candidate ids with their titles, and
   stop.
5. List the resolved ids and their titles for the person. Do not ask for a
   confirmation: the instruction is the approval.
6. Run `${CLAUDE_PLUGIN_ROOT}/scripts/vogon approve <id>...` with the resolved
   ids. If it warns that the user is not listed as Product Owner in
   `vogon.yaml`, report the warning as the script printed it. The approval is
   recorded.
7. Commit the changed `REQ-*.json` files with a message that names the
   approved ids, on the working branch where step 1 created one, or else on
   the current branch. Push the branch to the repository host. If the push is
   rejected, report the rejection; never force the push. Where step 1 created
   a working branch, open a pull request for it, as `process-files.md` step 7
   states.
8. Where step 1 derived a process file and no pull request is open for the
   working branch, push it and open one, as `process-files.md` step 7 states.
   Write one main log entry for the resolution and one for the recording, or
   one for the report of step 2, as `common.md` states.

## Loops

This skill produces no work, so it runs no loop of its own. A process file
derived in step 1 goes through the loop in `process-files.md`.

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Process file writer, only to derive a missing or outdated process file | `vogon/project/tracking.md` | Support evaluator; completeness evaluator | As `process-files.md` states |

## Stops for a person

- An approval. Where the instruction names no requirements, tell the Product
  Owner which requirements wait for approval. Where a tracker holds
  approvals, tell the Product Owner which tracker items wait for the approval
  transition.
- An instruction with more than one reading: report the readings and the
  candidate ids to the Product Owner who gave it. It is not an approval until
  it names one set.
- A gap in the validation plan, or tracker and test manager names read from
  an example item, while `tracking.md` is derived: the developer running the skill answers or
  confirms, as `process-files.md` states.

## Outputs

| Path or system | Format | When |
| --- | --- | --- |
| `vogon/requirements/<module>/REQ-*.json` | An `approved` entry appended to `steps` | No tracker holds approvals |
| Commit pushed to the current branch on the repository host | The changed state files | No tracker holds approvals and no process file derived |
| Branch and pull request on the repository host | The changed state files and the process file derived, per `process-files.md` | No tracker holds approvals and a process file derived |
| Branch and pull request on the repository host | The process file derived, per `process-files.md` | A tracker holds approvals and a process file derived |
| `vogon/logs/` main log | Entries as `common.md` states | Always |

The `approved` entry is defined in `common.md` "State-file entries". The
skill writes nothing to the tracker and nothing from it.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`
- `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, to derive a missing
  `tracking.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/tracking.md`
