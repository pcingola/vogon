---
id: REQ-REC-6
type: requirement
title: Generate the record index from the frontmatter
modules: [REC]
status: accepted
verification: test
gxp_risk: none
depends_on: [DEC-001, DEC-002]
tags: [index, generation]
---

# REQ-REC-6 — Generate the record index from the frontmatter

**Requirement.** VOGON MUST generate an index of every record from the
frontmatter, holding the id, title, status and modules, and MUST write it under
`vogon/out/`.

The index is the list of what exists and is what anyone consults before
minting a new id. Maintained by hand it disagrees with the records within a
week.

**What this does not require.** Writing anything into the record files, and
keeping an index per directory.

**Example.** Adding a constraint and re-running produces an index containing
it, with no other change.

**Acceptance.** For any set of records, the generated index lists every record
exactly once with the values held in its frontmatter, and re-running with no
change to the records produces a byte-identical file.
