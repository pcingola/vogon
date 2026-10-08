# Architecture

VOGON is a Claude Code plugin installed into a host project: the repository of
a regulated (GxP) software project. It carries out the
[steps of the GxP process](process/index.md) that do not need a person. The plugin is
a set of skills that work together, the sub-agents they start, and hooks where
a task needs one. Small scripts do the work that must give the same result
every time: `vogon id` allocates record ids, `vogon approve` records an
approval, and `vogon trace` builds the traceability matrix. Test results come
from pytest's own JUnit XML. All model work is done by Claude Code, and the
Python code calls no language model (`DEC-005`).

[Vocabulary](vocabulary.md) defines the terms used here. [Records](records.md)
defines the record format and the requirement state file. [The loop](loop.md)
defines how every skill produces and checks its work.

## Scope of this version

The host project is written in Python, tested with pytest, and kept in git.
The coding agent is Claude Code. Skills name each external system by its role
and never by product. The project names the system that fills each role in
[`vogon/project/vogon.yaml`](#project-configuration-and-process-files).

| Role | POC | Real version (example) |
| --- | --- | --- |
| Repository host | GitHub | GitHub |
| Tracker | The project's choice, for example GitHub Issues | The project's choice, for example Jira |
| Approval of requirements | `vogon approve`, recorded in `REQ-*.json`; the tracker holds no approval | Tracker workflow transition, cached in `REQ-*.json` |
| Test manager | None: `vogon trace` builds the matrix | Xray |
| Document system | None: documents stay in the repository | The company's controlled document system |
| Meetings | The project's choice, for example Google Meet | The project's choice, for example Teams |
| Mail | The project's choice, for example Gmail | The project's choice, for example Outlook |
| Chat | The project's choice, for example Slack | The project's choice, for example Teams |

The products named are examples. A project may fill a role with another
product, and the skills do not change. VOGON reaches the meeting, mail and chat
systems through the MCP connectors of the Claude Code session.

A POC approval records the approver's git identity, which the approver does not
re-enter at approval, so it is not an electronic signature under 21 CFR
Part 11. In the real version, approvals and signatures come from the tracker,
the test manager and the document system. A tracker or test manager transition
is an electronic signature only when the workflow makes the approver re-enter
their credentials at that transition; `vogon:init` reports a workflow that
does not.

VOGON never decides an approval and never signs (`CON-001`). In the POC the
Product Owner gives the approval in their own Claude Code session, and
`vogon:approve` records it only on that explicit instruction. A change to a
live system is recorded and approved in the host project's own change control
system; its requirements, tests and release documents go through the same
skills (`DEC-026`).

## Skills

One skill per task a person starts. A skill runs in the main Claude Code
session, which is the main agent of [the loop](loop.md).

| Skill | Does | Process page |
| --- | --- | --- |
| `vogon:init` | Writes `vogon/project/vogon.yaml`: the system for each role, the role holders and the options; files the validation plan in `vogon/sources/` | [Setup](process/setup.md) |
| `vogon:requirements` | Reads the selected sources, writes checked summaries of meetings, mail and chat, drafts records with their risk fields, checks them, opens the pull request, and in the real version sends the requirements to the tracker for approval | [Requirements from sources](process/requirements.md) |
| `vogon:approve` | Records the Product Owner's approval of the requirements they name, commits and pushes | [Approving requirements](process/approval.md) |
| `vogon:next` | Lists the approved requirements ready to start, lists the blocked ones with what blocks them, assigns the chosen one | [Planning](process/planning.md) |
| `vogon:tests` | Writes the test procedures of approved requirements before development, or generates them from the existing tests, as `tests.md` states, and registers them for approval | [Test procedures](process/test_procedures.md) |
| `vogon:implement` | Plans one or more requirements, or takes their plan, writes the code, tests and documentation part by part, has them reviewed, and opens the pull request | [Planning](process/planning.md), [Code, tests and documentation](process/implementation.md) |
| `vogon:release` | Drafts and checks the validation documents for a release commit, produces the traceability matrix, files the evidence | [Documents](process/documents.md) |

Approvals of requirements, test procedures, pull requests and documents are
given by people, and no skill gives them.

Every skill starts the same way. It reads the project process files it needs,
deriving a missing one first and regenerating one whose plan version is older
than the held plan. It then reads the requirements it concerns, their state
files, and the pull requests, commits and tracker items those files link, and
reports any difference between them. The linked source counts over the state
file, except for an approval, which "Approval of requirements" decides. Tasks happen weeks apart, by different developers, in any order. A skill
does not assume an earlier task ran. When one was skipped, the skill does what
still applies and reports the gap, such as code merged with no plan.

A skill's `SKILL.md` holds the task's steps, the loops it runs, what each
sub-agent receives, and where it stops for a person. The default checklists
are in the skill's `references/` directory. A project edits or removes their
items in its own files, in `vogon/project/checklists/`.

### Loops

Each skill runs its work through [the loop](loop.md). The loops are:

| Skill | Writing sub-agent produces | Evaluators check |
| --- | --- | --- |
| `vogon:init`, any skill | One project process file | Each statement is supported by the cited plan section; the file covers every topic it must |
| `vogon:requirements` | One summary per meeting, mail thread or chat channel | The summary against its source |
| `vogon:requirements` | One extract per attached or shared file, from its markdown copy | The extract against the file |
| `vogon:requirements` | Records with their risk fields | The requirement checklist |
| `vogon:tests` | Test procedures | Each procedure against its requirement and, where generated, its tests |
| `vogon:implement` | The plan for one or more requirements | The plan against the requirements and the code |
| `vogon:implement` | Code, tests and documentation for one part of the plan | The test checklist; the code checklist; Claude Code's code review |
| `vogon:release` | One validation document | The document against the requirements, the code and the results of the release commit |

The default requirement checklist holds that each
requirement:

- makes sense in practice: it solves a real problem, and its cost fits how
  often the situation occurs;
- contradicts no other requirement, constraint or decision, including those in
  open pull requests;
- does not contradict the project's design as its decision records state it,
  or names the decision it reverses;
- is not a duplicate and is not already covered by another requirement;
- can be tested, and every expected value comes from the source;
- states one thing, with one reading;
- has `gxp_impact` and `risk` values that follow from their reasons.

The default test checklist holds that each test checks the requirement and its
intent rather than trivial code behaviour, that no test uses a mock unless the
project authorized it, that the tests together cover every aspect of the
requirement, and that no test checks the behaviour of a library.

The default code checklist holds that the code covers the requirements, is
well written and not overengineered, uses defined data structures and classes
instead of dictionaries, follows the language's other best practices, and that
the documentation describes the current code.

### When a skill stops for a person

- An approval. The skill tells the role holder what is waiting and where.
- A finding that needs a choice. It goes to the developer running the skill,
  before the requirement is created or the pull request is opened. Only a
  finding on a requirement the Product Owner already approved goes back to the
  Product Owner, as a change that needs approval again.
- A plan for code, which the developers review and approve before any code
  is written.
- An instruction from the developer while code is written, if the developer
  chooses to give one.
- A gap in the validation plan while a project process file is derived. The
  developer answers, and the file records the answer with their name and the
  date.
- The tracker and test manager names read from example items while a project
  process file is derived. The developer confirms them.
- A required input the developer did not give. The skill asks for it.

Nothing else waits for confirmation.

## Project configuration and process files

VOGON knows generic concepts: requirement, defect, test, test procedure,
approval, and the steps done to a requirement. How a host project uses them
comes from its configuration and from its validation plan.

`vogon/project/vogon.yaml` is the configuration. It states the product that
fills each role (tracker, test manager, document system, repository host,
meetings, mail, chat), the people who hold each approval role, such as the
Product Owner, and the project's options, such as whether logs are committed.
`vogon:init` writes it from the commented template the plugin ships. It is
YAML because the scripts read it: `vogon approve` reads the Product Owner list
from it.

The validation plan is filed in `vogon/sources/` as the original document and
a markdown copy that the skills read ([Sources](sources.md)). The plan stays
the host project's controlled document, and VOGON never edits either copy.

The markdown files in `vogon/project/` are VOGON's reading of the plan:

| File | States |
| --- | --- |
| `tracking.md` | The controlled and exempt work types; the tracker item types for requirement, defect and test procedure; the fields for text, acceptance criteria and risk; the approval transitions; links; naming; where a test manager is configured, its item types, fields, links and naming |
| `requirements.md` | The requirement form; the risk fields and method; who approves and when; what a change to an approved requirement triggers |
| `tests.md` | What a test procedure is; who writes and approves it, and when; unit tests and formal tests; the formal test environment; how results are tied to a commit and an environment; the command that runs the test suite and where it runs ("Running the test suite") |
| `traceability.md` | Who produces the matrix and from what; what it links; where it is approved |
| `documents.md` | The documents VOGON drafts, with template, format, approvers and location; the documents left to the project |
| `release.md` | The contents of a release; its preconditions; the steps recorded |

Each file is written from a template that lists its topics, and its
frontmatter records the plan version it was derived from. A file is derived
when a skill first needs it. A writing sub-agent drafts the file, and each
statement cites a section of the plan. Evaluators check that each statement is
supported and that the file is complete. A gap in the plan is asked of the
developer, and the answer is recorded with their name and the date. Tracker
and test manager names are read from an example item and confirmed by the
developer. The file
is merged by pull request.

## Records

Requirements, domain facts, constraints and decisions are markdown files in
the host project's repository, under `vogon/`, in the format
[Records](records.md) defines. The markdown file is what people read and
review. Its frontmatter holds the record's identity and fixed attributes, and
its `status` is `active`, `withdrawn` or `superseded_by: <id>`.

A record gets its id when it is drafted, from `vogon id <type> <module>`.
There are no temporary ids. The script runs `git fetch`, reads the ids used in
the working tree, in every local and remote branch and in the history, and
prints the next unused number. Two branches that take an id before either
pushes can get the same one. A skill that opens a pull request adding records
first runs `vogon id --check`, which reports each of the branch's new ids that
another branch also uses, and renumbers them before it opens the pull request.

`vogon:requirements` drafts records from any source the session can reach:
meeting transcripts, mail threads, chat channels, documents, and existing code
with its documentation, git history, pull requests and issues.

Meeting transcripts, mail and chat contain personal data, and some countries
restrict keeping meeting transcripts. They are downloaded to `vogon/tmp/`,
which is gitignored, and are never committed. A writing sub-agent summarises
each one, and an evaluator checks the summary against its source. The checked
summary is committed to `vogon/sources/` with the source's id in its system,
its date and its participants ([Sources](sources.md)), and the downloaded
content is deleted. Records are drafted from the checked summary. The Product
Owner's approval makes a statement a requirement; the meeting or message is
only where it came from.

Files attached to a mail, posted in a chat or shared in a meeting are
documents, and are kept. Each is downloaded, filed in `vogon/sources/` as the
original, and converted to a markdown copy beside it. Records cite the markdown
copy. One sub-agent reads each file and returns what it states that bears on
requirements, with the location of each statement, such as the slide or page.
A long file, such as a presentation of 200 slides, is read only in that
sub-agent's context, never in the main agent's.

Code shows what the system does, and its history shows why. A requirement
drafted from code alone describes the current behaviour, defects included, so
an evaluator reports every requirement whose only source is the code, and the
developer confirms that the behaviour is intended.

## Approval of requirements

`REQ-*.md` and its state file `REQ-*.json` are both committed.

In the POC the Product Owner approves in their own Claude Code session, for
example "approve the last 10 requirements, then push". `vogon:approve` acts
only on such an explicit instruction. It lists the ids and titles it resolved,
runs `vogon approve <id>...`, commits and pushes. `vogon approve` appends to
each `REQ-*.json` an `approved` entry with the approver's git identity and the
date. If `vogon.yaml` does not list the user as Product Owner, the
script warns and still records the approval.

In the real version the requirements go to the tracker, and the Product Owner
approves each with the tracker's approval transition. The tracker is the
source: the item's status is the approval. The Product Owner may edit the text
in the tracker first. `vogon:approve` syncs each approval into `REQ-*.json`,
which caches it so that skills do not query the tracker for every read, and
copies the approved text into `REQ-*.md`. A skill that finds an approval not
yet synced reports it, and works from the text of a requirement only once it
is synced.

A skill never changes an approved requirement without the agreement of the
developer running it. A change goes in a pull request that appends a
`changed` entry to `REQ-*.json` and lists the requirement as needing approval
again. Without a tracker, the requirement is approved again when an
`approved` entry follows the `changed` entry; with a tracker, when the item is
approved again. Until then `vogon:next` does not offer it as ready.

## State of a requirement

`REQ-<MODULE>-<NUMBER>.json` records the state of the requirement: every step
done to it (drafted, approved, changed, planned, test procedures written,
implemented, released), each with its date and the pull request or commit that
holds it. The format is in [Records](records.md#state-file).

The pull request, commit or tracker item an entry links is the evidence, and
the entry is a pointer to it. A skill checks the linked source before acting on
an entry, and reports a difference instead of trusting the file.

## Risk

Each requirement carries four risk fields from the moment it is drafted:

- `gxp_impact`: patient safety, product quality, data integrity, or none;
- the reason for that value;
- `risk`: high, medium or low, from severity, probability and detectability;
- the reason for that value.

The reasons let a reader understand each value, and later challenge or change
it. [Records](records.md#requirement) defines where the fields are written.

Who approves the risk fields, and when, comes from `requirements.md`. Where the
validation plan says so, as in the first host project, they are approved with
the requirement by the Product Owner before development. Project-level risk
documents that the plan lists, such as a risk log or a data integrity risk
assessment, are separate documents, approved by the roles the plan names.

## Tests

A requirement is usually covered by several tests: edge cases and input
combinations.

- The requirement's acceptance criteria state what must be tested, and are
  approved with the requirement.
- The pytest code is the test case. Each test names the requirements it
  verifies in its marker, `@pytest.mark.req("REQ-PRN-12")`, and may name
  several. The link is on the test because whoever changes a test edits its
  marker in the same edit (`DEC-006`). Requirement ids are not written in
  implementation code. A commit names the requirements it implements.
- A test with no marker, such as a unit test of an internal function, is
  allowed and is not evidence.
- VOGON writes tests from the requirement and its intent, never from what the
  code does. It writes no mocks and uses no mocking library unless the project
  authorized it, because needing a mock indicates a problem in the design. It
  writes no tests of library behaviour.

A test procedure is a document: numbered steps in prose, each with its
expected result, given an id and linked to its requirement. It is not code.
Projects call it a test script, test protocol or manual test case; VOGON calls
it a test procedure. `tests.md` states whether the project needs test
procedures, whether
they are written before the tests, from the requirement, or after, generated
from the tests, and who approves them. `vogon:tests` follows that
order and imposes none of its own. Where procedures exist, each test also names its procedure,
`@pytest.mark.procedure("<procedure id>")`. Where the validation plan needs a test
document, such as a test specification, `vogon:release` prepares it from the
requirements, the procedures and the tests.

## Code from requirements

`vogon:implement` takes one or more approved requirements, or an existing plan
for them.

1. If there is no plan, a writing sub-agent writes one: a checklist of the
   parts to build and the tests that verify each, which refers to the
   requirements and the code rather than restating them. Evaluators check the
   plan against the requirements and the code.
2. The skill stops, and the developers review the plan. A change they ask for
   goes through the loop again. When a developer approves the plan, the skill
   commits it and records the approval, with the developer's git identity and
   the date, in the `planned` entry of each requirement's state file. No code
   is written before the plan is approved.
3. The main agent follows the plan. For each part it starts a sub-agent that
   writes that part's code, tests and documentation, given the plan, the
   requirements and the code it touches. Independent parts run in parallel.
4. Evaluators check each part: the test checklist, the code checklist, and
   Claude Code's code review. VOGON has no code reviewer of its own.
5. The main agent reads each sub-agent's log and its output against the plan.
   It sends back work that leaves the part it was given, does less than the
   part, or changes what the plan does not name.

The developer may steer the work while it runs, or may leave it to run. A
developer who steers can stop the work, ask to review each part before the
next starts, or give an instruction about a part, such as
a data structure to use or an approach to drop. The main agent passes the
instruction to the sub-agents it concerns and logs it. An instruction that
changes what the plan states is written into the plan, and the changed plan is
approved again before the work it changes continues. Without instructions, the
skill runs the plan to the end.

All tests are written and pass before the pull request is opened. A person
approves the pull request on the repository host.

## Traceability

A few lines in the host project's `conftest.py` copy each test's `req` and
`procedure` marker ids into the JUnit XML properties:

```python
def pytest_collection_modifyitems(items):
    for item in items:
        for name in ("req", "procedure"):
            for marker in item.iter_markers(name):
                for value in marker.args:
                    item.user_properties.append((name, value))
```

A test run records the commit it tested as the suite name:

```
pytest --junitxml=results.xml -o junit_suite_name=$(git rev-parse HEAD)
```

Where and how the suite runs is the project's choice. VOGON reads the file the
run produces. If the run was made on a working tree with uncommitted changes,
VOGON reports it, because the commit does not identify the code tested.

`traceability.md` states how the matrix is produced. Where a test manager
exists, VOGON uploads the JUnit XML unchanged and the test manager produces the
traceability report (`DEC-003`). Where none exists, `vogon trace <results.xml>`
acts as a minimal test manager: it joins the markers and the results of that
one commit into the matrix, listing each requirement, its procedures and tests,
their results, the commit, and every requirement with no test. It manages no
test cases and records no approvals. The matrix is evidence, so it always comes
from this join or from the test manager, never from a model.

## Release

`vogon:release` takes a release commit and the JUnit XML of a test run on that
commit. `release.md` states what the release contains and its preconditions.
The skill then:

1. Drafts each document `documents.md` lists, in its template and format, from
   the requirements, the tests, the code and the results of that commit. Each
   document cites what it states.
2. Checks each document with an evaluator in the loop.
3. Produces the traceability matrix as `traceability.md` states.
4. Files the documents, the matrix and the results where `documents.md` says:
   in the document system, or, in a project without one, in
   `vogon/documents/<release>/` in a pull request. It tells each role holder
   what is waiting for their approval.
5. Reads the filed copies back and reports any that differ from what was
   drafted.
6. Records the release step in the state file of each requirement in the
   release.
