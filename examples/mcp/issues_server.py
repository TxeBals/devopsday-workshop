"""Servidor MCP de ejemplo: un gestor de issues mínimo (stdio).

    python examples/mcp/issues_server.py      # lo arranca Forja según .forja/settings.json
"""
from __future__ import annotations

import json
from pathlib import Path

try:  # mcp >= 2.0
    from mcp.server.mcpserver import MCPServer as FastMCP
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError

DATA = Path(__file__).with_name("issues.json")
mcp = FastMCP("issues")


def _load() -> list[dict]:
    return json.loads(DATA.read_text(encoding="utf-8"))


@mcp.tool()
def list_issues(estado: str = "abierta") -> list[dict]:
    """Lista issues por estado (abierta | cerrada) con id, título y etiquetas."""
    return [{k: i[k] for k in ("id", "titulo", "etiquetas")} for i in _load() if i["estado"] == estado]


@mcp.tool()
def get_issue(id: int) -> dict:
    """Detalle completo de una issue: descripción, pasos para reproducir y comentarios."""
    for i in _load():
        if i["id"] == id:
            return i
    raise ToolError(f"no existe la issue #{id}")


@mcp.tool()
def comment_issue(id: int, texto: str) -> dict:
    """Añade un comentario a una issue (acción con efectos)."""
    issues = _load()
    for i in issues:
        if i["id"] == id:
            i.setdefault("comentarios", []).append(texto)
            DATA.write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
            return {"ok": True, "comentarios": len(i["comentarios"])}
    raise ToolError(f"no existe la issue #{id}")


if __name__ == "__main__":
    mcp.run()
