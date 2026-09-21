---
id: REQ-REC-5
type: requirement
title: Report an id reused after withdrawal
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-001]
references:
  - src/docs/dev/records.md
tags: [validation, identifiers]
---

# REQ-REC-5 — Report an id reused after withdrawal

**Requirement.** VOGON MUST report a record that takes an id previously held
by a record now withdrawn or superseded, and MUST report a record referenced
elsewhere whose file has been deleted rather than withdrawn.

An id is permanent. Recycling one makes every historical reference to it point
at a different statement, including references in issues already approved.

**What this does not require.** Preventing the reuse, and recovering a deleted
file.

**Example.** `REQ-REC-9` is withdrawn. A new record minting `REQ-REC-9` is
reported, as is the deletion of the withdrawn file.

**Acceptance.** For any git history reachable from the working tree, an id that
has ever existed appears in at most one live record, and any deviation is
reported with both revisions.
