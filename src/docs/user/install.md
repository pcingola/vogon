# Installation

VOGON is a Claude Code plugin. It is installed into Claude Code, and it
creates its records and configuration in the host project when it is set up.
Nothing from the plugin is copied into the host project.

## Requirements

- Claude Code.
- `uv`, which runs VOGON's scripts.
- Git, for the repository the records live in.
- Python 3.11 or later, which `uv` installs if it is missing.
- An MCP server connected to Claude Code for each of the tracker, the test
  manager, the repository host and the document system. Version 0.1 is built
  against Jira, Xray and GitHub. A role with no server is reported as not
  configured, and the steps and checks that need it are skipped.

## Install the plugin

Open Claude Code in the host project's repository and run:

```
/plugin marketplace add pcingola/vogon --scope project
/plugin install vogon@vogon --scope project
```

Both commands take `--scope project`. Without it they default to user scope,
which enables VOGON in every project the user opens. With it they write the
marketplace and the plugin into the host project's `.claude/settings.json`,
and nothing into the user's settings:

```json
{
  "extraKnownMarketplaces": {
    "vogon": {"source": {"source": "github", "repo": "pcingola/vogon"}}
  },
  "enabledPlugins": {"vogon@vogon": true}
}
```

Commit that file. Claude Code offers to install the plugin to every developer
who opens the project, and VOGON is active in no other project. Claude Code
keeps the downloaded plugin files in a cache under `~/.claude/plugins/`; the
cache does not enable the plugin anywhere.

## Set up a host project

Open Claude Code in the host project's repository. Until `vogon.yaml`
exists, VOGON's session-start hook tells Claude Code that the project is not
set up, and Claude Code offers to run setup at your first message. You can
also ask it to set up VOGON.

Claude Code first runs `vogon init`, which creates `vogon.yaml`, the records
directory `vogon/` with `modules.yaml`, adds `.vogon/` to `.gitignore`, and
registers the `req` test marker in the project's pytest configuration.
[Scripts](scripts.md#vogon-init) lists exactly what it writes. `vogon.yaml`
then holds the paths, the test command and the default approvals, each of
which has a default and needs no question.

Claude Code then fills in `systems` from the MCP servers connected to it:

- For each role, the server that provides the role's operations. With one
  candidate it is used. With several, you choose, because only you know which
  one company policy requires. With none, the role is left out.
- For the tracker and the test manager, Claude Code reads the workflow through
  the chosen server. It proposes as approved the states whose names say
  approval or signature, finds the tools that perform a transition and the
  argument of each that holds the transition id, and lists each transition id
  with its target state.

Claude Code shows everything it filled in as one list; you confirm or correct
it in one answer. It saves the tools of each configured server to
`.vogon/servers.json`, so that `vogon check` reports any operation VOGON needs
that a server lacks (`REQ-CLI-4`), and commits `vogon.yaml`. Role holders are
not asked for; `vogon check` reports each approval whose role has no holder
until you add one.

When a workflow changes in the tracker or the test manager, ask Claude Code to
set up that role again.

## vogon.yaml

`vogon.yaml` sits at the root of the host project and is committed. The
scripts and the hooks read it every time they run.

```yaml
paths:
  records: vogon
  tests: [tests]
test_command: python -m pytest
systems:
  tracker:
    server: acme-jira
    transition_tools:
      transition_issue: transition_id
    transitions:
      "11": In Review
      "21": Approved
      "31": Rejected
    approved_states: [Approved]
  test_manager:
    server: acme-xray
    transition_tools:
      transition_test: transition_id
    transitions:
      "41": Ready
      "51": Signed
    approved_states: [Signed]
  repository_host:
    server: github
  document_system:
    server: acme-documents
approvals:
  requirements: {roles: [product_owner], system: tracker}
  test_cases: {roles: [test_lead], system: test_manager}
  test_specification: {roles: [test_lead], system: document_system}
  change: {roles: [engineer], system: repository_host}
  risk_assessment: {roles: [system_owner, it_quality_manager], system: document_system}
  release: {roles: [system_owner, it_quality_manager], system: document_system}
roles:
  product_owner: [alice@example.com]
  test_lead: [bob@example.com]
  engineer: [carol@example.com, dave@example.com]
  system_owner: [erin@example.com]
  it_quality_manager: [frank@example.com]
```

| Key | Meaning | Default |
| --- | --- | --- |
| `paths.records` | The records directory. | `vogon` |
| `paths.tests` | The test paths, a string or a list. The test agents may read only these and the records directory. | `[tests]` |
| `test_command` | The command `vogon trace` runs, a string or a list. | `python -m pytest` |
| `systems.<role>.server` | The MCP server for a role: `tracker`, `test_manager`, `repository_host` or `document_system`. The name Claude Code lists for the server, or `plugin:<plugin>:<server>` for a server bundled in a plugin. | none |
| `systems.<role>.transition_tools` | Tracker and test manager only. Each tool that performs a transition, mapped to the argument holding the transition id. | none |
| `systems.<role>.transitions` | Tracker and test manager only. Each transition id, mapped to its target state. | none |
| `systems.<role>.approved_states` | Tracker and test manager only. The states that mean approved or signed. | none |
| `approvals.<approval>` | The roles that give an approval and the system role it is given in. | the approvals in the example |
| `roles.<role>` | The email of each person holding the role. | no holders |

`systems` has no default. A role with no entry is not configured. A
configured tracker or test manager missing `transition_tools`, `transitions`
or `approved_states` is a failure in `vogon check`, and the `transition` hook
refuses every call to its server until setup writes them, so an incomplete
setup cannot move an issue into an approved state (`REQ-TRK-1`).

An approval listed under `approvals` replaces the default of the same name; a
key it leaves out keeps the default. Every role an approval names must be
defined under `roles` (`REQ-CLI-5`). The approver the tracker reports for an
approval is compared with the holders of its roles (`REQ-TRK-9`), and with the
authors of the record (`REQ-TRK-8`). A number used as a transition id is
quoted, or YAML reads it as a number; either form is accepted.

## CI in the host project

The host project's CI runs `vogon check` on every push and pull request, and
`vogon change` on every pull request. It checks out the VOGON repository at
the tag `v<version>` of the plugin version the developers have installed
(`vogon --version` prints it), and runs the script from that checkout. The
host project is checked out with its full history, `fetch-depth: 0`, because
the held-document checks and `vogon change` read `git log`. `vogon init` does
not write this file.

For GitHub Actions, in `.github/workflows/vogon.yml`:

```yaml
name: vogon

on:
  push:
  pull_request:

jobs:
  vogon:
    runs-on: ubuntu-latest
    env:
      VOGON: uv run --script vogon-plugin/src/vogon/scripts/vogon
    steps:
      - uses: actions/checkout@v4
        with:
          path: host
          fetch-depth: 0
      - uses: actions/checkout@v4
        with:
          repository: pcingola/vogon
          ref: v0.1.0
          path: vogon-plugin
      - uses: astral-sh/setup-uv@v6
      - name: vogon check
        run: $VOGON check --root host
      - name: vogon change
        if: github.event_name == 'pull_request'
        env:
          BASE: ${{ github.base_ref }}
          DESCRIPTION: ${{ github.event.pull_request.body }}
        run: |
          printf '%s' "$DESCRIPTION" |
            $VOGON change "origin/$BASE" --description-file - --root host
```

`vogon change` fails when neither the commits of the pull request nor its
description name a record id, or when a named id resolves to no record
(`REQ-TRC-9`). The base branch and the description are passed through environment
variables, and the description reaches `vogon change` on standard input, so
text in them is never run by the shell.

`ref` is updated together with the installed plugin. The job runs no tests;
the host project's own test job runs them, and the `req` marker that
`vogon init` registered lets it pass under `--strict-markers` without the
plugin.
