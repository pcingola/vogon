---
name: init
description: Sets VOGON up in a host project. Writes vogon/project/vogon.yaml, files the validation plan, adds the VOGON .gitignore lines. TRIGGER when: user says set up VOGON, install VOGON, configure VOGON, file a new validation plan.
---

# vogon:init

Sets VOGON up in a host project, and updates the setup when it runs again.
It writes `vogon/project/vogon.yaml`, files the validation plan in
`vogon/sources/`, adds the VOGON lines to the host `.gitignore` and the test
marker lines to the host `conftest.py`, reports approval transitions that are
not electronic signatures, and opens a pull request. Use it once per project
before any other VOGON skill, and again when a system, role holder or module
changes or a new version of the validation plan is issued. It writes no
project process file: a skill derives each one when it first needs it.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first.

## Inputs

- The validation plan: a local path, or its location in a system the session
  reaches, such as the document system or mail. On a later run it is
  optional.
- From the developer, for what the repository and the MCP servers do not
  show: the system for each role, the holders of each approval role as git
  identities `Name <email>`, the modules, the options, and the tracker or
  test manager project whose approval workflow is read.
- The MCP servers connected to the session.
- The repository: the `origin` remote, the source tree and `.gitignore`.
- `vogon/project/vogon.yaml`, when it exists.

## Steps

1. Read `vogon/project/vogon.yaml` if it exists. Skip the other steps of
   `common.md` "Start of every skill", and derive no process file.
2. If the developer did not give the plan's location, ask for it. On a
   later run with no new plan, skip to step 5. If the project has no plan
   yet, skip to step 5. Report that no plan is held, so each skill that
   derives a process file will ask the developer about every topic of its template.
3. Start the plan filer and its copy check (Loops). The plan filer fetches
   the original itself, through the system that holds it. It:
   - reads the document's own date, title and version, and the approval
     roles the plan names, and states them in the first lines of its log;
   - files the original and its markdown copy as
     `${CLAUDE_PLUGIN_ROOT}/references/sources.md` states, with the plan's
     version in the slug, such as `2026-09-01_validation_plan_v0_1.pdf`, and
     with `kind: plan` and `authority: procedure`;
   - stops and reports, without writing, if either path exists, or if a held
     file in `vogon/sources/` has the same content.
4. Read the plan's date, title, version and roles from the plan filer's log.
5. Read the repository and the MCP servers, and propose values:
   - `repository_host`: from the host of `git remote get-url origin`;
   - every other role: a connected MCP server that provides the operations
     the skills need from that role. For a tracker, these are reading items,
     creating items and reading transitions; for a test manager, uploading
     results; for a document system, filing documents. Report each operation
     a proposed server lacks. When two servers can fill one role, propose
     both and ask the developer to choose;
   - `modules`: one per top-level package of the source tree, in uppercase
     letters and digits;
   - `roles`: `product_owner` and each approval role the plan names, under
     the plan's own role names, with no holder proposed;
   - `options`: the current values, or the template's defaults.
   On a later run, propose the current values of `vogon.yaml`, and mark each
   value that differs from what the repository and the MCP servers now show.
6. Ask the developer, in one message, to confirm or correct each proposed
   value and to give each role holder. When a tracker or a test manager is
   configured, also ask for the project in it whose approval workflow step 10
   checks. A role the developer says the project does not have is omitted
   from `vogon.yaml`.
7. Write `vogon/project/vogon.yaml` from
   `${CLAUDE_PLUGIN_ROOT}/templates/vogon.yaml` with the confirmed values,
   keeping the template's comments. On a later run, change only the values
   the developer confirmed in step 6.
8. In `.gitignore` at the repository root, add `vogon/tmp/` if it is not
   present. Add or remove the `vogon/logs/` line (`loop.md` "Logs").
9. Make each change `${CLAUDE_PLUGIN_ROOT}/references/markers.md` states
   that the host project lacks: the `conftest.py` lines and the marker
   registration.
10. For the tracker and the test manager named in `vogon.yaml`, read the
    workflow of the project the developer gave in step 6 through the MCP
    server. List each transition that records an approval. Report each
    transition that does not make the approver re-enter their credentials:
    it is not an electronic signature under 21 CFR Part 11. If the MCP server
    cannot read the workflow configuration, report that the check could not
    be made. Where neither system is configured, report that the check was
    not made. Change nothing in either system.
11. Commit the files of steps 3 to 9 on the working branch. Push and open a
    pull request on the repository host. The description states the systems,
    roles and modules written, the plan's path and version, the lines changed
    in `.gitignore` and `conftest.py`, and the report of step 10.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Plan filer | The original and the markdown copy of the validation plan in `vogon/sources/` | Copy check, which reads the original itself | The copy holds every section, heading number, table, list and sentence of the original, in its order and wording, and adds nothing; the frontmatter date, title and file names match the original and `sources.md` |

## Outputs

| Path or system | Format |
| --- | --- |
| `vogon/project/vogon.yaml` | YAML, in the template's structure and comments |
| `vogon/sources/<date>_<slug>.<ext>` | The plan's original, unchanged |
| `vogon/sources/<date>_<slug>.md` | Markdown copy of the plan, frontmatter as `sources.md` states |
| `.gitignore` | `vogon/tmp/`, and `vogon/logs/` as step 8 states |
| Host `conftest.py` and pytest configuration | As `markers.md` states, only where the project lacks a change |
| Repository host | The working branch and the pull request of step 11 |

No `REQ-*.json` entry: the skill concerns no requirement. The tracker and the
test manager are read only.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`: main agent and every
  sub-agent.
- `${CLAUDE_PLUGIN_ROOT}/references/loop.md`: main agent.
- `${CLAUDE_PLUGIN_ROOT}/references/sources.md`: plan filer and copy check.
- `${CLAUDE_PLUGIN_ROOT}/references/writing.md`: plan filer and copy check.
- `${CLAUDE_PLUGIN_ROOT}/templates/vogon.yaml`: main agent, step 7.
- `${CLAUDE_PLUGIN_ROOT}/references/markers.md`: main agent, step 9.
