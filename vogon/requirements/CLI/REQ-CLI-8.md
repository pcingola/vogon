---
id: REQ-CLI-8
type: requirement
title: Take the server, transitions and approved states for each role from setup, never from a default
modules: [CLI, TRK]
status: proposed
verification: test
gxp_risk: data integrity
depends_on: [DEC-025, REQ-CLI-3, REQ-CLI-4, REQ-TRK-1]
references:
  - src/docs/dev/architecture.md
tags: [configuration, setup, integration]
---

# REQ-CLI-8 — Take the server, transitions and approved states for each role from setup, never from a default

**Requirement.** VOGON MUST NOT default the server for a role, a role's
transitions or its approved states. Setup MUST derive them from the connected
servers and their workflows, MUST ask the person only where more than one
server could fill a role, and MUST have the person confirm the derived values
once. A role MUST be reached only through its configured server, and a role
with no entry MUST be reported as not configured.

A guessed server sends records to a system the company did not choose, and a
guessed approved state lets a transition into approval through the hook meant
to refuse it (`REQ-TRK-1`).

**What this does not require.** Choosing among several candidate servers for
the person, and checking the person's choice against company policy.

**Example.** One connected server provides the tracker's operations and two
provide the test manager's. Setup uses the first without a question, asks
which of the two fills the test manager, and shows every derived value as one
list for one confirmation.

**Acceptance.** With a `vogon.yaml` that has no `systems` entry, the
configuration VOGON reads holds no server, transitions or approved states for
any role, and a check needing the tracker reports a notice naming `tracker`
as not configured; that notice alone leaves the exit status zero. With one
candidate server for a role, the setup instructions use it without asking;
with two, they ask the person to choose; with none, they leave the role
absent. The setup instructions show every derived value as one list and
write `vogon.yaml` once, after the person confirms. `SKILL.md` states that a
role is reached only through its configured server.
