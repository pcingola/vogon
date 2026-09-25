# Plan (step 7)

A plan states what will be built for a change and how it will be tested,
before the code is written. It is not a description of what exists. Each item
below is a rule the plan meets or fails. The plan also follows
`references/writing.md`.

## File

- [ ] One plan per change, at `vogon/plans/plan_<slug>.md`. The slug is
      lowercase words joined by hyphens or underscores and names the change.
- [ ] The plan is written before the code it describes.
- [ ] Nothing committed outside `vogon/plans/` depends on the plan.

## Content

- [ ] `## Summary`: what the change builds, in a short paragraph.
- [ ] `## Records`: two lists of record ids. `Implements`: the requirements
      the change makes hold. `Rests on`: the other records the design uses.
      Each id resolves to a record whose status is `proposed` or `accepted`.
- [ ] The plan cites records by id and does not restate them. A statement
      that must hold is a record, not a plan item.
- [ ] The change builds the conditions of the implemented requirements as
      they are written, and nothing else. An input the requirements' text
      does not name keeps the behaviour it has before the change; the plan
      need not describe it, and does not argue whether it is covered.
- [ ] `## Design`: the source modules, files and data the change adds or
      alters, and the reason for each choice that is not obvious from the
      records. Tests are listed in `## Testing` and documentation in
      `## Documentation`, not here.
- [ ] `## Interface`: one entry for each function, method, class or command
      that the change adds or alters and that a new test in `## Testing`
      calls. Each entry gives:
  - [ ] the name and invocation: the import path and the signature with
        parameter names and types, or the command line with each argument
        and option the tests pass;
  - [ ] the result in each case a new test checks: the return value and its
        type, or the exit status and what is written to standard output or
        standard error;
  - [ ] each error raised or non-zero exit status, with its condition, for
        each condition an acceptance block of an implemented requirement
        names; where one input meets several failure conditions, which
        failures are reported, and each failure an implemented requirement
        requires for that input is among them;
  - [ ] each file the call creates, changes or deletes in a case a new test
        checks.
- [ ] An existing test the change makes fail is listed in `## Testing` with
      the change to it. Its other assertions are not restated in
      `## Interface`.
- [ ] `## Interface` describes only what the items above require. Behaviour
      the change does not alter and no new test checks is left out; its
      absence is not a failure.
- [ ] Each acceptance clause of an implemented requirement with
      `verification: test` can be tested from `## Interface` alone.
- [ ] `## Testing`: for each implemented requirement with `verification:
      test`, the test file its new tests go in and the acceptance clauses
      they cover.
- [ ] `## Steps`: a flat checklist of implementation steps, each naming the
      record ids it covers, in the order they are done.
- [ ] `## Documentation`: each documentation file the change alters.
- [ ] No open question, TBD or TODO. A question the plan depends on is asked
      of the person before the plan is written.
- [ ] `## Testing` names no expected value that is not in an acceptance
      block of an implemented requirement or worked out from its rule.

## Changes to the interface

- [ ] When the code needs an interface other than the one the plan names,
      the plan's `## Interface` is changed first and the tests that call it
      are checked again at step 9.

## Retiring a plan

- [ ] A plan implemented or abandoned is moved to `vogon/plans/done/` with
      `git mv`, unchanged.
- [ ] Before it is moved, everything in it that must stay true is written
      into the project's documentation or into records.
- [ ] A plan under `vogon/plans/done/` is never read as a description of the
      system and never updated.
