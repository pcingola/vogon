---
id: REQ-TRC-8
type: requirement
title: Fail on a marker naming a requirement whose acceptance is not accepted
modules: [TRC]
status: accepted
verification: test
gxp_risk: product quality
depends_on: [DEC-024, REQ-REC-12]
references:
  - src/docs/dev/architecture.md
tags: [markers, acceptance]
---

# REQ-TRC-8 — Fail on a marker naming a requirement whose acceptance is not accepted

**Requirement.** VOGON MUST fail when a test marker names a requirement whose
acceptance block is absent or carries no `acceptance_by`.

A test written against a requirement nobody has stated the expected results
for proves that the code agrees with itself. Refusing the marker is what
forces the ordering: the criteria exist first, the test implements them.

**What this does not require.** Checking that the test's assertions match the
acceptance block, which needs the meaning of the test.

**Example.** A test marked with a requirement whose acceptance block has no
`acceptance_by` fails the run, naming the requirement and the marker.

**Acceptance.** For any marked test, every requirement id it names resolves to
a record with an acceptance block carrying `acceptance_by`, or the run fails
and names the id and the test.
