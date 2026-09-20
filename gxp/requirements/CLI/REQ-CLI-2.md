---
id: REQ-CLI-2
type: requirement
title: Run every record and marker check without tracker access
modules: [CLI, REC, TRC]
status: accepted
verification: test
gxp_risk: none
depends_on: [DEC-001]
tags: [ci, offline]
---

# REQ-CLI-2 — Run every record and marker check without tracker access

**Requirement.** Every check over records and test markers MUST run with no
network access and no tracker credentials.

These checks run on every pull request, including from forks and from
environments that hold no credentials. A check that needs the tracker is a
check that gets disabled.

**What this does not require.** Running the drift and approval checks offline;
those read the tracker by definition and are reported as skipped when it is
unreachable.

**Example.** A pull request build with no credentials configured runs the
schema, link, id and marker checks and reports the tracker checks as skipped.

**Acceptance.** With the network unavailable, every record and marker check
completes and reports, and the exit status reflects their results alone.
