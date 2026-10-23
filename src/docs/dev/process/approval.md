# Approving requirements

Step 5 of the [steps](index.md). The Product Owner approves each requirement,
with its acceptance criteria and risk fields, when `requirements.md` states.
VOGON records the approval and never gives it
([Architecture](../architecture.md#approval-of-requirements)). The steps are in
`src/vogon/skills/approve/SKILL.md`.

Where no tracker holds approvals, the Product Owner gives an explicit
instruction in their own Claude Code session, such as "approve the last 10
requirements, then push". `vogon:approve` resolves it to ids, runs
`vogon approve`, commits and pushes. An instruction whose readings resolve to
different sets of ids records nothing. The approval is not an electronic
signature ([Architecture](../architecture.md#scope-and-roles)).

Where a tracker holds approvals, the Product Owner approves each item with the
tracker's approval transition, and may edit the text first. `vogon:approve`
does not record an approval itself. It copies each approval made after the
latest change, with the text as it stood at that transition, into
`REQ-*.json` and `REQ-*.md`, in a pull request that a person merges. The
approval counts once it is on the default branch.
