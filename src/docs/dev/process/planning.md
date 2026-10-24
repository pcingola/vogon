# Planning

Steps 7 and 8 of the [steps](index.md).

`vogon:next` lists the approved requirements ready to start and the blocked
ones with every reason, ordered by tracker priority and then by id, and assigns
the chosen requirement to the developer in the tracker. A requirement is
blocked by a missing or stale approval, or by not being sent to the tracker
where a tracker holds approvals; a dependency that is not
implemented, or is withdrawn or superseded; test procedures that `tests.md` requires
before development and that are missing, unapproved, or whose approval cannot
be read; or work in progress in an open pull request or on another branch. The
rules are in
`src/vogon/skills/next/SKILL.md`.

`vogon:implement` takes approved requirements or an existing plan. It resumes
a plan on a pushed branch, and revises a plan that is stale or not approved.
The plan is `vogon/plans/plan_<slug>.md`, in the format of
`src/vogon/skills/implement/references/plan-format.md`, checked against the
requirements and the code ([Architecture](../architecture.md#code-from-requirements)).
A developer approves it before any code is written, and the approval is
recorded in the `planned` entry of each requirement's `REQ-*.json`.
