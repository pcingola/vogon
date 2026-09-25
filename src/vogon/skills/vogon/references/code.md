# Code (steps 12, 13 and 14)

Writing the code a plan describes, running the traced tests until they pass,
and taking the change to review. Each item below is a rule the change meets
or fails.

## Step 12: writing the code

- [ ] The code implements the plan in `vogon/plans/`. Work the plan does not
      describe is added to the plan first.
- [ ] The interface matches the plan's `## Interface` section: import paths,
      signatures, return types, errors and files. A needed change is made in
      the plan first, and the tests that call it go back to step 9.
- [ ] Requirement ids are not written into the implementation source, in
      comments or elsewhere. The marker on the test is the link.
- [ ] Test files are not changed at this step.
- [ ] Records and held documents are not changed at this step.
- [ ] Each commit message is short, says what the commit does, and names the
      ids of the records the change implements. Every id named resolves to a
      record.
- [ ] The change as a whole names at least one record id, in a commit message
      or the pull request description. A change that implements no
      requirement, such as a typo fix, names `NO-REQ` in its place, as
      `vogon/NO-REQ.md` describes.

## Step 13: running the tests

- [ ] The work is committed before `vogon trace` runs. With uncommitted
      changes it records no build, and results without a build are never
      imported.
- [ ] `vogon trace` is the run whose outcomes are reported. The build it
      records is `git rev-parse HEAD`.
- [ ] A failing test is made to pass by changing the code.
- [ ] An expected value in a test is never changed to match what the code
      produced. When the person holds that the expected value is wrong, the
      acceptance block is corrected and accepted again by a person, then the
      test is changed at step 8 and checked at step 9.
- [ ] No test is deleted, skipped, marked as an expected failure, or weakened
      to make a run pass.
- [ ] The person is given the outcome for each requirement: the tests that
      passed and failed, and the build.
- [ ] `vogon check` reports no error.

## Step 14: review and merge

- [ ] The pull request is opened through the server the configuration names
      for `repository_host`.
- [ ] Its description says what the change does, names the record ids it
      implements, and names the plan.
- [ ] `vogon change` is run with the base branch and the pull request
      description, and reports no error.
- [ ] The person is told that the change awaits review by an engineer other
      than its author, as the repository host's rules for the default branch
      require.
- [ ] After the merge, the plan is retired as `plan.md` states.
