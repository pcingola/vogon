---
name: init
description: Sets VOGON up in a host project. Writes vogon/project/vogon.yaml, files the validation plan, adds the VOGON .gitignore lines. TRIGGER when: user says set up VOGON, install VOGON, configure VOGON, file a new validation plan.
---

# vogon:init

Sets VOGON up in a host project, and updates the setup when it runs again.
It writes `vogon/project/vogon.yaml`, files the validation plan in
`vogon/sources/`, adds the VOGON lines to the host `.gitignore`, reports
approval transitions that are not electronic signatures, and opens a pull
request. Use it once per project
before any other VOGON skill, and again when a system, role holder or module
changes or a new version of the validation plan is issued. It writes no
project process file: a skill derives each one when it first needs it.

Read `${CLAUDE_PLUGIN_ROOT}/references/common.md` first. It holds the start-of-skill reads, the loop, sub-agent prompts, systems by role, actions never taken, stops and commands.

## Inputs

- The validation plan: a local path, or its location in a system the session
  reaches, such as the document system or mail. On a later run it is
  optional.
- From the developer, for what the repository and the connectors do not
  show: the system for each role, the holders of each approval role as git
  identities `Name <email>`, the modules, the options, and the tracker or
  test manager project whose approval workflow is read.
- The MCP connectors of the session and the repository: the `origin` remote,
  the source tree, `.gitignore`.
- `vogon/project/vogon.yaml`, when it exists.

## Steps

1. Of the start-of-skill reads in `common.md`, do only the first: read
   `vogon/project/vogon.yaml` if it exists. Derive no process file. Create a
   working branch from the default branch.
2. If the developer did not give the plan's location, ask for it. On a
   later run with no new plan, skip to step 5. If the project has no plan
   yet, skip to step 5 and report that a skill that needs a project process
   file asks the developer its topics until a plan is filed.
3. File the plan in the loop under Loops. The writing sub-agent fetches the
   original itself, through the system that holds it, so the plan never
   enters the main agent's context. It:
   - reads the document's own date, title and version, and the approval
     roles the plan names, and states them in the first lines of its log;
   - names the files as `${CLAUDE_PLUGIN_ROOT}/references/sources.md`
     states, with the plan's version in the slug, such as
     `2026-09-01_validation_plan_v0_1.pdf`;
   - copies the original unchanged to `vogon/sources/<date>_<slug>.<ext>`,
     and writes the markdown copy beside it as `<date>_<slug>.md`, with the
     frontmatter `sources.md` states, `kind: plan` and
     `authority: procedure`. A plan that is already markdown is held
     once;
   - stops and reports, without writing, if either path exists, or if a held
     file in `vogon/sources/` has the same content. A held plan is never
     overwritten.
4. Read the plan's date, title, version and roles from the writing
   sub-agent's log.
5. Read the repository and the connectors, and propose values:
   - `repository_host`: from the host of `git remote get-url origin`;
   - every other role: from the MCP servers connected to the session. Propose
     a server for each role it can fill. A server is proposed for a role only
     when it provides the operations the skills need from that role, such as
     reading and creating items and reading transitions for a tracker,
     uploading results for a test manager, and filing documents for a
     document system; report each operation a proposed server lacks. Where
     two servers can fill one role, propose both and let the developer
     choose;
   - `modules`: one per top-level package of the source tree, in uppercase
     letters and digits;
   - `roles`: `product_owner` and each approval role the plan names, under
     the plan's own role names, with no holder proposed;
   - `options`: the current values, or the template's defaults.
   On a later run, propose the current values of `vogon.yaml`, and mark each
   value that differs from what the repository and connectors now show.
6. Ask the developer, in one message, to confirm or correct each proposed
   value and to give each role holder. Ask also for the tracker project and
   test manager project whose approval workflow step 9 reads, where those
   systems are configured. A role the developer says the project does not
   have is omitted from `vogon.yaml`; "Systems by role" in `common.md` states
   how a skill handles a role with no system.
7. Write `vogon/project/vogon.yaml` from
   `${CLAUDE_PLUGIN_ROOT}/templates/vogon.yaml` with the confirmed values,
   keeping the template's comments. On a later run, change only the values
   the developer confirmed in step 6. This file has no loop; the main agent
   writes it.
8. In `.gitignore` at the repository root, add `vogon/tmp/` if it is not
   present. Add or remove the `vogon/logs/` line so that `.gitignore` matches
   the Logs rule in `common.md` for the current `options.commit_logs`.
9. For each of the tracker and the test manager that `vogon.yaml` names,
   read through its connector the workflow of the project the developer
   gave in step 6. Where neither is configured, skip this step and report
   it, as "Systems by role" in `common.md` states. List each transition that
   records an approval. Report each one whose screen, validator or condition
   does not make the approver re-enter their credentials: it is not an
   electronic signature under 21 CFR Part 11. If the connector cannot read the workflow configuration,
   report that the check could not be made. Change nothing in either system.
10. Commit the files of steps 3 to 8 on the working branch, with the logs as
    the Logs rule in `common.md` states. Push and open a pull request on the
    repository host. The description states the systems, role holders and
    modules written, the plan's path and version, the lines changed in
    `.gitignore`, the report of step 9, and the loop and findings as `common.md`
    states. Tell the developer that the pull request waits for review on the
    repository host.

## Loops

| Writing sub-agent | Produces | Evaluators | Checklist or perspective |
| --- | --- | --- | --- |
| Plan filer | The original and the markdown copy of the validation plan in `vogon/sources/` | Copy check, which reads the original itself | The copy holds every section, heading number, table, list and sentence of the original, in its order and wording, and adds nothing; the frontmatter date, title and file names match the original and `sources.md` |

`vogon.yaml` and the `.gitignore` lines have no loop.

## Stops for a person

- An approval: the pull request waits for review on the repository host. Tell
  the developer.
- A finding that needs a choice, such as an original the writing sub-agent
  cannot read or a plan already held: it goes to the developer running the
  skill.

The questions of steps 2 and 6 ask for this skill's inputs.

## Outputs

| Path or system | Format | Written by |
| --- | --- | --- |
| `vogon/project/vogon.yaml` | YAML, in the template's structure and comments | Main agent |
| `vogon/sources/<date>_<slug>.<ext>` | The plan's original, unchanged | Plan filer |
| `vogon/sources/<date>_<slug>.md` | Markdown copy of the plan, frontmatter as `sources.md` states | Plan filer |
| `.gitignore` | `vogon/tmp/`, and `vogon/logs/` as the Logs rule in `common.md` states | Main agent |
| `vogon/logs/<yyyymmdd_hhmmss>_<task>.log.md` | Markdown, one per sub-agent run | Each sub-agent |
| `vogon/logs/` main log | One entry per sub-agent run and decision, as `common.md` states | Main agent |
| Repository host | The working branch and the pull request of step 10 | Main agent |

No `REQ-*.json` entry: the skill concerns no requirement. The tracker and the
test manager are read only.

## Reference files

- `${CLAUDE_PLUGIN_ROOT}/references/common.md`: main agent and every
  sub-agent.
- `${CLAUDE_PLUGIN_ROOT}/references/sources.md`: plan filer and copy check.
- `${CLAUDE_PLUGIN_ROOT}/references/writing.md`: plan filer and copy check,
  as `common.md` requires.
- `${CLAUDE_PLUGIN_ROOT}/templates/vogon.yaml`: main agent, step 7.
