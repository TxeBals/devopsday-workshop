"""LAB 10c — MCP: connect external tools without touching the agent.

An MCP server exposes tools (issues, database, wiki, CI…) over a standard protocol.
Forja starts them according to .forja/settings.json and registers their tools under a
namespaced name so they don't collide and so permission rules can be written:

    "mcpServers": {
      "issues": {"command": ["python", "examples/mcp/issues_server.py"]},
      "wiki":   {"url": "https://mcp.mycompany/wiki/mcp", "token_env": "WIKI_TOKEN"}
    }
    -> tools  mcp__issues__list_issues, mcp__issues__get_issue, …
    -> allow rules: ["mcp__issues__*"]

MCP tools have "exec" risk by default: they go through permissions like bash.
"""
from __future__ import annotations

import os
import re
from contextlib import ExitStack
from typing import Any

from .mcp_bridge import MCPBridge
from .tools import Tool

NAME_RE = re.compile(r"[^a-zA-Z0-9_]")


# ---- TODO 10.5 : namespaced name ---------------------------------------------
def mcp_tool_name(server: str, tool: str) -> str:
    """mcp__<server>__<tool>, only [a-zA-Z0-9_] (some models reject other characters in tool names)."""
    # TODO 10.5: 'mcp__' + server + '__' + tool, replacing any character outside [a-zA-Z0-9_] with '_' (NAME_RE).
    raise NotImplementedError("TODO 10.5")


def connect_servers(config: dict[str, dict[str, Any]], stack: ExitStack, read_only: set[str] | None = None,
                    cwd: str | None = None) -> tuple[list[Tool], list[str]]:
    """Starts each server inside `stack` (closed on exit). Returns (tools, errors).
    stdio servers run with `cwd` (the project root), so relative paths in settings.json resolve from the project.
    A failing server doesn't bring the session down: it is reported and we carry on."""
    tools: list[Tool] = []
    errors: list[str] = []
    for name, spec in config.items():
        try:
            if "url" in spec:
                token = os.getenv(spec["token_env"]) if spec.get("token_env") else None
                bridge = stack.enter_context(MCPBridge.http(spec["url"], token=token))
            else:
                bridge = stack.enter_context(MCPBridge(list(spec["command"]), env=spec.get("env"), cwd=spec.get("cwd", cwd)))
            for t in bridge.tools(prefix="", risk="exec"):
                t.name = mcp_tool_name(name, t.name)
                if read_only and t.name in read_only:
                    t.risk = "read"
                tools.append(t)
        except Exception as e:  # noqa: BLE001
            errors.append(f"MCP '{name}': {type(e).__name__}: {e}")
    return tools, errors
