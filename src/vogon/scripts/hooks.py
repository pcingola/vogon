"""The Claude Code hooks: `vogon hook <name>` reads the hook's JSON input on
stdin and prints what Claude Code reads back (`src/docs/dev/architecture.md`,
Hooks).

    session-start  SessionStart: prints the configuration as plain text, with
                   its errors and warnings.
    transition     PreToolUse on `mcp__.*`: refuses a transition into an
                   approved state, a transition id not in `transitions`, and
                   every call to a tracker or test manager server whose
                   transition setup is incomplete (REQ-TRK-1).
    test-read      PreToolUse on the file tools, Bash and MCP
                   tools: for `vogon-test-writer` and `vogon-test-checker`,
                   with or without the `vogon:` prefix, allows only paths
                   under the records directory and the test paths
                   (REQ-GEN-11, DEC-019).

The project root is the first directory holding `vogon.yaml` found from
`CLAUDE_PROJECT_DIR`, then upwards from the input's `cwd`, then upwards from
the process's working directory. With no `vogon.yaml` every hook prints
nothing, so a project without VOGON is unaffected.

A hook never stops the session: every hook exits 0. On input it cannot read,
or on an error of its own, a hook prints nothing, except `transition` and
`test-read`, which refuse the call in a project that has `vogon.yaml`, because
a call they cannot judge may be the one they exist to refuse.

MCP server names. Claude Code names an MCP tool `mcp__<server>__<tool>`, and a
tool of a server bundled in a plugin `mcp__plugin_<plugin>_<server>__<tool>`,
with every character outside `A-Z`, `a-z`, `0-9`, `_` and `-` replaced by `_`.
The `server` in `vogon.yaml` gets the same replacement and a call belongs to
it when the tool name is `mcp__<server>__<tool>` or
`mcp__plugin_<any plugin>_<server>__<tool>`. So `server` may be the name
Claude Code lists for the server, the scoped form `plugin:<plugin>:<server>`,
or a plugin-bundled server's own key. A name in `transition_tools` is the
tool's name after that prefix; the full `mcp__...` name is accepted too.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Callable, Mapping

import config as config_module
from checks import rel
from config import FILENAME, TRANSITION_ROLES, Config
from findings import Finding

TEST_AGENTS = ("vogon-test-writer", "vogon-test-checker")
AGENT_PREFIX = "vogon:"

# tool name -> the tool_input keys holding the paths it reads or writes
PATH_KEYS = {
    "Read": ("file_path",),
    "Write": ("file_path",),
    "Edit": ("file_path",),
    "MultiEdit": ("file_path",),
    "NotebookRead": ("notebook_path",),
    "NotebookEdit": ("notebook_path",),
    "LS": ("path",),
}
# Tools whose path argument is optional and defaults to the working directory.
SEARCH_TOOLS = ("Grep", "Glob")
SHELL_TOOLS = ("Bash",)
GLOB_CHARS = re.compile(r"[*?\[{]")


# Output


def deny(reason: str) -> str:
    return json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }})


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


def _cwd(data: dict, root: Path) -> Path:
    cwd = data.get("cwd")
    return Path(cwd) if isinstance(cwd, str) and cwd else root


def _under(path: Path, bases: list[Path]) -> bool:
    return any(path == b or b in path.parents for b in bases)


def _real(path: Path, cwd: Path) -> Path:
    return Path(os.path.realpath(cwd / Path(path).expanduser()))


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


# transition


def normalize_server(name: str) -> str:
    """A server name as it appears in a tool name."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def server_tool(tool_name: str, server: str) -> str | None:
    """The tool's name after the server prefix when the tool belongs to `server`,
    else None. See the module docstring for the rule."""
    n = re.escape(normalize_server(server))
    for pattern in (rf"mcp__{n}__(.+)", rf"mcp__plugin_[A-Za-z0-9_-]+?_{n}__(.+)"):
        m = re.fullmatch(pattern, tool_name, re.S)
        if m:
            return m.group(1)
    return None


def _transition_id(value) -> str | None:
    if isinstance(value, dict) and "id" in value:
        value = value["id"]
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        return None
    text = str(value).strip()
    return text or None


def transition(data: dict | None, root: Path) -> str:
    if data is None:
        return deny("VOGON could not read this call, so it cannot tell whether it is a "
                    "transition into an approved state; the call is refused.")
    tool_name = data.get("tool_name")
    if not isinstance(tool_name, str):
        return deny("VOGON could not read the tool name of this call, so it cannot tell "
                    "whether it is a transition into an approved state; the call is refused.")
    if not tool_name.startswith("mcp__"):
        return ""
    cfg = config_module.load(root)
    if cfg.systems_unreadable:
        bad = [f.message for f in cfg.findings if f.is_error]
        return deny(f"{FILENAME} cannot be read ({'; '.join(bad)}), so VOGON cannot tell "
                    "which MCP calls are transitions; every MCP call is refused until the "
                    "file is corrected.")
    tool_input = data.get("tool_input")
    tool_input = tool_input if isinstance(tool_input, dict) else {}
    reasons: list[str] = []
    for role, system in cfg.systems.items():
        tool = server_tool(tool_name, system.server)
        if tool is None or role not in TRANSITION_ROLES:
            continue
        missing = system.missing_transition_keys()
        if missing:
            reasons.append(
                f"the {role} server {system.server!r} has no {', '.join(missing)} in "
                f"{FILENAME}, so every call to it is refused until setup writes them")
            continue
        argument = system.transition_tools.get(tool) or system.transition_tools.get(tool_name)
        if argument is None:
            continue
        tid = _transition_id(tool_input.get(argument))
        approved = {s.strip().casefold() for s in system.approved_states}
        if tid is None:
            reasons.append(f"{tool_name} is a {role} transition tool and its argument "
                           f"{argument!r} holds no transition id")
        elif tid not in system.transitions:
            reasons.append(f"transition {tid} of the {role} is not in the transitions "
                           f"configured in {FILENAME}, so its target state is unknown")
        elif system.transitions[tid].strip().casefold() in approved:
            reasons.append(f"transition {tid} of the {role} leads to "
                           f"{system.transitions[tid]!r}, an approved state. A person makes "
                           "this transition with their own credentials")
    if not reasons:
        return ""
    return deny("VOGON refuses this call: " + "; ".join(reasons) + ".")


# test-read


def is_test_agent(agent_type) -> bool:
    if not isinstance(agent_type, str):
        return False
    name = agent_type[len(AGENT_PREFIX):] if agent_type.startswith(AGENT_PREFIX) else agent_type
    return name in TEST_AGENTS


def _glob_base(pattern: str) -> str | None:
    """The literal directory a glob pattern starts from, or None when the
    pattern contains `..` anywhere, such as in a brace alternative."""
    if ".." in pattern:
        return None
    parts = pattern.replace("\\", "/").split("/")
    literal = []
    for p in parts:
        if GLOB_CHARS.search(p):
            break
        literal.append(p)
    base = "/".join(literal)
    if pattern.startswith("/") and not base:
        base = "/"
    return base


def tool_paths(tool_name: str, tool_input: dict, cwd: Path) -> list[Path] | None:
    """The paths a tool call reads or writes, resolved; None when the call
    reads files the hook cannot name; [] when it reads no file."""
    if tool_name in SHELL_TOOLS or tool_name.startswith("mcp__"):
        return None
    if tool_name in PATH_KEYS:
        values = [tool_input.get(k) for k in PATH_KEYS[tool_name]]
        if not all(isinstance(v, str) and v for v in values):
            return None
        return [_real(Path(v), cwd) for v in values]
    if tool_name in SEARCH_TOOLS:
        path = tool_input.get("path")
        if path is not None and not (isinstance(path, str) and path):
            return None
        base = _real(Path(path), cwd) if path else _real(Path("."), cwd)
        out = [base]
        for key in ("pattern", "glob") if tool_name == "Glob" else ("glob",):
            pattern = tool_input.get(key)
            if not isinstance(pattern, str) or not pattern:
                continue
            start = _glob_base(pattern)
            if start is None:
                return None
            out.append(_real(Path(start), base) if start else base)
        return out
    return []


def test_read(data: dict | None, root: Path) -> str:
    if data is None:
        return deny("VOGON could not read this call, so it cannot tell whether a test agent "
                    "is reading outside the records and the tests; the call is refused.")
    agent_type = data.get("agent_type")
    if not is_test_agent(agent_type):
        return ""
    tool_name = data.get("tool_name")
    tool_input = data.get("tool_input")
    if not isinstance(tool_name, str) or not isinstance(tool_input, dict):
        return deny(f"{agent_type} may read only the records and the tests; VOGON could not "
                    "read this call, so it is refused.")
    cfg = config_module.load(root)
    allowed = [Path(os.path.realpath(p)) for p in (cfg.records_dir, *cfg.test_paths)]
    shown = ", ".join(f"{rel(cfg, p)}/" for p in (cfg.records_dir, *cfg.test_paths))
    paths = tool_paths(tool_name, tool_input, _cwd(data, root))
    if paths is None:
        return deny(f"{agent_type} may read only {shown}, through the file tools with a path "
                    f"under them. {tool_name} is refused, because the paths it reads cannot "
                    "be checked.")
    outside = [p for p in paths if not _under(p, allowed)]
    if not outside:
        return ""
    where = "The project root" if outside[0] == Path(os.path.realpath(root)) else rel(cfg, outside[0])
    return deny(f"{agent_type} may read only {shown}. {where} is outside them, so the "
                "call is refused: the tests are written and checked from the requirements, "
                "not from the code.")


# Dispatch

HOOKS: dict[str, Callable[[dict | None, Path], str]] = {
    "session-start": session_start,
    "transition": transition,
    "test-read": test_read,
}
# Hooks that refuse the call when they fail, rather than printing nothing.
FAIL_CLOSED = {"transition": transition, "test-read": test_read}


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
    except Exception as e:  # a hook never stops the session
        if name in FAIL_CLOSED:
            try:
                if find_root(parse_input(text), env) is not None:
                    return deny(f"VOGON's {name} hook failed ({type(e).__name__}: {e}), so "
                                "the call is refused.")
            except Exception:
                return ""
        return ""
