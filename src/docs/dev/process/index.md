# Development process

What happens in a regulated software project from a meeting to a signed
release, and what an agent does at each point to help the people doing it.
The agent is Claude Code, working in the developer's repository, with access
to the meeting system, the tracker, the test manager, the repository host
and the document system through MCP servers.

The agent does the work and reports what it did. It stops for a person in
three cases: where the regulation requires a named person's approval, where
a choice belongs to someone else, such as the Product Owner choosing between
two contradicting requirements, and once before work the developer asked for
leaves the repository for a system other people read, such as the tracker.
At that point the developer gets a short review of what is about to be sent.
It does not ask for confirmation of steps it can check itself.

Every piece of work the agent produces is checked by a second agent that did
not produce it. The checks are listed on each page. A finding goes back to
the agent that did the work until none remain; a finding that needs a
person's choice goes to that person.

## People and systems

| Role | Does |
| --- | --- |
| Developer | Builds the system; there are several |
| Product Owner | Accepts requirements and sets priority |
| Test Lead | Approves test cases and the test specification |
| System Owner | Signs the release |
| Quality Manager | Signs the release |

| System | Holds |
| --- | --- |
| Meeting system | Meetings and their transcripts |
| Git and the repository host | Requirements as text, plans, code, tests, documentation; pull request reviews |
| Tracker | The requirement issues, their approval, priority and assignee |
| Test manager | Test cases, their approval, and test results per build |
| Document system | Validation documents and their signatures |

The agent never approves or signs anything. Each approval is given by the
person who holds it, in the system that records it.

## Pages

- [Steps of the GxP process](steps.md): the steps every requirement goes through, in order
- [Setting up a project](setup.md)
- [When a check fails](failed_checks.md): the handling every page below uses when a check fails
- [From meetings to requirements](meetings.md)
- [Checking the new requirements](new_requirements.md)
- [What to work on next](next_work.md)
- [Planning one requirement](planning.md)
- [Test cases, code and tests](implementation.md)
- [Checking the tests](test_checks.md)
- [Compliance documents](documents.md)

## Rules for every step

- Steps happen weeks apart, by different people, in different orders. The
  agent works out where a requirement stands each time it is asked, by
  reading git, the tracker, the test manager and the document system as
  they are then.
- When a step was skipped, for example code merged without a plan or tests
  never checked, the agent does the step that still makes sense, such as
  checking the tests, and reports the gap.
- On a project with existing code, the agent drafts requirements from the
  code and its documentation, marked as describing existing behaviour, and
  the same checks and approvals apply from then on.
- The agent stops for a person only for an approval or a choice that is
  theirs. Everything else it does and reports.
