# Architecture

## Skills, and a little code

VOGON is a set of skills, slash commands and hooks for Claude Code, installed
as a library into a host project (`REQ-GEN-1`, `REQ-GEN-4`). The skills are the
rules, workflows and guidelines for developing software under GxP: what a
requirement looks like, how a transcript becomes records (`REQ-GEN-6`), how a
test case is drafted (`REQ-GEN-7`), what has to be true before a change is
registered in the tracker. They are the system.

The code is small and exists to serve the skills. It is a command line the
skills call where the answer has to be the same on every run: minting the next
id (`REQ-REC-7`), validating a record against the schema (`REQ-REC-1`),
resolving links (`REQ-REC-2`, `REQ-REC-4`), collecting test markers
(`REQ-TRC-1`), working out what the tracker should hold (`REQ-TRK-3`). An agent
can do any of those and will do most of them correctly most of the time, which
is not the standard a validation record is held to.

Claude Code does the work. VOGON calls no language model of its own, so the
command line can disagree with a draft because it did not produce it
(`DEC-005`, `REQ-GEN-3`, `FACT-005`).

What VOGON produces is documents: a requirement, a plan, a design
specification, a test specification, a risk assessment. Each is produced
complete, and each is a draft until a named person approves it (`REQ-GEN-2`).
VOGON never performs the approval (`CON-001`, `REQ-TRK-1`).

Change control, the assessment a board approves before a live validated system
is changed, is not in this version (`DEC-017`). The pipeline below covers
building the system and changing it; what a project does with a change once it
is live stays in that project's own procedure.

## The pipeline

VOGON covers the development cycle from the material a project starts with to
the evidence it ends with. Each step is a skill, a command or ordinary agent
work.

| # | Step | Produces | Built as |
| --- | --- | --- | --- |
| 1 | Install and configure | `vogon/`, `modules.yaml`, `vogon.yaml`, the skills in `.claude/` | Command `vogon init` |
| 2 | File the source material | Transcripts and documents in `vogon/sources/` (`REQ-GEN-6`, `REQ-REC-9`) | Skill `vogon-intake` |
| 3 | Draft the records | Requirements, facts, constraints and decisions in `vogon/` (`DEC-007`, `REQ-REC-1`) | Skill `vogon-records` |
| 4 | Review and accept | The record set checked for records that contradict or duplicate each other, a risk level and its reasoning per requirement, and records moved off `proposed` (`REQ-GEN-8`, `REQ-GEN-2`) | Skills `vogon-review` and `vogon-risk`, then a person |
| 5 | Register the requirements | Requirement issues in the tracker (`REQ-TRK-5`, `REQ-TRK-3`) | Skill `vogon-push` |
| 6 | Plan the change | `vogon/plans/plan_<slug>.md`: what will be built and how it will be tested, naming the records it implements (`DEC-014`, `REQ-GEN-10`) | Skill `vogon-plan` |
| 7 | Write the test cases | Test functions carrying markers (`REQ-TRC-1`, `REQ-TRC-8`) | Skill `vogon-tests`, in a subagent |
| 8 | Write the code | Source, and a commit naming the records it implements (`REQ-TRC-9`) | Agent work, following the plan |
| 9 | Run the tests and make them pass | Outcomes keyed to markers (`REQ-TRC-1`, `REQ-TRC-4`) | Command `vogon trace` |
| 10 | Register the tests and results, draft the documents | Test issues and results in the test manager, and the design and test specifications (`REQ-TRC-5`, `REQ-TRC-6`) | Skills `vogon-push` and `vogon-docs` |

Making a failing test pass has one direction it may not take. Expected values
come from the requirement and never from a run of the code, so a test is made
to pass by changing the code and not by moving the expected value to whatever
the code produced (`DEC-012`, `REQ-GEN-7`).

Three hooks, for the things that have to happen without anyone asking for them.
After a write under `vogon/`, the record checks run on that file. Before a
commit, a message naming no record is blocked (`REQ-TRC-9`). Before a call to
the tracker that would move an issue into an approved state, the call is
blocked (`CON-001`, `REQ-TRK-1`), which is what turns that constraint from an
instruction into something the agent cannot do by accident.

One subagent, the test author at step 7, with no read access to the
implementation, so the expected values can only come from the requirement.

## How VOGON is installed

VOGON is a Python package. A host project installs it with `uv add vogon` or
`pip install vogon`, and `vogon init` writes the skills, slash commands and
subagent definition into `.claude/`, adds the hook entries to
`.claude/settings.json`, and creates `vogon/` and `vogon.yaml`. Those files are
committed, so a change to them is reviewed like any other.

It is not distributed as a Claude Code plugin. The command line has to be
installed either way, so a plugin adds a second channel and a second version
number without removing the first. What this costs is a copy of the skills in
every host project, and an upgrade that is `uv add -U vogon`, `vogon init` and
a reviewed diff. `vogon check` reports where the installed files differ from
the copies in the package.

## Where things sit in a host project

The host project is a project VOGON is installed into, as against the VOGON
project, which is this repository.
[Vocabulary](vocabulary.md#the-two-projects) defines both.

```
<host-project>/
├── .claude/
│   ├── skills/vogon-*/   the skills. Claude Code loads them from here
│   ├── commands/vogon/   slash commands that start them
│   ├── agents/           subagent definitions
│   └── settings.json     hooks
├── vogon/
│   ├── modules.yaml      the module names the host project uses
│   ├── requirements/<module>/REQ-<MODULE>-NNN.md
│   ├── facts/FACT-NNN.md
│   ├── constraints/CON-NNN.md
│   ├── decisions/DEC-NNN.md
│   ├── sources/          held copies of every cited document, dated and flat
│   ├── plans/            what will be built, before it is. done/ holds the spent ones
│   └── out/              generated. Never hand-edited
├── tests/                test functions carrying requirement markers
└── vogon.yaml            configuration
```

All of it is plain text in git (`DEC-001`). There is no database.
Configuration sits in `vogon.yaml` at the host project's root, in the format
the records already use, and the layout above is the default, so a host project
that accepts the convention configures nothing (`REQ-CLI-3`).

`vogon/` is named for the tool because VOGON creates it, defines the format of
everything in it, mints the ids and validates it, which is what a directory a
tool owns in someone else's repository is named for. It is visible rather than
hidden because the records are reviewed in pull requests and read by people who
will never run the tool. The skills sit in `.claude/` instead, because that is
where Claude Code loads them from.

## Two stores

The specification lives twice.

In the host project's git repository, as markdown records under `vogon/`. This
is where the text is written and edited, where a change is reviewed in a pull
request, and where history is kept. It is cheap to change and it is not
controlled.

In the tracker — Jira, with Xray for tests — as issues under approval
(`CON-003`, `DEC-015`). This is where a named person approves a statement by
re-entering their credentials, and what an auditor is shown. It is expensive to
change and it is controlled. VOGON never performs the approval: an electronic
signature requires the signer to re-enter their own credentials (`FACT-001`),
so the transition stays a human action in the tracker (`CON-001`,
`REQ-TRK-1`).

In this version the markdown files are the source of truth. VOGON writes from
the repository to the tracker and reads the tracker's state back only to report
where the two have diverged: a record edited after its issue was approved
(`REQ-TRK-2`), a test marker naming a requirement that no longer exists
(`REQ-TRC-3`), an approval applied by the record's own author (`CON-002`,
`REQ-TRK-8`), a result imported from a build other than the one released
(`FACT-004`, `REQ-TRC-6`).

A later version may make the tracker the source of truth instead, with the
markdown dropped or kept as a cache of it. That reverses the direction, and
nothing is built now to anticipate it.

## Where the link between a test and a requirement is written

A requirement is verified by a test, and that link is written on the test: a
marker on the test function names the requirement ids it verifies (`DEC-006`,
`REQ-TRC-1`). Whoever changes a test is looking at the test, so they change the
marker in the same edit. The same link kept as a list of tests inside the
requirement file is edited by someone else, later, or not at all, so VOGON does
not use one.

Requirement ids are not written into the implementation source as comments.
Nothing checks a comment, so it stays behind when the code it described moves
or changes.

A commit message is short and names the records the change implements
(`REQ-TRC-9`). That is a different link from the marker: the marker says what
verifies a requirement, the commit says what built it.

Xray produces the coverage report and the traceability matrix, and VOGON
produces neither (`DEC-003`, `FACT-002`, `REQ-TRC-7`). What VOGON does is keep
the link Xray reports from: the Xray test issue exists, points at the right
requirement issue, and can be matched to the test that ran (`REQ-TRC-5`), and
the results are imported against those issues (`REQ-TRC-6`).

Xray can only report on what it holds, so a requirement that was never created
as an issue does not appear in its report at all. The checks that catch that
run locally, before anything is pushed: a marker naming an id that does not
exist (`REQ-TRC-2`), a marker on a withdrawn requirement (`REQ-TRC-3`), a
requirement carrying risk that no marker names (`REQ-TRC-4`). They fail the
build. They are not evidence.

## Reaching Jira and Xray

Jira and Xray are reached through the MCP servers the company provides. A
regulated company mandates both the product and the path to it, and the server
is often its own rather than the vendor's. The skills call that server's tools.

Every external system is named by the role it fills — the tracker, the test
manager, the repository host, the document system — and the product filling
each role is configuration (`DEC-011`). For each role VOGON states the
operations it needs from it, and a configured server that does not provide one
of them fails at install rather than at first use (`REQ-CLI-4`).

## Modules

A module names a part of the system a record belongs to, and appears in the
record's id. Each host project declares its own names in `vogon/modules.yaml`;
VOGON enforces only the shape of the name
(`DEC-016`, `REQ-REC-13`, `REQ-REC-14`). [Records](records.md) has the id
format.

The VOGON project's own modules:

| Module | Covers |
| --- | --- |
| `REC` | The record schema, id grammar, validation and indexes |
| `TRC` | Test markers, the link to Xray, result import |
| `TRK` | Reading and writing Jira and Xray issues, and reporting divergence |
| `GEN` | The instructions a coding agent follows to draft records, and the checks on what it produces |
| `CLI` | The command line and configuration |

## Version 0.1 assumes one stack

The first version is written against one set of tools and does not abstract
over alternatives:

- Python, for the host project and for VOGON itself
- GitHub, for the repository and pull requests
- Jira, for requirements under approval
- Xray, for tests, runs and coverage reporting
- Claude Code, as the coding agent

This is a deliberate narrowing (`DEC-004`).
Supporting a second tracker or a second test manager means an interface, and an
interface written before the second implementation exists is guesswork.

This version is built quickly, used, and then changed. Where a choice is
between the quick shape and the general one, it takes the quick shape.
