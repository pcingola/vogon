---
id: REQ-CLI-8
type: requirement
title: Take the server and approved states for each role from setup, never from a default
modules: [CLI, TRK]
status: proposed
verification: test
gxp_risk: data integrity
depends_on: [DEC-025, REQ-CLI-3, REQ-CLI-4, REQ-TRK-2]
references:
  - src/docs/dev/architecture.md
tags: [configuration, setup, integration]
---

# REQ-CLI-8 — Take the server and approved states for each role from setup, never from a default

**Requirement.** VOGON MUST NOT default the server for a role or a role's
approved states. Setup MUST derive them from the connected
servers and their workflows, MUST ask the person only where more than one
server could fill a role, MUST ask for the holders of every role an approval
uses, and MUST have the person confirm all of it once. A role MUST be reached
only through its configured server. A role an approval is given in that has
no entry MUST be reported as an error naming those approvals.

A guessed server sends records to a system the company did not choose, and a
guessed approved state makes VOGON misjudge which issues are approved
(`REQ-TRK-2`).

**What this does not require.** Choosing among several candidate servers for
the person, and checking the person's choice against company policy.

**Example.** One connected server provides the tracker's operations and two
provide the test manager's. Setup uses the first, asks which of the two
fills the test manager, and shows everything as one list for one
confirmation.

**Acceptance.** With no `systems` entry in `vogon.yaml`, VOGON reads no
server or approved states for any role, and `vogon check`
reports one error per role an approval is given in, naming those approvals,
and exits non-zero. With one candidate server for a role, the setup
instructions use it; with two, they ask the person to choose; with none, they
leave the role absent. They ask for the holders of every role an approval
uses, show everything as one list, and write `vogon.yaml` once, after the
person confirms. `SKILL.md` states that a role is reached only through its
configured server.
