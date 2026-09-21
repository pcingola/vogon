---
id: REQ-CLI-1
type: requirement
title: Exit non-zero when any check fails
modules: [CLI]
status: accepted
verification: test
gxp_risk: none
tags: [ci]
---

# REQ-CLI-1 — Exit non-zero when any check fails

**Requirement.** VOGON MUST exit with a non-zero status when any check
reports a failure, and with zero when none does.

The checks exist to fail a build. A command that reports problems on standard
output and exits zero passes CI.

**What this does not require.** A distinct exit code per kind of failure.

**Example.** A run finding one dangling `depends_on` prints it and exits
non-zero.

**Acceptance.** For any repository state, the exit status is zero if and only
if no check reported a failure.
