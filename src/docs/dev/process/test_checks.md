# Checking the tests

A separate agent, which did not write the tests, does two checks. It checks
the test cases against the requirement before they go to the Test Lead. It
checks the test code against the approved test cases, and for soundness,
before the pull request is opened. Both run again whenever the requirement,
the test cases or the tests change. It reads the requirement, the test cases,
the tests and the code. Findings go back to the agent that wrote the tests
until none remain. The report on the test cases goes to the Test Lead with
them.

Checks that the test cases and the tests test the requirement:

- Every acceptance criterion has a test.
- The boundary values and error cases the requirement names are tested:
  the value on each side of a limit, the invalid input, the missing input.
- Every expected value comes from the requirement or is worked out from its
  rule, never copied from a run of the code.
- No assertion goes beyond the requirement, such as a check of an internal
  detail the requirement does not state, which fails when the code is
  restructured without being wrong.
- Each test is linked to every requirement it verifies.
- Every approved test case is carried out by a test that uses its inputs and
  expected values.

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
- Each test checks one behaviour, and its name says which.
- No test is skipped or marked as an expected failure without a stated
  reason.
- The test checks the project's code, not the behaviour of a library it
  uses.
- A bug fix has a test that fails without the fix.
- The test data contains no real personal or patient data.
- The tests run in CI on the build that will be released, and the results
  are recorded against that build.

If an approved test case is later changed, or a test's expected value is
edited away from its test case to make a failing test pass, the agent reports
it on the pull request, and the change needs the Test Lead's approval again.
