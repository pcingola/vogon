---
name: requirements
description: Drafts requirements, domain facts, constraints and decisions from meetings, mail, chat, documents and code, and opens the pull request. TRIGGER when: user says draft requirements, requirements from a meeting, mail, chat, document or code.
---

# vogon:requirements

Drafts records from the sources the developer names: meetings, mail threads,
chat channels, documents, and code with its history, pull requests and issues.
It files the checked summaries and documents in `vogon/sources/`, drafts and
checks the records, and opens the pull request that sends the requirements for
approval.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. The process files
this skill needs are `requirements.md`, and `tracking.md` when `vogon.yaml`
names a tracker. Sub-agents read
`${CLAUDE_PLUGIN_ROOT}/references/sources.md` for sources and
`${CLAUDE_PLUGIN_ROOT}/references/records.md` for records.

## Steps

1. Create a working branch from the default branch. Do the start-of-skill
   reads. If the developer named no source, ask for one.
2. Where the developer gives a date range rather than ids, choose the
   meetings, mail threads and chat channels in that range by title,
   participants and content. A source attended by the role holders in
   `vogon.yaml` is likely the project's, whatever its title.
3. For each meeting, mail thread or chat channel, a writing sub-agent
   downloads it to its own directory `vogon/tmp/requirements/<n>/` and writes
   its summary in `vogon/sources/`, as `sources.md` states. The date is the
   meeting's date or the date of the latest message summarised.
4. For each attached, shared or named file, a writing sub-agent files the
   original and its markdown copy, as `sources.md` states, and writes to its
   directory an extract: each statement that bears on requirements, with its
   page or slide.
5. Check each summary and each extract in its loop. Delete each download once
   its summary is checked. A summary or extract with an open high finding is
   not committed, and no record is drafted from it.
6. A writing sub-agent drafts the records from the checked summaries and
   extracts, the markdown copies, the named code and the existing records,
   as `records.md` states, with the form, risk fields and method of
   `requirements.md`. A question no source answers goes in its log. A change
   to an approved requirement goes in its log as a proposal; the file is not
   changed. Its log lists the sources of each record.
7. Run the records loop.
8. Take each finding that needs a choice, each question and each proposed
   change to an approved requirement to the developer. Apply the answers and
   run the evaluators again on the changed records.
9. Delete `vogon/tmp/requirements/`. Run `vogon id --check` and renumber
   every id it reports. Commit, push and open the pull request. Its
   description lists the requirements drafted and changed, and those that
   need approval again.
10. Where a tracker is configured, create or update the tracker item of each
    new or changed requirement as `tracking.md` states, and for a changed
    approved requirement do what `requirements.md` states for a change.
11. Write the state files as `common.md` "State-file entries" states: a
    `drafted` entry for each new requirement, with `issue` where step 10
    created an item, and a `changed` entry for each changed approved
    requirement. Commit and push.
12. Tell the developer which sources were used, which were left out and why,
    and which meetings had no transcript. Tell the Product Owner which
    requirements wait for approval and where.

## Loops

| Writer | Evaluator | Checks |
| --- | --- | --- |
| Summary, one per meeting, thread or channel | One per summary | `sources.md` "Meetings, mail and chat", against the download |
| Extract, one per file | One per extract | Each statement is in the file at its location; none that bears on requirements is left out |
| Records | Requirement checklist | `requirement-checklist.md`, against the drafted records, existing records, records in open pull requests and the cited sources |
| | Record format | `records.md`, against the drafted records |
| | Code-only source | Lists each requirement whose only source is code. The developer confirms the behaviour is intended |
