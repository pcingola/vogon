---
plan_source: vogon/sources/<yyyy-mm-dd>_<slug>.md   # the held plan's markdown copy; omitted where no plan is held
plan_version: <the version the plan states on itself>   # omitted where no plan is held
derived_on: <yyyy-mm-dd>
---

# Tests

<!-- Derived from the validation plan as ${CLAUDE_PLUGIN_ROOT}/references/process-files.md
states. Write each topic as statements. End each statement with the plan
section it rests on: (plan §<number> <heading>). Where the plan states nothing
on a topic, or no plan is held, write nothing and report the gap; the developer's answer is
recorded as: Not stated in the plan. Answered by <Name> <email> on
<yyyy-mm-dd>: <answer>. Delete these comments. -->

## Test procedures

<!-- Whether the project needs test procedures, what a test procedure is in this project, and where it is kept. Cite the plan section. -->

## Writing and approval of test procedures

<!-- Who writes test procedures and who approves them; whether they are written before the tests, from the requirement, or after, generated from the tests; when approval is required. Cite the plan section. -->

## Unit tests and formal tests

<!-- Which tests are unit tests and which are formal tests, where each kind is recorded, and who signs each off. Cite the plan section. -->

## Formal test environment

<!-- The environment in which formal tests run. Cite the plan section. -->

## Results tied to a commit and an environment

<!-- How a test result is tied to the commit tested and to the environment it ran in. Cite the plan section. -->

## Running the test suite

<!-- The command that runs the project's test suite and the place the project runs it, such as a developer's machine or a CI service, as the plan or the developer states. Cite the plan section. -->
