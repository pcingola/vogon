---
id: REQ-TRK-11
type: requirement
title: Report an approval given after what it governs was used
modules: [TRK]
status: proposed
verification: test
gxp_risk: data integrity
depends_on: [DEC-024, FACT-003, FACT-004, REQ-TRC-6, REQ-TRC-9, REQ-TRK-7]
references:
  - src/docs/dev/architecture.md
tags: [approval, audit, timestamps]
---

# REQ-TRK-11 — Report an approval given after what it governs was used

**Requirement.** VOGON MUST report every requirement issue approved later than
the earliest commit on the default branch naming its record id, and every test
issue approved later than the earliest result imported against it, naming the
issue, the approval time and the time of that commit or import.

A requirement is used when code built on it reaches the default branch, and a
test case is used when its result becomes evidence. An approval given after
either is dated after the work it was meant to precede, which is a finding an
audit makes from the dates alone (`FACT-004`).

**What this does not require.** Preventing or withdrawing the approval,
establishing the true time of a commit whose date was set by the client
(`FACT-003`), and ordering approvals other than those of requirement and test
issues.

**Example.** A requirement issue is approved on 2026-05-10, and the first
commit on the default branch naming its id is dated 2026-05-08. The run
reports the issue with both dates.

**Acceptance.** For a requirement issue approved at 2026-05-10T09:00Z whose
record id is first named on the default branch by a commit dated
2026-05-08T16:00Z, the issue is reported with both times. Approved at
2026-05-08T15:00Z, it is not reported. For a test issue approved at
2026-06-02T10:00Z whose earliest imported result is dated 2026-06-01T12:00Z,
the issue is reported with both times; with no imported result, it is not
reported. An issue with no approval is not reported.
