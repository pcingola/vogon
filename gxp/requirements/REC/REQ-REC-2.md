---
id: REQ-REC-2
type: requirement
title: Report a reference to a record id that does not exist
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-001]
references:
  - src/docs/dev/records.md
tags: [validation, links]
---

# REQ-REC-2 — Report a reference to a record id that does not exist

**Requirement.** VOGON MUST report every `depends_on` entry and every
`superseded_by` value naming an id for which no record file exists.

A dependency on an id that was never minted, or on one whose file was deleted
rather than withdrawn, leaves a record resting on nothing.

**What this does not require.** Reporting a requirement that depends on
nothing, and following references that appear only in body prose.

**Example.** A requirement carrying `depends_on: [FACT-099]` where
`gxp/facts/` holds no `FACT-099.md` is reported.

**Acceptance.** For any record, every id referenced in frontmatter resolves to
a file, or the reference is reported with the referring record and the missing
id.
