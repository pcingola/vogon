---
id: REQ-TRC-9
type: requirement
title: Require a change to name the records it implements
modules: [TRC]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [DEC-006]
references:
  - src/docs/dev/architecture.md
tags: [git, traceability]
---

# REQ-TRC-9 — Require a change to name the records it implements

**Requirement.** VOGON MUST fail a change whose commit messages and pull
request description name no record id and no `NO-REQ`, and MUST fail one
naming an id that resolves to no record.

The id is accompanied by the record's title and by prose saying what the
change does, because nobody reads ids. A commit message is fixed when it is
written and describes that change, so an id in it stays true. This is what connects a record to the change that
implemented it, which a test marker does not give: the marker says what
verifies the record, not what built it.

A change that implements no requirement, such as a typo fix, a refactoring
or a dependency update, names `NO-REQ` in place of a record id. `vogon init`
writes `vogon/NO-REQ.md`, which says when to use it.

**What this does not require.** Judging whether the named record is the right
one, naming every record the change touches, or an id on a commit that is
part of a change whose other commits carry one.

**Example.** A pull request whose commits mention no record id fails. A
description reading "REQ-TRK-2 — report a record edited after its issue was
approved" clears it. A pull request fixing a typo, with a commit reading
"NO-REQ — fix a typo in the installation guide", clears it. Naming
`REQ-TRK-99`, which does not exist, fails.

**Acceptance.** For any change under review, at least one record id or
`NO-REQ` appears in its commit messages or its description, and every id that
appears resolves to a record, or the change is reported with the ids that did
not resolve.
