# Records

[Vocabulary](vocabulary.md) defines the four kinds of record.

## Layout

Records live in `vogon/`, in the host project's repository and in the VOGON
project's alike.

| Path | Holds |
| --- | --- |
| `vogon/project/` | `vogon.yaml`, the configuration, and the process files derived from the validation plan. See [Architecture](architecture.md#project-configuration-and-process-files). `checklists/` holds the project's own versions of the default checklists |
| `vogon/requirements/<module>/` | Requirement records, one directory per module: each `REQ-<MODULE>-<NUMBER>.md` with its [state file](#state-file) `REQ-<MODULE>-<NUMBER>.json` beside it, and [test procedures](#test-procedure) kept in the repository |
| `vogon/facts/` | Every `FACT-` |
| `vogon/constraints/` | Every `CON-` |
| `vogon/decisions/` | Every `DEC-` |
| `vogon/sources/` | Held copies of the documents records cite: the validation plan, checked summaries of meetings, mail and chat, and attached files with their markdown copies. See [Sources](sources.md) |
| `vogon/plans/` | Plans for code, approved by the developers before the code is written; `done/` holds the spent ones |
| `vogon/documents/<release>/` | Drafted documents for one release, where the project has no document system |
| `vogon/logs/` | Loop logs. Gitignored unless the project commits them |
| `vogon/tmp/` | Working files deleted before the skill finishes: downloaded transcripts, mail and chat, draft test procedures, draft release documents and the release checkout. Gitignored |

A record's identity is its id, not its path. Requirements are grouped by
module; facts, constraints and decisions are flat, because one is often cited
by several modules.

## Rules

The rules a writing sub-agent and an evaluator apply to every record are in
`src/vogon/references/records.md`: how a sentence is classified, the id and
file name, each frontmatter field, the body blocks of each type and the
suggested lengths. Every record also follows the writing standard,
`src/vogon/references/writing.md`.

A sentence often states two kinds of record. "The test manager reports
coverage from the link between a test issue and a requirement issue, so
maintain that link from the test source" is a fact and a requirement, written
as two records; the requirement names the fact in `depends_on`.

YAML frontmatter is read by the skills and scripts, and the markdown body by
people. No field and no body line states that a record was approved or
signed: approvals are in the [state file](#state-file).

`source` names every held document that states the record, not only the one
it was drafted from, strongest `authority` first ([Sources](sources.md#authority)).
A path in `source` asserts that the document says this, so only a passage that
was read is cited.

`references` names the documents that say how the record is realised, such as
the schema a decision settles. `source` names what the record came from;
`references` names what elaborates it.

### Status

`status` records whether the project is committed to the statement: `active`,
`withdrawn` or `{superseded_by: <id>}`. A record is never deleted. Build
progress is in the state file and the passing tests.

## Requirement

At `vogon/requirements/<module>/REQ-<MODULE>-<NUMBER>.md`.

The requirement adds `verification`, the four risk fields (`gxp_impact`,
`gxp_impact_reason`, `risk`, `risk_reason`), and the body blocks
`**Requirement.**`, `**Out of scope.**` and `**Acceptance criteria.**`.
`**Out of scope.**` names what the requirement does not cover, so that nobody
builds or tests it. The
risk method and levels come from `requirements.md` where the validation plan
states them. Each expected value in the acceptance criteria is worked out from
the requirement and its sources, never read off a run of the code, because a
value taken from the code makes the test that asserts it unable to fail. The
acceptance criteria are approved with the requirement.

### Worked example

```markdown
---
id: REQ-PRN-12
type: requirement
title: Print the sample id as a barcode on the tube label
modules: [PRN]
status: active
source:
  - vogon/sources/2026-09-15_sample_labelling.summary.md
verification: test
gxp_impact: data integrity
gxp_impact_reason: A wrong barcode attaches a result to the wrong sample.
risk: high
risk_reason: A mismatch harms the sample record, occurs whenever a label is
  reprinted from stale data, and is not visible to the person applying it.
---

# REQ-PRN-12: Print the sample id as a barcode on the tube label

**Requirement.** The label printer MUST encode the sample id stored for the
tube, and only that id, in a Code 128 barcode on its label.

**Out of scope.** The label layout, and printing labels for anything other
than sample tubes.

**Example.** Sample S-2026-00417 is registered. Its tube label carries a
barcode that a scanner reads as `S-2026-00417`.

**Acceptance criteria.**

- The barcode on a printed label decodes to the stored sample id.
- A label reprinted after the sample id was corrected decodes to the
  corrected id.
- A sample with no stored id produces no label and an error.
```

## State file

Each requirement has a state file beside its markdown file, named for the same
id with `.json`. It records every step done to the requirement, in order.
Entries are appended and never edited or removed. A withdrawal is the
record's `status`, not a step. Every entry and its fields are defined in
`src/vogon/references/common.md`, "State-file entries".

A requirement is approved when the state file on the default branch has an
`approved` entry after its latest `changed` entry; an `approved` entry that
only an open pull request holds does not count. For every other entry, the
pull request, commit or tracker item it names counts over the entry: a skill
checks it before acting and reports any difference
(`src/vogon/references/common.md`, "Start of every skill" and "Approval of a
requirement").

## Domain fact, constraint and decision

A fact is at `vogon/facts/FACT-<NUMBER>.md`, a constraint at
`vogon/constraints/CON-<NUMBER>.md`, a decision at
`vogon/decisions/DEC-<NUMBER>.md`, with no module in the id. A fact carries `as_of`, the date it was observed, so
it can be checked again. A constraint carries `imposed_by` and `lifts_when`. A
merged decision is never edited; a later decision supersedes it, and both
files stay.

## Test procedure

Where `tests.md` keeps test procedures in the repository, each is at
`vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md`, beside the requirements
it verifies, which its `verifies` field lists. Where they are kept in the
tracker or test manager, the item key is the id and VOGON writes no file.

## Identifiers

An id is a type, an optional module, and a number:

```
<TYPE>-<NUMBER>
<TYPE>-<MODULE>-<NUMBER>
```

`TYPE` is `REQ`, `FACT`, `CON`, `DEC`, or `TP` for a test procedure. `MODULE`
names the part of the system the record belongs to, in uppercase letters and
digits; facts, constraints and decisions, and every record of a project
without modules, omit it. The modules are listed in `vogon.yaml`, and a record may name
only a listed module. `NUMBER` is compared numerically when ids are ordered. Numbers count separately per type and module.

`vogon id <type> <module>` gives the next number from every branch and the
history. Two branches can take the same id before either pushes, so a skill
runs `vogon id --check` and renumbers before it opens its pull request
(`src/vogon/references/common.md`, "Commands").

Once merged, an id is permanent: never reused or renumbered, also after
withdrawal. The file is named for the id alone, such as `REQ-PRN-12.md`, so
that a changed title breaks no link. A record's history is its git history.
