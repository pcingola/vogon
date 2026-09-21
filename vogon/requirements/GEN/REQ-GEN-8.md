---
id: REQ-GEN-8
type: requirement
title: Require the risk assessment to give the reasoning behind each level
modules: [GEN]
status: accepted
verification: inspection
gxp_risk: product quality
depends_on: [DEC-013]
references:
  - src/docs/dev/records.md
tags: [risk, instructions]
---

# REQ-GEN-8 — Require the risk assessment to give the reasoning behind each level

**Requirement.** The instructions VOGON installs for the risk assessment MUST
require, for every requirement carrying a risk level, the level, what a
failure would damage, and the records, held documents and findings that
informed the level, each cited by id or path.

A level with no reasoning cannot be reviewed. The person approving the
assessment is deciding whether the judgement is right, and that needs what the
judgement was based on.

**What this does not require.** Judging whether the reasoning is sound, or
that every source that could bear on the risk was found.

**Example.** An assessment entry gives `data integrity`, says a failure would
let an unapproved statement reach the tracker, and cites the constraint and
the procedure it rests on.

**Acceptance.** The installed instructions require all four parts for every
requirement carrying a risk level, and the check that compares the installed
copy to the shipped one passes.
