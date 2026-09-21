---
id: REQ-GEN-7
type: requirement
title: Instruct the agent to derive expected values from the requirement
modules: [GEN]
status: accepted
verification: inspection
gxp_risk: product quality
depends_on: [DEC-012]
references:
  - src/docs/dev/records.md
tags: [instructions, acceptance]
---

# REQ-GEN-7 — Instruct the agent to derive expected values from the requirement

**Requirement.** The drafting instructions VOGON installs MUST state that an
expected value in an acceptance block or a test is derived from the
requirement and never from running the code, and MUST state that an
acceptance block is left without `acceptance_by` for a person to accept.

Nothing downstream can tell where a number came from. The instruction is the
only place this is addressed, and it is addressed where the drafting happens.

**What this does not require.** Detecting that an expected value was taken
from a run.

**Example.** An agent asked to draft the acceptance block for a rounding
requirement works the value out from the rule in the requirement, and leaves
`acceptance_by` absent.

**Acceptance.** The installed instructions contain both statements, and the
check that compares the installed copy to the shipped one passes.
