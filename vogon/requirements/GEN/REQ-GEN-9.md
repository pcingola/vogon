---
id: REQ-GEN-9
type: requirement
title: Report a risk assessment that no longer matches the records
modules: [GEN]
status: accepted
verification: test
gxp_risk: product quality
depends_on: [DEC-013]
references:
  - src/docs/dev/records.md
tags: [risk, validation]
---

# REQ-GEN-9 — Report a risk assessment that no longer matches the records

**Requirement.** VOGON MUST report a requirement carrying a risk level that
does not appear in the approved risk assessment, and a requirement whose
`gxp_risk` differs from the level the assessment approved.

The assessment is approved against the levels as they stood. A level raised or
lowered afterwards leaves the assessment asserting a judgement nobody made.

**What this does not require.** Re-approving the assessment, deciding whether
the difference matters, or checking the reasoning.

**Example.** A requirement approved in the assessment as `product quality` is
later edited to `safety`. The next run reports the requirement, the level in
the assessment and the level in the record.

**Acceptance.** For every requirement whose `gxp_risk` is not `none`, an entry
exists in the approved risk assessment and its level equals the record's, or
the requirement is reported with both levels.
