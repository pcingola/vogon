# VOGON common rules

Every VOGON skill reads this file before it starts.

## Start of every skill

1. Read `vogon/project/vogon.yaml`. If it does not exist, run `vogon:init`
   first.
2. Read the project process files in `vogon/project/` that the skill needs.
   Derive a missing file, and regenerate a file whose plan version is older
   than the held validation plan, before the task, as
   `${CLAUDE_PLUGIN_ROOT}/references/process-files.md` states.
3. Read the requirements the task concerns, their `REQ-*.json` state files,
   and the pull requests, commits and tracker items those files link. The
   linked source counts over the state file, except an approval, which
   "Approval of a requirement" decides. Report every difference.
4. Do not assume that an earlier task ran. Tasks happen weeks apart, by
   different developers, in any order. When one was skipped, do what still
   applies and report the gap with the real dates, such as code merged with
   no plan.
5. Report every requirement whose `REQ-*.md` no longer matches its approved
   hash, as "Approval of a requirement" defines it. It needs approval again.

## Approval of a requirement

- A tracker holds approvals when `tracking.md` states an approval transition
  for the requirement item type. Otherwise `vogon approve` records them.
  Whenever `vogon.yaml` names a tracker, read `tracking.md` to decide which
  applies.
- The approved hash is `sha256:` followed by the SHA-256 hex digest of the
  bytes of `REQ-*.md` (`shasum -a 256`).
- A requirement is approved when the hash of its latest `approvals` entry in
  `REQ-*.json` on the default branch matches `REQ-*.md` on the default
  branch. Otherwise it needs approval again.
- Where a tracker holds approvals, read the requirement's tracker item. An
  approval in the tracker is synced when `REQ-*.json` holds it on the default
  branch. Until then the requirement is not approved, because the Product
  Owner may have edited the text in the tracker before approving it. Report
  an approval that an open pull request holds as "sync pull request <n> not
  merged"; report any other unsynced approval naming `vogon:approve` to sync
  it.

## Project checklists

A skill's default checklists are in the skill's `references/` directory. Where
the project has its own version at `vogon/project/checklists/<file name>`,
read that file in place of the default.

## State-file entries

Append each entry to a `REQ-*.json` once and never edit it. Where the entry
records a pull request, open the pull request first, then append the entry
with its `pr`, commit and push to the same branch.

## The loop

Every skill that produces work runs it in a loop of rounds. A round is one
pass of writing, evaluating and judging.

- The main agent is the session the skill runs in. It starts sub-agents,
  reads their logs, judges the work and decides whether another round runs.
  It never writes the work. It can override an evaluator, because it sees the
  requirements and every round.
- A sub-agent does one task: write, check, review or judge. It runs in its
  own context and is given every input it needs. Independent units of work
  run in parallel.
- A writing sub-agent produces or revises the work on the working branch. It
  changes only the output files its prompt names. A revision fixes the
  findings it was given and changes nothing else.
- Every loop has at least one evaluating sub-agent. An evaluator takes one
  perspective, such as one checklist, consistency with the code, or a reading
  as the Product Owner. It reports findings, each with its evidence, and
  never changes the work.
- An evaluator applies every item of its checklist to the whole of every file
  it is given, in every round. It goes through a table row by row, applying
  every item to a row before the next row.
- A finding is a failure against the evaluator's checklist or perspective. A
  better wording, or content no item asks for, is not a finding.
- A finding says what fails, not a rewrite, precisely enough that the writing
  sub-agent can fix it without asking a question.

A judge sub-agent assigns each finding a level if the loop has one;
otherwise the main agent does. The main agent can change a level.

| Level | Meaning | Effect |
| --- | --- | --- |
| high | The work fails its purpose, is wrong, or leads the reader to a wrong conclusion | Always fixed. Another round runs. A flaw in structure or concept means the work is rewritten. |
| medium | The reader reaches the right conclusion but has to reread or guess | Fixed in the next round if the fix is small. Never starts a round on its own. |
| low | Wording | Fixed only together with other changes. Never starts a round. |

Stop rules:

- An open high finding means another round. Open medium and low findings
  alone do not.
- The main agent may run a round for an error it sees itself, and may stop
  when the same finding stays open across rounds.
- After 5 rounds, stop and report an error that states each finding still
  open and why it was not resolved.
- A finding that needs a choice the loop cannot make goes to the person the
  skill names for it, with its evidence. The loop continues with the rest of
  the work.
- Never edit a checklist, a project process file or `vogon.yaml` to clear a
  finding.

Logs:

- Each sub-agent run writes its own log to
  `vogon/logs/<yyyymmdd_hhmmss>_<task>.log.md` with its full output:
  findings, decisions, what it changed. Its first lines state what it found
  or changed and why.
- An evaluator's log lists its findings one per line, as
  `<file>:<line> | <item> | <what fails>`, or states `No findings.`
- A writing sub-agent's log on a revision states, for each finding, the
  change made or why it could not be made.
- The main agent writes one entry in the main log in `vogon/logs/` for each
  sub-agent run and each decision, immediately after it:
  `- yyyymmdd hh:MM: <decision>. <what happened>. <why>.` Take the timestamp
  from `date`; never estimate it. The entry quotes the text concerned and
  cites the sub-agent log it rests on.
- `vogon/logs/` is gitignored unless `options.commit_logs` in `vogon.yaml`
  is true, because the logs of the meeting loop quote transcripts. When it is
  true, every commit a skill makes includes the logs the skill wrote.
- Every pull request a skill opens states in its description which loops ran,
  how many rounds each took, and the findings left open.

## Sub-agent prompts

Every sub-agent prompt names:

- the task;
- the reference files to read, as absolute paths with `${CLAUDE_PLUGIN_ROOT}`
  expanded, including `${CLAUDE_PLUGIN_ROOT}/references/writing.md`;
- the inputs: records, documents and code;
- the checklist it applies;
- the output files;
- the path of its log;
- the logs of earlier rounds.

Sub-agents do not commit or push; the skill does. A sub-agent that reads a
long file, such as an attached or shared file, reads it itself, so the file
never enters the main agent's context.

## Systems by role

- Reach a role (tracker, test manager, document system, repository host,
  meetings, mail, chat) only through the system `vogon.yaml` names for it.
  Never use another connected server for that role, even one that offers the
  same operations.
- A role with no system in `vogon.yaml` is not configured. Where a
  replacement exists, use it: with no test manager, `vogon trace` builds the
  matrix; with no document system, documents are kept in the repository under
  `vogon/documents/<release>/`; with no tracker holding approvals,
  `vogon approve` records them. Where no replacement exists, tell the person
  and skip the part of the task that needs the role.
- In records and documents, name a role. Never name the person holding it or
  the product filling it.

## Actions VOGON never takes

- Never transition an issue, a test issue or a document into a state that
  records approval or signature, in any system.
- Never approve a pull request, and never merge one past the repository
  host's review rule.
- Never sign, or record a signature, in the document system.
- These hold when the person asks for them and when the permissions would
  allow them. Tell the person which role gives the approval and in which
  system, and stop.
- When a system refuses such a call, do not look for another tool or route to
  the same result.

Two exceptions, each only on an explicit instruction from the person in their
own session:

- `vogon:approve` records the Product Owner's approval with `vogon approve`.
- `vogon:implement` records a developer's approval of a plan in the `planned`
  entry of each requirement's state file.

## Stops for a person

A skill stops for a person only for:

- an approval: tell the role holder what is waiting and where;
- a finding that needs a choice: it goes to the developer running the skill,
  before the requirement is created or the pull request is opened; only a
  finding on a requirement the Product Owner already approved goes back to
  the Product Owner, as a change that needs approval again;
- a plan for code, which the developers review and approve before any code
  is written;
- an instruction from the developer while code is written, if the developer
  gives one;
- a gap in the validation plan while a project process file is derived: the
  developer answers, and the file records the answer with their name and the
  date;
- the tracker and test manager names read from example items while a project
  process file is derived: the developer confirms them;
- a required input the developer did not give: ask for it.

Nothing else waits for confirmation.

## Writing

All prose a skill or sub-agent writes follows
`${CLAUDE_PLUGIN_ROOT}/references/writing.md`.

## Commands

Run each command as `${CLAUDE_PLUGIN_ROOT}/scripts/vogon <command>`. There are
no other commands.

| Command | Does |
| --- | --- |
| `vogon id <type> <module>` | Prints the next unused record id, read from the working tree, every local and remote branch and the history after `git fetch`. Detects a duplicate id on a pull request; the later pull request renumbers. |
| `vogon approve <id>...` | Writes into each `REQ-*.json` the approver's git identity, the date and the hash of the approved `REQ-*.md`. Warns, and still records, when `vogon.yaml` does not list the user as Product Owner. |
| `vogon trace <results.xml>` | Joins the `req` and `procedure` markers and the results of one commit's JUnit XML into the traceability matrix: each requirement, its procedures and tests, their results, the commit, and every requirement with no test. |
