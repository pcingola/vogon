# What to work on next

A developer asks the agent what to work on next and how to prioritise the backlog.

1. The agent reads the current state from the systems: the tracker for
   rank, assignee, status and approval; the repository host for open
   branches and pull requests; the test manager for test status.
2. It gives the developer the requirements they can start, in the Product
   Owner's order, and lists
   the blocked ones separately, each with what blocks it and who can
   unblock it.
3. When the developer starts on a requirement, the agent assigns the tracker
   issue to them, so no other developer starts the same one.

Checks before a requirement is offered as ready:

- It is approved in the tracker, and its text has not changed since the approval.
- Every requirement it depends on is done or in the same piece of work.
- Nobody is assigned to it, and no open branch or pull request already
  implements it.
- No open pull request changes the code it will change in a way that
  conflicts.
- Where the Product Owner's order cannot be followed, such as a top item that depends on
  an unapproved one, the agent says so.
