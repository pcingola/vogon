# Writing the code, the documentation and the tests

1. A test-writing agent writes the tests from the requirement's acceptance
   criteria and the interface in the plan. It does not see the code, so the
   expected values come from the requirement.
2. The agent writes the code to the plan and updates the documentation the
   plan names. Where the code needs something the plan does not say, the
   agent changes the plan and has it checked again.
3. The agent runs all the tests. A failing test is fixed by changing the
   code. If the requirement's expected value is wrong, the agent tells the
   developer, because correcting it needs the Product Owner's acceptance
   again.
4. A second agent reviews the change (checks below).
5. Each commit names the requirement it implements. The agent opens a pull
   request whose purpose is to merge the implementation of the named
   requirements: the plan, the code, the tests, the documentation, and any
   edit the Product Owner made to the requirements' text in the tracker. Its
   description names the requirements and the plan. Another developer
   reviews and approves it on the repository host, as the branch rules
   require.

Checks on the code:

- It does what the plan says and nothing else.
- All tests pass, the existing ones included. No test was changed, skipped,
  deleted or weakened to make the run pass.
- Linting and type checks pass.
- Errors are handled where they enter the system and are not silently
  swallowed.
- Records that the regulation requires to be trustworthy stay so: no data
  is lost or overwritten without a trace, timestamps are correct and in one
  time zone, and every change to regulated data is attributable to a user.
- No secret, credential or personal data is in the code or the test data.
- Inputs from outside are validated.
- Performance meets what the requirement states, where it states it.
- Nothing runs more often than it needs to: no check, read or call in a
  path that runs on every request, turn or loop when what it guards
  against changes rarely.
- No leftover debugging code, commented-out code or unused code.
- The documentation says what the code does now.
