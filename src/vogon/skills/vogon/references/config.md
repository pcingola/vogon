# Setup (step 1)

Creating `vogon.yaml` and the records layout in a host project, and filling in
the server for each role from the MCP servers connected to Claude Code and
the role holders from the person (`REQ-CLI-6`, `REQ-CLI-8`, `DEC-025`). Each
item below is a rule the setup meets or fails. The schema of `vogon.yaml` is
in the docstring of `${CLAUDE_PLUGIN_ROOT}/scripts/config.py`.

## Initialising

- [ ] If neither `.claude/settings.json` nor `.claude/settings.local.json`
      enables `vogon@vogon`, the person is told to reinstall with
      `--scope project` (`REQ-CLI-9`).
- [ ] `vogon init` is run at the project root. It creates `vogon.yaml`, the
      records directory with `modules.yaml`, the `.vogon/` entry in
      `.gitignore` and the `req` marker in the pytest configuration, and
      prints each file it wrote. On a project already set up it changes
      nothing.
- [ ] The values `vogon init` writes are not asked of the person: the paths,
      `test_command` and the approval assignment.
- [ ] An error `vogon init` reports, such as a marker it cannot add, is
      shown to the person with the file it names.

## Running setup again for a role

- [ ] Setup for a role that is already configured, such as after its
      workflow changed, replaces that role's entry in `systems` in
      `vogon.yaml`. Every other role's entry is left as it is.

## The server for each role

The roles are `tracker`, `test_manager`, `repository_host` and
`document_system`. The operations each needs are `OPERATIONS` in
`${CLAUDE_PLUGIN_ROOT}/scripts/snapshots.py`; read them there.

- [ ] A candidate for a role is a connected server that has a tool for every
      operation the role needs, judged from each tool's name, description and
      input schema.
- [ ] With one candidate, that server is used and the person is not asked.
- [ ] With several, the person is asked to choose, and shown each candidate
      with the tools found for each operation. Claude Code does not choose.
- [ ] With none, the role is left out of `systems`, and the person is told
      the role is not configured, which operations no server provides, and
      which approvals cannot be given until it is.
- [ ] A server with tools for some of a role's operations and not all is not
      a candidate. It is named to the person with the operations it lacks.
- [ ] `server` is the name Claude Code lists for the server, the scoped name
      `plugin:<plugin>:<server>` for a server bundled in a plugin, or that
      server's own key.

## Approved states of the tracker and the test manager

- [ ] The statuses are read through the chosen server, for the issue types
      VOGON writes: requirement issues in the tracker and test issues in the
      test manager.
- [ ] `approved_states` proposes each status whose name says approval or
      signature, such as `Approved` or `Signed`.
- [ ] `server` and `approved_states` for a role are written together, in one
      write of `vogon.yaml`.

## Role holders

- [ ] The person is asked for the holders, as email addresses, of every role
      an approval under `approvals` uses. A role no approval uses is not
      asked about.
- [ ] The holders are written under `roles`, one list per role, as given.

## Confirming and writing

- [ ] Everything setup derived is shown as one list before any write: for
      each role the server, or that it is not configured; for the tracker and
      the test manager `approved_states`; the tool found for each operation;
      and each role an approval uses, with the approvals it gives, for the
      person to name its holders.
- [ ] The person confirms or corrects the list in one answer. Corrections are
      applied as given.
- [ ] `vogon.yaml` is written once, after that answer, keeping every key
      `vogon init` wrote.
- [ ] `.vogon/servers.json` is written for each configured server, in the
      format the docstring of `snapshots.py` gives: `tools` lists every tool
      the server offers, named by the part after `mcp__<server>__`, and
      `operations` maps each operation of the role to one of those tools.
- [ ] With `repository_host` configured, the rules for the default branch are
      read and saved to `.vogon/branch_rules.json` in the format the
      docstring of `snapshots.py` gives.

## Checking and committing

- [ ] `vogon check` is run. An error naming a role, a server and an
      operation means the server lacks it, and the person is told the role,
      the server and each missing operation.
- [ ] Setup is complete only when `vogon check` reports no error at
      `vogon.yaml`. Each such error is shown to the person, and setup is not
      reported as complete while one remains.
- [ ] Every warning is shown to the person.
- [ ] `vogon.yaml`, the records directory, `.gitignore` and the pytest
      configuration file are committed, with a message saying VOGON was set
      up. `.vogon/` is not committed.
- [ ] Nothing is written under `.claude/`, and no CI file is written.
