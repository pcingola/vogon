---
name: requirements
description: Drafts requirements, domain facts, constraints and decisions from meetings, mail, chat, documents and code, withdraws and supersedes requirements, and opens the pull request. TRIGGER when: user says draft requirements, requirements from a meeting, mail, chat, document or code, "withdraw REQ-", "supersede REQ-".
---

# vogon:requirements

Drafts records from the sources the developer names: meetings, mail threads,
chat channels, documents, and code with its commit history, pull requests and
tracker items. It writes a summary of each meeting, mail thread and chat
channel, files the reviewed summaries and the documents in `vogon/sources/`,
drafts and checks the records, and opens the pull request that sends the
requirements for approval. It also withdraws and supersedes requirements on
the developer's instruction.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- The sources the developer names, by id, by path or by a date range.
- An instruction to withdraw or supersede a requirement, by id, with the
  reason.
- `vogon/project/vogon.yaml`: the systems and the role holders.
- `vogon/project/requirements.md`: the requirement form, the risk fields and
  method, the requirement approver, and the steps the validation plan
  requires when an approved requirement changes.
- `vogon/project/tracking.md`, when `vogon.yaml` names a tracker.
- The existing records in `vogon/`, and the records in open pull requests.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   the Inputs name. If the developer named no source and no requirement to
   withdraw or supersede, ask for one.
2. When the developer gives a date range, a meeting, mail thread or chat
   channel in that range that a role holder in `vogon.yaml` attended or wrote
   in is likely the project's, whatever its title.
3. For each meeting, mail thread or chat channel, a writing sub-agent
   downloads it to its own directory `vogon/tmp/requirements/<n>/`, with `n`
   counting from 1, and writes
   its summary in `vogon/sources/` (`sources.md`).
4. For each attached, shared or named file, a writing sub-agent files the
   original and its markdown copy (`sources.md`), and writes an
   extract to its directory in `vogon/tmp/requirements/`: each statement that
   concerns the requirements, with its page or slide.
5. Run the review loop (`loop.md`) for each summary and each extract. A
   summary or extract with an open high finding is not committed, and no
   record is drafted from it.
6. A writing sub-agent, the records writer, drafts the records from the
   checked summaries and extracts, the markdown copies, the named code and
   the existing records, in the format of `records.md` and the requirement
   form of `requirements.md`. It applies each withdrawal and supersession the
   developer instructed (`lifecycle.md` "Withdrawal and supersession"). Any
   other change to an approved requirement goes in its log as a proposal and
   is not made until the developer agrees in step 8. A question no source
   answers goes in its log. Its log lists the sources of each record.
7. Run the review loop for the records.
8. Ask the developer about each finding that needs a choice, each question
   and each proposed change to an approved requirement in the records
   writer's log. For each requirement whose only source is code, ask the
   developer to confirm that the behaviour is intended. The records writer
   applies the answers, and the evaluators run again on the changed records.
9. Delete `vogon/tmp/requirements/`. Run `vogon id --check` and renumber
   each id it reports (`common.md` "Commands"). Commit, push and open the
   pull request. Its description lists the requirements drafted, changed,
   withdrawn and superseded, and those that need approval again.
10. Where a tracker is configured, create or update the tracker item of each
    new or changed requirement with the item type, fields and links
    `tracking.md` names.
    - For a changed approved requirement, also do each step listed in
      `requirements.md` "Change to an approved requirement".
    - For a withdrawn or superseded requirement, update the item
      (`lifecycle.md` "Withdrawal and supersession").
11. Append a `drafted` entry for each new requirement and a `changed` entry
    for each changed one (`lifecycle.md` "State file"). Commit and push.
12. Tell the developer which sources were used, which were left out and why,
    and which meetings had no transcript. Tell the requirement approver
    (`lifecycle.md`) which requirements wait for approval and where.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Summary writer, one per meeting, thread or channel | The summary | One per summary | `sources.md` "Meetings, mail and chat", against the download |
| Extract writer, one per file | The extract | One per extract | Each statement is in the file at its location; none that concerns the requirements is left out |
| Records writer | The records | Requirement checklist | `requirement-checklist.md`, against the drafted records, existing records, records in open pull requests and the cited sources |
| | | Record format | `records.md`, against the drafted records |

## Outputs

| Path or system | Format |
| --- | --- |
| `vogon/sources/<date>_<slug>.summary.md` | One summary per meeting, mail thread or chat channel, as `sources.md` states |
| `vogon/sources/<date>_<slug>.<ext>` and `<date>_<slug>.md` | Each filed document and its markdown copy, as `sources.md` states |
| `vogon/requirements/<module>/REQ-*.md`, `vogon/facts/`, `vogon/constraints/`, `vogon/decisions/` | Records, as `records.md` states |
| `vogon/requirements/<module>/REQ-*.json` | `drafted` and `changed` entries |
| Tracker item of each new or changed requirement | As `tracking.md` states |
| Repository host | The working branch and the pull request of step 9 |

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`: main agent and every
  sub-agent.
- `${CLAUDE_PLUGIN_ROOT}/references/loop.md`: main agent.
- `${CLAUDE_PLUGIN_ROOT}/references/lifecycle.md`: main agent, records writer.
- `${CLAUDE_PLUGIN_ROOT}/references/sources.md`: summary and extract writers
  and their evaluators.
- `${CLAUDE_PLUGIN_ROOT}/references/records.md`: records writer, requirement
  checklist and record format evaluators.
- `${CLAUDE_PLUGIN_ROOT}/skills/requirements/references/requirement-checklist.md`
  (`loop.md` "Project checklists"): requirement checklist evaluator.
- `${CLAUDE_PLUGIN_ROOT}/references/writing.md`: every sub-agent.
- `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`, to derive a missing or
  outdated process file.
