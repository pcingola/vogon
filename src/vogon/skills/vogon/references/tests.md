# Tests (steps 8, 9 and 10)

Writing the test cases for requirements, checking them against the
requirements, and handing them over for registration. Each item below is a
rule the tests or the report meet or fail.

The test agents read only the records directory and the test paths. They
never read the implementation source, run the code, or see its output.

## Which requirements

- [ ] Every requirement with `verification: test` and status `accepted`
      named for the change has tests.
- [ ] A test names only a requirement whose acceptance block has
      `acceptance_by` and `acceptance_on`. A requirement without them is
      reported, not tested.
- [ ] No test names a requirement that is `withdrawn` or superseded, or an id
      with no record.

## Step 8: writing the tests

- [ ] Tests are pytest functions in files under the test paths, in the file
      the plan's `## Testing` section names.
- [ ] Each test function, or its class, carries
      `@pytest.mark.req("<id>")` naming every requirement it verifies, with
      one or more ids as arguments. `pytestmark = pytest.mark.req(...)` marks
      a whole module.
- [ ] Each clause of the acceptance block is exercised by at least one test.
- [ ] Every expected value a test asserts is the value the acceptance block
      states, or one worked out from the requirement's rule. It is never
      taken from running the code.
- [ ] A value the acceptance block does not give is not invented. The clause
      is reported to the caller, and the acceptance block is changed and
      accepted again by a person before a test asserts it.
- [ ] Each assertion follows from the requirement. A test asserts nothing the
      requirement does not state.
- [ ] Tests call only what the plan's `## Interface` section names, with the
      signature it gives.
- [ ] Test inputs are real values and real files, created in the test, for
      example under `tmp_path`.
- [ ] A test's name and docstring say which clause it checks, in the words of
      the requirement.
- [ ] No requirement id appears in the test other than in its marker.

## Step 9: checking the tests

For every accepted requirement with `verification: test` named for the
change, the test checker reads the requirement, its acceptance block and every
test whose marker names it, and reports:

- [ ] each clause of the acceptance block that no test exercises;
- [ ] each expected value in a test that differs from the acceptance block;
- [ ] each assertion that does not follow from the requirement;
- [ ] each marker naming an unknown id, a withdrawn or superseded requirement,
      or a requirement without `acceptance_by`.

- [ ] The report names the requirement id and the test node id for each
      finding, as `<file>::<function>` or `<file>::<class>::<function>`.
- [ ] The report does not judge whether the tests are adequate.
- [ ] The comparison is between the requirement and the tests. Code
      coverage and marker counts are not used.

## Step 10: handing the tests over

- [ ] `vogon check` reports no error from the marker checks.
- [ ] The final step 9 report goes to the person with the test cases, for the
      roles `approvals.test_cases` names, who approve the test issues in the
      test manager.
- [ ] The test specification describes each test by node id: what it checks,
      its inputs and the expected values it asserts. It names no requirement
      and holds no table from requirements to tests: the markers and the test
      manager hold those links (`REQ-TRC-7`).
- [ ] The test specification is drafted following `references/documents.md`,
      filed in the document system and approved there by the roles
      `approvals.test_specification` names.
- [ ] Registering the test issues follows `tracker.md`.
