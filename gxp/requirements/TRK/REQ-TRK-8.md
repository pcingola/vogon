---
id: REQ-TRK-8
type: requirement
title: Report an approval applied by the record's author
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [CON-002, REQ-TRK-7]
tags: [approval, independence]
---

# REQ-TRK-8 — Report an approval applied by the record's author

**Requirement.** Where the person who approved a record's issue is also the
author of the record, VOGON MUST report it.

The separation between author and approver is the reason the roles exist. An
approval by the author records that one person looked at their own work.

**What this does not require.** Removing the approval, identifying the author
where the git history has been rewritten, and reconciling one person holding
several roles.

**Example.** A record whose only commits are by one person, approved in the
tracker by that person, is reported as an independence failure.

**Acceptance.** For any approved record whose authorship is determinable, the
approver differs from every author, or the record is reported naming both.
