---
id: REQ-TRC-6
type: requirement
title: Import results against the test issues, recording the build
modules: [TRC, TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [FACT-002, FACT-004, REQ-TRC-5]
tags: [test-manager, evidence]
---

# REQ-TRC-6 — Import results against the test issues, recording the build

**Requirement.** VOGON MUST import test execution results against the test
issues in the test manager, and MUST record with each import the identifier of
the build the tests ran on. VOGON MUST refuse an import with no build
identifier.

Evidence captured from a different build than the one released is one of the
findings a package attracts, and it is only detectable if the build is recorded
at import.

**What this does not require.** Deciding which build should have been tested,
and reconciling the build against a release.

**Example.** A run on commit `a1b2c3d` imports with that commit recorded. A run
whose build identifier is empty is refused and nothing is imported.

**Acceptance.** For any completed test run, the imported execution carries a
non-empty build identifier matching the revision under test, or no import
occurs.
