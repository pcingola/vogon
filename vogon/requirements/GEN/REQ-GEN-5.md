---
id: REQ-GEN-5
type: requirement
title: Generated text carries no satirical voice
modules: [GEN, TRK]
status: accepted
verification: inspection
gxp_risk: none
depends_on: [DEC-008]
references:
  - src/docs/dev/writing.md
  - assets/brand.md
tags: [writing, brand]
---

# REQ-GEN-5 — Generated text carries no satirical voice

**Requirement.** VOGON MUST NOT write the product's satirical voice into a
record, into a tracker field, into CLI output, or into any document it
generates. That voice is limited to the marketing page.

A record is read by someone deciding what to build and by someone answerable
for approving it. A joke in it costs them time and casts doubt on the rest.

**What this does not require.** Removing the voice from the places it belongs.

**Example.** A requirement pushed to the tracker reads as a requirement, and a
command that refuses to push says what it refused and why.

**Acceptance.** No fixed string from the brand guide appears in a record, in a
tracker field, in CLI output, or in any file written under `vogon/`.
