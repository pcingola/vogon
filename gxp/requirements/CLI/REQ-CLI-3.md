---
id: REQ-CLI-3
type: requirement
title: Work with no configuration when the project follows the default layout
modules: [CLI]
status: accepted
verification: test
gxp_risk: none
depends_on: [DEC-002]
references:
  - src/docs/dev/architecture.md
tags: [configuration]
---

# REQ-CLI-3 — Work with no configuration when the project follows the default layout

**Requirement.** VOGON MUST read its configuration from `[tool.vogon]` in the
host project's `pyproject.toml`, and MUST operate on the default layout when
that section is absent.

Most of the layout is convention. A tool that cannot start until it has been
configured is one people configure wrongly once and never revisit.

**What this does not require.** Supporting a configuration file of its own, and
supporting a project with no `pyproject.toml`.

**Example.** A project with `gxp/` in place and no `[tool.vogon]` section runs
every command.

**Acceptance.** With no `[tool.vogon]` section present, every command resolves
the documented default paths, and each documented setting overrides exactly one
of them.
