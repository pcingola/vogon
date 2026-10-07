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

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the start-of-skill reads, the loop, sub-agent prompts, systems by role, actions never taken, stops and commands.

## Inputs

- The release commit, and the release name used in the state files and in
  `vogon/documents/<release>/`. Both come from the developer.
- The JUnit XML of a test run on the release commit, made as the project runs
  its suite. The suite name is the commit tested.
- Process files: `release.md`, `documents.md`, `traceability.md`, `tests.md`,
  and `tracking.md` where `common.md` "Approval of a requirement" requires it.
- `vogon/project/vogon.yaml`: the document system, the test manager, the
  repository host, and the role holders.

## Steps

1. Create a working branch from the default branch.
2. Do the start-of-skill reads in `common.md`. The process files this skill
   needs are `release.md`, `documents.md`, `traceability.md` and `tests.md`,
   and `tracking.md` where `common.md` "Approval of a requirement" requires it. A
   process file derived here is committed on the working branch, as
   `process-files.md` states.
3. Check the results file.
   - Resolve the release commit with `git rev-parse --verify <commit>^{commit}`.
     Read the `name` of each `testsuite` in the JUnit XML. Report every suite
     name that is not the full hash of the release commit.
   - Report a run made on a working tree with uncommitted changes, because the
     commit then does not identify the code tested. The JUnit XML does not
     record this. Where the run was made in the working tree the skill runs
     in and `HEAD` there is still the release commit, check
     `git status --porcelain` there. Otherwise report that it could not be
     checked.
   - Report a JUnit XML with no `req` property: the host project lacks the
     lines `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/conftest.md`
     states, and the matrix shows every requirement as untested.
   - Report and continue. These findings do not stop the skill.
4. Read `release.md`. Determine the release contents as it states them,
   including the requirements in the release. Check each precondition it
   states against the repository, the state files and the configured systems,
   and report each one that is not met, with its evidence.
5. Read `documents.md` for each document VOGON drafts: its template, format,
   approvers and location. This includes a test document, such as a test
   specification, where the plan needs one. A template that cannot be read is
   reported, and that document is not drafted.
6. Prepare a read-only checkout of the release commit for the sub-agents, for
   example `git worktree add --detach vogon/tmp/release-<commit> <commit>`.
   Sub-agents read the requirements, test procedures, tests and code there,
   never from the current branch. Read the test procedures from where
   `tests.md` keeps them: the repository, the tracker or the test manager.
7. Draft each document. Start one writing sub-agent per document with the
   `vogon:vogon-writer` definition, in parallel. Give it the document's entry
   in `documents.md`, its template and format, the requirements in the
   release with their state files, the test procedures, the tests, the code,
   the JUnit XML, the output path, its log path and the logs of earlier
   rounds. The sub-agent writes the document in its template and format, and
   cites, for each statement, the requirement, procedure, test, file or
   result it rests on. Output path: `vogon/tmp/<release>/` when `vogon.yaml`
   names a document system; otherwise the location `common.md` "Systems by
   role" names, on the working branch.
8. Check each document. Start one evaluating sub-agent per document with the
   `vogon:vogon-checker` definition, with the perspective in the Loops table.
   Run the loop as `common.md` states.
9. Produce the traceability matrix as `traceability.md` states. A role with no
   system in `vogon.yaml` is replaced as `common.md` "Systems by role" states.
   - A test manager is configured: upload the JUnit XML unchanged to it. The
     test manager produces the traceability report. Download the report where
     the test manager offers it, and put it beside the documents in the format
     the test manager gives.
   - No test manager: save the output of the replacement unchanged as
     `traceability-matrix.md` beside the documents.
   - The matrix comes from the join or the test manager. No sub-agent writes
     or edits it, and the skill does not change it. Report what the matrix
     shows: requirements with no test, failed tests, and markers that name
     an unknown requirement.
10. File the documents, the matrix and the JUnit XML, unchanged, where
    `documents.md` states.
    - A document system is configured: upload each to the location
      `documents.md` names for it.
    - No document system: commit them on the working branch, at the location
      step 7 used.
11. Read each filed copy back from where it was filed and compare it with the
    draft. Report every copy that differs, with the difference.
12. Push the working branch and open a pull request on the repository host. If
    the branch has no commit yet, because a document system holds the
    documents, make an empty commit that names the release first. The
    description lists the documents, where each is filed, the unmet
    preconditions, the results-file findings, and the loops run as `common.md`
    states.
13. Append to the state file of each requirement in the release:
    `{"step": "released", "date": "<yyyy-mm-dd>", "commit": "<release commit>", "release": "<release>", "pr": <number>}`.
    Take the date from `date '+%Y-%m-%d'`.
14. Read the plan path from the `planned` entries of the requirements in the
    release. Move each plan whose named requirements all have a `released`
    entry from `vogon/plans/` to `vogon/plans/done/` with `git mv`. Commit the
    state files and the moves, and push to the same branch.
15. Tell each role holder `documents.md` names as approver which documents
    wait for their approval, and where: the document system location or the
    pull request. Name the role holders from `roles` in `vogon.yaml`.
16. Remove the checkout from step 6 with `git worktree remove`, and delete the
    drafts in `vogon/tmp/<release>/`.

## Loops

| Writing sub-agent (agent definition) | Produces | Evaluators (agent definition) | Checklist or perspective |
| --- | --- | --- | --- |
| `vogon:vogon-writer` | One document `documents.md` lists, in its template and format | `vogon:vogon-checker`, one per document | Each statement is true of the requirements, the code and the JUnit XML results of the release commit, and cites what it rests on. The document follows its template and format. It states nothing the cited sources do not. It names the release commit it was drafted from. It does not state that it was approved or signed and has no signature block; the document system or the pull request records the approval. |

## Stops for a person

- Approval of each document, the matrix and the results: each approver role
  `documents.md` names, in the document system or on the pull request. The
  skill tells them and does not wait.
- A required input the developer did not give, such as the release commit,
  the release name or the JUnit XML: the developer.
- A finding that needs a choice: the developer running the skill, before the
  pull request is opened.
- A gap in the validation plan while `release.md`, `documents.md`,
  `traceability.md`, `tests.md` or `tracking.md` is derived, and confirmation
  of the tracker and test manager names read from an example item: the
  developer, as `${CLAUDE_PLUGIN_ROOT}/references/process-files.md` states.

## Outputs

| Path or system | Format | Written by |
| --- | --- | --- |
| `vogon/documents/<release>/<document>` | Each document in the template and format `documents.md` names; without a document system only | Writing sub-agent |
| `vogon/tmp/<release>/<document>` | Draft of each document, gitignored, deleted at the end; with a document system only | Writing sub-agent |
| `traceability-matrix.md` beside the documents | Output of `vogon trace`, unchanged | `vogon trace` |
| Test manager's traceability report beside the documents | As the test manager gives it | Test manager |
| JUnit XML beside the documents | The input file, unchanged | Main agent |
| `vogon/requirements/<module>/REQ-*.json` | Appended `steps` entry `{"step": "released", "date", "commit", "release", "pr"}` | Main agent |
| `vogon/plans/done/plan_<slug>.md` | Each plan whose requirements are all released, moved with `git mv` in step 14 | Main agent |
| `vogon/logs/<yyyymmdd_hhmmss>_<task>.log.md` | One per sub-agent run, as `common.md` states | Each sub-agent |
| `vogon/logs/` main log | One entry per sub-agent run and decision | Main agent |

And any process file derived, per `process-files.md`.

External writes:

- Test manager: the JUnit XML, uploaded unchanged.
- Document system: the documents, the matrix and the JUnit XML, at the
  locations `documents.md` names.
- Repository host: one pull request with the state files, the moved plans
  and, without a document system, the filed documents.

## Reference files

- Main agent: `${CLAUDE_PLUGIN_ROOT}/references/common.md`,
  `${CLAUDE_PLUGIN_ROOT}/references/process-files.md`,
  `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/conftest.md`.
- Writing and evaluating sub-agents: `${CLAUDE_PLUGIN_ROOT}/references/writing.md`,
  `${CLAUDE_PLUGIN_ROOT}/references/records.md`.
