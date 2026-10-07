# Test cases, code and tests

VOGON does not set the order in which a developer writes code, test cases and
tests. It requires only that every expected value comes from the requirement,
never from the code, and that the Test Lead approves the test cases before
the merge. How formal the test cases are follows the requirement's risk
([Architecture](../architecture.md#test-cases-and-test-code)).

1. After the plan, the agent writes the requirement's test cases from the
   requirement: for each acceptance criterion, the cases that cover it, with
   their inputs and expected values. Each expected value comes from the
   requirement or is worked out from its rule. For a `high` or `medium` risk
   requirement they go in `REQ-<MODULE>-<NUMBER>.tests.md` beside the
   requirement; for a `low` one the acceptance criteria serve. Together they
   are the test specification. A requirement with `gxp_impact: none` has no
   formal test cases.
2. A second agent checks the test cases, as [Checking the tests](test_checks.md)
   describes.
3. The agent sends the test cases to the Test Lead: in the prototype on the
   pull request, in a deployment by registering them in the test manager,
   linked to the requirement issue. The Test Lead approves them there. The
   approval must come before the merge; work on the code does not wait for
   it. In a deployment the agent copies the approved test cases from the test
   manager back into the repository in the same pull request.
4. The code, the test code and the documentation the plan names are written
   in the order the developer chooses, by the developer or by the agent.
   A test that verifies requirements names them in its marker and may name
   several. Tests with no marker, such as unit tests, are allowed and are not
   evidence. Where the code needs something the plan does not say, the
   plan is changed and checked again.
5. The agent runs all the tests. A failing test is fixed by changing the
   code. If a test case is wrong, the corrected case goes back to the Test
   Lead. If the requirement's expected value is wrong, the agent tells the
   developer, because correcting it needs the Product Owner's approval again.
6. A second agent checks that every approved test case is carried out by a
   test, and reviews the change (checks below).
7. Each commit names the requirement it implements. The pull request's
   description names the requirements and the plan, and states any change to
   a test case since the Test Lead's approval. It holds the plan, the test
   cases, the code, the tests, the documentation, and any edit the Product
   Owner made to the requirements' text in the tracker. Another developer
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
