---
id: REQ-TRK-5
type: requirement
title: Create the issue for a record that has none and record its key
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [REQ-TRK-3, REQ-TRK-4]
tags: [jira]
---

# REQ-TRK-5 — Create the issue for a record that has none and record its key

**Requirement.** For an accepted record with no `tracked_as`, VOGON MUST
create the tracker issue and MUST write the resulting key into the record's
`tracked_as`.

The key is the only link between the repository copy and the controlled copy.
Left unrecorded, the next run creates a second issue.

**What this does not require.** Creating issues for records whose status is
`proposed` or `withdrawn`, and choosing the issue type per record.

**Example.** An accepted constraint with no `tracked_as` produces one issue
in the governing system, and the record gains that role and key.

**Acceptance.** After a run, every accepted record carries a `tracked_as` that
resolves to an existing issue, and every issue VOGON created is named by
exactly one record.
