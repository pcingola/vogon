# Documents (steps 4, 10 and 15)

Drafting the documents of the validation package, filing each into the
document system, and reading the approved copy back where a check needs it
(`DEC-023`). Each item below is a rule the document or the filing meets or
fails. Every document also follows `references/writing.md`.

## Location

- [ ] Every drafted document is in `vogon/documents/`, one file per document,
      named as below. Nothing is drafted into `vogon/out/`, which holds only
      what the scripts generate.

| Step | Document | File | Approval in `vogon.yaml` |
| --- | --- | --- | --- |
| 4 | Risk assessment | `risk_assessment.md` | `risk_assessment` |
| 10 | Test specification | `test_specification.md` | `test_specification` |
| 15 | Design specification | `design_specification.md` | `release` |
| 15 | Test report | `test_report.md` | `release` |

- [ ] A document is drafted by `vogon-writer` and checked by `vogon-checker`,
      as `SKILL.md` states for the writer and checker loop.
- [ ] A document is markdown, starting with `# <document name>`.

## Content of every document

- [ ] The first paragraph says what the document covers and names the commit
      it was drafted from (`git rev-parse HEAD`).
- [ ] It cites records by id and held documents by path, and does not restate
      a record where citing it is enough.
- [ ] Every statement follows from a record, a plan, a test or a result. A
      statement nothing supports is not written.
- [ ] It names roles, never the people holding them, and names no product
      filling a system role.
- [ ] No line states that the document was approved or signed, and it has no
      signature block. The document system records the approval.
- [ ] No count of requirements, tests or records. The document names them.

## Risk assessment

- [ ] It meets `references/risk.md`.

## Test specification

- [ ] It meets the step 10 items of `references/tests.md`.
- [ ] It covers the tests the final step 9 report covered, and no other.

## Design specification

- [ ] It describes the system as built at the named commit: the modules, the
      interfaces the plans in `vogon/plans/` name, and the data each reads
      and writes.
- [ ] It holds no table or list from requirements to modules. The
      traceability report comes from the test manager (`REQ-TRC-7`).
- [ ] Where the code differs from a plan, the code as built is described and
      the plan is not cited for that part.

## Test report

- [ ] It names the build `vogon trace` recorded, the test command, and the
      date of the run. Results with no build are not reported.
- [ ] It gives the outcome of each test node id for that build, from
      `.vogon/results.json`, and names each failed, skipped or errored test.
- [ ] It holds no table or list from requirements to tests or outcomes. The
      test manager produces the traceability report, which step 16 files
      (`REQ-TRC-7`); the report refers to it.

## Filing

- [ ] A document is filed only when `vogon check` reports no failure and the
      writer and checker loop ended with no findings.
- [ ] It is filed through the server `vogon.yaml` names for
      `document_system`, with the tool mapped to `upload_document` in
      `.vogon/servers.json`. With no `document_system`, the document stays a
      draft and the person is told the role is not configured.
- [ ] The file name in the document system is the file name above.
- [ ] The person is told which roles give the approval, from the `approvals`
      entry in the table above, and that it is given in the document system.
- [ ] A draft changed after filing is filed again as a new version, and the
      person is told that the approval has to be given again.

## Reading back

- [ ] After the risk assessment is approved, the approved version is read
      with the tool mapped to `download_document` and saved unchanged as
      `.vogon/risk_assessment.md`, then `vogon check` is run.
- [ ] A read-back copy is saved as the bytes the document system returned,
      with no conversion or reformatting.
