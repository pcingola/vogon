---
id: REQ-CLI-7
type: requirement
title: Report a repository that allows a merge without an independent review
modules: [CLI]
status: proposed
verification: test
gxp_risk: product quality
depends_on: [CON-002, DEC-025, DEC-018]
references:
  - src/docs/dev/architecture.md
tags: [code-review, repository, configuration]
---

# REQ-CLI-7 — Report a repository that allows a merge without an independent review

**Requirement.** VOGON MUST read the repository host's rules for the default
branch and MUST report where they allow a change to merge without at least one
approving review from someone other than its author.

A change to the code of a validated system is reviewed by a second engineer
before it merges. The repository host enforces that when it is configured to,
and VOGON checks that it is configured to rather than enforcing it again.

**What this does not require.** Changing the repository host's rules,
performing or judging the review, and checking branches other than the
default branch.

**Example.** A repository whose default branch requires no review before a
merge is reported, naming the branch and the missing rule.

**Acceptance.** For any repository reachable through the configured repository
host, the check passes if and only if the default branch requires at least one
approving review and excludes the author's own approval, and otherwise reports
the branch and each missing rule.
