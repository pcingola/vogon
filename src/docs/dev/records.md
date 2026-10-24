# Records

[Vocabulary](vocabulary.md) defines the four kinds of record. The rules for
every record, including ids, paths, frontmatter fields and body blocks, are in
`src/vogon/references/records.md`. Every record also follows
`src/vogon/references/writing.md`.

## Layout

VOGON creates this layout under `vogon/` in a host project. This repository's
`vogon/` holds VOGON's own constraints and decisions in the same format.

| Path | Holds |
| --- | --- |
| `vogon/project/` | `vogon.yaml` and the process files derived from the validation plan (`src/vogon/references/process-files.md`); `checklists/` holds the project's own versions of the default checklists |
| `vogon/requirements/<module>/` | Requirements `REQ-*.md`, each with its [state file](#state-file) `REQ-*.json` beside it, and the test procedures kept in the repository. A project without modules uses `vogon/requirements/` |
| `vogon/facts/` | Domain facts |
| `vogon/constraints/` | Constraints |
| `vogon/decisions/` | Decisions |
| `vogon/sources/` | Held copies of the documents records cite ([Sources](sources.md)) |
| `vogon/plans/` | Plans for code; `done/` holds the plans whose requirements have all been released |
| `vogon/documents/<release>/` | Drafted documents for one release, where the project has no document system |
| `vogon/tmp/` | Working files, such as downloaded transcripts and draft documents. Gitignored |

Requirements are grouped by module. Facts, constraints and decisions are
flat, because one is often cited by several modules.

## Format

YAML frontmatter is read by the skills and the commands, and the markdown
body by people. Approval is not a field and not a status:
`src/vogon/references/lifecycle.md` "Approval" states where an approval is
recorded.

`source` lists the held documents a record came from. Each path in it asserts
that the document says what the record says, so only a passage that was read
is cited.

`status` records whether the project is committed to the statement. Build
progress is in the state file and the passing tests.

## Requirement

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
id with `.json`. It records every step done to the requirement, in order. The
entries and their fields are defined in `lifecycle.md` "State file".

When an entry and the pull request, commit or tracker item it names differ, the
linked item is correct. For approvals, `lifecycle.md` "Approval" states which
record holds them (`src/vogon/references/common.md` "Start of every skill").

## Identifiers

A file is named for its id alone, such as `REQ-PRN-12.md`, so that a changed
title breaks no link. A record's history is its git history.

`vogon id` takes the next number from every branch and the history. Two
branches can take the same id before either pushes, so a skill runs
`vogon id --check` and renumbers before it opens its pull request
(`common.md` "Commands").
