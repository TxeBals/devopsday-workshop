"""LAB 10c — MCP: conectar herramientas externas sin tocar el agente.

Un servidor MCP expone tools (issues, base de datos, wiki, CI…) con un protocolo estándar.
Forja los arranca según .forja/settings.json y registra sus tools con un nombre con
espacio de nombres para que no choquen y para poder escribir reglas de permisos:

    "mcpServers": {
      "issues": {"command": ["python", "examples/mcp/issues_server.py"]},
      "wiki":   {"url": "https://mcp.miempresa/wiki/mcp", "token_env": "WIKI_TOKEN"}
    }
    -> tools  mcp__issues__list_issues, mcp__issues__get_issue, …
    -> reglas allow: ["mcp__issues__*"]

Las tools MCP son de riesgo "exec" por defecto: pasan por permisos como bash.
"""
from __future__ import annotations

import os
import re
from contextlib import ExitStack
from typing import Any

from .mcp_bridge import MCPBridge
from .tools import Tool

NAME_RE = re.compile(r"[^a-zA-Z0-9_]")


# ---- TODO 10.5 : nombre con espacio de nombres -------------------------------
def mcp_tool_name(server: str, tool: str) -> str:
    """mcp__<server>__<tool>, solo [a-zA-Z0-9_] (algunos modelos rechazan otros caracteres en nombres de tool)."""
    # TODO 10.5: 'mcp__' + server + '__' + tool, sustituyendo cualquier carácter fuera de [a-zA-Z0-9_] por '_' (NAME_RE).
    raise NotImplementedError("TODO 10.5")


def connect_servers(config: dict[str, dict[str, Any]], stack: ExitStack, read_only: set[str] | None = None) -> tuple[list[Tool], list[str]]:
    """Arranca cada servidor dentro de `stack` (se cierran al salir). Devuelve (tools, errores).
    Un servidor que falla no tumba la sesión: se informa y se sigue."""
    tools: list[Tool] = []
    errors: list[str] = []
    for name, spec in config.items():
        try:
            if "url" in spec:
                token = os.getenv(spec["token_env"]) if spec.get("token_env") else None
                bridge = stack.enter_context(MCPBridge.http(spec["url"], token=token))
            else:
                bridge = stack.enter_context(MCPBridge(list(spec["command"]), env=spec.get("env")))
            for t in bridge.tools(prefix="", risk="exec"):
                t.name = mcp_tool_name(name, t.name)
                if read_only and t.name in read_only:
                    t.risk = "read"
                tools.append(t)
        except Exception as e:  # noqa: BLE001
            errors.append(f"MCP '{name}': {type(e).__name__}: {e}")
    return tools, errors
