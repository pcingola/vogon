---
id: REQ-REC-13
type: requirement
title: Report an identifier that does not match the grammar
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-016]
references:
  - src/docs/dev/records.md
tags: [identifiers, validation]
---

# REQ-REC-13 — Report an identifier that does not match the grammar

**Requirement.** VOGON MUST report every record whose `id` is not
`<TYPE>-<NUMBER>` or `<TYPE>-<MODULE>-<NUMBER>`, where the type is three or
more uppercase letters naming one of the four record types, the module is one
or more uppercase letters and digits, and the number is one or more digits.

Every other link is written as an id: the test marker, the commit message,
`depends_on`, the key held in the tracker. An id that no pattern matches breaks
all of them at once, and it breaks them silently, because a reference to it
resolves to nothing rather than to the wrong thing.

**What this does not require.** Checking that a module name is one the host project
uses elsewhere, and choosing the module for a new record.

**Example.** A record carrying `id: REQ_TRK_2` is reported. A record carrying
`id: REQ-TRK-2` in a host project with no other `TRK` record is not.

**Acceptance.** For every record file, the `id` matches the grammar, or the
record is reported with its id and its path.
