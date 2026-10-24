# Test checklist

The default checklist for the tests of one part of a plan.

The evaluator reads the requirements the part covers, their acceptance
criteria, the plan entry for the part, and every test whose
`@pytest.mark.req(...)` marker names one of those requirements. Each item the
tests fail is a finding, with the test name, the file and line, and the
requirement text it concerns.

- [ ] Each test checks the requirement and its intent. A test of trivial code
      behaviour that the requirement does not care about, such as a getter, a
      default value or a constructor, is a finding.
- [ ] No assertion checks an internal detail the requirement does not state.
      Such an assertion fails when correct code is restructured.
- [ ] Each expected value is worked out
      (`${CLAUDE_PLUGIN_ROOT}/references/records.md` "Expected values").
- [ ] Where the requirement and its acceptance criteria give no expected
      value, the test does not invent one, and the writing sub-agent reports
      the missing value. An invented expected value is a finding.
- [ ] The tests together cover every aspect of each requirement: every
      acceptance criterion, and each edge case and input combination the
      requirement states. Where the requirement has them, the edge inputs are
      tested: empty, the largest allowed, malformed, non-ASCII, and the value
      on each side of a limit. An aspect no test checks is a finding.
- [ ] A rejected input is rejected with the error the requirement states, and
      the test asserts that error.
- [ ] Each test can fail: it would fail if the behaviour were removed or
      broken. A test that compares a value with itself, or computes its
      expected value with the code under test, is a finding.
- [ ] The test data contains no real personal or patient data.
- [ ] No test uses a mock, a patch or a mocking library, such as
      `unittest.mock` or `pytest-mock`, unless `vogon/project/tests.md` "Unit
      tests and formal tests" allows mocks. A real object is not a mock.
- [ ] No test was deleted, skipped, marked as an expected failure, or had an
      assertion weakened or an expected value changed to make a run pass. Such
      a change is a finding unless the writing sub-agent's log cites the
      requirement text the old value contradicts.
- [ ] The markers of each test follow
      `${CLAUDE_PLUGIN_ROOT}/references/markers.md`.
- [ ] Each test the plan entry lists for the part exists.
