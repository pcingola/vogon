---
id: REQ-CLI-4
type: requirement
title: Check at install time that the configured servers provide the operations VOGON needs
modules: [CLI]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-011]
references:
  - src/docs/dev/architecture.md
tags: [install, configuration]
---

# REQ-CLI-4 — Check at install time that the configured servers provide the operations VOGON needs

**Requirement.** VOGON MUST publish, for each external role it uses, the
operations it requires from that role, and MUST check at install time that
each configured server provides them, failing with the role, the server and
the missing operation named.

The product filling each role is the project's choice, so VOGON cannot assume
what a server offers. A missing operation found at install is a
configuration error; found on first use it is a half-written record and a
tracker that disagrees with the repository.

**What this does not require.** Checking that an operation behaves correctly,
checking credentials or permissions, or checking a role the project has not
configured.

**Example.** A project configures a tracker server that can read and create
issues but cannot link two issues. Install fails, naming the tracker role, the
server and the link operation.

**Acceptance.** For any configured role, every operation VOGON publishes for
that role is present on the configured server, or install exits non-zero
naming the role, the server and each missing operation.
