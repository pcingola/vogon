---
id: REQ-REC-8
type: requirement
title: Report the mechanically checkable writing violations
modules: [REC]
status: accepted
verification: test
gxp_risk: none
depends_on: [DEC-008]
references:
  - src/docs/dev/writing.md
tags: [writing, validation]
---

# REQ-REC-8 — Report the mechanically checkable writing violations

**Requirement.** VOGON MUST report a record containing a banned word or phrase
from the published list, a placeholder value where a field should be absent, a
heading phrased as a question, a section heading naming open questions, TODO,
TBD or next steps, or a body longer than the limit for that record type.

These are the parts of the writing standard a checker can decide. The rest is a
review judgement and is not claimed here.

**What this does not require.** Judging whether the prose is clear, and
rewriting what it reports.

**Example.** A record whose `source` list holds `N/A`, and one with a section
headed "Open questions", are both reported.

**Acceptance.** For any record, each listed violation is reported with the file
and the line, and a record free of them produces no output. Passing is not a
claim about the prose.
