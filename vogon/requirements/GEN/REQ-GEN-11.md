---
id: REQ-GEN-11
type: requirement
title: Ship a check of the test cases against what each requirement states
modules: [GEN, TRC]
status: proposed
verification: inspection
gxp_risk: product quality
depends_on: [DEC-024, DEC-019, REQ-TRC-1]
references:
  - src/docs/dev/architecture.md
tags: [tests, review, instructions]
---

# REQ-GEN-11 — Ship a check of the test cases against what each requirement states

**Requirement.** VOGON MUST ship instructions and a subagent definition
that, for every accepted requirement whose `verification` is `test`, compare
the requirement and its acceptance block with the tests whose markers name it,
and report each clause of the acceptance block that no test exercises, each
expected value that differs from the acceptance block, and each assertion that
does not follow from the requirement.

The marker checks establish that a test names a requirement. This is where the
tests are compared with what the requirement says, and the comparison has to
be made from the requirement, because a comparison with the code measures the
code.

**What this does not require.** Deciding that the tests are adequate, which
the Test Lead does, and checking requirements verified by inspection, analysis
or demonstration.

**Example.** A requirement's acceptance block gives the result for an empty
input and for a full one, and its only test uses a full input. The report
names the requirement and the clause for the empty input.

**Acceptance.** The instructions require all three kinds of finding for every
accepted requirement verified by test.
