---
id: FACT-004
type: fact
title: Audit findings come from documents approved out of order
modules: [TRK, TRC]
status: accepted
as_of: 2026-09-19
tags: [audit, timestamps]
---

# FACT-004 — Audit findings come from documents approved out of order

The findings a validation package attracts are narrow and specific, and each
one is visible in a comparison of timestamps: requirements approved after the
release shipped, a design approved after the test run it describes, expected
results edited once a test failed, and evidence captured from a different build
than the one released.

Whether the documents are well written does not affect any of the four.

**Example.** A test specification is approved on the 10th and the qualified run
is dated the 8th. Nothing in the content of either document shows the problem;
the two dates do.
