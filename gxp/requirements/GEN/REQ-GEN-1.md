---
id: REQ-GEN-1
type: requirement
title: Ship the instructions a coding agent follows to draft records
modules: [GEN]
status: accepted
verification: inspection
gxp_risk: none
depends_on: [DEC-005, DEC-004]
tags: [drafting, claude-code]
---

# REQ-GEN-1 — Ship the instructions a coding agent follows to draft records

**Requirement.** VOGON MUST install into the host project the instructions a
coding agent follows to turn a held source document into draft records, and
those instructions MUST state the record schema, the id grammar, and the order
in which a sentence is classified.

Drafting happens in the agent, not in VOGON. The instructions are how the tool
governs output it does not produce.

**What this does not require.** Running the agent, and supporting an agent
other than the one version 0.1 targets.

**Example.** Installing VOGON into a project writes the drafting instructions
where the coding agent reads them, alongside the project's existing
instructions rather than replacing them.

**Acceptance.** After installation, the instructions are present in the host
project, and they specify every frontmatter field the checker enforces.
