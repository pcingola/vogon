---
id: REQ-REC-3
type: requirement
title: Report a duplicated record id
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-001]
references:
  - src/docs/dev/records.md
tags: [validation, identifiers]
---

# REQ-REC-3 — Report a duplicated record id

**Requirement.** VOGON MUST report any id carried by more than one record
file, and any record whose `id` does not match its filename.

An id is the record's identity. Two records sharing one, or a file whose name
disagrees with the id inside it, make every reference to that id ambiguous.

**What this does not require.** Deciding which of the two is correct.

**Example.** Two files both declaring `id: REQ-REC-3`, and a file named
`REQ-REC-4.md` whose frontmatter says `id: REQ-REC-5`, are both reported.

**Acceptance.** For any set of record files, every id appears exactly once and
equals the filename stem, or the violation is reported with all the files
involved.
