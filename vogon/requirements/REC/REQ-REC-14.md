---
id: REQ-REC-14
type: requirement
title: Report a module name that the host project has not declared
modules: [REC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-016, REQ-REC-13]
references:
  - src/docs/dev/records.md
tags: [identifiers, modules, validation]
---

# REQ-REC-14 — Report a module name that the host project has not declared

**Requirement.** VOGON MUST read the module names the host project declares
from `vogon/modules.yaml`, and MUST report every record whose id or `modules`
frontmatter names a module that is not declared there.

VOGON cannot judge a module name, only its shape, so a typo mints a second
sequence instead of failing and the records split across two names that look
alike. The declared list is what turns that into an error, and it is committed
so that adding a module is a reviewed change rather than a side effect of
minting an id.

**What this does not require.** Requiring the file where a host project uses no
modules, checking that a declared module is used by any record, and judging
whether a module name is a good one.

**Example.** A host project declares `TRK` and `REC`. A record minted as `REQ-TRK-3`
passes; one minted as `REQ-TRCK-3` is reported, naming the record and the
undeclared module.

**Acceptance.** For every record, each module named in its id and in its
`modules` frontmatter appears in `vogon/modules.yaml`, or the record is
reported with the undeclared name.
