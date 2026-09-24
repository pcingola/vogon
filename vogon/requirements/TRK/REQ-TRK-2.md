---
id: REQ-TRK-2
type: requirement
title: Report a record edited after its issue was approved
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [CON-001, FACT-001, FACT-004]
tags: [approval, drift]
---

# REQ-TRK-2 — Report a record edited after its issue was approved

**Requirement.** Where a record has changed since the tracker approved the
issue it is tracked as, VOGON MUST report the record as requiring
re-approval and MUST NOT write the change to that issue.

Approval covers a specific version of the statement. An edit made afterwards
is outside what anyone approved, and a silent push would leave the tracker
asserting approval of text nobody read.

**What this does not require.** Deciding whether the change is material,
withdrawing the existing approval, and reverting the record.

**Example.** A requirement is approved in the tracker on the 3rd. On the 5th its
acceptance block gains a clause. The next run lists the record as requiring
re-approval and writes nothing to that issue.

**Acceptance.** For any record whose content differs from the content recorded
at the time of approval, the record appears in the report and no write is
issued for it.
