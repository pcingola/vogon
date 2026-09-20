---
id: REQ-REC-9
type: requirement
title: Report a held document that breaks the naming or frontmatter rules
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-009]
references:
  - src/docs/dev/sources.md
tags: [sources, validation]
---

# REQ-REC-9 — Report a held document that breaks the naming or frontmatter rules

**Requirement.** VOGON MUST report a file in `gxp/sources/` whose name does not
start with a date in `YYYY-MM-DD` form followed by a slug, a markdown document
there with no frontmatter, one whose `date` disagrees with its filename prefix,
and one whose `kind` or `authority` is outside the allowed set.

The date in the name is what makes the directory usable and what distinguishes
two versions of one document. Frontmatter is what the authority ordering and
the indexes are computed from.

**What this does not require.** Checking the slug against the document's
content, and requiring frontmatter on a held original that is not text.

**Example.** `procedure.pdf` is reported for having no date.
`2026-04-02_procedure.md` declaring `date: 2026-04-03` is reported for
disagreeing with its name.

**Acceptance.** For any file in `gxp/sources/`, the name matches the pattern
and a markdown file's frontmatter is complete and internally consistent, or the
file is reported with the rule it breaks.
