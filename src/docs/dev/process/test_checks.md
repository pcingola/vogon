# Checking the tests

The agent does this before opening the pull request, and again whenever the
requirement or its tests change. A separate agent, with no access to the
code, checks the tests against the requirement; a second pass, with the
code, checks that the tests are sound. Findings go back to the test-writing
agent until none remain. The final report goes to the Test Lead with the tests.

Checks that the tests test the requirement:

- Every acceptance criterion has a test.
- The boundary values and error cases the requirement names are tested:
  the value on each side of a limit, the invalid input, the missing input.
- Every expected value comes from the requirement or is worked out from its
  rule, never copied from a run of the code.
- No assertion goes beyond the requirement, such as a check of an internal
  detail the requirement does not state, which fails when the code is
  restructured without being wrong.
- Each test is linked to the requirement it verifies, and to no other.

Checks that the tests are sound:

- The test calls the real code. A mock replaces only what is outside the
  system under test, such as the network, the clock or a device, and never
  the feature being tested. A test that mocks the feature tests the mock.
- The test can fail. If the feature were removed or broken, at least one
  test would fail. A test that asserts what a mock was told to return, that
  compares a value with itself, or that computes its expected value with
  the code under test, cannot fail.
- Assertions are specific. "No exception was raised", "the result is
  truthy" or "the list is not empty" do not check the behaviour.
- Nothing in the test hides a failure: no broad exception handler around
  the assertion, no assertion inside a condition that may not run.
- The test gives the same result every run: no dependence on the current
  time, random values, test order, or the network.
- The test is independent: it creates its own data, does not rely on
  another test having run, and leaves nothing behind.
- The inputs are realistic, including edge cases: empty, the largest
  allowed, malformed, non-ASCII.
- A rejected input is rejected with the error the requirement states, not
  only "some error".
- Each test checks one behaviour, and its name says which criterion.
- No test is skipped or marked as an expected failure without a stated
  reason.
- The test checks the project's code, not the behaviour of a library it
  uses.
- A bug fix has a test that fails without the fix.
- The test data contains no real personal or patient data.
- The tests run in CI on the build that will be released, and the results
  are recorded against that build.

After the checks, if a developer later edits an expected value to make a
failing test pass, the agent reports it on that pull request. On merge the agent
registers the tests in the test manager, linked to the requirement issue, with the check
report. The Test Lead approves them in the test manager.
