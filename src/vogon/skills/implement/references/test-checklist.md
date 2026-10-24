# Test checklist

The default checklist for the tests of one part of a plan.

- [ ] Each expected value is worked out
      (`${CLAUDE_PLUGIN_ROOT}/references/records.md` "Expected values").
- [ ] Where the requirement and its acceptance criteria give no expected
      value, the test does not invent one, and the missing value is
      reported. An invented expected value is a finding.
- [ ] No test uses a mock, a patch or a mocking library, such as
      `unittest.mock` or `pytest-mock`, unless `vogon/project/tests.md` "Unit
      tests and formal tests" allows mocks. A real object is not a mock.
- [ ] To make a run pass, no test was deleted, skipped or marked as an
      expected failure, and no assertion was weakened or expected value
      changed. Such a change is a finding unless the sub-agent that made it
      cites the requirement text the old value contradicts.
- [ ] The markers of each test follow
      `${CLAUDE_PLUGIN_ROOT}/references/markers.md`.
