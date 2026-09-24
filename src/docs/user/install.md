# Installation

VOGON is distributed as a Python package and installed with `uv`.

## As a command-line tool

```sh
uv tool install vogon
```

## As a library

```sh
uv add vogon
```

## Requirements

- Python 3.11 or later.
- Git, for the repository the records live in.
- An issue tracker for requirements under approval, a test manager for test
  cases and results, and a repository host that reviews changes before they
  merge, each reached through an MCP server. Version 0.1 is built against Jira,
  Xray and GitHub.
- `vogon.yaml`, naming the system that fills each of those roles, the roles
  that give each approval, and the people who hold each role.
