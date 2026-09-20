---
id: REQ-TRK-4
type: requirement
title: Show the diff and require confirmation before writing
modules: [TRK, CLI]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [REQ-TRK-3]
tags: [jira, safety]
---

# REQ-TRK-4 — Show the diff and require confirmation before writing

**Requirement.** Before writing to the tracker, VOGON MUST present every
create and every field change it intends to make, and MUST NOT proceed without
confirmation, unless invoked with an explicit unattended option.

A write reaches a system other people read, and some of those writes are on
issues already in review. The default is that a person sees what is about to
happen.

**What this does not require.** Confirming each change separately, and
confirming reads.

**Example.** A run that would create four issues and edit two prints the four
summaries and the two field diffs, and stops until confirmed.

**Acceptance.** With no unattended option, no tracker write occurs before
confirmation, and the presented set equals the set applied.
