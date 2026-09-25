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

**Requirement.** VOGON MUST report, as an error that fails the run, every
role that a configured approval uses and that has no holder in `vogon.yaml`,
in one finding per role naming the role and every approval it gives.

An approval whose role has no holder cannot be given, so the step that needs
it cannot be completed. The gap is cheaper to close at setup than at that
step, and a run that passes with it open reports a setup as complete when it
is not.

**What this does not require.** Checking that the named holder exists in any
system, and reporting a role that no approval uses.

**Example.** The risk assessment and release approvals are given by the
System Owner and the IT Quality Manager, and only the System Owner has a
holder. A check reports one error naming the IT Quality Manager role and both
approvals, and exits non-zero.

**Acceptance.** For any configuration, each role that has an empty holder
list and that an approval uses appears in exactly one error, naming the role
and every approval that uses it. No role with a holder and no role that no
approval uses appears. The exit status is non-zero whenever such an error is
reported.
