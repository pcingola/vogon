# Setting up a project

Step 1 of the [steps](index.md). A developer installs the plugin and runs
`vogon:init`, once per project and again when a system, role holder or module
changes or a new version of the validation plan is issued. The steps are in
`src/vogon/skills/init/SKILL.md`.

`vogon:init` proposes the values of `vogon/project/vogon.yaml` from the
repository and the MCP servers of the session; the developer confirms them and
names the role holders. It files the validation plan in `vogon/sources/`
([Sources](../sources.md)), adds the `.gitignore` lines and the `conftest.py`
changes of `src/vogon/references/conftest.md`, reports each approval transition
that is not an electronic signature, and opens a pull request, which a person
approves on the repository host.

`vogon:init` writes no project process file. A skill derives each process file
when it first needs it, and again when the held plan is newer, as
[Architecture](../architecture.md#project-configuration-and-process-files)
describes. With no plan held, every topic of a process file is asked of the
developer.
