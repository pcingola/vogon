# Architecture

## Skills, and a little code

VOGON is a Claude Code plugin holding a skill, subagents, hooks and the
scripts they call, installed into a host project (`REQ-GEN-1`, `REQ-GEN-4`).
The skill holds the rules, workflows and guidelines for developing software
under GxP: what a requirement looks like, how a transcript becomes records
(`REQ-GEN-6`), how a test case is drafted (`REQ-GEN-7`), what has to be true
before a change is registered in the tracker. It is the system.

The code is small and exists to serve the skill. It is scripts the skill
calls where the answer has to be the same on every run: minting the next id
(`REQ-REC-7`), validating a record against the schema (`REQ-REC-1`), resolving
links (`REQ-REC-2`, `REQ-REC-4`), collecting test markers (`REQ-TRC-1`),
working out what the tracker should hold (`REQ-TRK-3`). An agent can do any of
those and will do most of them correctly most of the time, which is not the
standard a validation record is held to.

Claude Code does the work, including any subagents the skill starts. The
Python code calls no language model API and reaches no network, so the scripts
can disagree with a draft because they did not produce it (`DEC-005`,
`REQ-GEN-3`, `FACT-005`). Claude Code reads the external systems through MCP
and writes what it read as JSON under `.vogon/`, and the scripts compare that
with the records.

VOGON produces the records, the plan, the tests, the code, and the documents
a validation package holds: the risk assessment, the test specification, the
design specification and the test report. Each is produced complete, and each
is a draft until a named person approves it (`REQ-GEN-2`).
VOGON never performs the approval (`CON-001`, `REQ-TRK-1`).

Change control, the assessment a board approves before a live validated system
is changed, is not in this version (`DEC-017`). The pipeline below covers
building the system and changing it; what a project does with a change once it
is live stays in that project's own procedure.

## One skill, with a reference file per step

The plugin holds one skill, `vogon` (`DEC-021`). Its `SKILL.md` holds what
every step shares: the pipeline, the actions VOGON never takes, the rules for
subagents, the rule that a role is reached only through the server the
configuration names for it, and a table from each step to its reference file.
`SKILL.md` is at most 150 lines. Each reference file is at most 120 lines and
is a checklist of rules the step's output meets or fails.

| Reference file | Steps |
| --- | --- |
| `config.md` | 1 |
| `sources.md` | 2 |
| `records.md` | 3 |
| `review.md` | 4 |
| `risk.md` | 4 |
| `documents.md` | 4, 10, 15 |
| `tracker.md` | 5, 10, 15 |
| `plan.md` | 7 |
| `tests.md` | 8, 9, 10 |
| `code.md` | 12, 13, 14 |
| `evidence.md` | 16 |
| `writing.md` | Every step that writes prose |

## The pipeline

VOGON covers the development cycle from the material a project starts with to
the evidence it ends with. Each step is done by the `vogon` skill following a
reference file, by a script, or by a person giving an approval.

| # | Step | Produces | Done by |
| --- | --- | --- | --- |
| 1 | Install and configure | `vogon/`, `modules.yaml`, `vogon.yaml` naming the server for each role, the approval roles and their holders (`REQ-CLI-5`, `REQ-CLI-8`) | `/plugin install vogon@vogon --scope project`, then `vogon` with `config.md`, which runs script `vogon init` |
| 2 | File the source material | Transcripts and documents in `vogon/sources/` (`REQ-GEN-6`, `REQ-REC-9`) | `vogon` with `sources.md` |
| 3 | Draft the records | Requirements, facts, constraints and decisions in `vogon/` (`DEC-007`, `REQ-REC-1`) | `vogon` with `records.md` |
| 4 | Review and accept | The record set checked for records that contradict or duplicate each other, the risk assessment in `vogon/documents/` giving a risk level and its reasoning per requirement, and records moved off `proposed` (`REQ-GEN-8`, `REQ-GEN-2`) | `vogon` with `review.md`, `risk.md` and `documents.md`, then a person |
| 5 | Register the requirements | Requirement issues in the tracker (`REQ-TRK-5`, `REQ-TRK-3`) | `vogon` with `tracker.md` |
| 6 | Approve the requirements | Requirement issues in an approved state (`REQ-TRK-8`, `REQ-TRK-9`) | The Product Owner, in the tracker |
| 7 | Plan the change | `vogon/plans/plan_<slug>.md`: what will be built and how it will be tested, naming the records it implements and the interface the tests call (`DEC-014`, `REQ-GEN-10`) | `vogon` with `plan.md` |
| 8 | Write the test cases | Test functions carrying markers (`REQ-TRC-1`, `REQ-TRC-8`) | `vogon` with `tests.md`, in subagent `vogon-test-writer` |
| 9 | Check the test cases against the requirements | For each requirement, the acceptance clauses no test exercises, the expected values that differ from the acceptance block, and the assertions the requirement does not support (`DEC-019`, `REQ-GEN-11`) | `vogon` with `tests.md`, in subagent `vogon-test-checker` |
| 10 | Register the test cases, draft the test specification | Test issues in the test manager linked to the requirement issues (`REQ-TRC-5`), and the test specification in `vogon/documents/` | `vogon` with `tracker.md`, `tests.md` and `documents.md` |
| 11 | Approve the test cases | Test issues in an approved state, and the test specification approved (`DEC-023`, `DEC-024`) | The Test Lead: the test issues in the test manager, the test specification in the document system |
| 12 | Write the code | Source, and a commit naming the records it implements (`REQ-TRC-9`) | `vogon` with `code.md`, following the plan |
| 13 | Run the tests and make them pass | Outcomes keyed to markers, recording the build (`REQ-TRC-1`, `REQ-TRC-4`) | `vogon` with `code.md`, and script `vogon trace` |
| 14 | Review the change and merge it | An approving review by an engineer other than the author (`REQ-CLI-7`) | `vogon` with `code.md`, then a code reviewer on the repository host |
| 15 | Register the results, draft the documents | Results in the test manager recording the build (`REQ-TRC-6`), and the design specification and test report in `vogon/documents/` | `vogon` with `tracker.md` and `documents.md` |
| 16 | File the evidence | The test manager's traceability report and results for the released build, in the document system (`REQ-TRK-10`) | `vogon` with `evidence.md`, and script `vogon evidence` |
| 17 | Sign off | The validation package, signed | The sign-off roles, in the document system |

The roles in the last column are the default assignment. Which role gives each
approval, and who holds each role, is configuration (`DEC-018`); see
[Roles and approvals](#roles-and-approvals).

The pipeline is followed where the project allows. A step that was skipped is
done afterwards, with the real dates, and the order the steps were actually
done in is reported: an approval given after what it governs was used appears
in the report (`REQ-TRK-11`). A failing check still fails, whatever order the
steps ran in.

Making a failing test pass has one direction it may not take. Expected values
come from the requirement and never from a run of the code, so a test is made
to pass by changing the code and not by moving the expected value to whatever
the code produced (`DEC-024`, `REQ-GEN-7`).

## Writer and checker

A step that produces a record, a plan or a document runs a writer subagent
and a checker subagent (`DEC-022`). `vogon-writer` drafts the output. `vogon-checker` checks it
against the checklist in the step's reference file and runs `vogon check` on
it, and its findings go back to the writer. The loop ends when the checker
reports nothing. After five rounds, or when a finding the writer has already
been given is reported again, the remaining findings go to the person.

The test cases have their own pair. `vogon-test-writer` writes them at step 8
and `vogon-test-checker` compares them with the requirements at step 9. Both
read only `vogon/` and the test paths, so the expected values the first writes
and the comparison the second makes can only come from the requirement, and
the checker did not write the tests it checks (`DEC-019`). Neither has `Bash`.
The `test-read` hook enforces the read restriction: for a subagent whose
`agent_type` is one of the two, with or without the `vogon:` prefix, it allows
a read of a path under `vogon/` or a test path and refuses every other read.
It lists the paths allowed rather than the directories refused, because a list
of source directories misses code kept anywhere else. Since the test agents
cannot read the code, a plan names the interface the tests call.

## Hooks

Hooks cover what has to happen without anyone asking for it. Each entry in
`hooks/hooks.json` calls `${CLAUDE_PLUGIN_ROOT}/scripts/vogon hook <name>`.

| Hook | Runs | Does |
| --- | --- | --- |
| `session-start` | On `SessionStart` | Prints the configured server for each role, the approval roles and their holders. With no `vogon.yaml`, prints an instruction to run setup (`REQ-CLI-10`) |
| `post-write` | After a write | After a write under `vogon/`, runs `vogon check` on the file and returns the findings. After a write of `vogon.yaml`, returns the configuration |
| `commit` | Before a `git commit` | Refuses a message naming an id that resolves to no record |
| `transition` | Before a call to any `mcp__` tool | Refuses a transition into an approved state, and every call to a server whose transition setup is incomplete |
| `test-read` | Before a file tool, shell or MCP call | Refuses a test agent's read or write outside `vogon/` and the test paths |

The `commit` hook allows a message that names no record. `REQ-TRC-9` asks for a
record id per change, not per commit, and `vogon change` checks the change as
a whole: its commit messages and its pull request description.

The `transition` hook is what turns `CON-001` from an instruction into
something the agent cannot do by accident (`REQ-TRK-1`). A transition call
carries a transition id, not a target state, so the hook works from the
configuration. For a call to a tool listed in the role's `transition_tools`,
it reads the transition id from the argument named there, looks the id up in
`transitions`, and refuses the call when the target state is in
`approved_states` or the id is not in the table. For a role whose server is
configured and whose `transition_tools`, `transitions` or `approved_states`
is missing, it refuses every call to that server, so an incomplete setup
cannot approve anything. A call to a server not named in `systems` passes.
When `vogon.yaml` cannot be parsed, has a top-level key VOGON does not know,
or holds an error under `systems`, the hook cannot tell a transition from any
other call, and it refuses every MCP call until the file is corrected. An
error elsewhere in the file, such as in `approvals`, does not.

The hook finds a call's server in the tool name. Claude Code names an MCP tool
`mcp__<server>__<tool>`, and a tool of a server bundled in a plugin
`mcp__plugin_<plugin>_<server>__<tool>`, with every character outside
letters, digits, `_` and `-` replaced by `_`. The hook applies the same
replacement to `server` in `vogon.yaml`, and a call belongs to that server
when its tool name is `mcp__<server>__<tool>` or
`mcp__plugin_<plugin>_<server>__<tool>` for any plugin. So `server` holds the
name Claude Code lists for the server, the scoped name
`plugin:<plugin>:<server>`, or a bundled server's own key. A tool in
`transition_tools` is named by the part after that prefix, or by its full
name.

The `test-read` hook reads the path arguments of `Read`, `Grep`, `Glob`,
`LS`, `NotebookRead`, `NotebookEdit`, `Edit`, `MultiEdit` and `Write`, after
resolving symbolic links. A `Grep` or `Glob` with no `path` searches the
project root and is refused, as is a glob pattern containing `..`. It refuses
a test agent's `Bash`, `PowerShell` and MCP calls, because the paths they read
cannot be checked.

A hook exits with status zero in every case, so it cannot stop the session.
Given input it cannot read, or failing itself, a hook prints nothing, except
`transition` and `test-read`, which refuse the call.

The agent receives the configuration from the hooks, which Claude Code runs
without the agent asking for them. Claude Code adds a `SessionStart` hook's
standard output to the context, and `SessionStart` fires on `startup`,
`resume`, `clear`, `compact` and `fork`. After `vogon.yaml` is written,
`post-write` returns the new values as `additionalContext`. The plugin is
enabled per project, so a session in which the hooks run is in a project that
uses VOGON. When that project has no `vogon.yaml`, `session-start` prints an
instruction to run setup, step 1 with `config.md`, and names the missing file.
It finds the project from `CLAUDE_PROJECT_DIR`, which Claude Code sets for
every hook to the directory the session was started in. Every other hook
prints nothing until `vogon.yaml` exists. Subagents do not receive the values, because only the main agent
reaches external systems.

## Roles and approvals

Steps 4, 6, 11, 14 and 17 include approvals, and a person gives each one in
the system that holds what is approved. VOGON gives none of them (`CON-001`).
Records, instructions and generated documents name the role that approves,
never a person. `vogon.yaml` in the host project says which roles give each
approval, in which system, and who holds each role (`DEC-018`, `REQ-CLI-5`):

```yaml
approvals:
  requirements: {roles: [product_owner], system: tracker}
  risk_assessment: {roles: [system_owner, it_quality_manager], system: document_system}
  test_cases: {roles: [test_lead], system: test_manager}
  test_specification: {roles: [test_lead], system: document_system}
  change: {roles: [engineer], system: repository_host}
  release: {roles: [system_owner, it_quality_manager], system: document_system}
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
  engineer: [alice@example.com, bob@example.com, carol@example.com]
  system_owner: [dave@example.com]
  it_quality_manager: []
```

The assignment above is the default `vogon init` writes. Role holders are
emails. A role may be listed with no holder until the project's procedure
names one, and VOGON reports every approval whose role has none
(`REQ-CLI-6`). Once an approval has been given, VOGON reads who gave it and
reports an approver who does not hold the configured role (`REQ-TRK-9`) or who
is an author of what was approved (`CON-002`, `REQ-TRK-8`). A record's authors
are the author emails of the commits that changed its file up to the time of
the approval. The approver is the email the tracker reports for the
transition.

The review before a merge is enforced by the repository host, whose rules for
the default branch can require an approving review from someone other than
the author. VOGON checks that those rules are in place and reports where they
are not (`REQ-CLI-7`).

Step 16 moves the evidence the test manager produces into the document system
without changing it: the traceability report and the results for the build
being released, each recording that build (`REQ-TRK-10`). VOGON produces
neither report (`REQ-TRC-7`), and the people holding the release roles sign
the package in the document system.

## Documents

A document VOGON drafts, such as the risk assessment, the test specification,
the design specification or the test report, is written to `vogon/documents/`
in the host project (`DEC-023`). From there it is filed into the document
system and approved there, by the roles of its approval in `vogon.yaml`:
`risk_assessment` for the risk assessment, `test_specification` for the test
specification, and `release` for the design specification and the test
report. `vogon/out/` holds only generated output, which a
script can overwrite at any time, so a drafted document never goes there.

The risk assessment is `vogon/documents/risk_assessment.md`. It holds one
table whose first two columns are `Requirement` and `Risk`, with one row per
requirement and a `gxp_risk` value as the level; further columns hold the
reasoning. Once it is approved, Claude Code reads the approved version back
from the document system to `.vogon/risk_assessment.md`, and `vogon check`
reports a requirement whose `gxp_risk` is not `none` and whose level is absent
from that table or differs from it (`REQ-GEN-9`).

## How VOGON is installed

The VOGON repository is a Claude Code plugin marketplace.
`.claude-plugin/marketplace.json` at its root lists one plugin, `vogon`, whose
source is `src/vogon/`. A developer installs it from inside Claude Code,
opened in the host project, at project scope (`REQ-CLI-9`):

```
/plugin marketplace add pcingola/vogon --scope project
/plugin install vogon@vogon --scope project
```

Project scope writes the marketplace and the plugin into the host project's
committed `.claude/settings.json`, and nothing into the user's settings, so
VOGON is enabled in that project only and every developer of the project gets
it:

```json
{
  "extraKnownMarketplaces": {
    "vogon": {"source": {"source": "github", "repo": "pcingola/vogon"}}
  },
  "enabledPlugins": {"vogon@vogon": true}
}
```

Both commands default to user scope, which would enable VOGON in every project
the user opens; the documentation never gives them without `--scope project`.

The plugin is laid out as Claude Code expects:

```
src/vogon/
├── .claude-plugin/plugin.json   name, version, description
├── skills/vogon/                SKILL.md and references/
├── agents/                      vogon-writer, vogon-checker, vogon-test-writer, vogon-test-checker
├── hooks/hooks.json             hook entries, each calling a script
└── scripts/                     the Python scripts
    └── pytest_plugin/           vogon_pytest.py only, loaded into the host's test run
```

The version is in `plugin.json`, and each release of VOGON is tagged
`v<version>` from it. There is no Python distribution. The scripts run with
`uv run --script`, and each declares its own dependencies inline (PEP 723), so
a host project needs Claude Code, `uv` and git installed and nothing else. An
upgrade is a plugin update.

Nothing from the plugin is copied into the host project. The host project's
repository does not hold the skill text, and nothing compares an installed
copy with the plugin (`DEC-020`).

## Setup

Setup starts when the person asks Claude Code to set up VOGON, or when the
`session-start` hook reports that `vogon.yaml` is missing (`REQ-CLI-10`), and
the skill follows `config.md`. Claude Code runs `vogon init`, which creates `vogon/`,
`vogon/modules.yaml` and `vogon.yaml`, adds `.vogon/` to `.gitignore`, and
registers the `req` marker in the host project's pytest configuration. It
writes the values that need no question: the paths (`vogon`, `tests`),
`test_command` (`python -m pytest`) and the default approval assignment. It
writes nothing under `.claude/` and no CI file.

Claude Code then works out the rest from the connected MCP servers and asks
only where it cannot know (`REQ-CLI-8`):

- `systems`. For each role (`tracker`, `test_manager`, `repository_host`,
  `document_system`), the connected server that provides the role's
  operations. With one candidate, that server is used. With several, the
  person chooses, because only the person knows which one company policy
  requires. With none, the role stays absent, and every step and check that
  needs it reports the role as not configured.
- For the tracker and the test manager, Claude Code reads the workflow
  through the chosen server and proposes as approved the states whose names
  say approval or signature. It finds the tools that perform a transition
  and, from each tool's input schema, the argument that holds the transition
  id. Setup writes that role's `server`, `transition_tools`, `transitions`
  and `approved_states` in one write.
- Role holders are not asked. A role may have none until the procedure names
  one, and `vogon check` reports it (`REQ-CLI-6`).

Claude Code shows everything it filled in as one list, and the person
confirms or corrects it in one answer. Claude Code then commits `vogon.yaml`:

```yaml
systems:
  tracker:
    server: acme-tracker
    transition_tools: {transition_issue: transition_id}
    transitions: {"11": In Review, "21": Approved, "31": Rejected}
    approved_states: [Approved]
  test_manager:
    server: acme-tests
    transition_tools: {transition_test: transition}
    transitions: {"5": Ready for Review, "6": Approved}
    approved_states: [Approved]
  repository_host: {server: github}
  document_system: {server: acme-documents}
```

`transitions` is kept in the committed file and not under `.vogon/`, so every
clone has it. A changed workflow means running setup again for that role.
Setup first removes that role's entry, so the `transition` hook does not
refuse the calls that read the workflow.

At setup Claude Code also writes each configured server's tool list to
`.vogon/servers.json`, with the tool it found for each operation VOGON needs.
The operations are a list in `snapshots.py` (`OPERATIONS`), and `vogon check`
reports each operation a configured server lacks, with the role and the server
(`REQ-CLI-4`): an operation with no tool, or mapped to a tool the server does
not list. It also reads the repository host's rules for the default branch
into `.vogon/branch_rules.json`, and `vogon check` reports a default branch
that requires no approving review or counts the author's own approval
(`REQ-CLI-7`).

## Configuration and findings

The scripts and the hooks read `vogon.yaml` themselves, through `config.py`,
every time they run, so what they check never depends on what the agent was
told. A setting absent from the file takes its default: the paths,
`test_command` and the approval assignment have one (`REQ-CLI-3`,
`REQ-CLI-5`). `systems`, `transitions` and `approved_states` have none
(`REQ-CLI-8`).

A finding is a failure or a notice. Only a failure sets a non-zero exit status
(`REQ-CLI-1`). An approval whose role has no holder (`REQ-CLI-6`), a check
skipped because a system is unreachable (`REQ-CLI-2`) and a role that is not
configured are notices, so a fresh setup and a project with no external
systems pass `vogon check`.

## Where things sit in a host project

The host project is a project VOGON is installed into, as against the VOGON
project, which is this repository.
[Vocabulary](vocabulary.md#the-two-projects) defines both.

```
<host-project>/
├── .claude/
│   └── settings.json     names the VOGON marketplace and enables the plugin, written by the install commands (`REQ-CLI-9`)
├── vogon/
│   ├── modules.yaml      the module names the host project uses
│   ├── requirements/<module>/REQ-<MODULE>-NNN.md
│   ├── facts/FACT-NNN.md
│   ├── constraints/CON-NNN.md
│   ├── decisions/DEC-NNN.md
│   ├── sources/          held copies of every cited document, dated and flat
│   ├── plans/            what will be built, before it is. done/ holds the spent ones
│   ├── documents/        drafted documents of the validation package
│   └── out/              generated. Never hand-edited
├── .vogon/               tool state, gitignored: tracker.json, servers.json, branch_rules.json,
│                         risk_assessment.md, results.json, push_plan.json,
│                         push_created.json, evidence/<build>/
├── tests/                test functions carrying requirement markers
└── vogon.yaml            configuration
```

All of it is plain text in git (`DEC-001`), except `.vogon/`, which is
gitignored. There is no database. Configuration sits in `vogon.yaml` at the
host project's root, in the format the records already use, and the layout
above is the default, so a host project that accepts the convention changes
no path (`REQ-CLI-3`).

`vogon/` is named for the tool because VOGON creates it, defines the format of
everything in it, mints the ids and validates it, which is what a directory a
tool owns in someone else's repository is named for. It is visible rather than
hidden because the records are reviewed in pull requests and read by people who
will never run the tool. The skill, subagents and hooks are loaded from the
installed plugin and are not in the host project.

## Two stores

The specification lives twice.

In the host project's git repository, as markdown records under `vogon/`. This
is where the text is written and edited, where a change is reviewed in a pull
request, and where history is kept. It is cheap to change and it is not
controlled.

In the tracker, and the test manager for tests, as issues under approval
(`CON-003`, `DEC-015`). This is where a named person approves a statement by
re-entering their credentials, and what an auditor is shown. It is expensive to
change and it is controlled. VOGON never performs the approval: an electronic
signature requires the signer to re-enter their own credentials (`FACT-001`),
so the transition stays a human action in the tracker (`CON-001`,
`REQ-TRK-1`).

In this version the markdown files are the source of truth. VOGON writes from
the repository to the tracker and reads the tracker's state back only to report
where the two have diverged: a record edited after its issue was approved
(`REQ-TRK-2`), a test marker naming a requirement that no longer exists
(`REQ-TRC-3`), an approval applied by the record's own author (`CON-002`,
`REQ-TRK-8`), an approval given after what it governs was used
(`REQ-TRK-11`), a result imported from a build other than the one released
(`FACT-004`, `REQ-TRC-6`).

Claude Code reads the tracker and the test manager through MCP and saves what
it read to `.vogon/tracker.json`: per role, the server read and each issue with
its key, summary, description, status, links, every status transition with
the email of the person who made it and the time, and, for a test issue, the
results imported against it with their build. The scripts compare that file
with the records. The approval of an issue is the last transition into an
approved state, and its approver is the email on that transition. The formats
of every file under `.vogon/` are in the docstring of `snapshots.py`.

A check that needs one of these files and does not find it reports that it was
skipped, as a notice (`REQ-CLI-2`), when the role it reads is configured.

A later version may make the tracker the source of truth instead, with the
markdown dropped or kept as a cache of it. That reverses the direction, and
nothing is built now to anticipate it.

## Writing to the tracker

An issue's summary starts with its record id, and a test issue's summary
starts with the test's node id. The tracker's search finds an issue that way
without a custom field, which would need a tracker administrator to create,
and that id is what keys every write (`REQ-TRK-3`, `REQ-TRC-5`). The last line
of each issue description holds the record's content hash, so the description
at the time of approval carries the hash of the text that was approved
(`REQ-TRK-2`). A record's hash covers its frontmatter without `tracked_as`, and
its body, so recording the key does not change it. A test's hash covers the
test function's source with its decorators.

`vogon push --plan` prints the creates and the field changes that follow from
the records and `.vogon/tracker.json`. It plans no write for a record whose
status is `proposed` (`REQ-GEN-2`), and its output is the set Claude Code shows
the person and then applies (`REQ-TRK-4`). After applying it, Claude Code saves
the keys the tracker created to a file, and `vogon push --record FILE` writes
each key into its record's `tracked_as` (`REQ-TRK-5`), so the edit to the
record is made by tested code.

The plan is printed one line per write and saved to `.vogon/push_plan.json`,
which Claude Code applies. It creates issues only for `accepted` records, and
writes nothing to an issue in an approved state: a record or test changed
since that approval is reported instead (`REQ-TRK-2`). An issue that exists
for a record whose `tracked_as` does not name it yet is planned as a `track`
entry, which `vogon push --record` writes like a created key. A marked test
gets one test issue once a requirement it names has an issue, linked to each
such requirement issue (`REQ-TRC-5`). The results `vogon trace` saved are
planned as imports against the test issues, once per build, and results with
no build are refused (`REQ-TRC-6`). `commands/push.py` has the plan format.

## Where the link between a test and a requirement is written

A requirement is verified by a test, and that link is written on the test: a
marker on the test function names the requirement ids it verifies (`DEC-006`,
`REQ-TRC-1`). Whoever changes a test is looking at the test, so they change the
marker in the same edit. The same link kept as a list of tests inside the
requirement file is edited by someone else, later, or not at all, so VOGON does
not use one.

The marker is `@pytest.mark.req("REQ-TRK-2")`, with one or more ids as
arguments. The marker checks read the test files with Python's `ast` module
and do not import or run them. `vogon trace` runs the configured
`test_command` with `-p vogon_pytest` and the plugin's
`scripts/pytest_plugin/` on `PYTHONPATH`. That directory holds
`vogon_pytest.py` and nothing else, because a module on `PYTHONPATH` takes
precedence over an installed module of the same name, and the other script
modules, such as `config` and `records`, would replace the host project's own.
`vogon_pytest.py` uses only the standard library and pytest,
because it runs in the host project's environment. `uv run --script` puts the
scripts' own environment first on `PATH` and in `VIRTUAL_ENV`; `vogon trace`
removes it from both before starting the test command, or `python` in
`test_command` would be the scripts' interpreter, which has no pytest.
`vogon init` registers the
`req` marker in the host project's pytest configuration, so a run without the
plugin, as in CI, does not fail under `--strict-markers`.

`vogon trace` records the output of `git rev-parse HEAD` as the build. With
uncommitted changes in the working tree it records no build, and results with
no build are never imported, because the revision under test could not be
identified (`REQ-TRC-6`).

Requirement ids are not written into the implementation source as comments.
Nothing checks a comment, so it stays behind when the code it described moves
or changes.

A commit message is short and names the records the change implements
(`REQ-TRC-9`). That is a different link from the marker: the marker says what
verifies a requirement, the commit says what built it.

The test manager produces the coverage report and the traceability matrix,
and VOGON produces neither (`DEC-003`, `FACT-002`, `REQ-TRC-7`). What VOGON
does is keep the link the test manager reports from: the test issue exists,
points at the right requirement issue, and can be matched to the test that ran
(`REQ-TRC-5`), and the results are imported against those issues
(`REQ-TRC-6`).

The test manager can only report on what it holds, so a requirement that was
never created as an issue does not appear in its report at all. The checks
that catch that run locally, before anything is pushed: a marker naming an id
that does not exist (`REQ-TRC-2`), a marker on a withdrawn requirement
(`REQ-TRC-3`), a requirement verified by test that no marker names
(`REQ-TRC-4`). They exit non-zero, so a CI run that includes them fails. They
are not evidence.

A marker shows that a test names a requirement, and says nothing about what
the test asserts. Whether the tests exercise what the requirement states is
checked at step 9, for every requirement verified by test whatever its risk
level: each clause of the acceptance block has a test, and each expected value
matches the block (`DEC-019`, `REQ-GEN-11`). The comparison is between the
requirement and the tests. Code coverage, which measures which lines of the
implementation ran, is not used for it.

## Evidence

`vogon evidence <build>` compares the test manager's export for a build, which
Claude Code saves under `.vogon/evidence/<build>/export/`, with the copies
Claude Code reads back from the document system after filing them, which it
saves under `.vogon/evidence/<build>/filed/` with the same file names. Each
copy is byte-identical to the export, each names the build in its file name or
its content, and none is the export of another build under
`.vogon/evidence/`, or the difference is reported (`REQ-TRK-10`).

## Continuous integration in a host project

The host project's CI checks out the VOGON repository at the tag `v<version>`
of the installed plugin and runs `uv run --script src/vogon/scripts/vogon
check`, then `vogon change` with the base branch and the pull request
description. The host project is checked out with its full history
(`fetch-depth: 0`), because `REQ-REC-10` and `vogon change` read `git log`.
`vogon init` does not write the CI file; the job is described in the
installation guide.

## Reaching the external systems

The tracker, the test manager, the repository host and the document system are
reached through the MCP servers the company provides. A regulated company
mandates both the product and the path to it, and the server is often its own
rather than the vendor's. The skill calls that server's tools.

Every external system is named by the role it fills, and the product filling
each role is configuration (`DEC-025`). The server for a role has no default:
it is set during setup from the servers connected to Claude Code, and the
person chooses where several could fill the role, because a guessed server
would send records to the wrong system. A role is reached only through the
server the configuration names for it (`REQ-CLI-8`). For each role VOGON
states the operations it needs from it, and a configured server that does not
provide one of them is reported at setup rather than at first use
(`REQ-CLI-4`).

No script contacts an external system or a language model. Claude Code reaches
the external systems through MCP and hands the data to a script.

## Modules

A module names a part of the system a record belongs to, and appears in the
record's id. Each host project declares its own names in `vogon/modules.yaml`;
VOGON enforces only the shape of the name
(`DEC-016`, `REQ-REC-13`, `REQ-REC-14`). [Records](records.md) has the id
format.

The VOGON project's own modules, as declared in its `vogon/modules.yaml`:

| Module | Covers |
| --- | --- |
| `REC` | The record schema, id grammar, validation and indexes |
| `TRC` | Test markers, the link to the test manager, result import |
| `TRK` | Reading and writing tracker and test manager issues, filing evidence in the document system, and reporting divergence |
| `GEN` | The instructions a coding agent follows to draft records, and the checks on what it produces |
| `CLI` | The scripts and configuration, including the approval roles |

## Version 0.1 assumes one stack

The first version is written against one set of tools and does not abstract
over alternatives:

- Python, for the host project and for VOGON itself
- GitHub, as the repository host
- Jira, as the tracker
- Xray, as the test manager
- Claude Code, as the coding agent

This is a deliberate narrowing (`DEC-004`). The records and the generated
text name the role each product fills and never the product (`DEC-025`), so
the products above appear in configuration and in this section only.
Supporting a second tracker or a second test manager means an interface, and an
interface written before the second implementation exists is guesswork.

This version is built quickly, used, and then changed. Where a choice is
between the quick shape and the general one, it takes the quick shape.
