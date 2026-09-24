---
id: REQ-CLI-5
type: requirement
title: Read the approval roles and the people holding them from configuration
modules: [CLI, TRK]
status: proposed
verification: test
gxp_risk: data integrity
depends_on: [DEC-018, REQ-CLI-3]
references:
  - src/docs/dev/architecture.md
tags: [configuration, approval, roles]
---

# REQ-CLI-5 — Read the approval roles and the people holding them from configuration

**Requirement.** VOGON MUST read from `vogon.yaml`, for each approval, the roles
that give it and the system it is given in, and, for each role, the
people who hold it, and MUST use the shipped default assignment for any
approval the file does not configure.

Which role approves what is set by each company's procedure, and who holds a
role changes during a project. Both have to be changeable without changing
VOGON.

**What this does not require.** Checking that the configured assignment
matches the company's procedure, and reading role holders from a directory
service.

**Example.** A project configures the test cases to be approved by a role
named Validation Lead instead of Test Lead, and names one holder. VOGON checks
test-case approvals against that holder, and uses the default assignment for
every other approval.

**Acceptance.** For any `vogon.yaml`, each configured approval resolves to the
configured roles, system and holders, each unconfigured approval resolves to
the shipped default, and a configured approval naming a role that is not
defined fails with the approval and the role named.
