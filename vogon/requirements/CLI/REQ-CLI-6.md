---
id: REQ-CLI-6
type: requirement
title: Report an approval whose role has no holder
modules: [CLI, TRK]
status: proposed
verification: test
gxp_risk: data integrity
depends_on: [DEC-018, REQ-CLI-5]
tags: [configuration, approval, roles]
---

# REQ-CLI-6 — Report an approval whose role has no holder

**Requirement.** VOGON MUST report every configured approval whose role has
no holder in `vogon.yaml`, naming the approval and the role.

A role may be left without a holder until the procedure names one. The step
that needs the approval cannot be completed until then, and the gap is cheaper
to close before the step than at it.

**What this does not require.** Failing the run, and checking that the named
holder exists in any system.

**Example.** The sign-off roles are System Owner and IT Quality Manager, and
only the System Owner has a holder. A check reports the sign-off approval and
the IT Quality Manager role.

**Acceptance.** For any configuration, every approval whose role has an empty
holder list appears in the report with the approval and the role, and no
approval whose role has a holder appears.
