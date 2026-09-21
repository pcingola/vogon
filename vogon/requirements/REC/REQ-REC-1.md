---
id: REQ-REC-1
type: requirement
title: Validate every record against the schema
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-001, DEC-007]
references:
  - src/docs/dev/records.md
tags: [validation]
---

# REQ-REC-1 — Validate every record against the schema

**Requirement.** VOGON MUST report every record whose frontmatter is missing a
required field, carries a field the record's type does not define, or uses a
value outside the set that field allows.

The frontmatter is what the indexes, the checks and any export are generated
from. A field that is absent where it is required, or holds an unexpected
value, silently changes what those outputs say.

**What this does not require.** Judging the prose in the body, and checking
that the statement is testable.

**Example.** A requirement record with no `verification` field, and one with
`status: done`, are both reported.

**Acceptance.** For any record file, the report names the file, the field and
the rule it fails. A record that satisfies the schema produces no output.
