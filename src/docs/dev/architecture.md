# Architecture

VOGON is a Claude Code plugin installed into a host project: the repository of
a regulated (GxP) software project. It carries out the
[steps of the GxP process](process/steps.md) that do not need a person, as the
pages of [Development process](process/index.md) describe them. The plugin is
a set of skills and subagent definitions, plus a pytest plugin and one script.
All model work is done by Claude Code. The Python code calls no language model
and reaches no network (`DEC-005`).

[Vocabulary](vocabulary.md) defines the terms used here. [Records](records.md)
defines the record format and the requirement state file.

## Scope of this version

The host project is written in Python and tested with pytest. The coding
agent is Claude Code. External systems are named by role, and the product
filling each role is configuration:

| Role | Prototype | Deployment |
| --- | --- | --- |
| Repository host | GitHub | GitHub |
| Tracker | GitHub Issues | Jira |
| Approval of requirements | Pull request review on GitHub | Jira workflow transition |
| Test manager | None: test descriptions and results stay in the repository | Xray |
| Document system | None: documents stay in the repository | The company's controlled document system |

The prototype runs entirely on GitHub, and its approvals are pull request
reviews. GitHub does not make the reviewer re-enter credentials, so a
prototype approval is not an electronic signature under 21 CFR Part 11. A
deployment takes its approvals and signatures from Jira, Xray and the document
system. A Jira or Xray transition is an electronic signature only when the
workflow makes the approver re-enter their credentials at that transition;
setup reports a workflow that does not.

VOGON never approves or signs anything (`CON-001`). It drafts, checks, files
and reports. A change to a live system is recorded and approved in the host
project's own change control system; its requirements, tests and release
documents go through the same skills (`DEC-026`).

## Skills

One skill per task a person starts. A skill runs in the main Claude Code
session, which acts as the coordinator described below.

| Skill | Does | Steps | Process page |
| --- | --- | --- | --- |
| `vogon:setup` | Writes `vogon.yaml`, drafts the validation plan and sends it for approval | 1 | [Setup](process/setup.md) |
| `vogon:meetings` | Selects meetings, writes checked summaries, drafts records and their risk, checks them, opens the pull request, creates the tracker issues | 2–5 | [Meetings](process/meetings.md), [New requirements](process/new_requirements.md) |
| `vogon:from-code` | The same as `vogon:meetings`, drafting from existing code and its documentation | 3–5 | [Development process](process/index.md) |
| `vogon:next` | Lists the requirements ready to start in priority order, lists the blocked ones with what blocks them, assigns the chosen one | | [Next work](process/next_work.md) |
| `vogon:implement` | Plans one requirement, writes its test cases and sends them to the Test Lead, writes or checks the code and test code, opens the pull request | 7–10, 12–13 | [Planning](process/planning.md), [Implementation](process/implementation.md), [Tests](process/test_checks.md) |
| `vogon:release` | Drafts and checks the validation documents for a release commit, including the URS and the validation summary report, imports the results, files the evidence | 15–16 | [Documents](process/documents.md) |

Steps 6, 11, 14 and 17 are approvals given by people, and no skill performs
them.

Every skill starts the same way: it reads the current state of the
requirements it concerns from the repository, the tracker and each
requirement's [state file](#state-of-a-requirement), and reports any
difference between them. Tasks happen weeks apart, by different developers, in
any order. A skill does not assume an earlier task ran. When one was skipped,
the skill does what still applies and reports the gap, such as code merged
with no plan.

A skill's `SKILL.md` holds the task's steps, the subagents it starts, what
each receives, and where it stops for a person. Checklists are in the skill's
`references/` directory and are read by the subagents that apply them.

### Test cases and test code

A test case states what is tested: the acceptance criterion it covers, its
inputs and its expected values. Test code is the pytest function that carries
it out. VOGON imposes no order on code, test cases and test code.

How formal the testing is follows the requirement's risk:

| Risk | Test cases | Test Lead approval |
| --- | --- | --- |
| `high`, `medium` | Written as test cases in `REQ-<MODULE>-<NUMBER>.tests.md` | Required |
| `low` | The acceptance criteria are the test cases; no separate file | Required, of the tests on the pull request |
| `gxp_impact: none` | None; verified by whatever the `verification` field names | Not required |

`vogon:implement` writes the test cases from the requirement, never from the
code, and the `test-checker` checks every expected value against the
requirement whichever was written first. The Test Lead approves them (step
11): in the prototype by an approving review of the pull request, in a
deployment in the test manager, where the skill registers them linked to the
requirement issue. The approval must come before the merge and before any
result counts as evidence; it does not have to come before the code. In a
deployment, `vogon:implement` copies the approved test cases from the test
manager into the `.tests.md` file in the pull request, as it does for the
requirement text.

The developer writes the code and the test code in whatever order they work
in, with or without the agent. A test that verifies requirements names them in
its marker, and may name several. A test with no marker, such as a unit test
of an internal function, is allowed and is not evidence. The `test-checker`
confirms that every approved test case is carried out by a test. A test case
changed after its approval goes back to the Test Lead, and the skill reports
the change on the pull request.

## Coordinator and subagents

The main session coordinates. It reads state, starts subagents, passes
results between them, decides when a result is good enough to go on, and
stops for people. It drafts nothing itself. Its context holds the task, file
paths and short summaries, so it does not fill up over a long task.

A subagent is a separate Claude Code session started by the coordinator, with
its own instructions and context. It writes its output to files on the
working branch and returns a short summary and the paths it wrote. Independent
units of work run in parallel, for example one summary per meeting.

Workers produce things. Each worker has full access to the repository and to
whatever its work needs.

| Worker | Produces |
| --- | --- |
| `summariser` | One summary per meeting transcript |
| `drafter` | Records, with risk, drafted from summaries or from existing code |
| `planner` | The plan for one requirement |
| `implementer` | Test cases, code, test code and documentation |
| `document-writer` | One validation document for a release commit |

Checkers review what a worker produced. A checker is never the session whose
output it checks. It has read access to everything and edits nothing; it
returns findings, each with its evidence. Each checker applies one checklist.

| Checker | Checks | Checklist from |
| --- | --- | --- |
| `summary-checker` | A summary against its transcript | [Meetings](process/meetings.md) |
| `record-checker` | Drafts against the summaries, the other records, the open pull requests and the code | [New requirements](process/new_requirements.md) |
| `challenger` | Whether a requirement or a design makes sense in practice: how often the situation occurs, against how often the work runs and what it costs | [New requirements](process/new_requirements.md), [Planning](process/planning.md) |
| `risk-checker` | The risk level and its reasoning, against the requirement and similar requirements | [Risk](#risk) |
| `plan-checker` | A plan against the requirement and the code | [Planning](process/planning.md) |
| `test-checker` | Test cases against the requirement, and test code against the test cases and for soundness | [Tests](process/test_checks.md) |
| `code-reviewer` | The change against the plan and the code checklist | [Implementation](process/implementation.md) |
| `document-checker` | A document against the requirements, the code and the results of the release commit | [Documents](process/documents.md) |

### Fix loop

1. The coordinator gives the checker's findings to a worker, which fixes them
   or disputes a finding with evidence.
2. A fresh checker session checks the result.
3. A disputed finding gets one reply from the checker. If the two still
   disagree, both positions go to the developer.
4. After three rounds, the findings still open go to the developer with their
   evidence.

A finding that needs a decision from someone other than the developer goes to
that person as [When a check fails](process/failed_checks.md) describes.

### When a skill stops for a person

- An approval or a signature. VOGON tells the role holder what is waiting and
  where.
- A choice that belongs to someone else, such as the Product Owner choosing
  between contradicting requirements.
- Once before work leaves the developer's branch for a place other people
  read: before opening a pull request or writing to the tracker. The developer
  gets a short report of what is about to be sent.

Nothing else waits for confirmation.

## Records

Requirements, domain facts, constraints and decisions are markdown files in
the host project's repository, under `vogon/`, in the format
[Records](records.md) defines. The markdown file is what people read and
review. Its frontmatter holds the record's identity and fixed attributes, and
its `status` is `active`, `withdrawn` or `superseded_by: <id>`. Whether a
requirement is approved, and what has been done to it, is not in the markdown.

Meeting transcripts are never held. A summary in `vogon/sources/` records the
meeting's id in the meeting system, its date and its participants, and is
checked against the transcript before the transcript is deleted
([Sources](sources.md)). The Product Owner's approval makes a statement a
requirement; the meeting is only where it came from.

A draft carries a temporary id until the developer's review. When the skill
creates the tracker issues, it gives each requirement the next number not used
on `main`, in an open pull request or in a tracker issue, creates the issue
with that id in its title, and only then renames the draft. The tracker issue
reserves the id for every developer, whatever branch they are on. If the
tracker search then shows an earlier issue with the same id, the later one
takes the next free number before anything else uses it.

### Tracker issues and approval

After the developer's review, `vogon:meetings` and `vogon:from-code` create one
tracker issue per new requirement, holding its text and any finding that
needs the Product Owner's choice. The tracker issue carries priority and
assignee, and `vogon:next` reads and sets them.

In the prototype, a requirement is approved when a pull request that adds or
changes its file is approved on GitHub by the Product Owner and merged.

In a deployment, the approval is the tracker issue's transition into an
approved state. The Product Owner may edit the text in the tracker before
approving it, and `vogon:implement` copies the approved text into the markdown
file in the implementation pull request.

The approved text is read from the system that holds the approval: in the
prototype, the file at the merge commit of the approving pull request; in a
deployment, the tracker text at the approval transition. A requirement whose
text in that system has changed since its approval needs approval again, is
reported by every skill that reads it, and is not offered as ready by
`vogon:next`. In a deployment, a markdown file that differs from the approved
tracker text is reported as waiting to be copied, and does not block the
work. The `Accepted findings` block is not part of the compared text.

### Accepted findings

A finding the Product Owner accepts without changing the requirement stays on
the record, in an `Accepted findings` block of the markdown, with the reason
and the date ([When a check fails](process/failed_checks.md)). `vogon:next`
lists it beside the requirement, `vogon:implement` shows it before planning,
and the plan, the pull request and the test report cite it.

## State of a requirement

Each requirement has a state file beside its markdown file,
`REQ-<MODULE>-<NUMBER>.json`, committed with it. It records what has been
done to the requirement, one entry per step, each with the date and the
GitHub object that shows it: a pull request, a commit, an issue. The format is
in [Records](records.md#state-file).

A skill writes an entry only for a step it performs, on the branch that does
the work on that requirement: drafted, planned, test cases written,
implemented. Approvals, merges, assignment and releases happen in GitHub and
the tracker, and are read from there each time a skill needs them; they are
never written to the state file. `vogon:next` reads state files and writes
none. Only the branch working on a requirement edits its state file, so two
branches do not edit the same one.

The state file is a record of progress for people and skills to read. The
evidence is in GitHub, the tracker, the test manager and the test results,
never in the state file. Every skill compares the entries it reads with those
systems before it acts, and reports a difference instead of trusting the
file.

## Risk

Each requirement carries its risk from the moment it is drafted, so the
Product Owner approves the risk with the requirement and the plan can size the
testing to it. The frontmatter holds `gxp_impact` and `risk`, and the body has
a `Risk` block with the reasoning ([Records](records.md#requirement)). The
`risk-checker` compares the level with the reasoning and with similar
requirements.

The risk level decides the testing the plan calls for. A `high` requirement
has its boundary values and error cases tested. A requirement with
`gxp_impact: none` may be verified by inspection.

At release, `vogon:release` compiles the risk assessment document from the
risk fields and blocks of the requirements in the release. It does not assess
risk again.

## Tests and traceability

A test names the requirements it verifies with a pytest marker,
`@pytest.mark.req("REQ-PRN-12")`. The link is written on the test because
whoever changes a test edits its marker in the same edit (`DEC-006`).
Requirement ids are not written in implementation code. A commit names the
requirements it implements.

The approved test cases are the test specification. At release,
`vogon:release` assembles the test specification document from them: from the
`.tests.md` files and the acceptance criteria in the prototype, from the test
manager in a deployment.

Only results from runs after the Test Lead's approval count as evidence.

## Deterministic code

Code exists only where the output is validation evidence, or where a model's
mistake would go unnoticed. None of it calls a model or the network.

`vogon_pytest.py` is a pytest plugin. During a test run it writes each test's
node id, the requirement ids from its marker, its outcome and its duration,
keyed by the commit from `git rev-parse HEAD`. It records no commit when the
working tree has uncommitted changes, because the code under test could not
be identified. It writes the results in two forms:

- `vogon/out/results/<commit>.json`, read by `vogon trace` and the skills;
- `vogon/out/results/<commit>.xml`, in JUnit XML, carrying for each test the
  tracker keys of its requirements, read from the tracker issue titles, in the
  properties the test manager's import reads.

`vogon/out/results/` is gitignored, so a run never leaves the working tree
dirty. CI uploads both files as an artifact of the run.

In a deployment, `vogon:release` uploads that XML file to the test manager
unchanged. The test manager then produces the coverage and traceability
reports (`DEC-003`). The model transmits the file and never writes results.

`vogon trace <commit>` is used in the prototype, which has no test manager. It
reads the requirement files and the results for a commit and writes the
traceability matrix and the results table to `vogon/out/`: each requirement,
its tests, their outcomes on that commit, and each requirement verified by test
that has no test.

The pytest plugin depends only on pytest and the standard library, because it
runs in the host project's environment. There are no hooks. A skill reads
`vogon.yaml` when it starts.

## Release

`vogon:release` takes a release commit. The host project's CI runs the full
test suite on it with the pytest plugin, so the results are recorded against
that commit, and the skill downloads the results from that run's artifact.
The skill then:

1. Drafts the URS, the risk assessment, the test specification, the design
   specification, the test report and the validation summary report into
   `vogon/documents/<release>/`, each from the requirements, the tests, the
   code and the results of that commit. The URS is compiled from the approved
   requirements in the release. The summary report states, against the
   validation plan, what was done, what deviated and how each deviation was
   handled (`DEC-027`).
   Each document cites what it states.
2. Has each document checked by a `document-checker`.
3. In the prototype, writes the traceability matrix with `vogon trace`,
   copies the results of the release commit into `vogon/documents/<release>/`
   so git retains them, and opens a pull request with the documents. The
   approving reviews by the Test Lead, the System Owner and the Quality
   Manager are the prototype's sign-off. In a deployment,
   imports the results into the test manager, files the documents and the
   test manager's traceability report in the document system, and tells each
   role holder what is waiting to be signed.
4. After filing, reads the filed copies back and reports any that differ from
   what was drafted or exported.

The Test Lead approves the test specification, and the System Owner and the
Quality Manager sign the package (step 17).

The validation plan is drafted once per project by `vogon:setup`, kept in
`vogon/documents/validation_plan.md`, and approved by the System Owner and the
Quality Manager before any result counts as evidence. A change to its content
is approved the same way (`DEC-027`).
