---
name: next
description: Lists the requirements ready to start and the requirements not ready, with the reasons, then assigns the chosen one. TRIGGER when: "what next", "what can I work on", "next requirement", "pick up work", "assign me REQ-".
---

# vogon:next

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   `requirements.md`, `tests.md`, and `tracking.md` where `vogon.yaml` names
   a tracker.
2. Leave out every requirement whose `status` is `withdrawn` or
   `{superseded_by: <id>}`. Report each one that needs approval again
   (`lifecycle.md` "Withdrawal and supersession").
3. For each remaining requirement, decide with the rules in `lifecycle.md`
   whether it is approved, whether its approval is stale, whether it is
   implemented and whether it is in progress.
4. Classify each requirement that is not implemented.
   - Ready: all of these hold:
     - it is approved, and the approval is not stale;
     - it is not in progress;
     - every requirement in its `depends_on` is implemented;
     - where `tests.md` requires test procedures before development, the
       procedures exist: a `test_procedures_written` entry links a merged
       pull request or a commit on the default branch, or the tracker item
       links the test procedure items `tracking.md` names;
     - where `tests.md` also requires their approval before development,
       each procedure is approved in the place `tests.md` names.
   - Not ready: any condition of Ready fails. Give each failing condition as
     a reason.
   - Report a fact, constraint or decision in `depends_on` that does not
     exist, is withdrawn or is superseded. The requirement can still be ready.
5. Order each list by tracker priority where the tracker holds one, highest
   first, then by id: module, then number compared numerically. Without a
   tracker, order by id. VOGON adds no ranking of its own.
6. Write the lists in the session, with the order used. For a ready
   requirement with a `planned` entry, give the plan path, marked "not
   approved" where that entry has no `approved_by`.
7. Assign each requirement the developer chooses. The choice, given with the
   request or after the lists, is the instruction to assign.
   - Where `vogon.yaml` names a tracker and the requirement's `REQ-*.json` has
     an entry with an `issue` field, set the assignee of that tracker item to
     the developer running the skill: the user the tracker connection is
     authenticated as.
   - Where the requirement has no entry with an `issue` field, or no tracker
     is configured, report the choice and write nothing.
   - Where the chosen requirement is not ready, assign it as chosen and
     repeat its reasons from step 4.

The skill writes no tracker field other than the assignee, and performs no
transition.
