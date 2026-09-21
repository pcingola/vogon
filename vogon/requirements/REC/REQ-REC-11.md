---
id: REQ-REC-11
type: requirement
title: Report a source list that cites documents wrongly
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-009, DEC-010]
references:
  - src/docs/dev/sources.md
  - src/docs/dev/records.md
tags: [sources, validation]
---

# REQ-REC-11 — Report a source list that cites documents wrongly

**Requirement.** VOGON MUST report a `source` list whose entries are not
ordered by the cited documents' `authority`, strongest first; a record of type
`fact` whose every source is `informal`; and a summary cited without the
document its `derived_from` names appearing earlier in the same list.

The first entry is what a reader checks the record against. A meeting listed
above a regulation sends that reader to the weaker document, and a summary
cited alone sends them to generated text no person spoke or wrote.

**What this does not require.** Ranking two documents of the same authority,
judging whether a document's declared authority is right, and checking that a
summary agrees with the document it came from.

**Example.** A constraint sourced to a meeting transcript and then a regulation
is reported. A fact sourced only to a deck is reported. A requirement sourced
only to `2026-09-17_workshop.summary.md` is reported, and adding the transcript
above it clears the report.

**Acceptance.** For any record carrying `source`, each entry's authority is no
stronger than the entry before it, a fact has at least one source above
`informal`, and every cited summary is preceded by the document it derives
from, or the record is reported with the rule it breaks.
