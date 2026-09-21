---
id: REQ-TRK-1
type: requirement
title: Never transition an issue into an approved or signed state
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [CON-001, FACT-001]
tags: [approval, jira]
---

# REQ-TRK-1 — Never transition an issue into an approved or signed state

**Requirement.** VOGON MUST NOT transition a tracker issue into a state that
records approval or signature.

An electronic signature is applied by the signer entering their own
credentials. A transition performed by the tool names nobody, and the state it
leaves behind claims that someone is answerable when nobody is.

**What this does not require.** Preventing a person from making that
transition, and reporting who made it.

**Example.** A run that creates thirty requirement issues leaves all thirty in
a pre-approval state. No option changes that.

**Acceptance.** For any configured workflow, the set of transitions VOGON is
able to perform excludes every transition into a state configured as recording
approval, and attempting one is refused rather than attempted and failed.
