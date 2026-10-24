---
name: init
description: Sets VOGON up in a host project. Writes vogon/project/vogon.yaml, files the validation plan, adds the VOGON .gitignore lines. TRIGGER when: user says set up VOGON, install VOGON, configure VOGON, file a new validation plan.
---

# vogon:init

`vogon:init` writes no project process file: a skill derives each one when it first
needs it.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Steps

1. Read `vogon/project/vogon.yaml` if it exists. Skip the other steps of
   `common.md` "Start of every skill", and derive no process file.
2. If the developer gave no validation plan to file, skip to step 4. If
   `vogon/sources/` holds no validation plan, report that.
3. A sub-agent files the validation plan as `sources.md` states, with the
   plan's version in the slug, such as
   `2026-09-01_validation_plan_v0_1.pdf`, and with `kind: plan` and
   `authority: procedure`. It reports the approval roles the plan names.
4. Propose values:
   - every role other than `repository_host`: a connected MCP server that
     provides the operations the skills need from that role;
   - `modules`: one per top-level package of the source tree, in uppercase
     letters and digits;
   - `roles`: `product_owner` and each approval role the plan names, under
     the plan's own role names, with no holder proposed.
5. Ask the developer, in one message, to confirm or correct each proposed
   value and to give each role holder.
6. Write `vogon/project/vogon.yaml` from
   `${CLAUDE_PLUGIN_ROOT}/templates/vogon.yaml` with the confirmed values,
   keeping the template's comments.
7. In `.gitignore` at the repository root, add `vogon/tmp/` if it is not
   present.
8. Make each change in `markers.md` "Changes in the host project" that the
   host project does not have.
9. Commit, push and open a pull request on the repository host.
