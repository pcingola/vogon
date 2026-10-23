# Test procedures

Step 6 of the [steps](index.md). A developer runs `vogon:tests` to write the
[test procedures](../vocabulary.md) of approved requirements; other requirements are reported and left out. The steps are in
`src/vogon/skills/tests/SKILL.md`.

`tests.md` states whether the project needs test procedures, whether they are
written before development from the requirement or generated after it from
the tests, where they are kept (repository, tracker or test manager), the
formal test environment they run in, and who approves them. Every expected
result comes from the requirement and its sources, never from the code, a test
or a run of the code.

Procedures kept in the repository are `vogon/requirements/<module>/TP-*.md`
with ids from `vogon id TP <module>`; procedures kept in the tracker or test manager
take the item key as id. Generated procedures are named in each source test's
`procedure` marker. The skill opens a pull request, appends a
`test_procedures_written` entry to each `REQ-*.json`, and tells the roles
`tests.md` names what waits for their approval and where.
