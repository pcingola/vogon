---
name: implement
description: Plans requirements, then writes and checks their code, tests and docs, and opens the pull request. TRIGGER when: user says implement REQ-*, plan REQ-*, write the automated tests for REQ-*, or names vogon/plans/plan_*.md.
---

# vogon:implement

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Steps

1. When requirement ids are given, look for an unmerged pushed branch with a
   `planned` entry for one of them. If there is one, report it and continue
   as if its plan had been given. When a plan is given and it or its
   `planned` entries are on an unmerged pushed branch, work on that branch.
2. Do the steps of `common.md` "Start of every skill", with the process files
   `requirements.md`, `tests.md`, and `tracking.md` where `vogon.yaml` names
   a tracker. Report each requirement that is not approved or whose approval
   is stale, in the session and in the plan's Summary (`lifecycle.md`
   "Missing approval"). Include those requirements in the plan. When
   `tests.md` requires test procedures before the tests, report each
   requirement that has none.
3. If no plan was given, a sub-agent writes `vogon/plans/plan_<slug>.md` in
   the format of
   `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/plan-format.md`. If a
   plan was given, compare it with the plan in the commit of each
   requirement's `planned` entry:
   - every requirement has such an entry and the plan is unchanged: report
     each entry with no `approved_by`, and go to step 5;
   - otherwise, go to step 4 with the given plan.
4. Present the plan to the developers working on its requirements and ask
   them to approve it. Write no code before a developer answers. A developer
   approves the plan, asks for a change, or tells the skill to continue
   without approval. On the instruction to continue, the `planned` entry has
   no `approved_by`.
   - Make every change to what the plan states in the plan, whether it is
     asked for now or later. The changed plan goes through this step again
     before the work it changes continues.
   - On approval, or on the instruction to continue: commit the plan, push
     the branch, and append a `planned` entry to each requirement's state
     file (`lifecycle.md` "State file"). Commit and push the state files.
5. For each part of the plan, a sub-agent writes the part's code, tests and
   documentation. It works out each expected value (`records.md` "Expected
   values") and marks each test (`markers.md`). It calls only the interfaces
   the plan names. Where the part needs an interface the plan does not name,
   the sub-agent reports it and does not invent one; the plan is changed
   through step 4.
6. Each part is reviewed against
   `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/test-checklist.md`, and
   by a sub-agent running Claude Code's `code-review` skill on the part's
   diff, without `--fix`. The code review also checks that structured data
   uses defined data structures and classes, such as dataclasses or typed
   models, and not dictionaries passed between functions.
7. Run the test suite with the command in `tests.md` "Running the test
   suite". When that topic is empty, ask the developer and record the answer
   (`process-files.md` step 5). Fix the code for each failure, and change a
   test only where `test-checklist.md` allows it. Where the requirement itself
   is wrong:
   - With the developer's agreement, the requirement is changed
     (`lifecycle.md` "Change to an approved requirement"). The test follows
     the changed text.
   - Without that agreement, the test stays on the current text, and the
     finding is reported.
8. Commit the code, tests and documentation, with commit messages that name
   the requirements (`markers.md`). Push, and open the pull request. The
   description reports a plan that is not approved.
9. Append an `implemented` entry to each requirement's state file
   (`lifecycle.md` "State file"). Commit and push it on the same branch.
