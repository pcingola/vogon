# Checking the new requirements

The agent does this as part of drafting, without being asked, before
anything is committed or sent to the tracker. It fixes what
it can fix alone: a draft that duplicates an existing requirement is dropped,
one that restates part of another is cut back to what is new, one that is
ambiguous is rewritten from its source. The rest is handled as [When a check fails](failed_checks.md)
describes: first the developer, then the Product Owner on the tracker
issue, each finding with the statements involved and where each came from.

Checks against the other records, including those in other developers' open
pull requests:

- It contradicts no other requirement, constraint or decision: both cannot
  hold at once, or one forbids what the other requires.
- It is not already covered: no other requirement states it, in other words,
  or implies it as a special case.
- Its acceptance criteria do not test what another requirement's criteria
  already test.
- Everything it relies on is stated by some record, and none of those
  records is withdrawn.
- A term means the same thing here as in the other records.
- Its risk level is in line with the requirements it depends on or is
  similar to.

Checks against the code:

- The code does not already do it. If it does, the requirement describes
  existing behaviour and says so.
- It does not break behaviour that other requirements rely on.
- The system has what it needs: the data, the inputs, the interfaces to
  other systems. A requirement on data the system never receives cannot be
  met.

Checks that the requirement makes sense on its own:

- It can be tested: a test could fail, and the acceptance criteria are
  measurable.
- It is achievable. "Never fails" and "zero delay" are not.
- It is needed: it follows from a user need, a regulation or a decision,
  and is not a feature nobody asked for.
- It is complete: the inputs, the conditions, the expected behaviour, the
  error cases, and what it does not require.
- It has one reading. No "fast", "user-friendly", "as appropriate",
  "where possible".
- It states what the system must do, not how, unless the how is itself
  imposed.
- It states one thing. Two statements are two requirements.
- It is a requirement on the system, not on a person or another system.

Checks that the requirement makes sense in practice. A requirement can be
consistent with every other record and with the code, and still be
senseless. These checks are done by a separate agent whose only task is to
challenge the requirement: it assumes the requirement may be pointless and
looks for the reason it is, using the facts, the sources, the code and what
is known about the systems involved. The text being well formed does not
satisfy it. No person is added to the process; its findings go back to the
drafting agent like any other, and only a finding that needs a choice
reaches the Product Owner. For each requirement it writes down:

- The real situation it responds to, and how often that situation happens
  in practice, from the facts, the sources and what is known about the
  systems involved.
- How often the system will do the work the requirement asks for, and what
  each time costs: running time, calls to other systems, the developer's
  time, interruptions of a person.
- What goes wrong if the requirement is not met, for whom, and how badly.

It is a finding when these do not match: the work runs far more often than
the situation it guards against, or meeting the requirement costs more than
the failure it prevents. Re-reading a company system's configuration on
every turn of a conversation with the agent, when that configuration
changes once in years, is consistent text and a senseless requirement.
Checking a condition every 5 ms when it happens once in a thousand years is
the same. Other findings in this pass:

- The agent cannot say what problem the requirement solves, in one
  sentence a person in the domain would agree with.
- A cheaper way reaches the same outcome: checking once at setup, when the
  thing changes, or when something fails, instead of continuously.
- It adds steps, confirmations or files to the developer's work that nobody
  would miss if they were gone.

What happens to such a finding is in [When a check fails](failed_checks.md): a draft
that misread its source is rewritten; a senseless requirement the source
did ask for goes to the Product Owner with the cheaper form that meets the
same need and the reasoning: how often the situation happens, how often the
work would run, and what each costs.

Checks that it fits the project:

- It is within what the system is for. A requirement that turns a
  label printer into a scheduler is out of scope, however well written.
- It is consistent with the project's architecture decisions and
  constraints, or it says which decision it would reverse.
- Its regulatory weight is right: whether a failure would affect patient
  safety, product quality or data integrity. A requirement that makes a
  non-regulated part of the system regulated says so, because that changes
  the validation cost of that part.
- The set still reads as one system: the new requirements do not pull the
  design in two directions.
- The set as a whole is worth building: read together, the requirements
  describe a system that does something useful for its users, and the
  effort they demand goes where the risk is, not to rare or harmless
  cases.

When the checks are done:

1. The agent commits the summaries and the drafted records to the
   developer's branch. How the work reaches `main` is the developer's choice. The usual
   case is one pull request per meeting batch holding the summaries and
   all the records drafted from them, however many there are, so that every
   developer can see and pick the new requirements. When the
   developer is going to implement all of them at once, the records go in
   the same pull request as the implementation, and there is one merge.
   Every pull request names the ids of the records it adds or implements.
   A pull request that only adds records names the new ids, for example
   "REQ-SMP-141 to REQ-SMP-145: requirements from the 15 September barcode
   printing meeting". This links each record to the commit that added it.
2. It tells the developer what it did: the meetings it used and why, the
   meetings it left out, meetings with no transcript, the records it
   drafted, and the unanswered questions with the person who raised each
   one. It says that the requirements will go to the tracker for the
   Product Owner next, and gives the developer the chance to review them
   first. This is the one point before the tracker where the agent waits. An
   edit the developer makes is checked again against [From meetings to requirements](meetings.md) and
   [Checking the new requirements](new_requirements.md).
3. With the developer's feedback applied, or once the developer says to go
   ahead, the agent gives each draft its final id, reserved by creating its
   tracker issue, and renames the draft from its temporary id. It creates a
   tracker issue for each proposed requirement,
   from the branch, in the tracker's state for items awaiting review, so
   the Product Owner's approval does not wait for a merge. Each issue holds
   the requirement's text and acceptance criteria, and any finding above
   that needs the Product Owner's choice.
4. The Product Owner works in the tracker, not in the repository. On each
   issue they decide the findings that need a choice, edit the text if it
   is wrong, and approve the requirement or reject it.
5. The approval stays in the tracker, and the record does not copy it:
   whenever the agent needs to know whether a requirement is approved or
   rejected, it reads the tracker. No merge follows the approval.
6. An edit the Product Owner made to the text in the tracker is copied into
   the record by the implementation pull request of that requirement
   ([Test cases, code and tests](implementation.md)), so the code is built against the approved text.

Steps 4 to 6 describe a deployment, where the tracker records the approval.
In the prototype, the tracker is GitHub Issues and holds priority and
assignee only. The Product Owner approves the requirements by approving the
pull request that adds them, edits the text in that pull request, and the
pull request merges after the approval.
