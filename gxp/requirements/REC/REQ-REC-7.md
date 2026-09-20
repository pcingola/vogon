---
id: REQ-REC-7
type: requirement
title: Mint the next unused identifier for a new record
modules: [REC, CLI]
status: accepted
verification: test
gxp_risk: none
depends_on: [DEC-001]
tags: [identifiers]
---

# REQ-REC-7 — Mint the next unused identifier for a new record

**Requirement.** When creating a record, VOGON MUST assign the lowest number
not used by any record of that type and module, including withdrawn and
superseded ones, and MUST write the file named for that id.

**What this does not require.** Filling in the body, and choosing the module.

**Example.** A module holding `REQ-REC-1` through `REQ-REC-7`, one of them
withdrawn, gets `REQ-REC-8`.

**Acceptance.** For any set of existing records, the minted id is unused in
that set and in the history of that set, and the file created is named for it.
