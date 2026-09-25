---
id: REQ-CLI-10
type: requirement
title: Ask for setup at session start when vogon.yaml is missing
modules: [CLI]
status: proposed
verification: test
gxp_risk: none
depends_on: [REQ-CLI-9, REQ-CLI-8]
references:
  - src/docs/dev/architecture.md
tags: [configuration, setup, hooks]
---

# REQ-CLI-10 — Ask for setup at session start when vogon.yaml is missing

**Requirement.** When a Claude Code session starts in a host project that has no
`vogon.yaml`, VOGON MUST add to the session's context an instruction to run
setup, naming the missing file and the skill and reference file that perform
setup. The host project is the directory in `CLAUDE_PROJECT_DIR`. Every other hook
MUST print nothing in that host project until `vogon.yaml` exists.

The plugin is enabled only in host projects (`REQ-CLI-9`), so a
session in which the hooks run is in a host project, and a missing
`vogon.yaml` means setup has not been done. Without the instruction the
configuration that step 1 derives is never written unless the person knows to
ask for it.

**What this does not require.** Running setup from the hook, and starting a
turn before the person's first message.

**Example.** A developer enables the plugin in a new repository and opens
Claude Code there. The context holds "VOGON is enabled in this project, but
`<host-project>/vogon.yaml` does not exist", followed by the instruction to load
the `vogon` skill and follow `references/config.md`.

**Acceptance.** Given `CLAUDE_PROJECT_DIR` naming a directory with no
`vogon.yaml`, `vogon hook session-start` prints text naming
`<directory>/vogon.yaml`, the `vogon` skill, `references/config.md` and
`vogon init`, and `vogon hook transition` prints nothing. Given a
`CLAUDE_PROJECT_DIR` with no `vogon.yaml` and a hook input whose `cwd` lies
inside a directory that has one, `session-start` still prints the
instruction. Given no `CLAUDE_PROJECT_DIR` and no `vogon.yaml` above `cwd`,
every hook prints nothing.
