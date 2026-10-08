# Approving requirements

Step 6 of the [steps](index.md). The Product Owner approves each requirement,
with its acceptance criteria and risk fields, before development. VOGON records
the approval and never gives it. The rule is in
[Architecture](../architecture.md#approval-of-requirements).

## Without a tracker

The requirements and their approvals are in `REQ-*.md` and `REQ-*.json`, both
committed. The Product Owner approves in their own Claude Code session with an
explicit instruction, for example "approve the last 10 requirements, then
push". `vogon:approve` lists the ids and titles it resolved, runs
`vogon approve <id>...`, commits and pushes.

`vogon approve` appends to each `REQ-*.json` an `approved` entry with the
approver's git identity and the date. If `vogon.yaml` does not list the
user as Product Owner, it warns and still records the approval. A git identity
is not re-entered at approval, so this approval is not an electronic signature
under 21 CFR Part 11.

## With a tracker

The requirements are tracker items, created in step 5. The Product Owner may
edit the text in the tracker, then approves each item with the tracker's
approval transition. The item's status is the approval. `vogon:approve` syncs
each approval into `REQ-*.json` and copies the approved text into `REQ-*.md`.
Skills report an approval that is in the tracker and not yet synced, and work
from a requirement's text only once it is synced.

## After a change

A skill changes an approved requirement only with the agreement of the
developer running it. The pull request with the change appends a `changed`
entry to `REQ-*.json` and lists the requirement as needing approval again.
Until the Product Owner approves it again, `vogon:next` does not offer it as
ready. `requirements.md` states what else a change to an approved
requirement triggers, such as a tracker transition.
