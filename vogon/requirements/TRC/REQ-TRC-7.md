---
id: REQ-TRC-7
type: requirement
title: Do not generate a coverage or traceability report
modules: [TRC]
status: accepted
verification: inspection
gxp_risk: data integrity
depends_on: [DEC-003, FACT-005]
references:
  - src/docs/dev/architecture.md
tags: [evidence, scope]
---

# REQ-TRC-7 — Do not generate a coverage or traceability report

**Requirement.** VOGON MUST NOT produce a requirements coverage report or a
traceability matrix.

Producing one would make VOGON a tool whose output is offered as validation
evidence, which carries its own fitness-for-use obligation. The test manager produces both
from the links and results VOGON maintains.

**What this does not require.** Suppressing the local build checks in this
module, which report gaps to developers and are not offered as evidence.

**Example.** A command that printed requirement-to-test coverage for the
package would violate this. The check that fails the build on an unmarked
requirement does not, because its output is not part of the package.

**Acceptance.** No command writes a coverage report or traceability matrix into
`vogon/out/` or to standard output in a form intended for a validation package.
