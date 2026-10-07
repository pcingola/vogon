# Planning

Steps 9 and 10 of the [steps](index.md). `vogon:next` lists the approved
requirements ready to start and those that are blocked. A developer runs
`vogon:implement` for one or more approved requirements, or for an existing
plan.

## Step 9: write the plan

If there is no plan, a writing sub-agent writes one in `vogon/plans/`: a
checklist of the parts to build and the tests that verify each. It refers to
the requirements and the code and does not restate them. Evaluators check the
plan against the requirements, so that every acceptance criterion is built and
tested and nothing else is, and against the code, so that what the plan names
exists and existing code is reused.

## Step 10: approve the plan

The skill stops, and the developers review the plan. A change they ask for
goes through the loop again. When a developer approves it, the skill commits
the plan and records the approval, with the developer's git identity and the
date, in the `planned` entry of each requirement's `REQ-*.json`. No code is
written before the plan is approved.

A change to the plan made later, while code is written, is written into the
plan and approved again before the work it changes continues
([Code, tests and documentation](implementation.md)).
