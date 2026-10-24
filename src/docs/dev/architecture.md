# Architecture

VOGON is a Claude Code plugin installed into a host project: the repository of
a regulated (GxP) software project. It carries out the [steps of the GxP
process](#skills) that do not need a person. The plugin is a set of skills,
the sub-agents they start, and the commands `vogon id`, `vogon approve` and
`vogon trace` for the work that must give the same result every time. Claude
Code does all model work, and the Python code calls no language model
(`DEC-005`).

`src/vogon/references/common.md` holds the rules every skill applies and lists
the topic file in `src/vogon/references/` that holds each other rule. Each
skill's steps are in `src/vogon/skills/<skill>/SKILL.md`. Sub-agents do the
work in their own contexts, so the main agent's context stays small over a
long task. A different sub-agent reviews each piece (principle 6, `common.md`
"Sub-agents").
[Vocabulary](vocabulary.md) defines the terms, and [Records](records.md)
describes the files under `vogon/`, including the state file.

## Scope and systems

Version 0.1 is developed and tested against one stack: a host project in
Python with pytest, GitHub as repository host, Jira as tracker, Xray as test
manager, and Claude Code. No abstraction layer is written before a second
implementation exists (`DEC-004`).

The host project's validation plan chooses its products, so a skill names
each external system by its role: repository host, tracker, test manager,
document system, meetings, mail and chat (`common.md` "Systems by role").

VOGON never moves an item into a state that records approval or signature,
because a signature requires the signer's own credentials (`CON-001`).
`common.md` "Actions VOGON never takes" lists these actions and their
exceptions. An approval recorded by `vogon approve` carries the approver's
git identity and asks for no credentials, so it is not an electronic
signature under 21 CFR Part 11.

A change to a live system is recorded and approved in the host project's own
change control system. VOGON writes no change record and no impact
assessment, and the change's requirements, tests, code and release documents
go through the same skills as the first release (`DEC-026`).

## Skills

One skill per task a person starts. Each runs in the main Claude Code session.

| # | Step | Skill | Produces | Approved by |
| --- | --- | --- | --- | --- |
| 1 | Configure | `vogon:init` | `vogon/project/vogon.yaml`, the validation plan in `vogon/sources/`, the `.gitignore` lines, the `conftest.py` lines and the marker registration | A person, on the pull request |
| 2 | File the sources | `vogon:requirements` | Reviewed summaries of meetings, mail and chat; filed documents with their markdown copies | |
| 3 | Draft and review the records | `vogon:requirements` | Requirements with acceptance criteria and risk fields; facts, constraints and decisions; withdrawals and supersessions | |
| 4 | Send the requirements for approval | `vogon:requirements` | The pull request with `REQ-*.md` and `REQ-*.json`; tracker items where a tracker is configured | |
| 5 | Approve the requirements | `vogon:approve`, or the tracker | An `approved` entry in `REQ-*.json`, or the tracker's approval transition where a tracker holds approvals | The requirement approver |
| 6 | Write the test procedures | `vogon:tests` | Test procedures, where `tests.md` requires them | The roles `tests.md` names |
| 7 | Choose a requirement | `vogon:next` | The ready and not-ready lists; the tracker item assigned | |
| 8 | Plan | `vogon:implement` | A reviewed plan, and a `planned` entry | A developer, when asked |
| 9 | Write the code, tests and documentation | `vogon:implement` | Reviewed code, tests and documentation, all tests passing, in one pull request | A person, on the repository host |
| 10 | Release | `vogon:release` | The documents `documents.md` lists, the traceability matrix and the results, filed | The roles `documents.md` names |

Different requirements are at different steps at the same time. Step 6 comes
before step 7 or after step 9, as `tests.md` states; a project that needs no
test procedures skips it. A change to a requirement after step 4 appends a
`changed` entry and returns the requirement to step 5.

The default checklists are in the `references/` directory of the
`requirements` and `implement` skills. Each is a separate file so that a
project can replace one with a file of the same name in
`vogon/project/checklists/` (`common.md` "Sub-agents").

## Start of a skill

Tasks happen weeks apart, by different developers, in any order, so a skill
does not assume an earlier task ran (`common.md` "Start of every skill").

## Project configuration and process files

`vogon/project/vogon.yaml` names the system for each role, the holders of
each approval role and the modules. `vogon:init` writes it from
`src/vogon/templates/vogon.yaml`. It is YAML because the commands read it.

The validation plan is filed in `vogon/sources/` as the original and a
markdown copy ([Sources](sources.md)). It stays the host project's controlled
document, and VOGON never edits either copy. The process files in
`vogon/project/` are VOGON's reading of the plan: `tracking.md`,
`requirements.md`, `tests.md`, `traceability.md`, `documents.md` and
`release.md`. Their topics are in their templates in `src/vogon/templates/`.

## Sources and records

Records are markdown files under `vogon/` in the host repository
([Records](records.md)), drafted from held documents and reviewed summaries
([Sources](sources.md)). A requirement whose only source is code describes
current behaviour, defects included, so the developer confirms that the
behaviour is intended (`src/vogon/skills/requirements/SKILL.md`, step 5).

## Requirement lifecycle

The rules for approval, change, withdrawal and supersession are in
`src/vogon/references/lifecycle.md`.

The requirement approver is the role named in the "Approval" section of
`requirements.md`, because the validation plan sets who approves (principle
2). When that section names no role, it is the Product Owner.

A requirement is approved in one of two places: in the tracker, where
`tracking.md` states an approval transition for the requirement item type,
and otherwise in the state file, by `vogon approve`.

On a withdrawal or a supersession, `vogon:requirements` reports the tests,
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

An expected value is worked out from the requirement and its sources, because
a value read off the code makes the test that asserts it unable to fail
(`records.md` "Expected values").

## Code from requirements

`vogon:implement` writes a plan, `vogon/plans/plan_<slug>.md`, that divides the
work into parts. Each part is written by its own sub-agent and reviewed against the test checklist and by Claude Code's `code-review` skill.
VOGON has no code reviewer of its own.

## Traceability

`vogon:init` adds lines to the host `conftest.py` that copy each test's `req`
and `procedure` marker ids into the JUnit XML properties (`markers.md`).
`tests.md` states how a test run is tied to the commit it tested. By default the
suite name is the full commit hash. A pytest run that names the suite this way
is:

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
code released. The steps are in `src/vogon/skills/release/SKILL.md`.
