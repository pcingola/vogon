---
id: REQ-GEN-6
type: requirement
title: Cover the meeting pipeline in the installed instructions
modules: [GEN]
status: accepted
verification: inspection
gxp_risk: none
depends_on: [DEC-005, DEC-009, DEC-010, REQ-GEN-1]
references:
  - src/docs/dev/sources.md
tags: [meetings, drafting]
---

# REQ-GEN-6 — Cover the meeting pipeline in the installed instructions

**Requirement.** The instructions VOGON installs MUST state how a meeting
becomes held documents: the recording is transcribed, the transcript is filed
in `gxp/sources/` with `kind: transcript`, the meeting's date and its
participants, a summary is produced from that transcript and filed beside it
with `kind: summary` and `derived_from` naming it, and records are drafted from
the transcript rather than from the summary.

Transcription and summarising are language tasks, so they happen in the coding
agent. What VOGON governs is where the output lands and what it declares.

**What this does not require.** Performing the transcription, choosing a
transcription tool, and requiring a summary for every transcript.

**Example.** A recorded workshop yields
`gxp/sources/2026-09-17_requirements_workshop.md` and
`gxp/sources/2026-09-17_requirements_workshop.summary.md`, and the requirements
drafted from it cite the first.

**Acceptance.** The installed instructions name each step, the frontmatter each
produced file carries, and the rule that drafting reads the transcript.
