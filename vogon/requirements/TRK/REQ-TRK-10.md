---
id: REQ-TRK-10
type: requirement
title: File the test manager's traceability report and results in the document system
modules: [TRK, TRC]
status: proposed
verification: test
gxp_risk: data integrity
depends_on: [DEC-003, DEC-025, REQ-TRC-6, REQ-TRC-7]
references:
  - src/docs/dev/architecture.md
tags: [evidence, document-system]
---

# REQ-TRK-10 — File the test manager's traceability report and results in the document system

**Requirement.** VOGON MUST export the traceability report and the test
results the test manager produces for a named build, and MUST file them in the
document system unchanged, recording the build with each file. VOGON MUST
refuse to file results for a build other than the one named.

The validation package holds the traceability report and the results for the
build being released, filed where the package is signed. Carrying the files
across by hand is where a report from an earlier build ends up in the package.

**What this does not require.** Producing the traceability report, which the
test manager does (`REQ-TRC-7`), signing the package, and deciding which build
is released.

**Example.** A release of build `a1b2c3d` exports the test manager's
traceability report and the results for that build, and files both in the
document system as drafts awaiting signature, each recording `a1b2c3d`.

**Acceptance.** For any named build, the files placed in the document system
are byte-identical to the test manager's export, each records the build, and
no result from another build is filed.
