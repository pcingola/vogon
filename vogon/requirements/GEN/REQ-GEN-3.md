---
id: REQ-GEN-3
type: requirement
title: No command calls a language model
modules: [GEN, CLI]
status: accepted
verification: inspection
gxp_risk: data integrity
depends_on: [DEC-005, FACT-005]
tags: [determinism, scope]
---

# REQ-GEN-3 — No command calls a language model

**Requirement.** VOGON MUST NOT call a language model in any command, and the
distribution MUST NOT depend on a model client library.

Every command staying deterministic is what makes VOGON testable and what
allows it to disagree with a draft it did not write.

**What this does not require.** Preventing the user from running an agent
alongside it.

**Example.** A command that summarised a transcript by calling a model would
violate this, whoever paid for the call.

**Acceptance.** The plugin's scripts depend on no model client library, and no
script performs a network call.
