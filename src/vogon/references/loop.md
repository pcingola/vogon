# Review loop

A skill produces its outputs in rounds: a writer writes or revises,
evaluating sub-agents check, and a judge sub-agent or the main agent assigns
levels to the findings. An output is checked when its loop ended with no open
high finding.

Every output a skill produces is evaluated by an evaluating sub-agent other
than the agent that wrote it. Logs are not evaluated.

## Roles

- The main agent is the session the skill runs in. It starts sub-agents,
  reads their logs, judges the work and decides whether another round runs.
  It can override an evaluator. It may write outputs itself; a different
  agent checks each one.
- A sub-agent does one task: write, evaluate or judge. Independent units of
  work run in parallel.
- A writing sub-agent produces or revises the work on the working branch. It
  changes only the output files its prompt names. A revision fixes the
  findings it was given and changes nothing else.

## Evaluators

- Every loop has at least one evaluating sub-agent. An evaluator takes one
  perspective, such as one checklist, consistency with the code, or a reading
  as the requirement approver. It reports findings, each with its evidence,
  and never changes the work.
- Every evaluator also applies `writing.md` to the prose it checks.
- An evaluator applies every item of its checklist to the whole of every file
  it is given, in every round. It goes through a table row by row, applying
  every item to a row before the next row.
- A finding is a failure against the evaluator's checklist or perspective. A
  better wording, or content no item asks for, is not a finding.
- A finding states what fails, precisely enough that the writing sub-agent
  can fix it without asking a question. It does not propose a rewrite.

## Output check

Before each push and each external write, one evaluating sub-agent checks
every output the main agent wrote since the previous check:

- each file against the file that defines it: `lifecycle.md` for state-file
  entries, `markers.md` for marker and `conftest.py` changes, the template for
  `vogon.yaml`;
- commit messages and the pull request description against `writing.md` and
  the facts of the run;
- tracker and test manager field values against the checked draft or
  `REQ-*.md` they come from, and against `tracking.md`.

When a skill already runs an evaluator before that push or write, that
evaluator also does the output check. The skill's Loops table names it.

After an external write, the main agent reads the item back, compares it with
what was written, and reports each difference.

## Levels and stop rules

In a loop with a judge sub-agent, the judge assigns each finding a level.
Otherwise the main agent does. The main agent can change a level.

| Level | Meaning | Effect |
| --- | --- | --- |
| high | The work fails its purpose, is wrong, or leads the reader to a wrong conclusion | Always fixed. Another round runs. A flaw in structure or concept means the work is rewritten. |
| medium | The reader reaches the right conclusion but has to reread or guess | Fixed in the next round if the fix is small. Never starts a round on its own. |
| low | Wording | Fixed only together with other changes. Never starts a round. |

- An open high finding means another round. Open medium and low findings
  alone do not.
- The main agent may run a round for an error it sees itself.
- After 5 rounds, stop and report an error that states each finding still
  open and why it was not resolved.
- The main agent may stop before round 5 when the same high finding stays
  open in consecutive rounds. It then reports each open finding and why it
  was not resolved.
- A finding that needs a choice goes to the developer (`common.md` "Stops for
  a person"). The loop continues with the rest of the work.

## Project checklists

A skill's default checklists are in the skill's `references/` directory. Where
the project has its own version at `vogon/project/checklists/<file name>`,
read that file in place of the default.

Never edit a checklist, a project process file or `vogon.yaml` to clear a
finding.

## Logs

- Each sub-agent run writes its own log to
  `vogon/logs/<yyyymmdd_hhmmss>_<task>.log.md` with its full output:
  findings, decisions, what it changed. Its first lines state what it found
  or changed and why.
- An evaluator's log lists its findings one per line, as
  `<file>:<line> | <item> | <what fails>`, or states `No findings.`
- A writing sub-agent's log on a revision states, for each finding, the
  change made or why it could not be made.
- After each sub-agent run and each decision, the main agent appends one
  entry to the main log in `vogon/logs/`:
  `- yyyymmdd hh:MM: <decision>. <what happened>. <why>.` Take the timestamp
  from `date`; never estimate it. The entry quotes the text concerned and
  cites the sub-agent log it rests on.
- `vogon/logs/` is gitignored, because the logs of meeting, mail and chat
  summaries quote the messages. When `options.commit_logs` in `vogon.yaml` is
  true, the directory is not ignored, and every commit a skill makes includes
  the logs the skill wrote.

## Pull request description

Every pull request a skill opens states in its description which loops ran,
how many rounds each took, and the findings left open.

## Sub-agent prompts

Every sub-agent prompt names the task, its inputs and output files, the
checklist it applies, its log path, the logs of earlier rounds, and its
reference files as absolute paths with `${CLAUDE_PLUGIN_ROOT}` expanded,
including `${CLAUDE_PLUGIN_ROOT}/references/writing.md`.

Sub-agents do not commit or push; the skill does. A sub-agent that reads a
long file, such as an attached or shared file, reads it itself, so the file
never enters the main agent's context.
