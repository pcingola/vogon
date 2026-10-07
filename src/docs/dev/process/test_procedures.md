# Test procedures

Steps 7 and 8 of the [steps](index.md). A test procedure is a document:
numbered steps in prose, each with its expected result, with an id and linked
to the requirements it verifies ([Architecture](../architecture.md#tests)).

The project's `tests.md` decides:

- whether the project needs test procedures. If it does not, both steps are
  skipped;
- whether they are written before development, from the requirement, or after
  it, generated from the tests;
- where they are kept: the repository, the tracker or the test manager;
- who approves them, and when.

## Step 7: write the procedures

A developer runs `vogon:tests` for one or more approved requirements. One
writing sub-agent per requirement writes its procedures. Each expected result
comes from the requirement and its sources, never from the code or a run of
it. A procedure generated from tests reports each test whose assertion
differs from the requirement. An evaluator checks each procedure against its
requirement and, where generated, its tests.

Each procedure gets its id in the repository from `vogon id TP <module>`, or
as the key of its item in the tracker or test manager. After development, each
test a procedure was generated from names it in a
`@pytest.mark.procedure("<id>")` marker. The skill opens a pull request and
adds a `test_procedures_written` entry to each requirement's `REQ-*.json`.

## Step 8: approve the procedures

The roles `tests.md` names approve the procedures, in the pull request or in
the tracker or test manager. `vogon:tests` tells each of them what waits for
their approval and where.
