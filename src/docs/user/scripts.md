# Scripts

`vogon` is the plugin's command-line program, `scripts/vogon` in the installed
plugin. The skill and the hooks call it; a person or a CI job can call it too.
It runs under `uv run --script`, which installs its one dependency, PyYAML, on
first use:

```sh
uv run --script /path/to/plugin/scripts/vogon check
```

The scripts call no language model and reach no network. What VOGON needs
from the tracker, the test manager, the repository host and the document
system, Claude Code reads through MCP and saves under `.vogon/` in the host
project, and the scripts compare those files with the records.

## Options every command takes

| Option | Meaning |
| --- | --- |
| `--root DIR` | The project root holding `vogon.yaml`. Default: the current directory. |
| `--format text\|json` | How findings are printed. Default: `text`. |

The options follow the command name: `vogon check --root host --format json`.
Every command reads `vogon.yaml` from the root each time it runs. With no
`vogon.yaml` the default layout applies: records in `vogon/`, tests in
`tests/`, test command `python -m pytest`.

`vogon --version` (or `-V`) prints the plugin version. `vogon` with no command
prints the help on standard error and exits 1.

## Findings and exit status

A command reports what it found as findings. A finding is an error or a
warning. An error is a condition a requirement forbids, including a setup that
leaves an approval impossible to give. A warning reports something that is not
an error, such as a check that was skipped because the file it reads is
absent.

The exit status is 1 when at least one finding is an error, and 0 otherwise,
so a run that reports only warnings exits 0 (`REQ-CLI-1`). An argument error
exits 2.

In text format each finding is one line on standard output: the severity in
capitals, the file and line, and the message.

```
ERROR: vogon/requirements/API/REQ-API-3.md:6: depends_on names REQ-API-9, for which no record file exists
ERROR: vogon.yaml: no holder for the role system_owner, which gives the risk_assessment and release approvals
WARNING: .vogon/servers.json: Server operation check skipped: .vogon/servers.json is absent; Claude Code writes it from what it reads through MCP
```

A location that does not apply is left out, as in `ERROR: message`. In JSON
format standard output is one object,
`{"findings": [{"severity", "message", "path", "line"}, ...]}`, with
`severity` `error` or `warning`.
A command's own output, described under each command below, is printed before
the findings.

## vogon check

Runs every check that needs no external system. It writes nothing.

```sh
vogon check
```

No arguments. It reads:

- `vogon.yaml`: invalid values and unknown keys are errors. So is each
  incomplete part of setup, one line per role: a role that an approval uses
  and that has no holder under `roles` (`REQ-CLI-6`), a system role that an
  approval is given in and that has no server under `systems`, and a
  configured tracker or test manager missing `approved_states` (`REQ-CLI-8`). Each line names the
  approvals that cannot be given. A role that no approval uses is not
  reported.
- The records directory: the frontmatter schema, ids and file names, links
  between records, `source` and `references` paths, modules against
  `modules.yaml`, acceptance blocks, approval claims, id reuse, the writing
  checks and the brand strings. [Records](../dev/records.md) and
  [Writing standard](../dev/writing.md) list what each enforces.
- `sources/` in the records directory: file names, that no held file changed
  after it was added, and the order of `source` lists
  ([Sources](../dev/sources.md)).
- The test files under the test paths, parsed with `ast` and never run: every
  id a `req` marker names resolves to a requirement, and every accepted
  requirement verified by test is named by a marker.
- The files Claude Code saved under `.vogon/`: `tracker.json`,
  `servers.json`, `branch_rules.json` and `risk_assessment.md`, compared with
  the records. It reports a record edited after approval, a `tracked_as` key
  naming no issue, a record approved by its own author, an approver who holds
  none of the roles for that approval, an approval given after the thing it
  governs was used, a server missing an operation VOGON needs, a default
  branch that allows a merge without an independent review, and a risk level
  that differs from the approved risk assessment. When one of these files is
  absent the check that reads it is skipped with a warning (`REQ-CLI-2`),
  and only when its role is configured.
- The git history, for the author of each record and for held documents.

## vogon id

Mints the next unused id of a record type and creates the record file named
for it.

```sh
vogon id requirement --module API --title "Reject an expired token"
```

| Argument | Meaning |
| --- | --- |
| `type` | `REQ`, `FACT`, `CON`, `DEC`, or `requirement`, `fact`, `constraint`, `decision`. |
| `--module`, `-m` | The module the id carries. It must be declared in `modules.yaml`. |
| `--title` | The record's title, written into the frontmatter. |

The number is the lowest that no record of that type and module holds, in the
working tree or anywhere in the git history, whatever that record's status
(`REQ-REC-7`). The file is created under the records directory with `id`,
`type`, `title` when given, `modules` when a module is given, and
`status: proposed`. It prints `<id> <path>`.

It fails on an unknown type, a module that is not uppercase letters and
digits, a module not declared in `modules.yaml`, or a file that already
exists.

## vogon index

Writes the index of every record to `out/index.md` in the records directory
(`REQ-REC-6`).

```sh
vogon index
```

No arguments. The index is a table of id, title, status and modules, one row
per record file, sorted by type, module and number. It carries no timestamp,
so a second run with no change to the records leaves the file unchanged. It
prints the path written. A record file that cannot be parsed is left out of
the index and reported as an error.

## vogon trace

Runs the tests and records the outcome of each test carrying a `req` marker,
with the build it ran on (`REQ-TRC-1`, `REQ-TRC-6`).

```sh
vogon trace
vogon trace -- tests/test_api.py -k token
```

| Argument | Meaning |
| --- | --- |
| `test_args` | Further arguments for the test command, after `--`. |

It runs `test_command` from `vogon.yaml` with `-p vogon_pytest` and the test
arguments, in the project root. `vogon_pytest` is a pytest plugin that uses
only the standard library and pytest, because it runs in the host project's
own environment. `vogon trace` puts the plugin's `scripts/pytest_plugin/` on
`PYTHONPATH` for the run; that directory holds `vogon_pytest.py` alone, so no
other VOGON module can replace a module the host project's tests import. The
environment `uv` made for the scripts is removed from `PATH` and `VIRTUAL_ENV`
before the run, so `python` in `test_command` is the one the project's own
environment provides. The test command's output goes to standard error.

The results go to `.vogon/results.json`: for each marked test, its node id,
the requirement ids its markers name and its outcome, one of `passed`,
`failed`, `skipped`, `error`, `xfailed`, `xpassed`.

The build is the output of `git rev-parse HEAD`. It is recorded only when the
working tree has no uncommitted change, tracked or untracked, before the run,
and neither the commit nor a tracked file changed during it. Otherwise the
results are written with `build` null and a warning gives the reason. Results
with no build are never imported into the test manager.

It prints `<results path> build <commit>`, or `build none`. It fails when the
test command cannot be run, writes no results file, or exits non-zero.

## vogon change

Checks that a change names the records it implements (`REQ-TRC-9`).

```sh
vogon change origin/main --description-file pr.md
```

| Argument | Meaning |
| --- | --- |
| `base` | The branch the change merges into, such as `origin/main`. |
| `--description` | The pull request description. |
| `--description-file` | A file holding the pull request description; `-` reads standard input. |

`--description` and `--description-file` exclude each other; with neither, the
description is empty. The change is the commits of `git log <base>..HEAD` and
the description. It fails when none of them names a record id or `FAKE-REQ`,
and for each named id that resolves to no record, stating where the id
appears. A commit that names no id passes when another commit or the
description names one. `FAKE-REQ` marks a change that implements no
requirement, such as a typo fix; `vogon/fake/FAKE-REQ.md` says when to use it. It
fails when git cannot resolve `base`, which happens in a clone without full
history.

## vogon init

Creates the files VOGON needs in a host project. The setup step of the skill
runs it.

```sh
vogon init
```

No arguments. It writes, where each is missing:

- `vogon.yaml`, with the paths, `test_command`, the default approvals and the
  roles with no holders, and no `systems`;
- the records directory with `modules.yaml`, `fake/FAKE-REQ.md` and a directory for
  each kind of record, `sources/`, `plans/` and `documents/`;
- `.vogon/` in `.gitignore`;
- the `req` marker in the pytest configuration: `pytest.ini`, `.pytest.ini`,
  `pyproject.toml` with `[tool.pytest.ini_options]`, `tox.ini` with `[pytest]`
  or `setup.cfg` with `[tool:pytest]`, the first found in that order, or
  `pyproject.toml` when there is none. A test run without the plugin, as in
  CI, then passes under `--strict-markers`.

An existing file is changed only to add what is missing, so a second run
changes nothing. Nothing is written under `.claude/`, and no CI file is
written. It prints each path it created or changed. It fails when the marker
cannot be added to the pytest configuration by editing it; the message says
what to add by hand.

## vogon hook

Runs one Claude Code hook. `hooks/hooks.json` in the plugin wires each hook to
its event, and Claude Code runs it; a person does not.

```sh
vogon hook session-start < input.json
```

| Argument | Meaning |
| --- | --- |
| `name` | `session-start`. |

It reads the hook's JSON input on standard input and prints the hook's output
on standard output. The exit status is always 0. In a project with no
`vogon.yaml`, `session-start` prints an instruction to set VOGON up, naming
the file it looked for in `CLAUDE_PROJECT_DIR`.

| Hook | Event | Does |
| --- | --- | --- |
| `session-start` | `SessionStart` | Prints the configured server for each role, the approvals and the role holders; with no `vogon.yaml`, an instruction to run setup. |

## vogon push

Works out the writes that bring the tracker and the test manager in line with
the records, and records the keys of the issues Claude Code created.

```sh
vogon push --plan
vogon push --record created.json
```

| Argument | Meaning |
| --- | --- |
| `--plan` | Print the planned writes and save them to `.vogon/push_plan.json`. |
| `--record FILE` | Write the issue keys in `FILE` into the records' `tracked_as`. |

Exactly one of the two is required.

`--plan` reads the records, the marked tests, `.vogon/results.json` and
`.vogon/tracker.json`, and prints one line per write: `create`, `update`,
`link`, `import` or `track`, or `no changes`. It writes nothing to any system;
Claude Code shows the lines and, once the person confirms, applies exactly the
writes in `.vogon/push_plan.json` (`REQ-TRK-4`). The rules:

- Only an `accepted` record gets an issue or a write (`REQ-GEN-2`).
- An issue is found by the key in `tracked_as`, or by the record id or test
  node id its summary starts with, so a second run creates nothing
  (`REQ-TRK-3`).
- Nothing is written to an issue in an approved state. A record or test
  changed since its issue was approved is reported as an error instead
  (`REQ-TRK-2`).
- A marked test gets one test issue once a requirement it names has an issue,
  linked to each such requirement issue (`REQ-TRC-5`).
- A test result is planned as an import against its test issue once per build.
  Results with no build are refused (`REQ-TRC-6`).

It fails when `.vogon/tracker.json` is absent or does not hold a configured
role. A role not configured in `vogon.yaml` is a warning, and nothing is
planned for it.

`--record FILE` reads a JSON list of `{"id", "role", "key"}` entries, or an
object whose `created` member holds one, and writes each key into its
record's `tracked_as`, adding `governs` when the record had none
(`REQ-TRK-5`). It prints `<id> tracked_as.<role>: <key>` for each key written.
Entries for test node ids are skipped. It fails for an id with no record, and
for a key already named by another record or for a record that already names
another key for that role; neither record is changed.

## vogon evidence

Compares the test manager's export for a build with the copies filed in the
document system (`REQ-TRK-10`).

```sh
vogon evidence 3f2c9a1e7b...
```

| Argument | Meaning |
| --- | --- |
| `build` | The build the evidence is for, as the test manager records it: normally the full commit hash `vogon trace` recorded. |

Claude Code saves the files it exported from the test manager for the build
under `.vogon/evidence/<build>/export/`, files them in the document system,
reads each back, and saves the copies under `.vogon/evidence/<build>/filed/`
with the same relative paths. The command fails for:

- an exported file with no filed copy, and a filed copy with no exported file;
- a filed copy whose bytes differ from the exported file;
- a filed copy that names the build neither in its file name nor in its
  content;
- a filed copy that differs from its own export and is byte-identical to a
  file exported for another build under `.vogon/evidence/`.

It also fails when either directory is empty or absent. When every copy
matches it prints `every filed copy for build <build> matches the export`.
