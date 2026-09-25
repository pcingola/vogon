# Planning one requirement

A developer tells the agent to implement a requirement.

1. The agent reads the requirement, the requirements and decisions it
   depends on, and the code it will change. If the requirement has
   accepted findings, it shows them first and asks once whether to go
   ahead or send the requirement back to the Product Owner.
2. It writes a plan: what changes in the code, the interface the tests will
   call, which tests cover which acceptance criteria, and which
   documentation changes.
3. A second agent checks the plan. Findings go back until none remain.
4. The agent goes on to [Writing the code](implementation.md). The developer can read the plan and is
   not asked to approve it.

Checks on the plan against the requirements:

- Every acceptance criterion is built and has a test.
- It builds nothing the requirement does not ask for.
- It breaks no other requirement, including requirements outside the plan
  whose behaviour the changed code also serves.
- It cites the requirements and does not restate them.

Checks on the plan against the code:

- Every file, module and function it names exists, with the signature it
  gives, or is marked as new.
- It follows the patterns and decisions the code already uses, and reuses
  existing code instead of writing a second version.
- It lists the existing tests the change will break and what changes in
  each.
- It says what happens to data already stored: migration, compatibility
  with older records, audit trail.

Checks that the plan makes sense:

- It is the simplest design that meets the requirement: no abstraction for
  a case that does not exist, no configuration nobody needs.
- The interface can be tested directly, without mocking the feature itself.
- It names the risks the change carries for data integrity, security and
  performance, where the requirement touches them.
- It has no open question. A question the plan depends on is answered from
  the records or the code, or asked of the person who owns it, before the
  plan is written.
- It is no longer than it needs to be.
- The mechanism is proportionate, checked by the same challenging agent as
  for requirements: for
  each thing the design runs, when it runs, what triggers it, how often,
  and what it costs, against how often the situation it handles happens. A
  design that checks or re-reads something on every request, every turn or
  every run, for a situation that happens rarely, is a finding even when
  the requirement is sound. The design reacts to the event, or checks once
  at setup or on failure. The planning agent changes the design;
  the requirement is not touched and nobody is asked.
