"""The Claude Code hooks: `vogon hook <name>` reads the hook's JSON input on
stdin and prints what Claude Code reads back (`src/docs/dev/architecture.md`,
Hooks).

    session-start  SessionStart: prints the configuration as plain text.
    post-write     PostToolUse on Write, Edit, MultiEdit, NotebookEdit: after a
                   write under the records directory, the findings on that
                   file; after a write of vogon.yaml, the configuration. Both
                   as `additionalContext`.
    commit         PreToolUse on Bash and PowerShell: refuses a `git commit`
                   whose message names an id that resolves to no record
                   (REQ-TRC-9). A message naming no id is allowed.
    transition     PreToolUse on `mcp__.*`: refuses a transition into an
                   approved state, a transition id not in `transitions`, and
                   every call to a tracker or test manager server whose
                   transition setup is incomplete (REQ-TRK-1).
    test-read      PreToolUse on the file tools, Bash, PowerShell and MCP
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
import shlex
from pathlib import Path
from typing import Callable, Mapping

import config as config_module
import ids
import records
from checks import rel
from config import FILENAME, TRANSITION_ROLES, Config

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
SHELL_TOOLS = ("Bash", "PowerShell")
GLOB_CHARS = re.compile(r"[*?\[{]")


# Output


def deny(reason: str) -> str:
    return json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }})


def context(event: str, text: str) -> str:
    return json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}})


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
    the approvals and the role holders, then what is invalid or unset."""
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
    found = [*cfg.findings, *config_module.check(cfg)]
    if found:
        lines.append("Findings:")
        lines.extend(f"- {f.format()}" for f in found)
    return "\n".join(lines)


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


# post-write


def post_write(data: dict | None, root: Path) -> str:
    if data is None:
        return ""
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    value = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(value, str) or not value:
        return ""
    path = _real(Path(value), _cwd(data, root))
    cfg = config_module.load(root)
    if path == Path(os.path.realpath(root / FILENAME)):
        return context("PostToolUse", configuration_text(cfg))
    records_dir = Path(os.path.realpath(cfg.records_dir))
    if not _under(path, [records_dir]) or path == records_dir:
        return ""
    from commands.check import CHECKS  # imported here: it pulls in every check module

    name = rel(cfg, path)
    found = [f for check in CHECKS for f in check(cfg) if f.path == name]
    if not found:
        return ""
    text = f"vogon check on {name}:\n" + "\n".join(f"- {f.format()}" for f in found)
    return context("PostToolUse", text)


# commit


# Words that run the command after them, so `git` after one is still a command.
COMMAND_PREFIXES = ("sudo", "env", "command", "exec", "time", "nohup", "then", "do", "else")
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _at_command_position(tokens: list[str], i: int) -> bool:
    """Whether tokens[i] is the command word: first after a shell operator, or
    after environment assignments and command prefixes only."""
    j = i - 1
    while j >= 0 and not _is_operator(tokens[j]):
        if not (ASSIGNMENT_RE.match(tokens[j]) or tokens[j] in COMMAND_PREFIXES):
            return False
        j -= 1
    return True


def _git_commit_args(tokens: list[str]) -> list[tuple[list[str], str | None]]:
    """For each `git ... commit` run as a command in the token list, its
    arguments and its `-C` directory. Tokens are split at shell operators."""
    found = []
    i = 0
    while i < len(tokens):
        if (tokens[i] != "git" and not tokens[i].endswith("/git")) \
                or not _at_command_position(tokens, i):
            i += 1
            continue
        i += 1
        directory = None
        while i < len(tokens) and tokens[i].startswith("-"):
            opt = tokens[i]
            if opt in ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path") \
                    and i + 1 < len(tokens):
                if opt == "-C":
                    directory = tokens[i + 1] if directory is None else str(Path(directory) / tokens[i + 1])
                i += 2
            else:
                i += 1
        if i < len(tokens) and tokens[i] == "commit":
            i += 1
            args = []
            while i < len(tokens) and not _is_operator(tokens[i]):
                args.append(tokens[i])
                i += 1
            found.append((args, directory))
    return found


def _is_operator(token: str) -> bool:
    return bool(token) and all(c in "();<>|&\n" for c in token)


# Long options of `git commit` whose value may be the next token.
LONG_WITH_VALUE = ("--message", "--file", "--trailer", "--author", "--date", "--cleanup",
                   "--template", "--reuse-message", "--reedit-message", "--fixup", "--squash",
                   "--pathspec-from-file")
# Short options whose value is the rest of the cluster or the next token.
SHORT_WITH_VALUE = "mFcCt"


def commit_message(args: list[str], directory: Path, heredocs: list[str]) -> str:
    """The text of a commit message given on the command line: every `-m`,
    every `-F` file (`-` reads the command's here-documents) and every trailer."""
    parts: list[str] = []

    def file_text(name: str) -> None:
        if name in ("-", "/dev/stdin"):
            parts.extend(heredocs)
            return
        try:
            parts.append((directory / name).read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass

    i = 0
    while i < len(args):
        a = args[i]
        i += 1
        if a == "--":
            break
        if a.startswith("--"):
            name, eq, value = a.partition("=")
            if name not in LONG_WITH_VALUE:
                continue
            if not eq:
                if i >= len(args):
                    break
                value = args[i]
                i += 1
            if name == "--message":
                parts.append(value)
            elif name == "--file":
                file_text(value)
            elif name == "--trailer":
                parts.append(value)
            continue
        if a.startswith("-") and len(a) > 1:
            for j, c in enumerate(a[1:], start=1):
                if c not in SHORT_WITH_VALUE:
                    continue
                value = a[j + 1:]
                if not value:
                    if i >= len(args):
                        break
                    value = args[i]
                    i += 1
                if c == "m":
                    parts.append(value)
                elif c == "F":
                    file_text(value)
                break
    return "\n\n".join(parts)


HEREDOC_RE = re.compile(r"<<-?[ \t]*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?:\n|$)", re.S)


def commit_messages(command: str, cwd: Path) -> list[str]:
    """The message of each `git commit` in a shell command. When the command
    cannot be split into words, the whole command is the message if it runs
    `git ... commit`."""
    heredocs = [m.group(3) for m in HEREDOC_RE.finditer(command)]
    try:
        # An unquoted newline separates commands like `;`; a quoted one stays in its word.
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()<>\n")
        lexer.whitespace_split = True
        lexer.whitespace = " \t\r"
        tokens = list(lexer)
    except ValueError:
        return [command] if re.search(r"\bgit\b.*\bcommit\b", command, re.S) else []
    out = []
    for args, directory in _git_commit_args(tokens):
        base = cwd / directory if directory else cwd
        out.append(commit_message(args, base, heredocs))
    return out


def commit(data: dict | None, root: Path) -> str:
    if data is None:
        return ""
    tool_input = data.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or "commit" not in command:
        return ""
    messages = commit_messages(command, _cwd(data, root))
    named = [i for m in messages for i in ids.find_in_text(m)]
    if not named:
        return ""
    cfg = config_module.load(root)
    keys = records.existing_keys(cfg.records_dir)
    unknown: list[str] = []
    for text in named:
        rid = ids.parse(text)
        if (rid is None or rid.key not in keys) and text not in unknown:
            unknown.append(text)
    if not unknown:
        return ""
    where = rel(cfg, cfg.records_dir)
    return deny(f"The commit message names {', '.join(unknown)}, which resolve"
                f"{'s' if len(unknown) == 1 else ''} to no record under {where}/. Name the "
                "record the change implements, or create the record first (REQ-TRC-9).")


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
                    "transition into an approved state; the call is refused (REQ-TRK-1).")
    tool_name = data.get("tool_name")
    if not isinstance(tool_name, str):
        return deny("VOGON could not read the tool name of this call, so it cannot tell "
                    "whether it is a transition into an approved state; the call is refused "
                    "(REQ-TRK-1).")
    if not tool_name.startswith("mcp__"):
        return ""
    cfg = config_module.load(root)
    if cfg.systems_unreadable:
        bad = [f.message for f in cfg.findings if f.is_failure]
        return deny(f"{FILENAME} cannot be read ({'; '.join(bad)}), so VOGON cannot tell "
                    "which MCP calls are transitions; every MCP call is refused until the "
                    "file is corrected (REQ-TRK-1).")
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
                           "this transition with their own credentials (CON-001)")
    if not reasons:
        return ""
    return deny("VOGON refuses this call: " + "; ".join(reasons) + " (REQ-TRK-1).")


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
                    "be checked (DEC-019).")
    outside = [p for p in paths if not _under(p, allowed)]
    if not outside:
        return ""
    where = "The project root" if outside[0] == Path(os.path.realpath(root)) else rel(cfg, outside[0])
    return deny(f"{agent_type} may read only {shown}. {where} is outside them, so the "
                "call is refused: the tests are written and checked from the requirements, "
                "not from the code (DEC-019).")


# Dispatch

HOOKS: dict[str, Callable[[dict | None, Path], str]] = {
    "session-start": session_start,
    "post-write": post_write,
    "commit": commit,
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
