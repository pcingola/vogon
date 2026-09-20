---
id: REQ-TRC-1
type: requirement
title: Provide a test marker naming the requirements a test verifies
modules: [TRC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-006]
references:
  - src/docs/dev/architecture.md
tags: [markers, pytest]
---

# REQ-TRC-1 — Provide a test marker naming the requirements a test verifies

**Requirement.** VOGON MUST provide a test marker that names one or more
requirement ids, and MUST collect the marked tests and their outcomes from a
test run.

The marker is the only link between a test and the requirement it verifies. It
sits on the test so that whoever changes the test changes the link, in the same
commit.

**What this does not require.** Marking every test. Tests that verify nothing
in `gxp/` carry no marker and are not reported as a gap.

**Example.** A test function marked with `REQ-TRC-4` and `REQ-TRC-5` is
collected once for each id, with the outcome of that run.

**Acceptance.** For any test run, every marked test appears in the collected
output with its node id, the requirement ids it names, and its outcome.
