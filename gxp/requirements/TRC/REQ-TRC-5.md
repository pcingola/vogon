---
id: REQ-TRC-5
type: requirement
title: Maintain the link between the Xray test issue and the requirement issue
modules: [TRC, TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [FACT-002, DEC-003, DEC-006, REQ-TRC-1]
tags: [xray, links]
---

# REQ-TRC-5 — Maintain the link between the Xray test issue and the requirement issue

**Requirement.** For every marked test, VOGON MUST ensure an Xray test issue
exists and is linked to the requirement issue named by the marker.

Xray builds its coverage report from that link. The marker in the test source
is the project's statement of what verifies what, and this is where it reaches
the tracker.

**What this does not require.** Copying the test's code into the issue, and
removing a link a person added by hand.

**Example.** A test marked `REQ-TRC-4`, where that requirement is tracked as a
Jira issue and no Xray test issue exists for the test, results in one test
issue created and linked.

**Acceptance.** After a run, every marked test whose requirement has an issue
has exactly one Xray test issue linked to that requirement issue, and running
again creates nothing further.
