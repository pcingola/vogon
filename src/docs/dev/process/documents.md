# Release documents

Steps 13 to 15 of the [steps](index.md). A developer runs `vogon:release` with
a release commit and the JUnit XML of a test run on that commit. The rules are
in [Architecture](../architecture.md#release).

## Step 13: draft the documents and the matrix

`release.md` states what the release contains and its preconditions. The skill
reports each precondition not met, each suite name in the JUnit XML that is not
the release commit, and a run made on uncommitted changes.

`documents.md` lists the documents VOGON drafts, each with its template,
format, approvers and location, and the documents left to the project. One
writing sub-agent per document drafts it from the requirements, test
procedures, tests, code and results of the release commit, and cites what each
statement rests on. An evaluator checks each document against those sources.

The traceability matrix is produced as `traceability.md` states. Where a test
manager is configured, VOGON uploads the JUnit XML unchanged and the test
manager produces the traceability report. Where none is, `vogon trace` joins
the `req` and `procedure` markers and the results of that commit into the
matrix ([Architecture](../architecture.md#traceability)). No model writes or
edits the matrix. The skill reports what it shows: requirements with no test,
failed tests, and markers that name an unknown requirement.

## Step 14: file the evidence

The documents, the matrix and the JUnit XML are filed unchanged where
`documents.md` states: in the document system, or, in a project without one,
on the working branch. The skill reads each filed copy back and reports any
that differs from the draft. It opens a pull request and adds a `released`
entry to the `REQ-*.json` of each requirement in the release.

## Step 15: sign off

The roles `documents.md` names approve each document: in the document system,
or by approving the pull request in a project without one. `vogon:release`
tells each role holder what waits for their approval and where. VOGON signs
nothing.
