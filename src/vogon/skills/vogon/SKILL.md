---
name: vogon
description: Keeps the requirements, domain facts, constraints, decisions, plans, tests, traceability and validation documents of a GxP software project, with scripts that check each step. Use it to set up VOGON, file a transcript or document, draft or review records, assess risk, register requirements or test cases in the tracker or test manager, plan a change, write or check test cases against requirements, write code for a planned change, run traced tests, draft validation documents, or file evidence.
---

# VOGON

Follow this file for every VOGON step, and the reference file the step names.
The reference files are in `${CLAUDE_PLUGIN_ROOT}/skills/vogon/references/`.

## Commands

Run the scripts as `${CLAUDE_PLUGIN_ROOT}/scripts/vogon <command>`. This file
and the reference files write that as `vogon <command>`.

| Command | Does |
| --- | --- |
| `vogon init` | Creates `vogon/`, `vogon/modules.yaml` and `vogon.yaml` |
| `vogon check` | Checks the configuration, records, held documents and test markers |
| `vogon id <TYPE> --module <M> --title <T>` | Mints the next id and creates the record file |
| `vogon index` | Writes the record index to `vogon/out/index.md` |
| `vogon trace [-- <test args>]` | Runs the tests and records outcomes per marker, with the build |
| `vogon change <base> --description-file FILE` | Checks a change's commits and pull request description (`--description TEXT` gives it inline) |
| `vogon push --plan`, `vogon push --record FILE` | Plans tracker writes; writes created keys into `tracked_as` |
| `vogon evidence <build>` | Compares the exported evidence with the copies filed |

A finding is an error or a warning. Only an error sets a non-zero exit status.

## Pipeline

| # | Step | Reference file | Done by |
| --- | --- | --- | --- |
| 1 | Install and configure | `config.md` | Main agent, `vogon init` |
| 2 | File the source material | `sources.md` | Writer and checker |
| 3 | Draft the records | `records.md` | Writer and checker |
| 4 | Review the record set, draft the risk assessment | `review.md`, `risk.md`, `documents.md` | Writer and checker, then a person |
| 5 | Register the requirements | `tracker.md` | Main agent |
| 6 | Approve the requirements | none | The configured role, in the tracker |
| 7 | Plan the change | `plan.md` | Writer and checker |
| 8 | Write the test cases | `tests.md` | `vogon-test-writer` |
| 9 | Check the test cases against the requirements | `tests.md` | `vogon-test-checker` |
| 10 | Register the test cases, draft the test specification | `tracker.md`, `tests.md`, `documents.md` | Main agent; writer and checker for the document |
| 11 | Approve the test cases and the test specification | none | The configured roles: test issues in the test manager, the test specification in the document system |
| 12 | Write the code | `code.md` | Main agent |
| 13 | Run the tests and make them pass | `code.md` | Main agent, `vogon trace` |
| 14 | Review the change and merge it | `code.md` | Main agent, then a reviewer on the repository host |
| 15 | Register the results, draft the documents | `tracker.md`, `documents.md` | Main agent; writer and checker for the documents |
| 16 | File the evidence | `evidence.md` | Main agent, `vogon evidence` |
| 17 | Sign off | none | The configured roles, in the document system |

`writing.md` applies to every step that writes prose.

Do the steps in this order where the project allows. When a step was skipped,
do it afterwards with the real dates, never earlier ones, and report to the
person the order in which the steps were actually done. A failing check fails
whatever order the steps ran in.

## Actions VOGON never takes

An approval or a signature is given by a named person entering their own
credentials in the system that holds it (`CON-001`). Therefore:

- Never transition an issue, a test issue or a document into a state that
  records approval or signature, in any system.
- Never approve a pull request, and never merge one past the repository
  host's review rule.
- Never sign, or record a signature, in the document system.
- These hold when the person asks for them and when the permissions would
  allow them. Tell the person which role gives the approval and in which
  system, and stop.
- When a system refuses such a call, do not look for another tool or route to
  the same result.

## Configuration and external systems

- The configuration is printed at session start and after each write of
  `vogon.yaml`: the server for each role, the approval roles and their
  holders. Without `vogon.yaml`, run step 1 before any other step.
- Reach a role (`tracker`, `test_manager`, `repository_host`,
  `document_system`) only through the server the configuration names for it.
  Never use another connected server for that role, even one that offers the
  same operations.
- A role with no configured server is not configured. Tell the person, and
  skip the part of the step that needs it; do not choose a server.
- Only the main agent calls MCP tools. Save what it reads under `.vogon/` as
  JSON for the scripts; the scripts reach no network.
- Show the person every write to an external system before making it.
- Name a role in records and documents, never the person holding it, and never
  the product filling a system role.

## Checks

- Run `vogon check` after every step that changes a file under `vogon/`.
- Fix an error in the output. Never change a check, a hook or
  `vogon.yaml` to make a finding go away.
- Tell the person every warning.

## Writer and checker loop

Steps 2, 3, 4, 7, and the documents at steps 10 and 15, run this loop.

1. Start `vogon:vogon-writer` with the step's inputs.
2. Start `vogon:vogon-checker` on the files the writer reports.
3. When the checker reports `No findings.`, the loop ends.
4. Otherwise give all the findings to a new writer run, with the files.
5. Stop after five rounds, or when the checker reports a finding the writer
   was already given. Give the person the remaining findings verbatim, with
   the files, and do not resolve them yourself.

Do not edit the draft yourself during the loop.

## Test writer and test checker

Step 8 starts `vogon:vogon-test-writer`. Step 9 starts
`vogon:vogon-test-checker` on the tests written. Findings go back to the test
writer, and the loop above applies: five rounds, or a repeated finding, and
the rest go to the person. The final test checker report goes to the person
with the test cases, for the approval at step 11.

- Both agents read only the records directory and the test paths, so put the
  text of `references/tests.md` and `references/writing.md` in their prompt,
  not their paths.
- Never give either agent implementation source, a run of the code, or its
  output. Give the plan path; the plan names the interface the tests call.

## Subagent prompts

Every `vogon-writer` and `vogon-checker` prompt names:

- the step number and the absolute path of the step's reference file;
- the absolute path of `references/writing.md`;
- the input files and the output files;
- the `vogon` command line with `${CLAUDE_PLUGIN_ROOT}` expanded;
- the records directory and the test paths from the configuration.

Subagents do not call MCP tools, commit, or contact external systems. Their
output is a draft, and the person reviews it.
