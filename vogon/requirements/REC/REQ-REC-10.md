---
id: REQ-REC-10
type: requirement
title: Report a held document edited after it was filed
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-009, FACT-004]
references:
  - src/docs/dev/sources.md
tags: [sources, evidence]
---

# REQ-REC-10 — Report a held document edited after it was filed

**Requirement.** VOGON MUST report a file in `vogon/sources/` whose content has
changed since the commit that added it.

A citation asserts that a specific document says something. A document that can
be edited afterwards cannot support that, and the edit is invisible to everyone
who read the record before it.

**What this does not require.** Preventing the edit, and reporting a file that
was deleted.

**Example.** A transcript filed in March and corrected in June is reported,
naming both commits. The correct fix is a new file dated June.

**Acceptance.** For any file in `vogon/sources/` reachable in the git history,
its current content equals the content of the commit that introduced it, or the
file is reported with both revisions.
