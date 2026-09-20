---
id: FACT-002
type: fact
title: Xray reports coverage from issue links and imported results
modules: [TRC, TRK]
status: accepted
as_of: 2026-09-19
tags: [xray, coverage]
---

# FACT-002 — Xray reports coverage from issue links and imported results

Xray produces requirement coverage and traceability reports from two things: a
link between an Xray test issue and the requirement issue it verifies, and test
execution results imported against those test issues.

It reports on what it holds. A requirement with no linked test issue is
reported as uncovered; a requirement that was never created as an issue is not
reported at all, and the report shows full coverage of the issues that do
exist.

**Example.** A project has forty requirement records and thirty-eight
requirement issues. Xray reports coverage of thirty-eight, and nothing in the
report indicates that two are missing.
