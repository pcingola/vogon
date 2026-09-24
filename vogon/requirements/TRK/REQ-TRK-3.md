---
id: REQ-TRK-3
type: requirement
title: Make writes idempotent, keyed by record id
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-001]
tags: [tracker, idempotency]
---

# REQ-TRK-3 — Make writes idempotent, keyed by record id

**Requirement.** VOGON MUST key every write to the tracker on the record id,
and a second run over unchanged records MUST create nothing and change
nothing.

A run that duplicates issues on retry produces two issues claiming to be one
requirement, and an approval on the wrong one.

**What this does not require.** Reconciling duplicates a person created, and
detecting an issue whose record id was edited in the tracker.

**Example.** A run interrupted after twelve of thirty issues, then re-run,
creates the remaining eighteen and touches none of the twelve.

**Acceptance.** For any set of records, running twice with no change between
runs leaves the tracker in the state the first run produced, and the second run
reports no write.
