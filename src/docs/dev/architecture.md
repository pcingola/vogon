# Architecture

VOGON is a Claude Code plugin installed into a host project: the repository of
a regulated (GxP) software project. It carries out the [steps of the GxP
process](process/index.md) that do not need a person. The plugin is a set of
skills, the sub-agents they start, and scripts for the work that must give the
same result every time: `vogon id` allocates record ids, `vogon approve`
records an approval, and `vogon trace` builds the traceability matrix. All
model work is done by Claude Code; the Python code calls no language model
(`DEC-005`). The design follows the [principles](index.md#principles).

The rules every skill applies are in `src/vogon/references/common.md`, and each
skill's steps, loops, stops and outputs in `src/vogon/skills/<skill>/SKILL.md`.
[Vocabulary](vocabulary.md) defines the terms, and [Records](records.md) the
record format and the state file.

## Scope and roles

The host project is written in Python, tested with pytest and kept in git.
Skills name each external system by its role, never by product, and reach it
only through the system `vogon/project/vogon.yaml` names for that role, through
the MCP connectors of the session.

| Role | Example system | When no system is configured |
| --- | --- | --- |
| Repository host | GitHub | The skill tells the person and skips the steps that need it |
| Tracker | Jira, GitHub Issues | `vogon approve` records approvals |
| Test manager | Xray | `vogon trace` builds the matrix |
| Document system | The company's controlled document system | Documents are kept in the repository, in `vogon/documents/<release>/` |
| Meetings, mail, chat | Teams, Outlook, Slack | The skill tells the person and skips that source |

A tracker holds approvals when `tracking.md` states an approval transition for
the requirement item type. An approval recorded by `vogon approve` carries the
approver's git identity, which the approver does not re-enter at approval, so
it is not an electronic signature under 21 CFR Part 11. A tracker or test
manager transition is one only when the workflow makes the approver re-enter
their credentials at that transition; `vogon:init` reports each approval
transition that does not.

VOGON never decides an approval and never signs (`CON-001`). A change to a live
system is approved in the host project's own change control system, and its
requirements, tests and documents go through the same skills (`DEC-026`).

## Skills

One skill per task a person starts. Each runs in the main Claude Code session.

| Skill | Does | Process page |
| --- | --- | --- |
| `vogon:init` | Writes `vogon.yaml`, files the validation plan, adds the `.gitignore` and `conftest.py` lines | [Setup](process/setup.md) |
| `vogon:requirements` | Drafts and checks records from meetings, mail, chat, documents and code; creates tracker items where a tracker is configured | [Requirements from sources](process/requirements.md) |
| `vogon:approve` | Records the Product Owner's approval of the requirements they name, or syncs approvals from the tracker | [Approving requirements](process/approval.md) |
| `vogon:next` | Lists ready and blocked requirements, assigns the chosen one in the tracker | [Planning](process/planning.md) |
| `vogon:tests` | Writes the test procedures of approved requirements, as `tests.md` states | [Test procedures](process/test_procedures.md) |
| `vogon:implement` | Writes the plan, then the code, tests and documentation | [Planning](process/planning.md), [Code, tests and documentation](process/implementation.md) |
| `vogon:release` | Drafts the validation documents of a release commit, produces the matrix, files the evidence | [Release documents](process/documents.md) |

The default checklists are in `src/vogon/skills/requirements/references/`,
`src/vogon/skills/tests/references/` and `src/vogon/skills/implement/references/`.
A project replaces one with a file of the same name in
`vogon/project/checklists/`.

## Start of a skill

Tasks happen weeks apart, by different developers, in any order, so a skill
does not assume an earlier task ran. Every skill except `vogon:init` first
reads the process files it needs, deriving any that is missing or outdated,
then the requirements it concerns, their state files and the sources those
link, and reports every difference. When a task was skipped, the skill does
what still applies and reports the gap, such as code merged with no plan
(`common.md` "Start of every skill").

## The loop

Every skill that produces work runs it in a loop of rounds. The main agent, the
session the skill runs in, coordinates and never writes the work. Its context
holds the task, file paths and summaries of sub-agent logs, so it stays small
over a long task. Sub-agents write and evaluate in their own contexts, each
given every input it needs; independent units run in parallel. An evaluator
never changes the work. The main agent judges the result and can overrule an
evaluator, because it sees every evaluator's findings and the whole task, and
each evaluator takes one perspective.

The finding levels, the limit of 5 rounds and the log formats are in
`common.md` "The loop"; each `SKILL.md` lists its writers and evaluators in its
"Loops" table.

## Stops for a person

A skill stops for an approval, a plan review, a finding that needs a choice, a
gap in the validation plan, the tracker and test manager names read from example items, a
developer's instruction during coding, and a missing input. Nothing else waits
for confirmation. `common.md` "Stops for a person" states who each goes to.

## Project configuration and process files

`vogon/project/vogon.yaml` states the system for each role, the holders of each
approval role, the modules and the options. `vogon:init` writes it from
`src/vogon/templates/vogon.yaml`; it is YAML because the scripts read it.

The validation plan is filed in `vogon/sources/` as the original and a markdown
copy ([Sources](sources.md)). It stays the host project's controlled document,
and VOGON never edits either copy. The process files in `vogon/project/` are
VOGON's reading of the plan: `tracking.md` (tracker and test manager item
types, fields, approval transitions), `requirements.md` (requirement form, risk
method, approver and timing), `tests.md` (test procedures, test environment,
how the suite runs), `traceability.md`, `documents.md` (the documents VOGON
drafts) and `release.md`.

A skill derives a process file when it first needs it, and again when a newer
plan is held. Each statement cites its plan section; the developer answers a
gap, and the answer is recorded with their name and date. The procedure is in
`src/vogon/references/process-files.md`, the topics in `src/vogon/templates/`.

## Records

Records are markdown files under `vogon/` in the host repository
([Records](records.md)). Each takes its id from `vogon id`, never from choosing
a number. Two branches can take the same id before either pushes, so a skill
runs `vogon id --check` and renumbers before it opens a pull request.

Transcripts, mail and chat contain personal data, and some countries restrict
keeping meeting transcripts, so they are downloaded to the gitignored
`vogon/tmp/` and deleted after use; only a checked summary is committed to
`vogon/sources/`. Attached and shared files are kept as the original and a
markdown copy, and a long file is read only in a sub-agent's context. A
requirement whose only source is code describes current behaviour, defects
included, so the developer confirms it is intended
(`src/vogon/skills/requirements/SKILL.md`, step 8).

## Approval of requirements

The Product Owner approves requirements; `vogon.yaml` lists the holders under
`product_owner`. Where no tracker holds approvals, `vogon approve` records the
approval on the Product Owner's explicit instruction. Where a tracker holds
approvals, the Product Owner approves with the tracker's transition, and
`vogon:approve` copies the approval and the approved text into `REQ-*.json` and
`REQ-*.md` through a pull request. A skill works from a requirement's text only
once its approval is synced, and reports a tracker approval not yet synced and
an `approved` entry whose tracker item no longer shows approval. The procedure for
both cases is on [Approving requirements](process/approval.md).

A requirement is approved when `REQ-*.json` on the default branch has an
`approved` entry after its latest `changed` entry. A skill changes an approved
requirement only with the developer's agreement, and appends a `changed` entry,
so it needs approval again (`common.md` "Approval of a requirement").

## State of a requirement

`REQ-<MODULE>-<NUMBER>.json` records the steps done to the requirement:
drafted, approved, changed, planned, test procedures written, implemented,
released ([Records](records.md#state-file)). An entry other than `approved`
points at the pull request, commit or tracker item that holds the step. That
source is the evidence: a skill checks it before acting on an entry and reports
a difference. An approval is decided by the state file on the default branch
alone.

## Risk

Each requirement carries `gxp_impact` and `risk`, each with its reason, from
the moment it is drafted, so a reader can challenge a value. The values and
method are in `src/vogon/references/records.md`, overridden by
`requirements.md` where the validation plan states them; `requirements.md` also
states who approves them and when. Project-level risk documents the plan
lists, such as a risk log or a data integrity risk assessment, are separate
documents, approved by the roles the plan names.

## Tests

The pytest code is the test case. Each test names the requirements it verifies
in `@pytest.mark.req("REQ-PRN-12")`, and, where procedures exist, its procedure
in `@pytest.mark.procedure("<id>")`. The link is on the test because whoever
changes a test edits its marker in the same edit (`DEC-006`). Requirement ids
are not written in implementation code; commits name them. A test with no
marker is allowed and is not evidence. VOGON writes tests from the
requirement's intent, never from what the code does. It writes no mocks unless
the project authorizes them, because needing a mock indicates a problem in the
design.

A test procedure is a document of numbered steps, each with its expected
result. `tests.md` states whether the project needs procedures, whether they
are written before development or generated from the tests, and who approves
them. `vogon:tests` imposes no order of its own.

## Code from requirements

`vogon:implement` has a sub-agent write a plan, `vogon/plans/plan_<slug>.md`,
in the format of `src/vogon/skills/implement/references/plan-format.md`. No
code is written before a developer approves the plan; the approval is recorded
in the `planned` entry of each requirement's state file. The main agent then
has each part written by its own sub-agent and checked by the
test checklist, and a code reviewer that runs Claude Code's `code-review` skill
and then the code checklist. VOGON has no code reviewer of its own. A
developer's instruction that changes the plan sends it back for approval. All
tests pass before the pull request is opened.

## Traceability

`vogon:init` adds lines to the host `conftest.py` that copy each test's `req`
and `procedure` marker ids into the JUnit XML properties
(`src/vogon/references/conftest.md`). A test run records the commit it tested
as the suite name, and `vogon:release` reports a suite name that is not the
release commit. Where and how the suite runs is the project's choice; a pytest
run that names the suite this way is:

```
pytest --junitxml=results.xml -o junit_suite_name=$(git rev-parse HEAD)
```

A run on a working tree with uncommitted changes is reported, because the
commit then does not identify the code tested.

Where a test manager exists, VOGON uploads the JUnit XML unchanged and the test
manager produces the traceability report (`DEC-003`). Where none exists, `vogon
trace` joins the markers and results of one commit into the matrix, including
every requirement with no test. It manages no test cases and records no
approvals. The matrix is evidence, so it comes from this
join or from the test manager, never from a model.

## Release

`vogon:release` takes a release commit, a release name and the JUnit XML of a
test run on that commit. Sub-agents draft each document `documents.md` lists
from a read-only checkout of that commit, citing what each statement rests on,
and evaluators check them. The skill produces the matrix, files documents,
matrix and results, reads the filed copies back and tells each approver what
waits. A plan whose requirements all have a `released` entry moves to
`vogon/plans/done/`.
