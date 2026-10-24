# VOGON common rules

## Topic files

The topic files are in `${CLAUDE_PLUGIN_ROOT}/references/`.

| File | Holds |
| --- | --- |
| `lifecycle.md` | The requirement approver; approval, change, withdrawal and supersession of a requirement; the `REQ-*.json` state file |
| `records.md` | The format, ids and paths of records and test procedures; expected values |
| `sources.md` | Held documents in `vogon/sources/` |
| `process-files.md` | Deriving `vogon/project/*.md` from the validation plan |
| `markers.md` | Requirement ids in tests, commits and code; the lines a host project adds to `conftest.py` |
| `writing.md` | The writing standard for all prose a skill or sub-agent writes |

## Sub-agents

The main agent coordinates; sub-agents do the work, and a different sub-agent
reviews each piece, including what the main agent writes. A skill's default
checklists are in the skill's `references/` directory. Where
`vogon/project/checklists/<file name>` exists, it is read in place of the
default.

## Start of every skill

1. Read `vogon/project/vogon.yaml`. If it does not exist, run `vogon:init`
   first, and continue on init's branch, so the commits go in init's pull
   request. A skill works on a branch, never on the default branch.
2. For each file in `vogon/project/` the skill needs, derive it if it is
   missing or outdated (`process-files.md`). Read it.
3. Where a `REQ-*.json` disagrees with a pull request, commit or tracker item
   it links, the linked item is correct. For approvals, `lifecycle.md`
   "Approval" states which record holds them. Report every difference.
4. Do not assume that an earlier skill ran. When one did not, do the steps
   that do not depend on it. Report the skill that did not run, with the dates
   of what happened instead, such as the merge date of code that has no plan.
5. Report every requirement that needs approval again (`lifecycle.md`).

## Systems by role

The roles are the keys of `systems` in `vogon.yaml`: `repository_host`,
`tracker`, `test_manager`, `document_system`, `meetings`, `mail` and `chat`.

- Reach a role only through the system `vogon.yaml` names for it. Never use
  another connected MCP server for that role, even one that offers the same
  operations.
- A role with no system in `vogon.yaml` is not configured:

| Role not configured | What the skill does |
| --- | --- |
| Test manager | `vogon trace` builds the traceability matrix |
| Document system | Documents are kept in the repository in `vogon/documents/<release>/` |
| Any other role | Report that the role is not configured, and skip the steps that use it |

## Actions VOGON never takes

- Never move a tracker item, a test manager item or a document into a state
  that records approval or signature, in any system.
- Never approve a pull request, and never merge one that the repository
  host's review rules block.
- Never sign, or record a signature, in the document system.
- These rules hold even when the person asks for the action and the
  permissions allow it.
- When a system refuses such a call, do not look for another tool or route to
  the same result.

Exceptions, each only on an explicit instruction from the person in their
own session:

- `vogon:approve` runs `vogon approve` to record the approval of the
  requirement approver (`lifecycle.md`).
- `vogon:implement` records a developer's approval of a plan in the `planned`
  entry of each requirement's state file.

## Stops for a person

A skill stops for a person only for:

- a finding that needs the developer's choice: ask before the skill writes
  the record or opens the pull request;
- a finding that an approved requirement is wrong: ask the developer to agree
  to a change (`lifecycle.md` "Change to an approved requirement");
- a plan for code: the developers working on the requirements in the plan are
  asked to approve it;
- a topic the validation plan does not state, while a process file is derived
  (`process-files.md` step 5);
- confirmation of the names read from example tracker and test manager items
  (`process-files.md` step 2);
- a required input the developer did not give.

Nothing else waits for confirmation. A missing approval is reported, and the
skill continues.

## Commands

Run each command as `${CLAUDE_PLUGIN_ROOT}/scripts/vogon <command>`.

| Command | Does |
| --- | --- |
| `vogon id <type> <module>` | Prints the next unused record id, read from the working tree, every local and remote branch and the history after `git fetch`. With `--check`, reports each id added on the current branch that the default branch or another branch also uses. |
| `vogon approve --role <key> <id>...` | Appends to each `REQ-*.json` an `approved` entry with the approver's git identity and the date. Warns, and still records, when `vogon.yaml` does not list the user under `roles.<key>`. |
| `vogon trace <results.xml>` | Reads the `req` and `procedure` properties and the results from the JUnit XML of one commit, and writes the traceability matrix: each requirement, its procedures and tests, their results, the commit, and every requirement with no test. |
