---
id: REQ-TRK-9
type: requirement
title: Report an approval given by a person who does not hold the configured role
modules: [TRK]
status: proposed
verification: test
gxp_risk: data integrity
depends_on: [DEC-018, REQ-CLI-5, REQ-TRK-7]
tags: [approval, roles]
---

# REQ-TRK-9 — Report an approval given by a person who does not hold the configured role

**Requirement.** Where an issue is in an approved state and the person who
moved it there does not hold the role configured to give that approval, VOGON
MUST report the issue, the person and the role.

The procedure assigns each approval to a role so that the person answerable
for it is known in advance. An approval by someone else is recorded in the
system and answers for nothing the procedure asked for.

**What this does not require.** Removing the approval, and checking whether
the person held the role on the date of the approval.

**Example.** The requirements are configured to be approved by the Product
Owner. A requirement issue approved by an engineer who is not a configured
holder of that role is reported.

**Acceptance.** For any approved issue whose approver can be read, the
approver is a configured holder of the role for that approval, or the issue is
reported with the approver and the role.
