---
id: REQ-CLI-9
type: requirement
title: Enable the plugin in the host project only
modules: [CLI]
status: proposed
verification: inspection
gxp_risk: none
depends_on: [DEC-020]
references:
  - src/docs/user/install.md
  - src/docs/dev/architecture.md
tags: [install, distribution, claude-code]
---

# REQ-CLI-9 — Enable the plugin in the host project only

**Requirement.** Every install command VOGON's documentation gives MUST
enable the plugin at project scope, run in the host project, so that the
marketplace and the plugin are named in the host project's `.claude/settings.json`
and in no user settings file.

Claude Code's `/plugin marketplace add` and `/plugin install` default to user
scope, which enables a plugin in every repository the user opens. VOGON's skill,
agents and hooks then load in repositories that do not use it, and the hooks
cannot tell a host project that has not been set up from a repository that
does not use VOGON.

**What this does not require.** Preventing a person from installing the
plugin at user scope, and controlling where Claude Code caches the plugin
files.

**Example.** `install.md` gives `/plugin marketplace add pcingola/vogon
--scope project` followed by `/plugin install vogon@vogon --scope project`,
and shows the `.claude/settings.json` entries they write.

**Acceptance.** Every `/plugin marketplace add` and `/plugin install` command
in `src/docs/` carries `--scope project`, and no document tells the reader to
enable the plugin in `~/.claude/settings.json`.
