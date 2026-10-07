# Records

How to write a requirement, a domain fact, a constraint or a decision. What
those four words mean is in [Vocabulary](vocabulary.md).

## Layout

Records live in `vogon/`, in the host project's repository and in the VOGON
project's alike.

| Path | Holds |
| --- | --- |
| `vogon/project/` | `vogon.yaml`, the configuration, and the process files derived from the validation plan. See [Architecture](architecture.md#project-configuration-and-process-files). `checklists/` holds the project's own versions of the default checklists |
| `vogon/requirements/<module>/` | Requirement records, one directory per module: each `REQ-<MODULE>-<NUMBER>.md` with its [state file](#state-file) `REQ-<MODULE>-<NUMBER>.json` beside it |
| `vogon/facts/` | Every `FACT-` |
| `vogon/constraints/` | Every `CON-` |
| `vogon/decisions/` | Every `DEC-` |
| `vogon/fake/FAKE-REQ.md` | Named by a change that implements no requirement, such as a typo fix, in place of a record id. Written by `vogon:init`; not a record |
| `vogon/sources/` | Held copies of the documents records cite: the validation plan, checked summaries of meetings, mail and chat, and attached files with their markdown copies. See [Sources](sources.md) |
| `vogon/plans/` | Plans for code, approved by the developers before the code is written; `done/` holds the spent ones |
| `vogon/documents/<release>/` | Drafted documents for one release, where the project has no document system |
| `vogon/logs/` | Loop logs. Gitignored unless the project commits them |
| `vogon/tmp/` | Downloaded transcripts, mail and chat, deleted after their summary is checked. Gitignored |

A record's identity is its id, not its path. Requirements are grouped by
module; facts, constraints and decisions are flat, because one is often cited
by several modules.

## Deciding which one a sentence is

Applied to each statement in a checked summary, a document or code, in this
order. The first match wins.

1. Could you write a test that our system fails? → **requirement**.
2. Is it true whether or not we build anything? → **domain fact**.
3. Is it a limit imposed from outside that we cannot trade away? → **constraint**.
4. Did we choose it, among options? → **decision**. Choosing *not* to build
   something is a decision.
5. Does nobody know the answer yet? → it goes to the developer as a question,
   and it is not written down as a record.
6. Is it only what somebody said? → it stays in the summary and goes nowhere
   else.

A single sentence often splits. "The test manager reports coverage from the
link between a test issue and a requirement issue, so maintain that link from
the test source" is a fact and a requirement, written as two records that link
to each other.

## The shape of a record

YAML frontmatter, read by the skills and scripts, followed by a markdown body,
read by people.

Frontmatter common to all four types:

| Field | Rule |
| --- | --- |
| `id` | Namespaced, permanent, never reused. A withdrawn record keeps its id and its file |
| `type` | `requirement`, `fact`, `constraint`, `decision`, or `test_procedure` for a [test procedure](#test-procedure) |
| `title` | One line naming what the record is, in the words someone would search for. Not an allusion, not a question |
| `modules` | Which modules it belongs to, as a list. A fact cited by two modules carries both |
| `status` | `active`, `withdrawn`, or `superseded_by: <id>`, written as a mapping: `status: {superseded_by: DEC-024}`. Approval is not a status; it is in the state file |
| `source` | Every held document that states this, as a list of paths. See [below](#source-lists-every-document-that-states-it). Absent on a record the project originated itself |
| `reviewed_by`, `reviewed_on` | Who read it in detail and when. Absent until someone has |
| `tags` | Free-form, for searching across modules. Optional |
| `depends_on` | The records this one rests on, by id. Absent on a fact, which rests on nothing |
| `references` | The documents that say how this is realised, as a list of paths. Absent where no document does. See [below](#references-points-at-the-documentation) |

The body carries the statement as one sentence with no rationale in it, a
description of a short paragraph saying what it means and what it does not
cover, and one concrete example marked as illustration.

A field or block with nothing to say is omitted
([Writing standard](writing.md)).

### `source` lists every document that states it

`source` names every held document that states the record, not only the one
it was drafted from, ordered by `authority`, strongest first
([Sources](sources.md#authority-decides-what-a-record-may-claim)). A path in
`source` asserts that the document says this, so cite only a passage you have
read. Where documents disagree, both are listed and the record states the
difference; where only a meeting, mail or chat supports a claim, the record
says so. A fact that only a meeting supports is either badly sourced or not a
fact. A record the project originated itself has no `source`.

### `references` points at the documentation

A record says what must hold, not how. `references` names the documents that
say how, such as the schema a decision settles, as paths from the repository
root. It is the reverse of `source`: `source` names what the record came from,
`references` what elaborates it. An evaluator reports a path that does not
resolve.

### Status is about the statement, not about the work

Status says whether we are committed to the statement, not whether anything
has been built. Whether a requirement is built is shown by its passing tests;
the progress of the work is in the state file.

## How a record is written

Every record follows the [writing standard](writing.md).

### Length

Suggested lengths for the body, everything after the frontmatter. A record well
over its suggested length usually states two things and is split into two
records.

| Type | Suggested words in the body |
| --- | --- |
| Requirement | 300 |
| Domain fact | 200 |
| Constraint | 200 |
| Decision | 600 |

## Requirement

At `vogon/requirements/<module>/REQ-<MODULE>-<NUMBER>.md`. Written as a MUST
statement, solution-free. If the sentence cannot be failed by a test, it is not
a requirement yet.

Frontmatter it adds:

| Field | Rule |
| --- | --- |
| `verification` | One of `inspection`, `analysis`, `demonstration` or `test` |
| `gxp_impact` | One of `patient safety`, `product quality`, `data integrity` or `none`. What a failure of this requirement would damage |
| `gxp_impact_reason` | Why that value: what a failure would damage, and how |
| `risk` | One of `high`, `medium` or `low`, from the severity of a failure, its probability, and how likely it is to be detected |
| `risk_reason` | Why that value: the severity, probability and detectability behind it |

The method and levels may differ per project; `requirements.md` states them
where the validation plan does.

Body blocks it adds:

- **Out of scope**: behaviour a reader might expect from the requirement that
  it does not require, so that nobody builds or tests it.
- **Acceptance criteria**: what must be tested. Each expected value is worked
  out from the requirement and its sources, never read off a run of the code,
  because a value taken from the code makes the test that asserts it unable to
  fail. The acceptance criteria are approved with the requirement.

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
id with `.json`. It records the requirement's approvals and every step done to
it, each with its date and the pull request or commit that holds it. Entries
are appended and never edited or removed; a new approval is a new entry.

```json
{
  "id": "REQ-PRN-12",
  "approvals": [
    {"by": "Alice Smith <alice@example.com>", "date": "2026-09-18", "hash": "sha256:3f9a…", "via": "vogon approve"}
  ],
  "steps": [
    {"step": "drafted", "date": "2026-09-15", "pr": 230},
    {"step": "planned", "date": "2026-09-22", "commit": "a12f9c0", "plan": "vogon/plans/plan_REQ-PRN-12.md", "approved_by": "Bob Jones <bob@example.com>"},
    {"step": "implemented", "date": "2026-09-25", "pr": 241, "commit": "b77d031"},
    {"step": "released", "date": "2026-10-02", "pr": 252, "commit": "c4e8a10", "release": "1.2"}
  ]
}
```

| Field | Rule |
| --- | --- |
| `issue` | The requirement's key in the tracker, where a tracker holds it |
| `approvals` | Who approved, when, and the hash of `REQ-*.md` they approved. Written by `vogon approve`, or copied from the tracker in the real version (`via` names the tracker) |
| `step` | `drafted`, `planned`, `test_procedures_written`, `implemented`, `released` or `withdrawn` |
| `pr`, `commit` | The pull request and the commit that hold the step's work. A `planned` entry has a `commit` and no `pr` |
| `plan` | In a `planned` entry, the path of the approved plan |
| `approved_by` | In a `planned` entry, the git identity of the developer who approved the plan |
| `release` | In a `released` entry, the release the requirement is part of |

The pull request, commit or tracker item an entry names is what counts. A skill
checks it before acting on the entry and reports any difference.

## Domain fact

At `vogon/facts/FACT-NNN.md`. Written in the present tense with no modal verb.
No acceptance criteria and no `depends_on`: a fact is true on its own.

Frontmatter it adds: `as_of`, the date the fact was observed or read, so it
can be checked again.

## Constraint

At `vogon/constraints/CON-NNN.md`. The body says what it forbids or forces.

Frontmatter it adds: `imposed_by`, what imposes it (a regulation, a numbered
procedure, a standard or a platform behaviour), and `lifts_when`, the condition
under which it stops applying, or `permanent`.

## Decision

At `vogon/decisions/DEC-NNN.md`. The body has the context, the options and
what each costs, the decision, its consequences including the bad ones, and an
example of the decision applied. A decision is never edited once accepted; a
later decision supersedes it, and both files stay.

## Test procedure

Only where `tests.md` keeps test procedures in the repository. At
`vogon/requirements/<module>/TP-<MODULE>-<NUMBER>.md`, beside the
requirements it verifies, with its id from `vogon id TP <module>`. The
frontmatter adds `verifies`, the requirement ids. The body is numbered steps,
each with its expected result. Where test procedures are kept in the tracker,
the tracker key is the id and VOGON writes no file.

## Identifiers

An id is a type, an optional module, and a number:

```
<TYPE>-<NUMBER>
<TYPE>-<MODULE>-<NUMBER>
```

`TYPE` is `REQ`, `FACT`, `CON`, `DEC`, or `TP` for a test procedure. `MODULE` names the part of the system
the record belongs to, in uppercase letters and digits; a project without
modules omits it. The modules are listed in `vogon.yaml`, and a record may name
only a listed module. `NUMBER` is compared numerically, so `REQ-PRN-12` and
`REQ-PRN-012` are the same id. Numbers count separately per type and module.

`vogon id <type> <module>` gives the next number. It runs `git fetch` and reads
the ids in the working tree, in every local and remote branch and in the
history. Two branches that take an id before either pushes can get the same
one; `vogon id` reports the duplicate on the pull request, and the later pull
request renumbers before it merges.

Once merged, an id is permanent: never reused or renumbered, also after
withdrawal. The file is named for the id alone, such as `REQ-PRN-12.md`, so
that a changed title breaks no link. A record's history is its git history.
