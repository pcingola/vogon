---
id: REQ-REC-12
type: requirement
title: Require an accepted acceptance block on a requirement carrying risk or verified by test
modules: [REC]
status: accepted
verification: test
gxp_risk: product quality
depends_on: [DEC-024, REQ-TRC-4, REQ-TRC-8]
references:
  - src/docs/dev/records.md
tags: [acceptance, validation]
---

# REQ-REC-12 — Require an accepted acceptance block on a requirement carrying risk or verified by test

**Requirement.** VOGON MUST report a requirement whose `gxp_risk` is anything
other than `none`, or whose `verification` is `test`, and which has no
acceptance block, or whose acceptance block carries no `acceptance_by` and
`acceptance_on`. VOGON MUST report such a record if its `status` is anything
other than `proposed`.

The acceptance block is the only statement of what correct means that was
written before the code, and a test may name only a requirement whose block
has been accepted (`REQ-TRC-8`). Without a named person and a date against it,
there is nothing to distinguish criteria a person set from criteria a draft
proposed.

**What this does not require.** Judging whether the criteria are adequate,
whether the expected values are right, or whether the named person wrote them
rather than approving a draft.

**Example.** A requirement with `gxp_risk: safety` and an acceptance block
with no `acceptance_by` is reported and cannot leave `proposed`. Adding the
name and the date clears it.

**Acceptance.** For any requirement whose `gxp_risk` is not `none` or whose
`verification` is `test`, an acceptance block is present and `acceptance_by`
and `acceptance_on` are set, or the record is reported; and the record's status
is `proposed` until both hold.
