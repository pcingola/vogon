"""The Claude Code hooks: `vogon hook <name>` reads the hook's JSON input on
stdin and prints what Claude Code reads back (`src/docs/dev/architecture.md`,
Hooks).

    session-start  SessionStart: prints the configuration as plain text, with
                   its errors and warnings.

The project root is the first directory holding `vogon.yaml` found from
`CLAUDE_PROJECT_DIR`, then upwards from the input's `cwd`, then upwards from
the process's working directory. With no `vogon.yaml` every hook prints
nothing, so a project without VOGON is unaffected.

A hook never stops the session: every hook exits 0. On input it cannot read,
or on an error of its own, a hook prints nothing.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, Mapping

import config as config_module
from config import FILENAME, Config
from findings import Finding


# Input and project root


def parse_input(text: str) -> dict | None:
    """The hook input as a mapping, or None when it is not a JSON object."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return None
    return data if isinstance(data, dict) else None


def find_root(data: dict | None, env: Mapping[str, str]) -> Path | None:
    """The project root, or None when it holds no `vogon.yaml`. Claude Code sets
    `CLAUDE_PROJECT_DIR` for every hook, and then that directory is the only one
    looked at. Without it, as when the hook is run by hand, the root is the first
    directory holding `vogon.yaml` from the input's `cwd` upwards."""
    project = env.get("CLAUDE_PROJECT_DIR")
    if project:
        return Path(project) if (Path(project) / FILENAME).is_file() else None
    cwd = data.get("cwd") if data else None
    start = Path(cwd) if isinstance(cwd, str) and cwd else Path.cwd()
    start = start.resolve()
    for d in (start, *start.parents):
        if (d / FILENAME).is_file():
            return d
    return None


# session-start and the configuration text


def configuration_text(cfg: Config) -> str:
    """The configuration as the agent receives it: the server for each role,
    the approvals and the role holders, then the errors and the warnings."""
    lines = [f"VOGON configuration, read from {FILENAME}. A role is reached only "
             "through the server named for it here."]
    lines.append("Servers:")
    for role in config_module.SYSTEM_ROLES:
        system = cfg.system(role)
        if system is None:
            lines.append(f"- {role}: not configured")
            continue
        line = f"- {role}: {system.server}"
        if system.approved_states:
            line += f" (approved states, never transitioned into: {', '.join(system.approved_states)})"
        lines.append(line)
    lines.append("Approvals:")
    for name, approval in cfg.approvals.items():
        lines.append(f"- {name}: by {', '.join(approval.roles)}, in the {approval.system}")
    lines.append("Role holders:")
    for role, holders in cfg.roles.items():
        lines.append(f"- {role}: {', '.join(holders) if holders else 'no holder'}")
    lines.extend(finding_sections([*cfg.findings, *config_module.check(cfg)]))
    return "\n".join(lines)


SETUP_INCOMPLETE = ("VOGON setup is incomplete. Complete it by loading the `vogon` skill and "
                    "following step 1, `references/config.md`.")


def finding_sections(found: list[Finding]) -> list[str]:
    """`Errors:` and `Warnings:`, each only when it has a line, and after any
    error the instruction to complete setup."""
    errors = [f for f in found if f.is_error]
    warnings = [f for f in found if not f.is_error]
    lines: list[str] = []
    if errors:
        lines.append("Errors:")
        lines.extend(f"- {f.format()}" for f in errors)
    if warnings:
        lines.append("Warnings:")
        lines.extend(f"- {f.format()}" for f in warnings)
    if errors:
        lines.append(SETUP_INCOMPLETE)
    return lines


def session_start(data: dict | None, root: Path) -> str:
    return configuration_text(config_module.load(root))


def setup_needed(env: Mapping[str, str]) -> str:
    """The setup instruction for a session started in a project with no
    `vogon.yaml`, or "" when Claude Code gave no project directory. The plugin
    is enabled per project, so a session that runs this hook is in a project
    that uses VOGON."""
    project = env.get("CLAUDE_PROJECT_DIR")
    if not project or not Path(project).is_dir():
        return ""
    return (f"VOGON is enabled in this project, but {Path(project) / FILENAME} does not "
            "exist, so VOGON is not set up. Before any other VOGON step, tell the person "
            "and run setup: load the `vogon` skill and follow step 1, "
            "`references/config.md`, which runs `vogon init` and then fills in the "
            "systems for the person to confirm.")


# Dispatch

HOOKS: dict[str, Callable[[dict | None, Path], str]] = {
    "session-start": session_start,
}


def run(name: str, text: str, env: Mapping[str, str] | None = None) -> str:
    """Run one hook on its JSON input and return what it prints. Never raises.
    `env` is the environment the hook reads `CLAUDE_PROJECT_DIR` from, by
    default this process's."""
    env = os.environ if env is None else env
    try:
        data = parse_input(text)
        root = find_root(data, env)
        if root is None:
            return setup_needed(env) if name == "session-start" else ""
        return HOOKS[name](data, root)
    except Exception:  # a hook never stops the session
        return ""
