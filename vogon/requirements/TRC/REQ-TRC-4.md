---
id: REQ-TRC-4
type: requirement
title: Fail on a requirement carrying risk with no marker
modules: [TRC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-006, FACT-002, REQ-TRC-1]
tags: [coverage, ci]
---

# REQ-TRC-4 — Fail on a requirement carrying risk with no marker

**Requirement.** VOGON MUST fail where an accepted requirement whose
`gxp_risk` is not `none` is named by no test marker.

Xray reports coverage only of the requirement issues it holds. A requirement
that was never pushed, or was pushed with no linked test, does not appear as a
gap in that report; this check is what makes it visible.

**What this does not require.** Failing on a requirement with `gxp_risk: none`,
and failing on a requirement whose `verification` is `inspection` or
`analysis`, which is verified by a person rather than a test.

**Example.** A requirement with `gxp_risk: data integrity` and
`verification: test` that no marker names fails the run.

**Acceptance.** For any set of records and markers, every accepted requirement
with a non-null risk and `verification: test` is named by at least one marker,
or the run fails naming the requirement.
