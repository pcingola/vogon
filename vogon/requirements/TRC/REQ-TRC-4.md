---
id: REQ-TRC-4
type: requirement
title: Fail on a requirement verified by test that no test names
modules: [TRC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-006, FACT-002, REQ-TRC-1]
references:
  - src/docs/dev/architecture.md
tags: [coverage, ci]
---

# REQ-TRC-4 — Fail on a requirement verified by test that no test names

**Requirement.** VOGON MUST fail where an accepted requirement whose
`verification` is `test` is named by no test marker, whatever its `gxp_risk`.

A requirement verified by test with no test naming it has not been verified.
The test manager reports coverage only of the requirement issues it holds, so a
requirement that was never pushed, or was pushed with no linked test, does not
appear as a gap in that report; this check is what makes it visible.

**What this does not require.** Failing on a requirement whose `verification`
is `inspection`, `analysis` or `demonstration`, which a person verifies rather
than a test, and judging whether the tests that name a requirement cover what
it states, which the test review does (`REQ-GEN-11`).

**Example.** A requirement with `gxp_risk: none` and `verification: test` that
no marker names fails the check, as does one with `gxp_risk: data integrity`.

**Acceptance.** For any set of records and markers, every accepted requirement
with `verification: test` is named by at least one marker, or the check exits
non-zero naming the requirement.
