---
name: release
description: Drafts and checks the validation documents for a release commit, builds the traceability matrix and files the evidence. TRIGGER when: "release", "prepare the release", "validation report", "traceability matrix", "file the release evidence".
---

# vogon:release

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- The release commit, and the release name used in the state files and in
  `vogon/documents/<release>/`.
- The JUnit XML of a test run on the release commit, made with the command in
  `tests.md` "Running the test suite".

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   `release.md`, `documents.md`, `traceability.md`, `tests.md`,
   `requirements.md`, and `tracking.md` where `vogon.yaml` names a tracker.
2. Read the `name` of each `testsuite` in the JUnit XML. Report every suite
   name that does not identify the release commit in the form `tests.md`
   "Results tied to a commit and an environment" gives. Where that topic is
   empty, report every suite name that is not the commit's full hash.
3. Determine the release contents as `release.md` states them. Report each
   precondition it states that is not met, with its evidence.
4. Prepare a read-only checkout of the release commit. Sub-agents read the
   requirements, test procedures, tests and code there, never from the
   current branch.
5. A sub-agent drafts each document `documents.md` lists for VOGON, in its
   template and format, and cites, for each statement, the requirement,
   procedure, test, file or result it rests on. Output path:
   `vogon/tmp/<release>/` when `vogon.yaml` names a document system;
   otherwise `vogon/documents/<release>/` (`common.md` "Systems by role").
6. The review of each document, given the other drafted documents of the
   release, checks that:
   - it names the release commit it was drafted from;
   - it does not state that it was approved or signed and has no signature
     block;
   - every requirement or document in the release that was edited after its
     approval is reported;
   - it agrees with the other documents of the release: the same
     requirements, the same risk values, the same commit.
7. Produce the traceability matrix as `traceability.md` states.
   - A test manager is configured: upload the JUnit XML unchanged to it. The
     test manager produces the traceability report. Download the report where
     the test manager offers it, and put it beside the documents in the format
     the test manager gives.
   - No test manager: save the output of `vogon trace` unchanged as
     `traceability-matrix.md` beside the documents.
   - The matrix comes from `vogon trace` or the test manager. No sub-agent
     writes or edits it, and the skill does not change it. Report what the
     matrix shows: requirements with no test, failed tests, and markers that
     name an unknown requirement.
8. File the documents, the matrix and the JUnit XML, unchanged, where
   `documents.md` states: in the document system where one is configured,
   otherwise committed at the location step 5 used.
9. Push and open a pull request.
10. Append a `released` entry to the state file of each requirement in the
    release (`lifecycle.md` "State file").
11. For each plan named in a `planned` entry of a requirement in the release:
    when every requirement the plan names has a `released` entry, move the
    plan from `vogon/plans/` to `vogon/plans/done/`. Commit the state files and the
    moves, and push to the same branch.
12. For each approver role `documents.md` names, tell each holder listed
    under `roles` in `vogon.yaml` which documents wait for their approval,
    and where:
    the document system location or the pull request.
