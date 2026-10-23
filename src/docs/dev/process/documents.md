# Release documents

Step 10 of the [steps](index.md). A developer runs `vogon:release` with a
release commit, a release name and the JUnit XML of a test run on that commit.
The design is in [Architecture](../architecture.md#release) and the steps in
`src/vogon/skills/release/SKILL.md`.

The skill reports each unmet precondition of `release.md` and each problem
with the results file, and continues. It drafts and checks each document `documents.md` lists from a read-only checkout
of the release commit, and produces the traceability matrix as
`traceability.md` states ([Architecture](../architecture.md#traceability)).
No model writes or edits the matrix.

The documents, the matrix and the JUnit XML are filed unchanged in the
document system or, without one, in `vogon/documents/<release>/`, and read
back. The skill opens a pull request, appends a `released` entry to each
requirement's `REQ-*.json`, and moves each plan whose requirements are all
released to `vogon/plans/done/`. The roles `documents.md` names approve the
documents in the document system or on the pull request. VOGON signs nothing.
