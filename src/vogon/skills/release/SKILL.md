---
name: release
description: Drafts and checks the validation documents for a release commit, builds the traceability matrix and files the evidence. TRIGGER when: "release", "prepare the release", "validation report", "traceability matrix", "file the release evidence".
---

# vogon:release

Drafts and checks the documents a release needs, from the requirements, test
procedures, tests, code and test results of one release commit. Produces the
traceability matrix, files the documents, the matrix and the results for
approval, and records the release step in each requirement's state file. Use it
when a commit is to be released and a test run on that commit exists. People
sign off the documents; VOGON never signs.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- The release commit, and the release name used in the state files and in
  `vogon/documents/<release>/`. Both come from the developer.
- The JUnit XML of a test run on the release commit, made with the command in
  `tests.md` "Running the test suite". Its suite name identifies the commit
  in the form `tests.md` "Results tied to a commit and an environment" gives.
  When that topic is empty, the suite name is the full hash of the release
  commit.
- Process files: `release.md`, `documents.md`, `traceability.md`, `tests.md`,
  `requirements.md`, and `tracking.md` where `vogon.yaml` names a tracker.
- `vogon/project/vogon.yaml`: the document system, the test manager, the
  repository host, and the role holders.

## Steps

1. Do the steps of `common.md` "Start of every skill", with the process files
   the Inputs name.
2. Check the results file.
   - Read the `name` of each `testsuite` in the JUnit XML. Report every suite
     name that does not identify the release commit in the form the Inputs
     give.
   - Uncommitted changes in the tested working tree mean the commit does not
     identify the code tested. Check for them only when the run was made in
     the skill's working tree and `HEAD` there is still the release commit.
     Report any found. Otherwise report that the check could not be made.
   - Report a JUnit XML with no `req` property. The host `conftest.py` then
     lacks the lines of `markers.md`, and the matrix shows every requirement
     as untested.
3. Read `release.md`. Determine the release contents as it states them,
   including the requirements in the release. Check each precondition it
   states against the repository, the state files and the configured systems,
   and report each one that is not met, with its evidence.
4. Read `documents.md` for each document VOGON drafts: its template, format,
   approvers and location. A template that cannot be read is reported, and
   that document is not drafted.
5. Prepare a read-only checkout of the release commit for the sub-agents.
   Sub-agents read the requirements, test procedures, tests and code there,
   never from the current branch. Read the test procedures from where
   `tests.md` keeps them: the repository, the tracker or the test manager.
6. Draft each document. Start one writing sub-agent per document, in
   parallel. Give it the document's entry in `documents.md`, its template and
   format, the requirements in the release with their state files, the test
   procedures, the tests, the code, the JUnit XML, the output path, its log
   path and the logs of earlier rounds. The sub-agent writes the document in
   its template and format, and cites, for each statement, the requirement,
   procedure, test, file or result it rests on. Output path:
   `vogon/tmp/<release>/` when `vogon.yaml` names a document system;
   otherwise `vogon/documents/<release>/` on the working branch (`common.md`
   "Systems by role").
7. Check each document. Start one evaluating sub-agent per document, with
   the perspective in the Loops table, and give it the other drafted
   documents of the release. Run the review loop (`loop.md`).
8. Produce the traceability matrix as `traceability.md` states.
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
9. File the documents, the matrix and the JUnit XML, unchanged, where
   `documents.md` states.
   - A document system is configured: upload each to the location
     `documents.md` names for it.
   - No document system: commit them on the working branch, at the location
     step 6 used.
10. Push the working branch and open a pull request on the repository host.
    The description lists the documents, where each is filed, the unmet
    preconditions and the results-file findings.
11. Append a `released` entry to the state file of each requirement in the
    release (`lifecycle.md` "State file").
12. Read the plan path from the `planned` entries of the requirements in the
    release. Move each plan whose named requirements all have a `released`
    entry from `vogon/plans/` to `vogon/plans/done/` with `git mv`. Commit the
    state files and the moves, and push to the same branch.
13. Find the approver roles of each document in `documents.md` and their
    holders in `roles` in `vogon.yaml`. Tell each holder which documents wait
    for their approval, and where: the document system location or the pull
    request.
14. Remove the checkout from step 5, and delete the drafts in
    `vogon/tmp/<release>/`.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| One per document | One document `documents.md` lists, in its template and format | One per document | The release document checklist below |

Release document checklist:

- Each statement is true of the requirements, the code and the JUnit XML
  results of the release commit, and cites what it rests on.
- The document follows its template and format.
- It states nothing the cited sources do not.
- It names the release commit it was drafted from.
- It does not state that it was approved or signed and has no signature block;
  the document system or the pull request records the approval.
- It agrees with the other documents of the release: the same requirements, the
  same risk values, the same commit.
- Every requirement or document in the release that was edited after its
  approval is reported.

## Outputs

| Path or system | Format |
| --- | --- |
| `vogon/documents/<release>/<document>` | Each document in the template and format `documents.md` names; without a document system only |
| `vogon/tmp/<release>/<document>` | Draft of each document, gitignored, deleted at the end; with a document system only |
| `traceability-matrix.md` beside the documents | Output of `vogon trace`, unchanged |
| Test manager's traceability report beside the documents | As the test manager gives it |
| JUnit XML beside the documents | The input file, unchanged |
| `vogon/requirements/<module>/REQ-*.json` | A `released` entry |
| `vogon/plans/done/plan_<slug>.md` | Each plan whose requirements are all released, moved with `git mv` in step 12 |

External writes:

- Test manager: the JUnit XML, uploaded unchanged.
- Document system: the documents, the matrix and the JUnit XML, at the
  locations `documents.md` names.
- Repository host: one pull request with the state files, the moved plans
  and, without a document system, the filed documents.

## Reference files

- Main agent: `${CLAUDE_PLUGIN_ROOT}/references/common.md`,
  `${CLAUDE_PLUGIN_ROOT}/references/loop.md`,
  `${CLAUDE_PLUGIN_ROOT}/references/lifecycle.md`,
  `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`,
  `${CLAUDE_PLUGIN_ROOT}/references/markers.md`.
- Writing and evaluating sub-agents:
  `${CLAUDE_PLUGIN_ROOT}/references/writing.md`,
  `${CLAUDE_PLUGIN_ROOT}/references/records.md`.
