# Approving requirements

Step 5 of the [steps](index.md). The Product Owner approves each requirement,
with its acceptance criteria and risk fields, when `requirements.md` states.
VOGON never gives an approval
([Architecture](../architecture.md#approval-of-requirements)). The steps are in
`src/vogon/skills/approve/SKILL.md`.

Where no tracker holds approvals, the Product Owner gives an explicit
instruction in their own Claude Code session, such as "approve the last 10
requirements, then push". `vogon:approve` resolves it to ids, runs
`vogon approve`, commits and pushes. An instruction whose readings resolve to
different sets of ids records nothing. The approval is not an electronic
signature ([Architecture](../architecture.md#scope-and-roles)).

Where a tracker holds approvals, the Product Owner approves each item with the
tracker's approval transition. The approval stays in the tracker: skills read
it from the item, and `vogon:approve` records nothing and tells the Product
Owner to use the transition. Text the Product Owner edits in the tracker is
reported as a difference from `REQ-*.md`, and the developer resolves it as a
change to the requirement.
