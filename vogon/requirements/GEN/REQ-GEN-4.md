---
id: REQ-GEN-4
type: requirement
title: Ship the writing standard with the drafting instructions
modules: [GEN]
status: accepted
verification: inspection
gxp_risk: none
depends_on: [DEC-008, REQ-GEN-1]
references:
  - src/docs/dev/writing.md
tags: [writing, drafting]
---

# REQ-GEN-4 — Ship the writing standard with the drafting instructions

**Requirement.** VOGON MUST ship the writing standard with the drafting
instructions, and the instructions MUST require every drafted
record to follow it.

A schema constrains the fields. Nothing else constrains the prose, and prose is
what the reader reads.

**What this does not require.** Rewriting text a person wrote, and applying the
standard to the host project's own code comments.

**Example.** With the plugin installed, the coding agent reads both the
drafting instructions and the writing standard from it.

**Acceptance.** The plugin holds both documents, and the drafting instructions
reference the standard by path.
