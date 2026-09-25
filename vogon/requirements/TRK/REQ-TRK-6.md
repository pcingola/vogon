---
id: REQ-TRK-6
type: requirement
title: Report a tracked_as key that no longer resolves
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [REQ-TRK-5]
tags: [tracker, drift]
---

# REQ-TRK-6 — Report a tracked_as key that no longer resolves

**Requirement.** VOGON MUST report every record whose `tracked_as` names, under any role, an
issue that does not exist, has been deleted, or has been moved to another
tracker project.

A record pointing at a missing issue looks tracked and is not. Its approval
state cannot be read, and the coverage report in the tracker does not include
it.

**What this does not require.** Recreating the issue, and clearing the field.

**Example.** A record tracked as an issue since deleted is reported, naming the
record and the key.

**Acceptance.** For any set of records carrying `tracked_as`, every key under every role
resolves to a reachable issue, or the record is reported with the key and the
reason it did not resolve.
