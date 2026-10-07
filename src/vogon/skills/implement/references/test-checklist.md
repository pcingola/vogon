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
- [ ] Each expected value comes from the requirement or its acceptance
      criteria, or is worked out from them. An expected value that matches
      only what the code returns is a finding.
- [ ] Where the requirement and its acceptance criteria give no expected
      value, the test does not invent one. The writing sub-agent reports the
      missing value; the requirement is corrected and approved again before a
      test asserts it. An invented expected value is a finding.
- [ ] No test was deleted, skipped, marked as an expected failure, or had an
      assertion weakened or an expected value changed to make a run pass. Such
      a change is a finding unless the writing sub-agent's log cites the
      requirement text the old value contradicts.
- [ ] The tests together cover every aspect of each requirement: every
      acceptance criterion, and each edge case and input combination the
      requirement states. An aspect no test checks is a finding.
- [ ] No test uses a mock, a patch or a mocking library, such as
      `unittest.mock` or `pytest-mock`, unless `options.mocks_authorized` in
      `vogon/project/vogon.yaml` is `true` or the project's own documents
      authorize it. A real object is not a mock.
- [ ] No test checks the behaviour of a library, such as whether a JSON file
      parses or a standard function returns its documented value.
- [ ] Each test names the requirements it verifies in
      `@pytest.mark.req(...)`, and only requirements it verifies. Where a test
      procedure for the requirement exists, the test also names it in
      `@pytest.mark.procedure(...)`.
- [ ] Each test the plan entry lists for the part exists.
