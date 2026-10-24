# Plan format

The format of a plan for code, `vogon/plans/plan_<slug>.md`. The slug names
the requirements or the feature, such as `plan_REQ-PRN-12.md`. The plan is a
checklist of the parts to build and the tests that verify each part. It refers
to the requirements and the code by id and path, and does not restate them.

## Sections, in this order

1. **Title** (H1). Names what is built.
2. **Summary.** One short paragraph for an engineer who has not seen the
   requirements discussion: what is missing or wrong in the code today, and
   what is true once the plan is implemented. It names the requirements by id
   and does not quote them.
3. **Requirements.** One line per requirement: its id and the path of its
   `REQ-*.md`. Nothing else from the requirement.
4. **References.** The code files, modules and documentation the parts touch,
   as paths without line numbers, and the records the plan rests on, such as a
   decision or a constraint, by id.
5. **Decisions.** One line per design choice the requirements leave open, in
   the form "X, because Y". Name the rejected alternative.
6. **Parts.** The checklist. One entry per part, each a unit one sub-agent
   builds. Each entry states:
   - what the part builds, in one or two sentences;
   - the files it creates or changes;
   - the acceptance criteria it covers, by requirement id and position, such
     as `REQ-PRN-12` criterion 2;
   - the tests that verify it: one line per test, naming the acceptance
     criterion it checks and the test file, and the test procedure where
     `tests.md` keeps procedures;
   - the documentation it changes, with a one-line note on what changes;
   - the parts it depends on, by number.
7. **Verification.** How the project runs its test suite, as `tests.md` topic
   "Running the test suite" states, and the manual checks a person makes
   where a part has a visible surface that no test covers.

## Rules

- Every acceptance criterion of every requirement in the plan is covered by at
  least one test in some part. A part that covers no acceptance criterion
  exists only to support another part, and says which.
- Nothing in the plan goes beyond the requirements. A part that builds what no
  requirement asks for is removed.
- Each test names its requirements and procedures in pytest markers
  (`${CLAUDE_PLUGIN_ROOT}/references/markers.md`). When the host project
  lacks a change that `markers.md` "Changes in the host project" states, the
  plan reports it and adds no part for it.
- The plan describes the design in prose. A code block of a few lines is allowed
  only where prose cannot state an interface or a data structure.
- The plan leaves no choice to the reader ("either X or Y").
