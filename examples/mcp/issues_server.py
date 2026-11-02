"""Example MCP server: a minimal issue tracker (stdio).

    python examples/mcp/issues_server.py      # Forja starts it according to .forja/settings.json
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
def list_issues(status: str = "open") -> list[dict]:
    """Lists issues by status (open | closed) with id, title and labels."""
    return [{k: i[k] for k in ("id", "title", "labels")} for i in _load() if i["status"] == status]


@mcp.tool()
def get_issue(id: int) -> dict:
    """Full detail of an issue: description, steps to reproduce and comments."""
    for i in _load():
        if i["id"] == id:
            return i
    raise ToolError(f"issue #{id} does not exist")


@mcp.tool()
def comment_issue(id: int, text: str) -> dict:
    """Adds a comment to an issue (an action with side effects)."""
    issues = _load()
    for i in issues:
        if i["id"] == id:
            i.setdefault("comments", []).append(text)
            DATA.write_text(json.dumps(issues, ensure_ascii=False, indent=1), encoding="utf-8")
            return {"ok": True, "comments": len(i["comments"])}
    raise ToolError(f"issue #{id} does not exist")


if __name__ == "__main__":
    mcp.run()
