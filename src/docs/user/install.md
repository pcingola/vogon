# Installation

VOGON is a Claude Code plugin. It is installed into Claude Code, and it
creates its records and configuration in the host project when it is set up.

## Requirements

- Claude Code.
- `uv`, which runs VOGON's scripts.
- Git, for the repository the records live in.
- Python 3.11 or later, which `uv` installs if it is missing.
- An MCP server connected to Claude Code for each of the tracker, the test
  manager and the repository host. Version 0.1 is built against Jira, Xray and
  GitHub.

## Install the plugin

In Claude Code:

```
/plugin marketplace add pcingola/vogon
/plugin install vogon@vogon
```

To make the plugin available to every developer on a host project, commit
these entries in the project's `.claude/settings.json`. Claude Code then offers
to install the plugin when the project is opened.

```json
{
  "extraKnownMarketplaces": {
    "vogon": {"source": {"source": "github", "repo": "pcingola/vogon"}}
  },
  "enabledPlugins": {"vogon@vogon": true}
}
```

## Set up a host project

Ask Claude Code to set up VOGON. The skill runs `vogon init`, which creates
`vogon/`, `vogon/modules.yaml` and `vogon.yaml`, and adds `.vogon/` to
`.gitignore`. Claude Code then checks that each configured MCP server provides
the operations VOGON needs, and names any that are missing.

`vogon.yaml` names the system that fills each role, the roles that give each
approval, and the people who hold each role.
[Roles and approvals](../dev/architecture.md#roles-and-approvals) shows the
format.
