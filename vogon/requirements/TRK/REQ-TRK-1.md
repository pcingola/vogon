---
id: REQ-TRK-1
type: requirement
title: Never transition an issue into an approved or signed state
modules: [TRK]
status: accepted
verification: test
gxp_risk: data integrity
depends_on: [CON-001, FACT-001]
references:
  - src/docs/dev/architecture.md
  - src/docs/user/install.md
tags: [approval, tracker]
---

# REQ-TRK-1 — Never transition an issue into an approved or signed state

**Requirement.** VOGON MUST NOT transition an issue in the tracker or the test
manager into a state that records approval or signature.

An electronic signature is applied by the signer entering their own
credentials. A transition performed by the tool names nobody, and the state it
leaves behind claims that someone is answerable when nobody is.

VOGON cannot refuse such a call itself: a server's tools are not known in
advance, and a generic tool or a shell command reaches the same API. The
tracker and the test manager enforce it, with a workflow in which a transition
into an approved state requires the approver's own credentials. VOGON needs no
transition, instructs the agent never to make one, and states that workflow as
an installation requirement.

**What this does not require.** Detecting or refusing a transition call,
preventing a person from making that transition, and reporting who made it.

**Example.** A run that creates thirty requirement issues and twelve test
issues leaves all of them in a pre-approval state. No option changes that.

**Acceptance.** The operations VOGON needs from the tracker and the test
manager (`OPERATIONS` in `snapshots.py`) include none that performs a
transition. `SKILL.md` forbids a transition into a state that records approval
or signature. The installation guide lists, as a requirement, a workflow in
which a transition into an approved or signed state requires the approver's
own credentials.
