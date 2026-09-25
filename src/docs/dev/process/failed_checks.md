# When a check fails

Every check in these pages can fail, at any step. Each failure is handled
the same way: the agent fixes what it can, the rest goes up one person at a
time, and whatever is decided about a problem that remains is written down
where it will be seen again.

## Who resolves a finding

1. The agent that did the work, when the finding is its own mistake and the
   fix changes nothing anyone asked for: a misread source, a wrong value, an
   ambiguous sentence, a duplicate of an existing record, a design that runs
   something too often. It fixes it, the check runs again, and the fix is
   listed in the report to the developer. Nobody is asked.
2. The developer, at the one review before anything goes to the tracker,
   for a finding the agent cannot fix without changing what someone asked
   for. The agent gives the finding, its evidence and a proposed fix. The
   developer applies the fix, drops the draft, or passes the finding to the
   Product Owner. A draft the developer drops is never created: nothing is
   committed and nothing is sent to the tracker.
3. The Product Owner, in the tracker, for a finding the developer passes on
   and for every finding that only the Product Owner may settle: a conflict
   with an accepted requirement, a change of scope, or a risk to patient
   safety, product quality, data integrity or security. The developer
   cannot waive these. The Product Owner accepts the proposed fix, rejects
   the requirement, or accepts it as it is.

When two agents disagree about a finding, they get one exchange, and then
the disagreement goes to the developer with both positions.

## What each finding usually leads to

| Finding | The agent fixes it when | Otherwise it goes to | Outcomes |
| --- | --- | --- | --- |
| Contradicts other requirements | the draft misread its source | Product Owner | one requirement changes, one is rejected, or a decision record states which one holds |
| Duplicates or is covered by another requirement | always: the draft is dropped or cut to what is new | | |
| Goes against an architecture decision | the source did not ask for that design | Product Owner, with the decision it would reverse | the requirement changes, or it is accepted and a new decision replaces the old one |
| Outside what the project is for | | Product Owner | rejected, or accepted with the scope change stated |
| Senseless in practice (cost against frequency and harm) | the draft misread its source | developer, then Product Owner | rewritten in the cheaper form that meets the same need, rejected, or accepted as it is |
| Security problem | the fix does not change what was asked for | Product Owner | changed, or rejected. Accepting it as it is needs the Product Owner to state the reason |
| Cannot run where the system runs (platform, hardware, missing data or interface) | | Product Owner | changed, rejected, or accepted together with the change to the environment it needs |
| Cannot be tested, or a needed value is missing | the source gives the value | the person who raised it in the meeting, through the developer | the value is supplied, or the requirement stays proposed until it is |
| Wrong risk level | always | | |

## What is written down

- A finding the agent fixed leaves no trace in the record. The report to
  the developer lists it, and the git history holds the change.
- A draft dropped before anything was committed or sent leaves nothing.
- A requirement rejected after it was committed or sent to the tracker is
  withdrawn, not deleted. The record keeps its id and states why it was
  rejected, and the tracker issue is closed as rejected with the same
  reason.
- A requirement accepted with a finding still standing carries it in the
  record, in a block named `Accepted findings`. Each entry states the check
  that failed, what it found, the evidence, and the Product Owner's reason
  for accepting it, with the date. The same text is on the tracker issue,
  where the approval is. This is a settled statement, not an open question:
  the problem is known and someone with the authority chose to go ahead.

## Seeing it again later

A requirement with an `Accepted findings` block is flagged every time
someone is about to act on it:

- In [What to work on next](next_work.md), it is listed with its findings.
- When a developer starts on it ([Planning one requirement](planning.md)), the agent shows the findings
  before planning and asks once whether to go ahead or send it back to the
  Product Owner. This is the only question it asks at that point.
- The plan, the implementation pull request and the test report cite the
  findings, so the reviewer and the approvers see them.
- If a finding no longer holds, for example the requirement it
  contradicted has since been withdrawn, the agent says so instead of
  flagging it.

The same handling applies to the later steps. A finding on a plan, code, a
test or a document that the agent cannot fix goes to the developer. If the
cause is the requirement itself, the requirement goes back to the Product
Owner through the tracker, and its implementation waits for the answer.
