# VOGON common rules

Every VOGON skill reads this file before it starts.

## Topic files

Each topic has one file in `${CLAUDE_PLUGIN_ROOT}/references/`. A skill cites
the file and section of each rule it applies.

| File | Holds |
| --- | --- |
| `lifecycle.md` | The requirement approver; approval, change, withdrawal and supersession of a requirement; the `REQ-*.json` state file |
| `records.md` | The format, ids and paths of records and test procedures; expected values |
| `sources.md` | Held documents in `vogon/sources/` |
| `process-files.md` | Deriving `vogon/project/*.md` from the validation plan |
| `loop.md` | The review loop, logs, sub-agent prompts |
| `markers.md` | Requirement ids in tests, commits and code; the host `conftest.py` lines |
| `writing.md` | The writing standard for all prose a skill or sub-agent writes |

## Start of every skill

1. Read `vogon/project/vogon.yaml`. If it does not exist, run `vogon:init`
   first.
2. For each file in `vogon/project/` the skill needs, derive it if it is
   missing or outdated (`process-files.md`). Read it.
3. Read the requirements the task concerns, their `REQ-*.json` state files,
   and the pull requests, commits and tracker items those files link. When a
   pull request, commit or tracker item differs from the state file, the pull
   request, commit or tracker item is correct, except for approvals
   (`lifecycle.md` "Approval"). Report every difference.
4. Do not assume that an earlier task ran. When one was skipped, do the steps
   of the current task that do not depend on it. Report the skipped task with
   the real dates, for example code merged with no plan.
5. Report every requirement that needs approval again (`lifecycle.md`).

## Working branch

- A skill that writes to the repository creates a working branch from the
  default branch before its first write. Every commit of the run goes on it.
- A skill that ran `vogon:init` continues on init's working branch. Its
  commits go in init's pull request.
- When a skill must open a pull request and its branch has no commit, it
  first makes an empty commit whose message names the requirements or the
  release.

## Systems by role

The roles are the keys of `systems` in `vogon.yaml`: `repository_host`,
`tracker`, `test_manager`, `document_system`, `meetings`, `mail` and `chat`.

- Reach a role only through the system `vogon.yaml` names for it. Never use
  another connected server for that role, even one that offers the same
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
- Never approve a pull request, and never merge one past the repository
  host's review rule.
- Never sign, or record a signature, in the document system.
- These rules hold even when the person asks for the action and the
  permissions allow it. Tell the person which role gives the approval and in
  which system, and do not take the action.
- When a system refuses such a call, do not look for another tool or route to
  the same result.

Two exceptions, each only on an explicit instruction from the person in their
own session:

- `vogon:approve` runs `vogon approve` to record the approval of the
  requirement approver (`lifecycle.md`).
- `vogon:implement` records a developer's approval of a plan in the `planned`
  entry of each requirement's state file.

## Stops for a person

A skill stops for a person only for:

- a finding that needs a choice: ask the developer running the skill before
  the requirement is created or the pull request is opened;
- a finding that an approved requirement is wrong: ask the developer to agree
  to a change (`lifecycle.md` "Change to an approved requirement");
- a plan for code: the developers are asked to approve it. A developer
  approves it, asks for a change, or tells the skill to continue without
  approval;
- a gap in the validation plan, or confirmation of the names read from
  example tracker and test manager items, while a process file is derived (`process-files.md`);
- a required input the developer did not give: ask for it.

Nothing else waits for confirmation. A missing approval is reported, and the
skill continues.

## Commands

Run each command as `${CLAUDE_PLUGIN_ROOT}/scripts/vogon <command>`. There are
no other commands.

| Command | Does |
| --- | --- |
| `vogon id <type> <module>` | Prints the next unused record id, read from the working tree, every local and remote branch and the history after `git fetch`. With `--check`, reports each id added on the current branch that the default branch or another branch also uses. The skill renumbers each reported id before it opens its pull request: it takes a new id from `vogon id`, renames the file and changes every reference to the old id on the branch. |
| `vogon approve --role <key> <id>...` | Appends to each `REQ-*.json` an `approved` entry with the approver's git identity and the date. Warns, and still records, when `vogon.yaml` does not list the user under `roles.<key>`. `<key>` defaults to `product_owner`. |
| `vogon trace <results.xml>` | Reads the `req` and `procedure` properties and the results from the JUnit XML of one commit, and writes the traceability matrix: each requirement, its procedures and tests, their results, the commit, and every requirement with no test. |
