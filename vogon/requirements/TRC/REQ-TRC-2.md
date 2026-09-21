---
id: REQ-TRC-2
type: requirement
title: Fail on a marker naming a requirement that does not exist
modules: [TRC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-006, REQ-TRC-1]
tags: [markers, ci]
---

# REQ-TRC-2 — Fail on a marker naming a requirement that does not exist

**Requirement.** VOGON MUST fail where a test marker names an id for which no
requirement record exists.

A marker naming nothing is a trace that silently verifies nothing, and it
survives every rename and deletion until something checks it.

**What this does not require.** Checking that the test verifies what the
requirement says.

**Example.** A test marked `REQ-TRC-40` in a project whose highest `TRC`
requirement is 8 fails the run.

**Acceptance.** For any set of markers and records, a marker naming an id with
no record produces a failure naming the test and the id.
