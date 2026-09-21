---
id: REQ-CLI-3
type: requirement
title: Work with no configuration when the host project follows the default layout
modules: [CLI]
status: accepted
verification: test
gxp_risk: none
depends_on: [DEC-002]
references:
  - src/docs/dev/architecture.md
tags: [configuration]
---

# REQ-CLI-3 — Work with no configuration when the host project follows the default layout

**Requirement.** VOGON MUST read its configuration from `vogon.yaml` at the
host project's root, and MUST operate on the default layout when that file is
absent.

Most of the layout is convention. A tool that cannot start until it has been
configured is one people configure wrongly once and never revisit. The format
is the one the records already use, so no second parser is needed.

**What this does not require.** Reading configuration from the host project's
build file, and supporting a layered or per-environment configuration.

**Example.** A project with `vogon/` in place and no `vogon.yaml` runs every
command.

**Acceptance.** With no `vogon.yaml` present, every command resolves the
documented default paths, and each documented setting overrides exactly one of
them.
