---
id: REQ-TRC-5
type: requirement
title: Maintain the link between the test issue and the requirement issue
modules: [TRC, TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [FACT-002, DEC-003, DEC-006, REQ-TRC-1]
tags: [test-manager, links]
---

# REQ-TRC-5 — Maintain the link between the test issue and the requirement issue

**Requirement.** For every marked test, VOGON MUST ensure a test issue exists
in the test manager and is linked to the requirement issue named by the
marker.

The test manager builds its coverage report from that link. The marker in the test source
is the host project's statement of what verifies what, and this is where it reaches
the tracker.

**What this does not require.** Copying the test's code into the issue, and
removing a link a person added by hand.

**Example.** A test marked `REQ-TRC-4`, where that requirement is tracked as a
tracker issue and no test issue exists for the test, results in one test
issue created and linked.

**Acceptance.** After a run, every marked test whose requirement has an issue
has exactly one test issue linked to that requirement issue, and running
again creates nothing further.
