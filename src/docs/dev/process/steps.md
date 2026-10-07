# Steps of the GxP process

The steps a requirement goes through from source material to a signed
release, agreed with GxP practitioners. Each requirement goes through them in
this order. Different requirements are at different steps at the same time,
and a project works on several at once.

| # | Step | Produces | Done by | Skill |
| --- | --- | --- | --- | --- |
| 1 | Install and configure | The project configuration: the system for each role, the approval roles and who holds them; the validation plan, approved by the System Owner and the Quality Manager | Developer, with VOGON | `vogon:setup` |
| 2 | File the source material | Meeting summaries and source documents in the repository | VOGON | `vogon:meetings` |
| 3 | Draft the records | Requirements, facts, constraints and decisions | VOGON | `vogon:meetings`, `vogon:from-code` |
| 4 | Review and accept | The records checked against each other for contradictions and duplicates, and a risk level with its reasoning for each requirement | VOGON, then the developer | `vogon:meetings`, `vogon:from-code` |
| 5 | Register the requirements | One tracker issue per requirement | VOGON | `vogon:meetings`, `vogon:from-code` |
| 6 | Approve the requirements | Requirements in an approved state | Product Owner, in the tracker, or by pull request review in the prototype | |
| 7 | Plan the change | A plan: what will be built, the interface the tests call, which tests cover which acceptance criteria | VOGON | `vogon:implement` |
| 8 | Write the test cases | Test cases: for each acceptance criterion, the cases covering it with their inputs and expected values, as formal as the requirement's risk calls for | VOGON | `vogon:implement` |
| 9 | Check the test cases against the requirements | For each requirement, the acceptance criteria no test covers, the expected values that differ from the requirement, the assertions the requirement does not support | VOGON | `vogon:implement` |
| 10 | Register the test cases, draft the test specification | The test cases sent to the Test Lead, in the test manager linked to their requirements in a deployment; the test case files are the test specification | VOGON | `vogon:implement` |
| 11 | Approve the test cases | Test cases and their test specification entries in an approved state | Test Lead, in the test manager, or by pull request review in the prototype | |
| 12 | Write the code | Code, test code and documentation, and commits naming the requirements they implement | VOGON | `vogon:implement` |
| 13 | Run the tests and make them pass | Test results recorded against the commit tested | VOGON | `vogon:implement` |
| 14 | Review the change and merge it | An approving review by a developer other than the author | Code reviewer, on the repository host | |
| 15 | Register the results, draft the documents | Results in the test manager for the release build, and the URS, risk assessment, test specification, design specification, test report and validation summary report | VOGON | `vogon:release` |
| 16 | File the evidence | The traceability report and the results for the release build, in the document system | VOGON | `vogon:release` |
| 17 | Sign off | The signed validation package | System Owner and Quality Manager, in the document system | |

Step 12 does not wait for step 11. The code and the test code may be written
before, during or after the approval of the test cases, in the order the
developer works in. Step 11 must be done before the merge and before any
result counts as evidence.

The validation plan (step 1) and the URS and validation summary report (step
15) were added to the agreed steps by `DEC-027`.

Steps 6, 11, 14 and 17 are approvals, and so is the approval of the validation
plan at step 1. A person gives each one in the system
that records it, and VOGON gives none of them.

Steps are sometimes done late or out of order. The step is then done with its
real date, and the order in which the steps were actually done is reported:
an approval given after what it governs was used shows in the report.

The pages of this section describe how the steps are carried out.
[Architecture](../architecture.md) describes the skills.
