---
id: REQ-REC-4
type: requirement
title: Report a source or references path that does not resolve
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-001]
references:
  - src/docs/dev/records.md
tags: [validation, sources]
---

# REQ-REC-4 — Report a source or references path that does not resolve

**Requirement.** VOGON MUST report every `source` and `references` entry that
does not resolve to a file in the repository.

A path in `source` asserts that the named document states the record, and a
path in `references` asserts that the named document says how it is realised.
A path that resolves to nothing asserts either against a document nobody can
read.

**What this does not require.** Checking that the document says what the
record claims, and checking the order of a `source` list.

**Example.** A record citing `vogon/sources/2026-04-02_procedure.md` where no
such file is held is reported.

**Acceptance.** For any record carrying either field, every entry resolves to
a file, or the entry is reported with the citing record and the field it came
from.
