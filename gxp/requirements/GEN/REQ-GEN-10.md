---
id: REQ-GEN-10
type: requirement
title: Ship the instructions for writing and retiring a plan
modules: [GEN]
status: accepted
verification: inspection
gxp_risk: product quality
depends_on: [DEC-014]
references:
  - src/docs/dev/architecture.md
tags: [plans, instructions]
---

# REQ-GEN-10 — Ship the instructions for writing and retiring a plan

**Requirement.** The instructions VOGON installs MUST require a plan to state
what will be built and name the records it implements, to be written before
the code, to live at `gxp/plans/plan_<slug>.md`, and to be moved to
`gxp/plans/done/` once implemented or abandoned, with anything that must stay
true written into the documentation first.

A plan that is not retired is read later as though it described the system. A
plan retired without its lasting content moved out loses that content.

**What this does not require.** Checking that the plan was followed, or that
the documentation was updated before the plan moved.

**Example.** An agent asked to plan a change writes
`gxp/plans/plan_result-import.md` naming the requirements it implements, and
moves it to `gxp/plans/done/` when the change merges.

**Acceptance.** The installed instructions state all four rules, and the check
that compares the installed copy to the shipped one passes.
