---
id: REQ-TRK-7
type: requirement
title: Read approval state from the tracker and reject it in a record
modules: [TRK, REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [CON-003, FACT-003]
tags: [approval, validation]
---

# REQ-TRK-7 — Read approval state from the tracker and reject it in a record

**Requirement.** VOGON MUST read a record's approval state from the tracker,
and MUST report as invalid any record whose frontmatter or body asserts that
the record was approved or signed.

Git records what changed, not who changed it or when, so a repository claiming
approval asserts something it cannot evidence. The tracker holds the signature
and is the only place the state can be read from.

**What this does not require.** Removing the assertion, and preventing the
commit that added it.

**Example.** A record carrying `approved_by: jsmith` is reported as invalid.
Its approval state is obtained by asking the tracker about its `tracked_as`
issue.

**Acceptance.** No field naming an approver or a signature is accepted in a
record, and the approval state VOGON reports for a record comes from the
tracker in every case.
