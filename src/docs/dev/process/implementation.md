# Code, tests and documentation

Step 9 of the [steps](index.md). `vogon:implement` continues from the approved
plan ([Planning](planning.md)). The design is in
[Architecture](../architecture.md#code-from-requirements) and the steps in
`src/vogon/skills/implement/SKILL.md`.

One writing sub-agent per part of the plan writes its code, tests and
documentation. Its evaluators check it: one applies
`src/vogon/skills/implement/references/test-checklist.md`, the other runs
Claude Code's code review on the part's diff and then applies
`src/vogon/skills/implement/references/code-checklist.md`. The developer may
steer the work or leave it to run.

The skill runs the test suite as `tests.md` states. A failure is fixed in the
code; a test is never deleted, skipped or weakened to make the run pass. All
tests pass before the pull request is opened. The skill opens the pull
request and then appends an `implemented` entry to each requirement's
`REQ-*.json`; the entry counts once the pull request is merged. A person
approves the pull request on the repository host.
