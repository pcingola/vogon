# The loop

Every VOGON skill that produces work runs it in a loop. A main agent repeats
rounds until the work meets its checklist or a limit is reached. A round is
one pass of writing, evaluating and judging.

## Main agent

The main agent is the Claude Code session in which the skill runs. It
coordinates the loop:

- It starts sub-agents, reads their logs, and decides whether another round
  runs.
- It never writes the work. Its context holds the task, file paths and the
  summaries of sub-agent logs, so it does not fill up over a long task.
- It reads the work and judges it. It can override an evaluator, because it
  sees the requirements and every round, and an evaluator does not.

## Sub-agents

A sub-agent does one task: write, check, review or judge. Each runs in its
own context and is given every input it needs: the task, the relevant records,
documents and code, the checklist it applies, and the logs of earlier rounds.
Independent units of work run in parallel, for example one summary per
meeting.

A writing sub-agent produces or revises the work on the working branch. A
revision fixes the findings it was given and changes nothing else.

Every loop has at least one evaluating sub-agent. An evaluator reads the work
and reports findings, each with its evidence. It never changes the work. Each
evaluator takes one perspective, such as one checklist, consistency with the
code, or a reading as the Product Owner.

## Findings

Each finding has one of three levels. A judge sub-agent assigns them if the
loop has one; otherwise the main agent does. The main agent can change a
level.

| Level | Meaning | Effect |
| --- | --- | --- |
| high | The work fails its purpose, is wrong, or leads the reader to a wrong conclusion | Always fixed. Another round runs. A flaw in structure or concept means the work is rewritten. |
| medium | The reader reaches the right conclusion but has to reread or guess | Fixed in the next round if the fix is small. Never starts a round on its own. |
| low | Wording | Fixed only together with other changes. Never starts a round. |

## Iteration and stop

The main agent decides whether another round runs, from the current work, the
logs of every round and its own reading. An open high finding means another
round. Open medium and low findings alone do not. The main agent may still run
a round for an error it sees itself, and may stop when the same finding stays
open across rounds.

After 5 rounds the main agent stops and reports an error that states each
finding still open and why it was not resolved.

A finding that needs a choice the loop cannot make goes to the person the
skill names for it, with its evidence. The loop continues with the rest of the
work.

## Logs

Each sub-agent run writes its own log, `<yyyymmdd_hhmmss>_<task>.log.md`,
with its full output: findings, decisions, what it changed. Its first lines
state what it found or changed and why.

The main agent writes one entry in the main log for each sub-agent run and
each decision, immediately after it, in the form
`- yyyymmdd hh:MM: <decision>. <what happened>. <why>.` The timestamp comes
from `date` and is never estimated. The entry quotes the text concerned and
cites the sub-agent log it rests on.

Logs are written to `vogon/logs/`, which is gitignored by default because the
logs of the meeting loop quote transcripts. A project may configure them to be
committed. Every pull request a skill opens states in its description which
loops ran, how many rounds each took, and the findings left open.
