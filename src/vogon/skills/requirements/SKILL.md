---
name: requirements
description: Drafts requirements, domain facts, constraints and decisions from meetings, mail, chat, documents and code, and opens the pull request. TRIGGER when: user says draft requirements, requirements from a meeting, mail, chat, document or code.
---

# vogon:requirements

Drafts records (requirements, domain facts, constraints and decisions) from
any source the session's MCP connectors reach: meetings, mail threads, chat
channels, documents, and code with its git history, pull requests and issues.
It files checked summaries and the attached files in `vogon/sources/`, drafts
the records with their risk fields, checks them, and opens the pull request
that sends the requirements for approval. Use it when the developer asks for
requirements from a meeting, a mail thread, a chat channel, a document or
existing code.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the
start-of-skill reads, the loop, sub-agent prompts, systems by role, actions
never taken, stops and commands.

## Inputs

- The sources the developer names: meetings, mail threads and chat channels
  (by id, title or date range), documents (by path or by their location in
  the document system), and code (paths, commits, pull requests, issues).
- `vogon/project/vogon.yaml`: the system for each role and the modules.
- `vogon/project/requirements.md`: requirement form, risk fields and method,
  approval, change to an approved requirement.
- `vogon/project/tracking.md`, when `vogon.yaml` names a tracker.
- The records already in `vogon/` and in open pull requests.

## Steps

1. Create a working branch from the default branch, before any process file
   is derived or anything is written. Every later commit of the run goes on
   it. Do the start-of-skill reads of `common.md`. The process files this
   skill needs are `requirements.md`, and `tracking.md` when a tracker is
   configured. If the developer named no source, ask for the sources, as
   `common.md` "Stops for a person" states.
2. Read the requirement checklist, `requirement-checklist.md`, as `common.md`
   "Project checklists" states.
3. Meetings, mail and chat. Where the developer names a date range and a
   topic rather than ids, choose the meetings, mail threads and chat channels
   in that range from their title, their participants and a summary of their
   content. Match the participants against the role holders `vogon.yaml`
   lists: a source attended by them is likely about the project, and
   one with none of them is likely not. Keep a source whose title looks
   unrelated when its participants and content are the project's. Then start
   one writing sub-agent per meeting, mail thread or chat channel, in
   parallel. Give each sub-agent its own
   directory, `vogon/tmp/requirements/<n>/`, where `<n>` is a number the main
   agent assigns and no other sub-agent of the run uses. Each:
   - downloads the transcript, thread or channel messages through the system
     `vogon.yaml` names for the role, to its directory;
   - writes a summary to `vogon/sources/<yyyy-mm-dd>_<slug>.summary.md`, named
     and with frontmatter as `sources.md` states, with `kind: summary`,
     `authority: informal`, the `participants`, and in `retrieved_from` the
     system and the source's id in it. The date is the meeting's date, or for
     a thread or channel the date of the latest message summarised. A
     statement proposed and then rejected or changed later in the same
     meeting, thread or channel is summarised as it ended. The summary holds
     nothing personal: no personal remarks, no health or HR matters, no
     opinions about people.
4. For each summary, start an evaluating sub-agent that checks the summary
   against its downloaded source: every statement of the summary is supported
   by the source, nothing in the source that bears on requirements is left
   out, each statement is as it ended, and nothing personal is in it. Run the
   loop. Delete each download once its summary is checked,
   and in every case before the skill ends. A summary left with an open high
   finding is not committed, and no record is drafted from it.
5. Attached and shared files. For each file attached to a mail, posted in a
   chat or shared in a meeting, and each document the developer names, start
   one writing sub-agent, in parallel, with its own directory
   `vogon/tmp/requirements/<n>/` as in step 3. Each:
   - downloads the file to its directory, and files the original in
     `vogon/sources/` with a markdown copy beside it, as `sources.md` states;
   - reads the markdown copy and writes an extract to `extract.md` in its
     directory: each statement in the file that bears on requirements, with
     its location, such as the page or slide.
6. For each extract, start an evaluating sub-agent that checks the extract
   against the file: each statement is in the file at the stated location,
   and no statement that bears on requirements is left out. Run the loop.
7. Draft the records. Start a writing sub-agent with the checked summaries,
   the checked extracts, the markdown copies, the code paths the developer
   named with their git history, pull requests and issues, and the existing
   records. It:
   - classifies each statement as `records.md` "Classifying a sentence"
     states, and writes a question it cannot answer from the sources into
     its log, not into a record;
   - writes each record in the format of `records.md`, a requirement in the
     form and with the risk fields and method of `requirements.md`, citing the
     markdown copies and summaries in `source`;
   - takes each id from `vogon id <type> <module>`, omitting the module for
     `FACT`, `CON` and `DEC`, and in a project without modules;
   - changes an existing record in place when a source changes it, and lists
     in its log each changed requirement that has an approval. A statement
     changed in a later meeting, thread or channel is recorded as the latest
     summary states it;
   - lists in its log, for each record, the sources and code it was drafted
     from.
8. Start the two evaluating sub-agents of the records loop (see Loops) and
   run the loop.
9. Take every finding that needs a choice, and every question from step 7, to
   the developer with its evidence, before any record is committed. Take a
   finding on a requirement that is approved, as `common.md` "Approval of a
   requirement" defines it, to the Product Owner instead, as a change that
   needs approval again. Give the answers to the writing sub-agent and run
   the evaluators again on the changed records.
10. Delete `vogon/tmp/requirements/`, with every download and extract in it.
    Commit the summaries, the filed originals and markdown copies and the
    records on the working branch step 1 created.
    Run `vogon id --check`. For each id it reports, take a new id from
    `vogon id`, rename the record and its state file, and change every
    reference to the old id on the branch. Push, and open the pull request on the
    repository host. The description lists the requirements drafted and
    changed, each changed requirement that needs approval again, and the loops
    run as `common.md` states.
11. Where a tracker is configured, create one tracker item per new
    requirement as `tracking.md` states: its item type, its fields for the
    text, the acceptance criteria and the risk fields, its links and its
    naming. For each changed requirement whose `REQ-*.json` has an `issue`
    field, set the text, acceptance criteria and risk fields of that tracker
    item to the new text, as `tracking.md` states. For each changed
    requirement that was approved, do in the tracker what `requirements.md`
    "Change to an approved requirement" states, with the transitions
    `tracking.md` names; where it names none, report that the item stays in
    its approved state.
12. Write beside each new requirement its state file `REQ-*.json` with the
    `id`, the tracker item's key in `issue` where step 11 created one, and one
    `drafted` entry with the date from `date '+%Y-%m-%d'` and the pull request
    number in `pr`, as `common.md` "State-file entries" states. Commit and
    push the state files to the same branch.
13. Tell the developer which sources were used, which were left out and why,
    and which meetings had no transcript.
14. Tell the Product Owner which requirements wait for approval, and where:
    the tracker items or the pull request with `vogon:approve`, as `common.md`
    "Approval of a requirement" decides.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| One per meeting, mail thread or chat channel | Summary in `vogon/sources/` | One per summary | The summary against its downloaded source: each statement supported, nothing bearing on requirements left out, each statement as it ended, nothing personal |
| One per attached, shared or named file | Original and markdown copy in `vogon/sources/`; extract in `vogon/tmp/requirements/<n>/` | One per extract | The extract against the file: each statement at its stated location, nothing bearing on requirements left out |
| Records | Records with risk fields | Requirement checklist | The checklist of step 2, against the drafted records, the existing records, the records in open pull requests and the cited sources |
| | | Code-only source | Reports every requirement whose only source is code, its git history, pull requests or issues, read from the writer's log and the record's `source`. The developer confirms that the behaviour is intended |

## Stops for a person

- A finding that needs a choice, a question no source answers, and a
  requirement whose only source is code: the developer running the skill,
  before any record is committed.
- A finding on a requirement the Product Owner already approved: the Product
  Owner, as a change that needs approval again.
- The approval of the drafted requirements: the Product Owner is told what is
  waiting and where.
- No source named: the developer running the skill is asked for the
  sources.
- A gap in the validation plan, and the confirmation of tracker and test
  manager names read from an example item, while `requirements.md` or `tracking.md` is derived:
  the developer, as `process-files.md` states.

## Outputs

| Path or system | Format | Written by |
| --- | --- | --- |
| `vogon/tmp/requirements/<n>/` | One directory per sub-agent: downloaded transcript, mail, chat or file; `extract.md`. Gitignored, deleted in step 10 | Writing sub-agents |
| `vogon/sources/<yyyy-mm-dd>_<slug>.summary.md` | Markdown with the frontmatter of step 3 | Summary writers |
| `vogon/sources/<yyyy-mm-dd>_<slug>.<ext>` and `.md` | The original file and its markdown copy, as `sources.md` states | File writers |
| `vogon/requirements/<module>/REQ-<MODULE>-<NUMBER>.md` | Requirement record, `records.md` | Records writer |
| `vogon/requirements/<module>/REQ-<MODULE>-<NUMBER>.json` | State file, `records.md`: `id`; `issue` where a tracker holds the item; `steps` with one entry `{"step": "drafted", "date": "<yyyy-mm-dd>", "pr": <number>}` | Main agent, after the pull request is opened |
| `vogon/facts/FACT-NNN.md`, `vogon/constraints/CON-NNN.md`, `vogon/decisions/DEC-NNN.md` | Records, `records.md` | Records writer |
| `vogon/logs/` | One log per sub-agent run, and the main log, as `common.md` states | Sub-agents; main agent |
| Repository host | Working branch and pull request | Main agent |
| Tracker | One item per new requirement, as `tracking.md` states; never transitioned into an approved state | Main agent |
| Tracker | The text, acceptance criteria and risk fields of the item of each changed requirement, set to its new text, as `tracking.md` states | Main agent |
| Tracker | For each changed requirement that was approved, the transitions `requirements.md` "Change to an approved requirement" states, as `tracking.md` names them; where it names none, a report that the item stays in its approved state | Main agent |

The pull request also carries any process file derived, per `process-files.md`.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`: the main agent.
- `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`: the main agent, when a
  process file is missing or older than the held plan.
- `${CLAUDE_PLUGIN_ROOT}/references/writing.md`: every sub-agent.
- `${CLAUDE_PLUGIN_ROOT}/references/sources.md`: summary and file writers and
  their evaluators, for file names, frontmatter and markdown copies.
- `${CLAUDE_PLUGIN_ROOT}/references/records.md`: the records writer and both
  records evaluators.
- `${CLAUDE_PLUGIN_ROOT}/skills/requirements/references/requirement-checklist.md`:
  the requirement checklist evaluator, as step 2 states.
