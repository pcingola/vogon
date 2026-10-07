# Code, tests and documentation

Steps 11 and 12 of the [steps](index.md). `vogon:implement` continues from the
approved plan ([Planning](planning.md)). The rules are in
[Architecture](../architecture.md#code-from-requirements).

## Step 11: write the code, tests and documentation

The main agent follows the plan. For each part it starts a sub-agent that
writes that part's code, tests and documentation, given the plan, the
requirements and the code it touches. Independent parts run in parallel. Each
test names the requirements it verifies in its `req` marker. Where the host
project's `conftest.py` lacks the lines that copy the markers into the JUnit
XML, the skill adds them.

Three evaluators check each part: the test checklist, the code checklist
([Architecture](../architecture.md#loops)), and Claude Code's code review. The
main agent also reads each sub-agent's output against the plan and sends back
work that leaves its part, does less than its part, or changes what the plan
does not name.

The developer may steer the work or leave it to run. A developer who steers
can stop it, ask to review each part before the next starts, or give an
instruction about a part. The main agent passes the instruction to the
sub-agents it concerns and logs it. Without instructions, the skill runs the
plan to the end.

All tests are written and pass before the pull request is opened. Where and
how the test suite runs is the project's choice, as `tests.md` states. The
pull request description names the requirements implemented and states the
loops run, their rounds and the findings left open. The skill adds an
`implemented` entry to each requirement's `REQ-*.json`.

## Step 12: approve the pull request

A code reviewer approves the pull request on the repository host, as the
project's own practice requires. VOGON gives no approval.
