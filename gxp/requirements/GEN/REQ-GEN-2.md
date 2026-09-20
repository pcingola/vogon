---
id: REQ-GEN-2
type: requirement
title: A drafted record is proposed until a person accepts it
modules: [GEN, TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-005, REQ-TRK-5]
tags: [drafting, approval]
---

# REQ-GEN-2 — A drafted record is proposed until a person accepts it

**Requirement.** A record produced by drafting MUST carry status `proposed`,
and VOGON MUST NOT create a tracker issue for a record whose status is
`proposed`.

A model draft that nobody read has the same shape as one that was reviewed.
Holding it at `proposed` until a person changes the status makes the review a
distinct act with a commit behind it.

**What this does not require.** Detecting whether the person actually read it,
and preventing them from changing the status in the same commit.

**Example.** Twelve records drafted from a transcript are all `proposed`. A
push writes none of them until their status is changed.

**Acceptance.** For any record with status `proposed`, no tracker write is
issued, and the drafting instructions produce no other status.
