# Steps of the GxP process

The steps a requirement goes through from source material to signed release,
in order. Different requirements are at different steps at the same time.

| # | Step | Produces | Skill | Approved by |
| --- | --- | --- | --- | --- |
| 1 | [Configure](setup.md) | `vogon/project/vogon.yaml`, the validation plan in `vogon/sources/`, the `.gitignore` and `conftest.py` lines | `vogon:init` | A person, on the pull request |
| 2 | [File the sources](requirements.md) | Checked summaries of meetings, mail and chat; filed documents with their markdown copies | `vogon:requirements` | |
| 3 | [Draft and check the records](requirements.md) | Requirements with acceptance criteria and risk fields; facts, constraints and decisions | `vogon:requirements` | |
| 4 | [Send the requirements for approval](requirements.md) | The pull request with `REQ-*.md` and `REQ-*.json`; tracker items where a tracker is configured | `vogon:requirements` | |
| 5 | [Approve the requirements](approval.md) | An `approved` entry in `REQ-*.json` | `vogon:approve` | Product Owner |
| 6 | [Write the test procedures](test_procedures.md) | Test procedures, where `tests.md` requires them | `vogon:tests` | The roles `tests.md` names |
| 7 | [Choose a requirement](planning.md) | The ready and blocked lists; the tracker item assigned | `vogon:next` | |
| 8 | [Plan](planning.md) | A checked plan, and a `planned` entry once approved | `vogon:implement` | A developer |
| 9 | [Write the code, tests and documentation](implementation.md) | Checked code, tests and documentation, all tests passing, in one pull request | `vogon:implement` | A person, on the repository host |
| 10 | [Release](documents.md) | The documents `documents.md` lists, the traceability matrix and the results, filed | `vogon:release` | The roles `documents.md` names |

Step 6 comes before step 7 or after step 9, as `tests.md` states. A project
that needs no test procedures skips it.

A change to an approved requirement appends a `changed` entry to its
`REQ-*.json`, and the requirement returns to step 5. `vogon:next` does not
offer it as ready until it is approved again.

`REQ-*.json` records the steps done to each requirement
([Records](../records.md#state-file)). A step done late or out of order is
done with its real date, and the skill reports the gap with the real dates.

