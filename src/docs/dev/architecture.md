# Architecture

VOGON is a Claude Code plugin installed into a host project: the repository of
a regulated (GxP) software project. It carries out the [steps of the GxP
process](#skills) that do not need a person. The plugin is a set of skills,
the sub-agents they start, and the commands `vogon id`, `vogon approve` and
`vogon trace` for the work that must give the same result every time. Claude
Code does all model work, and the Python code calls no language model, so
every command is deterministic and VOGON holds no model credentials
(`DEC-005`). The design follows the [principles](index.md#principles).

`src/vogon/references/common.md` holds the rules every skill applies and lists
the topic file in `src/vogon/references/` that holds each other rule. Each
skill's steps, loops and outputs are in `src/vogon/skills/<skill>/SKILL.md`.
[Vocabulary](vocabulary.md) defines the terms, and [Records](records.md)
describes the files under `vogon/`, including the state file.

## Scope and systems

Version 0.1 is developed and tested against one stack: a host project in
Python with pytest, GitHub as repository host, Jira as tracker, Xray as test
manager, and Claude Code. No abstraction layer is written before a second
implementation exists (`DEC-004`).

The host project's validation plan chooses its products, so a skill names
each external system by its role: repository host, tracker, test manager,
document system, meetings, mail and chat. It reaches a role only through the
system `vogon/project/vogon.yaml` names for it. The rules are in
`common.md` "Systems by role".

VOGON never moves an item into a state that records approval or signature,
because a signature requires the signer's own credentials (`CON-001`).
`common.md` "Actions VOGON never takes" lists these actions and the two
exceptions. An approval recorded by `vogon approve` carries the approver's
git identity, which the approver does not re-enter. It is therefore not an
electronic signature under 21 CFR Part 11. A tracker or test manager
transition is an electronic signature only when the workflow makes the
approver re-enter their credentials. `vogon:init` reports each approval
transition that does not.

A change to a live system is recorded and approved in the host project's own
change control system. VOGON writes no change record and no impact
assessment, and the change's requirements, tests, code and release documents
go through the same skills as the first release (`DEC-026`).

## Skills

One skill per task a person starts. Each runs in the main Claude Code session.

| # | Step | Skill | Produces | Approved by |
| --- | --- | --- | --- | --- |
| 1 | Configure | `vogon:init` | `vogon/project/vogon.yaml`, the validation plan in `vogon/sources/`, the `.gitignore` lines, the `conftest.py` lines and the marker registration | A person, on the pull request |
| 2 | File the sources | `vogon:requirements` | Checked summaries of meetings, mail and chat; filed documents with their markdown copies | |
| 3 | Draft and check the records | `vogon:requirements` | Requirements with acceptance criteria and risk fields; facts, constraints and decisions; withdrawals and supersessions | |
| 4 | Send the requirements for approval | `vogon:requirements` | The pull request with `REQ-*.md` and `REQ-*.json`; tracker items where a tracker is configured | |
| 5 | Approve the requirements | `vogon:approve`, or the tracker | An `approved` entry in `REQ-*.json`, or the tracker's approval transition where a tracker holds approvals | The requirement approver |
| 6 | Write the test procedures | `vogon:tests` | Test procedures, where `tests.md` requires them | The roles `tests.md` names |
| 7 | Choose a requirement | `vogon:next` | The ready and not-ready lists; the tracker item assigned | |
| 8 | Plan | `vogon:implement` | A checked plan, and a `planned` entry | A developer, when asked |
| 9 | Write the code, tests and documentation | `vogon:implement` | Checked code, tests and documentation, all tests passing, in one pull request | A person, on the repository host |
| 10 | Release | `vogon:release` | The documents `documents.md` lists, the traceability matrix and the results, filed | The roles `documents.md` names |

Different requirements are at different steps at the same time. Step 6 comes
before step 7 or after step 9, as `tests.md` states; a project that needs no
test procedures skips it. A change to a requirement after step 4 appends a
`changed` entry and returns the requirement to step 5.

No step waits for an approval (principle 3). `vogon:tests` and
`vogon:implement` work on a requirement that is not approved and report the
missing approval (`lifecycle.md` "Missing approval"). `vogon:next` lists such
a requirement as not ready, with the reason.

The default checklists are in the `references/` directory of the
`requirements`, `tests` and `implement` skills. Each is a separate file so
that a project replaces one with a file of the same name in
`vogon/project/checklists/` (`loop.md` "Project checklists").

## Start of a skill

Tasks happen weeks apart, by different developers, in any order, so a skill does
not assume an earlier task ran. It reads the process files, requirements and
state files it needs, does the steps that do not depend on a skipped task, and
reports each skipped task and each difference, such as code merged with no plan
(`common.md` "Start of every skill").

## The review loop

Every output a skill produces is checked by an evaluating sub-agent other than
the agent that wrote it (principle 6). The main agent, the session the skill
runs in, coordinates. Sub-agents write and evaluate in their own contexts,
each given every input it needs, so the main agent's context holds only the
task, file paths and summaries of logs and stays small over a long task. The
main agent may write an output itself, and a different agent checks it before
the next push or external write. An evaluator never changes the work. The
main agent judges the result and can overrule an evaluator. Each evaluator
takes one perspective, and the main agent sees every evaluator's findings and
the whole task.

The roles, the finding levels, the round limit and the log formats are in
`src/vogon/references/loop.md`. Each `SKILL.md` lists its writers and
evaluators in its "Loops" table.

## Stops for a person

A skill stops only for the cases `common.md` "Stops for a person" lists.
Nothing else waits for confirmation. A missing approval is not a stop: the
skill reports it and continues, and only a person approves (principles 3 and
4).

## Project configuration and process files

`vogon/project/vogon.yaml` names the system for each role, the holders of
each approval role, the modules and the options. `vogon:init` writes it from
`src/vogon/templates/vogon.yaml`. It is YAML because the commands read it.

The validation plan is filed in `vogon/sources/` as the original and a
markdown copy ([Sources](sources.md)). It stays the host project's controlled
document, and VOGON never edits either copy. The process files in
`vogon/project/` are VOGON's reading of the plan: `tracking.md`,
`requirements.md`, `tests.md`, `traceability.md`, `documents.md` and
`release.md`. Their topics are in their templates in `src/vogon/templates/`.

A skill derives a process file when it first needs it, and again when it is
outdated (`process-files.md` "When to derive a file"). Each statement cites the
plan section it rests on, so a reviewer can check it against the plan. A topic
the plan does not state is asked of the developer, and the answer is recorded
with their name and date. The procedure is in
`src/vogon/references/process-files.md`.

## Sources and records

Records are markdown files under `vogon/` in the host repository
([Records](records.md)), drafted from held documents and checked summaries
([Sources](sources.md)). A requirement whose only source is code describes
current behaviour, defects included, so the developer confirms that the
behaviour is intended (`src/vogon/skills/requirements/SKILL.md`, step 8).

## Requirement lifecycle

The rules for approval, change, withdrawal and supersession are in
`src/vogon/references/lifecycle.md`.

The requirement approver is the role named in the "Approval" section of
`requirements.md`, because the validation plan sets who approves (principle
2). When that section names no role, the requirement approver is the Product
Owner.

A requirement is approved in one of two places. Where `tracking.md` states an
approval transition for the requirement item type, the tracker holds
approvals: the requirement approver approves with that transition, the
tracker item is the only record of the approval, and nothing copies it into
the repository. Otherwise `vogon approve` records the approval in the state
file, on the requirement approver's explicit instruction in their own
session.

A skill changes an approved requirement only with the developer's agreement.
The change appends a `changed` entry, so the requirement needs approval
again. A withdrawal or a supersession is such a change, made with
`vogon:requirements`, and has no step of its own. The skill reports the tests,
procedures, plans and records that name the old id and changes none of them,
because changing them is work for `vogon:implement` and `vogon:tests`.

## Risk

Each requirement carries `gxp_impact` and `risk`, each with its reason, from
the moment it is drafted, so a reader can challenge a value. The default
values and method are in `src/vogon/references/records.md` "Requirement", and
`requirements.md` replaces them where the validation plan states its own.
Project-level risk documents the plan lists, such as a risk log or a data
integrity risk assessment, are separate documents, approved by the roles the
plan names.

## Tests

The pytest code is the test case. Each test names the requirements it
verifies in `@pytest.mark.req`, and where procedures exist, its procedures in
`@pytest.mark.procedure`. The link is on the test because whoever changes a
test edits its marker in the same edit (`DEC-006`). The marker rules are in
`src/vogon/references/markers.md`. A test with no `req` marker is allowed and
verifies no requirement in the matrix.

VOGON writes tests from the requirement's intent. An expected value is worked
out from the requirement and its sources, because a value read off the code
makes the test that asserts it unable to fail (`records.md` "Expected
values"). A test uses a mock only where `tests.md` "Unit tests and formal
tests" allows it.

A test procedure is a document of numbered steps, each with its expected
result. `tests.md` states whether the project needs procedures, whether they
are written before development or generated from the tests, and who approves
them. `vogon:tests` imposes no order of its own.

## Code from requirements

`vogon:implement` has a sub-agent write a plan, `vogon/plans/plan_<slug>.md`,
in the format of `src/vogon/skills/implement/references/plan-format.md`. The
developers are asked to approve the plan before code is written. A developer
may tell the skill to continue without approval; the `planned` entry then has
no `approved_by`, and the pull request reports it. Each part of the plan is
written by its own sub-agent and checked by a test checker and by a code
reviewer that runs Claude Code's `code-review` skill and then the code
checklist. VOGON has no code reviewer of its own.

## Traceability

`vogon:init` adds lines to the host `conftest.py` that copy each test's `req`
and `procedure` marker ids into the JUnit XML properties (`markers.md`).
`tests.md` states how a test run is tied to the commit it tested. By default the
suite name is the full commit hash. `vogon:release` reports a run that does not
identify the release commit. Where and how the suite runs is the project's
choice. A pytest run that names the suite this way is:

```
pytest --junitxml=results.xml -o junit_suite_name=$(git rev-parse HEAD)
```

Where a test manager is configured, VOGON uploads the JUnit XML unchanged and
the test manager produces the traceability report, because it is a tool with
its own validation (`DEC-003`). Where none is configured, `vogon trace` joins
the markers and results of one commit into the matrix, including every
requirement with no test. The matrix is evidence, so it comes from the test
manager or from `vogon trace`, never from a model (principle 5).

## Release

`vogon:release` takes a release commit, a release name and the JUnit XML of a
test run on that commit. Sub-agents draft each document `documents.md` lists
from a read-only checkout of that commit, so every statement describes the
code released, and each statement cites what it rests on. The skill files the
documents, the matrix and the results, and tells each approver what waits for
them. The steps are in `src/vogon/skills/release/SKILL.md`.
