---
id: REQ-TRC-3
type: requirement
title: Fail on a marker naming a withdrawn or superseded requirement
modules: [TRC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-006, REQ-TRC-1]
tags: [markers, ci]
---

# REQ-TRC-3 — Fail on a marker naming a withdrawn or superseded requirement

**Requirement.** VOGON MUST fail where a test marker names a requirement whose
status is `withdrawn` or `superseded_by`.

A withdrawn requirement keeps its file and its id, so a marker pointing at it
resolves and looks healthy. The test is verifying a statement the host project has
retracted.

**What this does not require.** Deleting the test, and retargeting the marker
at the superseding record.

**Example.** A requirement is superseded by a later one. A test still marked
with the superseded id fails, naming both ids.

**Acceptance.** For any marker resolving to a record whose status is not
`proposed` or `accepted`, the run fails and the message names the test, the id
and the status.
