---
id: FACT-003
type: fact
title: Git commit metadata is supplied by the client
modules: [REC]
status: accepted
as_of: 2026-09-19
tags: [git, audit-trail]
---

# FACT-003 — Git commit metadata is supplied by the client

A git commit records an author name, an email address and a timestamp. All
three are taken from the client's configuration at commit time and can be set
to any value, and a history can be rewritten after the fact. A commit is
therefore a record of what changed, not an attributable record of who changed
it or when.

**Example.** `git commit --date` sets an arbitrary commit date, and
`git rebase` rewrites the history of commits already made.
