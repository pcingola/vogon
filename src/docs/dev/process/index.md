# Steps of the GxP process

The steps a requirement goes through from source material to a signed
release. Each requirement goes through them in this order. Different
requirements are at different steps at the same time, and a project works on
several at once.

| # | Step | Produces | Done by | Skill |
| --- | --- | --- | --- | --- |
| 1 | Configure | `vogon/project/vogon.yaml`: the system for each role, the role holders and the options; the validation plan filed in `vogon/sources/` | Developer, with VOGON | `vogon:init` |
| 2 | File the sources | Checked summaries of meetings, mail and chat; attached and shared files with their markdown copies | VOGON | `vogon:requirements` |
| 3 | Draft the records | Requirements with their acceptance criteria and risk fields; domain facts, constraints and decisions | VOGON | `vogon:requirements` |
| 4 | Check the records | Records checked against the requirement checklist; findings that need a choice settled by the developer | VOGON, then the developer | `vogon:requirements` |
| 5 | Send the requirements for approval | The pull request with `REQ-*.md` and `REQ-*.json`; in the real version, the tracker items | VOGON | `vogon:requirements` |
| 6 | Approve the requirements | The approval, recorded in `REQ-*.json` | Product Owner | `vogon:approve`, or the tracker in the real version |
| 7 | Write the test procedures | Test procedures, where `tests.md` requires them | VOGON | `vogon:tests` |
| 8 | Approve the test procedures | The approval, where `tests.md` states | The roles `tests.md` names | |
| 9 | Plan | A checked plan for one or more requirements | VOGON | `vogon:implement` |
| 10 | Approve the plan | The approval, recorded in the `planned` entries of the state files | Developers | |
| 11 | Write the code, tests and documentation | Code, tests and documentation for each part of the plan, checked, with all tests passing | VOGON, steered by the developer if they choose | `vogon:implement` |
| 12 | Approve the pull request | The approval on the repository host | A person | |
| 13 | Draft the release documents | The documents `documents.md` lists, and the traceability matrix, for a release commit | VOGON | `vogon:release` |
| 14 | File the evidence | The documents, the matrix and the results, where `documents.md` states | VOGON | `vogon:release` |
| 15 | Sign off | The signed documents | The roles `documents.md` names | |

Steps 7 and 8 come before step 9 or after step 11, as `tests.md` states. Before
step 9, the test procedures are written from the requirements. After step 11,
they are generated from the tests. A project that needs no test procedures
skips both steps.

Steps 6, 8, 10, 12 and 15 are approvals. A person gives each one, and VOGON
gives none of them.

Each step VOGON performs on a requirement is recorded in its `REQ-*.json`, with
the date and the pull request or commit that holds the result
([Architecture](../architecture.md#state-of-a-requirement)).

Steps are sometimes done late or out of order. The step is then done with its
real date, and the order in which the steps were actually done is reported:
an approval given after what it governs was used shows in the report.

The pages of this section describe how the steps are carried out.
[Architecture](../architecture.md) describes the skills and holds their rules.

| Steps | Page |
| --- | --- |
| 1 | [Setting up a project](setup.md) |
| 2 to 5 | [Requirements from sources](requirements.md) |
| 6 | [Approving requirements](approval.md) |
| 7 and 8 | [Test procedures](test_procedures.md) |
| 9 and 10 | [Planning](planning.md) |
| 11 and 12 | [Code, tests and documentation](implementation.md) |
| 13 to 15 | [Release documents](documents.md) |
