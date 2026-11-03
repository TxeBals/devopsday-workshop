"""LAB 04b — Permissions: adjustable autonomy with rules.

Modes (the same concepts commercial coding agents use):
  default      -> reads free; edits and bash ask
  accept_edits -> reads and edits free; bash asks
  plan         -> READ-only; editing or executing is denied (lab 08)
  bypass       -> everything allowed except deny rules (for sandbox/CI, never on your laptop)

Rules:  "tool_name"  or  "tool_name(pattern)"  — the pattern (fnmatch) is matched against the
call's "subject": the command for bash, the path for file tools.
  allow: ["bash(pytest*)", "bash(git status*)", "edit_file(src/*)"]
  deny:  ["bash(sudo *)", "read_file(.env*)"]
Evaluation order: deny > plan mode > allow > risk/mode > ask.
"""
from __future__ import annotations

import fnmatch
import re
import shlex
from typing import Any, Literal

from .tools import Tool

Mode = Literal["default", "accept_edits", "plan", "bypass"]
Decision = Literal["allow", "ask", "deny"]
MODES: tuple[Mode, ...] = ("default", "accept_edits", "plan", "bypass")
RULE_RE = re.compile(r"^([\w.\-*?]+)(?:\((.*)\))?$")


def parse_rule(rule: str) -> tuple[str, str | None]:
    m = RULE_RE.match(rule.strip())
    if not m:
        raise ValueError(f"invalid rule: {rule!r}")
    return m.group(1), m.group(2)


# ---- TODO 04.3 : does a rule match a call? --------------------------------
def rule_matches(rule: str, tool: Tool, args: dict[str, Any]) -> bool:
    # TODO 04.3: name, pattern = parse_rule(rule). The tool name is matched with fnmatchcase (allows 'mcp__issues__*'). No pattern: match. With a pattern: fnmatchcase(tool.subject(args), pattern); for bash normalise whitespace (' '.join(split())).
    raise NotImplementedError("TODO 04.3")


def split_commands(command: str) -> list[str]:
    """`pytest -q && rm -rf /` is TWO commands: an allow rule for pytest must not let the second one through."""
    parts = re.split(r"\s*(?:&&|\|\||;|\|)\s*", command.strip())
    return [p for p in parts if p]


# ---- TODO 04.4 : the decision ---------------------------------------------
def decide(tool: Tool, args: dict[str, Any], mode: Mode, allow: list[str], deny: list[str]) -> tuple[Decision, str]:
    # TODO 04.4: 1) deny (also for each bash subcommand via split_commands) -> 'deny'. 2) plan and risk != read -> 'deny'. 3) allow: for bash ALL subcommands must match some rule; for the rest, some rule. 4) read risk or bypass mode -> allow. 5) accept_edits and edit risk -> allow. 6) 'ask'. Return (decision, reason).
    raise NotImplementedError("TODO 04.4")


# ---- TODO 04.5 : suggest a rule for "always approve" --------------------------
def suggest_rule(tool: Tool, args: dict[str, Any]) -> str:
    """When the answer is 'always', we save a sensible rule, not the literal command:
    bash `pytest -q tests/x.py` -> `bash(pytest*)`; edit_file -> `edit_file`."""
    # TODO 04.5: bash: shlex.split; 'python -m X' -> bash(python -m X*); git/npm/uv/pip/docker… -> bash(<cmd> <subcmd>*); others -> bash(<cmd>*). Other tools: their name.
    raise NotImplementedError("TODO 04.5")
