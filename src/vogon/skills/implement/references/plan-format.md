# Plan format

The format of a plan for code, `vogon/plans/plan_<slug>.md`. The slug names
the requirements or the feature, such as `plan_REQ-PRN-12.md`. The plan is a
checklist of the parts to build and the tests that verify each part. It refers
to the requirements and the code by id and path, and does not restate them. The
developers approve it before any code is written.

## Sections, in this order

Omit a section only when nothing in it applies.

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
   the form "X, because Y". Name the rejected alternative when the rejection is
   not evident.
6. **Parts.** The checklist. One entry per part, each a unit one writing
   sub-agent builds. Each entry states:
   - what the part builds, in one or two sentences;
   - the files it creates or changes, with line numbers where they help;
   - the acceptance criteria it covers, by requirement id and position, such
     as `REQ-PRN-12` criterion 2;
   - the tests that verify it: one line per test, naming the acceptance
     criterion it checks and the test file, and the test procedure where
     `tests.md` keeps procedures;
   - the documentation it changes, with a one-line note on what changes;
   - the parts it depends on, by number. A part with no dependency on another
     part can be built in parallel with it.
7. **Verification.** How the project runs its test suite, as `tests.md` topic
   "Running the test suite" states, and the manual checks a person makes where a part has
   a visible surface that no test covers.

## Rules

- Every acceptance criterion of every requirement in the plan is covered by at
  least one test in some part. A part that covers no acceptance criterion
  exists only to support another part, and says which.
- Nothing in the plan goes beyond the requirements. A part that builds what no
  requirement asks for is removed.
- Tests follow the host project's existing test conventions: framework, layout
  and style.
- Each test names its requirements in `@pytest.mark.req("<id>", ...)` and,
  where procedures exist, its procedures in
  `@pytest.mark.procedure("<id>", ...)`. Where the host project lacks a change
  that `${CLAUDE_PLUGIN_ROOT}/skills/implement/references/conftest.md` states,
  the plan has a part that makes it as that file states.
- Requirement ids are not written in implementation code. Commits name them.
- The plan describes design, not code. A code block of a few lines is allowed
  only where prose cannot state an interface or a data structure.
- The plan is finished or it is not. It holds no TBD, no open question and no
  choice left to the reader ("either X or Y"). A question the code, the
  records or the requirements answer is answered in the plan. A question only
  a developer can answer is asked before the plan is presented for approval,
  and the answer is written into Decisions.
