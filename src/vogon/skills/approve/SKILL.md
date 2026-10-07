---
name: approve
description: Records the Product Owner's approval of named requirements in REQ-*.json, or syncs approvals from the tracker. TRIGGER when: user says "approve REQ-...", "approve the last 10 requirements", "sync approvals from the tracker".
---

# vogon:approve

Records approvals of requirements in their `REQ-*.json` state files. Where no
tracker holds approvals, the Product Owner approves in their own Claude Code
session, and the skill records the approval with `vogon approve`. Where a
tracker holds approvals, the skill copies each approval and the approved text
from the tracker into the repository. Use it when the Product Owner gives an
approval instruction, or to bring the state files up to date with the tracker.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the start-of-skill reads, the loop, sub-agent prompts, systems by role, actions never taken, stops and commands.

## Inputs

- The person's instruction in this session.
- `vogon/project/vogon.yaml`: the tracker, the repository host and the Product
  Owner list.
- `vogon/project/tracking.md`, when `vogon.yaml` names a tracker: the item type
  that holds a requirement, the fields that hold its text, and the transition
  that records its approval.
- The requirements concerned, `vogon/requirements/<module>/REQ-*.md` and
  `REQ-*.json`.
- Where a tracker holds approvals, each requirement's tracker item, read
  through the tracker, with its transition history and field history.

## Steps

1. Do the start-of-skill reads in `common.md`. Read `tracking.md` only when
   `vogon.yaml` names a tracker. Before anything is derived or written, create
   a working branch from the default branch when `tracking.md` is missing or
   older than the held plan, or when a tracker holds approvals, as `common.md`
   "Approval of a requirement" states. Every later commit of the run goes on
   it. Then derive a missing file, as
   `${CLAUDE_PLUGIN_ROOT}/references/process-files.md` states.
2. Where a tracker holds approvals, as `common.md` "Approval of a requirement"
   states, follow "A tracker holds approvals". Otherwise follow "No tracker
   holds approvals". Never follow both in one run.

### No tracker holds approvals

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
8. Write one main log entry for the resolution and one for the recording, as
   `common.md` states.

### A tracker holds approvals

3. If the person asks the skill to approve a requirement, do not record it.
   Tell the Product Owner to approve it in the tracker with the transition
   `tracking.md` names, and continue with the sync.
4. Select the requirements: those the person names, or every `REQ-*.json`
   with an `issue` field. Report each active requirement with no `issue`
   field: it has not been sent to the tracker.
5. For each selected requirement, read its tracker item. For each transition
   that `tracking.md` names as the approval of a requirement and that has no
   entry in `approvals` with the same date and approver, on the default branch
   or in an open pull request:
   1. Take the approved text: the values of the fields `tracking.md` names
      for the requirement text, the acceptance criteria and the risk fields,
      as they were at the time of the transition. If the field history does
      not show them at that time, record nothing for the requirement and
      report it.
   2. If the approved text differs from `REQ-*.md`, replace each block or
      frontmatter field of `REQ-*.md` with the value of the tracker field that
      holds it, word for word. If a value cannot be placed in one block or
      field, record nothing for the requirement and report it to the
      developer with both texts.
   3. Append an approval entry to `REQ-*.json` as Outputs and `common.md`
      "State-file entries" state. Take
      `hash` from `REQ-*.md` as written in step 5.2, as `common.md` "Approval
      of a requirement" states.
   4. If the approver is not listed in `vogon.yaml` under the role
      `tracking.md` names for the transition, report it.
6. Report each tracker item that left the approved state after an approval
   entry was recorded for it. Leave the entry as `common.md` "State-file
   entries" states.
7. If any file changed, commit the changed `REQ-*.md` and `REQ-*.json` files
   on the working branch step 1 created, and open a pull request on the
   repository host.
   The description lists each requirement synced with its tracker key,
   approver and date, quotes each text copied from the tracker with the text
   it replaced, states that no loop ran on the records, and lists every
   report from steps 4 to 6. A person merges it.
8. Write one main log entry per requirement synced or reported, as
   `common.md` states.

## Loops

This skill produces no work, so it runs no loop of its own. A process file
derived in step 1 goes through the loop in `process-files.md`.

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Process file writer, only to derive a missing or outdated process file | `vogon/project/tracking.md` | Support evaluator; completeness evaluator | As `process-files.md` states |

## Stops for a person

- An approval. Where no tracker holds approvals and the instruction names no
  requirements, tell the Product Owner which requirements wait for approval.
  Where a tracker holds approvals, tell the Product Owner which tracker items
  wait for the approval transition.
- An instruction with more than one reading: report the readings and the
  candidate ids to the Product Owner who gave it. It is not an approval until
  it names one set.
- Tracker text that cannot be placed in `REQ-*.md`: report it to the
  developer running the skill, with both texts.
- A gap in the validation plan, or tracker and test manager names read from
  an example item, while `tracking.md` is derived: the developer running the skill answers or
  confirms, as `process-files.md` states.

## Outputs

| Path or system | Format | When |
| --- | --- | --- |
| `vogon/requirements/<module>/REQ-*.json` | An entry appended to `approvals` | When an approval is recorded or synced |
| `vogon/requirements/<module>/REQ-*.md` | Blocks and frontmatter fields replaced with the approved text from the tracker | A tracker holds approvals |
| Commit pushed to the current branch on the repository host | The changed state files | No tracker holds approvals and no process file derived |
| Branch and pull request on the repository host | The changed state files and the process file derived, per `process-files.md` | No tracker holds approvals and a process file derived |
| Branch and pull request on the repository host | The changed records, with the description in step 7 of "A tracker holds approvals", and any process file derived, per `process-files.md` | A tracker holds approvals |
| `vogon/logs/` main log | Entries as `common.md` states | Always |

An approval entry has these fields:

- `by`: the approver as `Name <email>`. Without a tracker, the git identity
  `vogon approve` reads. With a tracker, the user who performed the
  transition, as the tracker records them.
- `date`: the date of the approval, `yyyy-mm-dd`. With a tracker, the date of
  the transition.
- `hash`: the approved hash, as `common.md` "Approval of a requirement"
  states.
- `via`: `vogon approve` without a tracker; the tracker's name from
  `vogon.yaml` with a tracker.

Entries follow `common.md` "State-file entries". The skill writes nothing to
the tracker.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`
- `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, to derive a missing
  `tracking.md`
- `${CLAUDE_PLUGIN_ROOT}/templates/tracking.md`
