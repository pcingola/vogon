# Architecture

## What VOGON does

VOGON turns a conversation into the compliance record a regulated change needs,
and keeps that record correct while the code is written.

From a conversation, a transcript or a document, it produces a requirement, the
tracker items that requirement implies, the link from the tests back to it, and
the documents a validation package is assembled from. Its users are developers,
project owners and quality staff.

The work it removes is transcription: the design specification written from
finished code, the test specification transcribed from existing tests, the
traceability matrix, and the structure of the summary report. The work it does
not remove is the qualified test run, change control, and the judgement in a
risk assessment. Those are the parts a regulator relies on, and they are the
parts that cannot be generated.

## Two stores, one direction

The specification lives twice.

In the project's git repository, as markdown records under `gxp/`. This is
where the text is written and edited, where a change is reviewed in a pull
request, and where history is kept. It is cheap to change and it is not
controlled.

In the tracker — Jira, with Xray for tests — as issues under approval. This is
where a named person approves a statement by re-entering their credentials, and
what an auditor is shown. It is expensive to change and it is controlled.

VOGON writes from the repository to the tracker and never the other way. It
reads the tracker's state back to report where the two have diverged: a record
edited after its issue was approved, a test marker naming a requirement that no
longer exists, a result imported from a build other than the one released.

It never performs the approval. An electronic signature requires the signer to
re-enter their own credentials, so the approval transition stays a human action
in the tracker.

## Where things sit in a project

VOGON is installed as a library and a command line into a real project.

```
<project>/
├── gxp/
│   ├── requirements/<module>/REQ-<MODULE>-NNN.md
│   ├── facts/FACT-NNN.md
│   ├── constraints/CON-NNN.md
│   ├── decisions/DEC-NNN.md
│   ├── sources/        held copies of every cited document, dated and flat
│   └── out/            generated. Never hand-edited
├── tests/              test functions carrying requirement markers
├── .vogon/             tool state. Gitignored
└── pyproject.toml      [tool.vogon]
```

All of it is plain text in git. There is no database. Configuration sits in
`[tool.vogon]` in `pyproject.toml`, and the layout above is the default, so a
project that accepts the convention configures nothing.

`gxp/` is visible rather than hidden. The records are reviewed in pull requests
and read by people who will never run the tool.

## Traceability

The trace runs from the test to the requirement, not from the requirement to
the test. A marker on the test function names the requirement ids it verifies,
and whoever changes the test changes the marker, in the same commit. Requirement
ids are not written into the source as comments: they drift and nothing checks
them.

Coverage and traceability reporting is Xray's. VOGON maintains the link Xray
reports on — the Xray test issue exists, points at the right requirement issue,
and can be matched to the test that ran — and imports the results keyed to those
issues.

What VOGON checks locally is what Xray cannot see, because Xray can only report
on what it was told about: a marker naming an id that does not exist, a marker
on a withdrawn requirement, a requirement carrying risk with no marker anywhere.
Those fail the build before anything is pushed. They are build hygiene, not
evidence.

## Drafting

VOGON does not call a language model. Records are drafted by a coding agent
working in the repository, from the instructions VOGON ships; VOGON validates
what the agent wrote and refuses what does not hold together.

Keeping generation outside the tool keeps every command deterministic and
testable, and it keeps the tool able to disagree with the draft. A checker that
also generates cannot catch a generated record that is internally consistent
and wrong.

A drafted record is `proposed` until a person accepts it, and nothing
`proposed` is pushed to the tracker.

## Modules

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
- Claude Code, as the coding agent that drafts records and writes tests

This is a deliberate narrowing, recorded in `gxp/decisions/DEC-004.md`.
Supporting a second tracker or a second test manager means an interface, and an
interface written before the second implementation exists is guesswork.
