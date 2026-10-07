# Setting up a project

Step 1 of the [steps](index.md). A developer installs the plugin into the
project's repository and runs `vogon:init`. It is run once per project, and
again when a system, a role holder or the validation plan changes.

## Configuration

`vogon:init` proposes a value for each entry of `vogon/project/vogon.yaml`:

- the system for each role (tracker, test manager, document system,
  repository host, meetings, mail, chat), from the git remote and the MCP
  servers connected to the session. Where two servers can fill one role, the
  developer chooses;
- the modules, one per top-level package of the source tree;
- the approval roles the validation plan names, under the plan's own names,
  and the Product Owner;
- the project options, such as whether logs are committed.

The developer confirms or corrects every value and gives the holder of each
role, in one answer. A role the project does not have is left out, and a skill
that needs it reports what it skipped. `vogon:init` writes the file from the
commented template the plugin ships.

For the tracker and the test manager, `vogon:init` reads the approval workflow
and reports each approval transition that does not make the approver re-enter
their credentials, because such a transition is not an electronic signature
under 21 CFR Part 11. It changes nothing in either system.

## The validation plan

The validation plan is the host project's controlled document. `vogon:init`
files it in `vogon/sources/` as the original, unchanged, and a markdown copy
beside it, named by the plan's own date with its version in the slug
([Sources](../sources.md)). A plan already held is never overwritten; a new
version is filed beside the old one.

`vogon:init` commits the configuration and the filed plan on a branch and
opens a pull request. A person approves it on the repository host.

## Project process files

The markdown files in `vogon/project/` state how VOGON works in this project:
`tracking.md`, `requirements.md`, `tests.md`, `traceability.md`,
`documents.md` and `release.md`. The table in
[Architecture](../architecture.md#project-configuration-and-process-files)
says what each states. `vogon:init` does not write them.

A file is derived when a skill first needs it, before the skill does its task:

1. A writing sub-agent drafts the file from its template, and each statement
   cites a section of the plan.
2. Evaluators check that each statement is supported by the cited section and
   that the file covers every topic of its template.
3. A topic the plan does not settle is asked of the developer. The answer is
   written into the file with the developer's name and the date.
4. Tracker and test manager names, such as item types and transitions, are
   read from an example item and confirmed by the developer.
5. The file goes in the pull request of the skill that derived it.

Each file records in its frontmatter the plan version it was derived from.
When the held plan is newer, the next skill that reads the file derives it
again before acting.
