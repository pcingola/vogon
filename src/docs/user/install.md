# Installation

VOGON is a Claude Code plugin. It is installed into Claude Code, and it
creates its records and configuration in the host project when it is set up.
Nothing from the plugin is copied into the host project.

## Requirements

- Claude Code.
- Git, for the repository the records live in.
- `uv`, which runs VOGON's scripts.
- Python 3.11 or later, which `uv` installs if it is missing.
- An MCP server connected to Claude Code for each system role the project
  uses: tracker (for example Jira or GitHub Issues), test manager (for example
  Xray), document system, repository host (for example GitHub), meetings (for
  example Teams or Google Meet), mail (for example Outlook or Gmail) and chat
  (for example Teams or Slack). A role with no server is not used.
- In the tracker and the test manager, every transition that records an
  approval asks the approver for their own credentials.

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

Commit that file. Claude Code then offers to install the plugin to every
developer who opens the project, and VOGON is active in no other project.
Claude Code keeps the downloaded plugin files in a cache under
`~/.claude/plugins/`; the cache does not enable the plugin anywhere.

## Set up a host project

Ask Claude Code to set up VOGON. It runs the `vogon:init` skill.
[Setting up a project](../dev/process/setup.md) describes what setup does.
