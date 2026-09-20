# Records

How to write a requirement, a domain fact, a constraint or a decision. What
those four words mean is in [Vocabulary](vocabulary.md).

This format is VOGON's, not the host project's. VOGON supplies the schema, the
id grammar and the checks; the host project supplies the module names, the
records and the documents they cite.

## Layout

Records live in `gxp/`, in the host project's repository and in the VOGON
project's alike.

| Path | Holds |
| --- | --- |
| `gxp/requirements/<module>/` | Requirement records, one directory per module |
| `gxp/facts/` | Every `FACT-` |
| `gxp/constraints/` | Every `CON-` |
| `gxp/decisions/` | Every `DEC-` |
| `gxp/sources/` | Held copies of the documents records cite. See [Sources](sources.md) |
| `gxp/out/` | Generated output. Never hand-edited |

Nothing depends on where a file sits. Identity is the id, the queryable
structure is the frontmatter, and the directory exists so a person can browse.
Requirements are grouped per module because there are enough of them for that
to help. Facts, constraints and decisions are flat, because a fact is routinely
cited by two modules and a constraint by all of them.

`gxp/` is visible rather than hidden under a dot-directory, because the records
are reviewed in pull requests and read by people who have never run VOGON.
`.vogon/` holds tool state — the last-seen tracker state, the trace collector's
output — and is gitignored.

## Deciding which one a sentence is

Applied to each sentence of a transcript, deck or procedure, in this order. The
first match wins.

1. Could you write a test that our system fails? → **requirement**.
2. Is it true whether or not we build anything? → **domain fact**.
3. Is it a limit imposed from outside that we cannot trade away? → **constraint**.
4. Did we choose it, among options? → **decision**. Choosing *not* to build
   something is a decision.
5. Does nobody know the answer yet? → it is raised in conversation and answered
   there, and it is not written down as a record.
6. Is it only what somebody said? → it stays in the meeting summary and goes
   nowhere else.

A single sentence often splits. "Xray reports coverage from the link between a
test issue and a requirement issue, so maintain that link from the test source"
is a fact and a requirement, written as two records that link to each other.

## The shape of a record

YAML frontmatter followed by a markdown body. The frontmatter is what machines
read — the indexes, the checks and any export are generated from it — and the
body is what people read.

Frontmatter common to all four types:

| Field | Rule |
| --- | --- |
| `id` | Namespaced, permanent, never reused. A withdrawn record keeps its id and its file |
| `type` | `requirement`, `fact`, `constraint` or `decision` |
| `title` | One line naming what the record is, in the words someone would search for. Not an allusion, not a question |
| `modules` | Which modules it belongs to, as a list. A fact cited by two modules carries both |
| `status` | `proposed`, `accepted`, `withdrawn`, or `superseded_by: <id>` |
| `source` | Every held document that states this, as a list of paths. See [below](#source-lists-every-document-that-states-it). Absent on a record the project originated itself |
| `reviewed_by`, `reviewed_on` | Who read it in detail and when. Absent until someone has |
| `tags` | Free-form, for searching across modules. Optional |
| `tracked_as` | Where this record is registered outside the repository, as a map from the role of each system to the key the record has in it. One entry is `governs: <role>`, naming the role whose approval state counts. Absent until the record is registered anywhere |
| `depends_on` | The records this one rests on, by id. Absent on a fact, which rests on nothing |
| `references` | The documents that say how this is realised, as a list of paths. Absent where no document does. See [below](#references-points-at-the-documentation) |

The body carries the statement as one sentence with no rationale in it, a
description of a short paragraph saying what it means and what it does not
cover, and one concrete example marked as illustration.

An absent field is absent. Never `N/A`, never "none considered", never an empty
list. A record with no example has no example block, and that hole is the
signal that it has not been thought through.

### `source` lists every document that states it

`source` names every held document that supports the record, not only the one
it was written from. A fact is true whether or not this project exists, so a
fact that only a meeting attests to is either badly sourced or not a fact.
Before writing one, look for the document that states it and cite what you
find alongside the meeting.

Order the list by authority, strongest first, using the `authority` each held
document declares: `regulation`, `standard`, `procedure`, `project`,
`informal`. The first entry is what a reader checks the record against; the
later ones say who else confirmed it and where it was elicited. Where a
meeting is cited, the transcript comes before its summary and the summary
never replaces it. [Sources](sources.md) has the rules the held documents
themselves follow.

Citing a document means having read the passage. A path in `source` asserts
that the document says this. Do not list a document because its title suggests
it would.

Where the documents disagree, both go in the list and the record says what the
difference is. Where a meeting claims something no controlled document
supports, the record says so in a sentence, and that sentence is the finding.

A record the project originated itself — a requirement on VOGON's own
behaviour, a decision taken in a design conversation — has no `source`. There
is no document to cite, and inventing one is worse than the field's absence.

### `references` points at the documentation

A record says what must hold. It does not say how. `references` names the
documents that do: the schema a decision settles, the format a requirement is
checked against. A reader who needs the mechanism does not have to search for
it.

It is the reverse of `source`. `source` names what the record came from, and
`references` names what elaborates it. A record may carry both, one, or
neither, and which of the four types usually carries it is said in the
sections below.

Paths resolve from the repository root and are checked, so a document moved
without updating the records that point at it fails.

### `tracked_as` holds every system, and names the one that governs

A project runs more than one system, and the same record can be registered in
several of them: the tracker that approves it, the test manager that plans
tests against it, whatever a company's quality organisation adds. `tracked_as`
records all of them, keyed by role, so a reader can reach any of them from the
record.

One role is named as governing. Approval state is read from that system and
from no other, which is what `CON-003` requires: there is one answer to
whether the record is approved. The other entries are addresses, and VOGON
checks that each key still resolves without comparing what the systems say to
each other. Where two systems hold the same statement and disagree, that is
the project's disagreement to resolve, not something VOGON arbitrates.

```yaml
tracked_as:
  governs: tracker
  tracker: PROJ-412
  test_manager: TEST-88
```

### Status is about the statement, not about the work

Status says whether we are committed to the requirement, not whether anything
has been built. There is deliberately no `implemented` value: it would be wrong
the moment someone changed the code, and nobody would notice. Whether a
requirement is built is answered by its link to a passing test.

## How a record is written

Every record follows the [writing standard](writing.md), which is the same
standard this documentation follows. Its reader is an engineer who knows
software and does not know the application domain or compliance, and that
reader is the test every field has to pass.

Two of its rules decide most reviews. Define or link every domain term at
first use: no term appears in a record that the record has not either explained
in a clause or linked to the fact that explains it. And a record is finished
when that engineer could implement it without asking a question, not when it is
comprehensive.

## Requirement

At `gxp/requirements/<module>/REQ-<MODULE>-<NUMBER>.md`. Written as a MUST
statement, solution-free. If the sentence cannot be failed by a test, it is not
a requirement yet.

Frontmatter it adds:

| Field | Rule |
| --- | --- |
| `verification` | One of `inspection`, `analysis`, `demonstration` or `test` |
| `gxp_risk` | One of `safety`, `product quality`, `data integrity` or `none`. What a failure of this requirement would damage in a regulated project. It decides how much verification the requirement needs and is expensive to add retrospectively |
| `acceptance_by`, `acceptance_on` | Who accepted the acceptance block and when. Required where `gxp_risk` is not `none`, and absent until a person has accepted it |

A requirement carries `references` where a document specifies the mechanism it
is checked against — the schema, the marker format, the tracker rules. A
requirement whose mechanism is not written down anywhere carries none, and the
absence says the mechanism has not been settled.

Body blocks it adds:

- **What this does not require** — the boundary. Usually the most useful block
  in the file.
- **Acceptance** — properties that hold for any project using VOGON, never
  facts about the files that happen to be on this machine. A criterion written
  around one repository describes a system that can only be demonstrated on
  that repository.

Where a value is expected, the acceptance block states it. It is worked out
from the requirement and never read off a run of the code, because a value
taken from the code makes the test that asserts it unable to fail. On a
requirement carrying risk the block is accepted by a named person before the
record leaves `proposed`, and a test marker naming a requirement whose block
has not been accepted fails the run. `DEC-012` has the reasoning.

### Worked example

```markdown
---
id: REQ-TRK-2
type: requirement
title: Report a record edited after its issue was approved
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [CON-001, FACT-004]
references:
  - src/docs/dev/architecture.md
tags: [jira, approval]
---

# REQ-TRK-2 — Report a record edited after its issue was approved

**Requirement.** Where a record has changed since the tracker approved the
issue it is tracked as, VOGON MUST report the record as requiring
re-approval and MUST NOT push the change.

Approval is recorded in the tracker against a specific version of the
statement. An edit made afterwards is outside what anyone approved, and a
silent push would leave the tracker asserting approval of text nobody read.

**What this does not require.** Deciding whether the change is material, and
withdrawing the existing approval.

**Example.** A requirement is approved in Jira on the 3rd. On the 5th its
acceptance block gains a clause. The next run lists the record as requiring
re-approval and writes nothing to Jira.

**Acceptance.** For any record whose content hash differs from the hash
recorded at the time of approval, the record appears in the report and no
write is issued for it.
```

## Domain fact

At `gxp/facts/FACT-NNN.md`. No acceptance criteria, and no `depends_on`: a
fact is true on its own. Written in the plain present tense with no modal
verb.

Frontmatter it adds: `as_of`, the date it was observed or read, because facts
about a system's behaviour go stale and a fact with no date cannot be
re-checked.

A fact normally carries no `references`. Nothing of ours specifies how the
world works; what a fact needs is a `source` naming the document that states
it.

## Constraint

At `gxp/constraints/CON-NNN.md`. Its body says what it forbids or forces, and
`modules` is usually every module, which is what makes it a constraint rather
than a requirement.

Frontmatter it adds: `imposed_by`, naming exactly what imposes it — a
regulation, a numbered procedure, a standard, or a platform behaviour — and
`lifts_when`, the condition under which it stops applying, or `permanent`.

`references` points at the document describing how the constraint is honoured
in the design. `imposed_by` names what put the constraint there and is not a
path; `references` names our own document and is.

## Decision

At `gxp/decisions/DEC-NNN.md`. The body is the architecture decision record:
context, the options and what each costs, the decision, the consequences
including the ones accepted as bad, and an example. The example shows the
decision playing out in a situation a reader recognises, which is how a
reader checks they have understood the choice rather than the words.

A decision states the choice, not the mechanism. Where the mechanism is
written up, the decision carries `references` naming that document, so a
reader who wants to know how the choice was realised does not have to search
for it. A decision taken but not yet written up carries none, and that absence
is the signal that the documentation is behind.

A decision is never edited once accepted. It is superseded by a later decision
that names it, and both files stay.

## Identifiers

An id is a type, an optional module, and a number:

```
<TYPE>-<NUMBER>
<TYPE>-<MODULE>-<NUMBER>
```

`TYPE` is three or more uppercase letters and says which of the four kinds of
record it is: `REQ`, `FACT`, `CON`, `DEC`. It comes first so that one pattern
matches any id and no id is ambiguous in prose.

`MODULE` is optional and names the part of the system the record belongs to.
Three uppercase letters is the suggested length, because an id is read inside a
commit message and a test marker, but VOGON enforces only the shape: uppercase
letters and digits. A project that does not use modules omits the segment.
Where a record carries a module its `modules` frontmatter carries it too, and a
record belonging to several modules still has at most one module in its id.

The module names a project uses are listed in `vogon/modules.yaml`, one name to
a line of description, and a record naming a module that is not in that file is
reported. The file is committed, so the list is the team's and a new module is
added in a reviewed change rather than by whoever mints the next id.

```yaml
TRK: Reading and writing the tracker, and reporting divergence
REC: The record schema, id grammar, validation and indexes
```


`NUMBER` is one or more digits, compared numerically, so `REQ-TRK-2` and
`REQ-TRK-02` would be the same id and only one of them may exist.

| Id | Reads as |
| --- | --- |
| `REQ-TRK-2` | Requirement 2 of the `TRK` module |
| `REQ-7` | Requirement 7, in a project using no modules |
| `FACT-004` | Domain fact 4 |
| `CON-001` | Constraint 1 |
| `DEC-007` | Decision 7 |

Numbers are minted per type and module, so `REQ-TRK-2` and `REQ-REC-2` are
different records and both are valid.

An id is permanent. It is never reused, never renumbered, and never recycled
after withdrawal. A withdrawn record keeps its file, with status `withdrawn`
and the reason in it.

The file is named for the id alone, `REQ-TRK-2.md`, not the id plus a title.
Titles change; links should not break.

A record's change history is its git history. There is no log file per record.
