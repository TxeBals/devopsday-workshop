"""MCP -> ToolRegistry bridge (PROVIDED; used by lab 10c).

The MCP SDK is async; our agent is synchronous on purpose (easier to follow).
We start an event loop in a thread and expose each MCP tool as a normal `Tool`.
Supports local (stdio) and remote (Streamable HTTP with token) servers.
Compatible with the `mcp` SDK 1.x and 2.x.
"""
from __future__ import annotations

import asyncio
import json
import sys
import threading
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import ConfigDict, create_model

from .tools import Tool


class MCPTool(Tool):
    """Tool whose schema comes from the MCP server (not from type hints)."""

    input_schema: dict[str, Any]

    def schema(self) -> dict[str, Any]:
        params = dict(self.input_schema or {"type": "object", "properties": {}})
        params.pop("title", None)
        return {"type": "function", "function": {"name": self.name, "description": self.description, "parameters": params}}


class MCPBridge:
    """Usage:
        with MCPBridge(["python", "examples/mcp/issues_server.py"]) as mcp:
            registry.register(*mcp.tools(prefix="core_"))
    """

    def __init__(self, command: list[str], env: dict[str, str] | None = None, timeout: float = 30.0):
        self.params = StdioServerParameters(command=command[0] if command[0] != "python" else sys.executable, args=command[1:], env=env) if command else None
        self.url: str | None = None
        self.headers: dict[str, str] = {}
        self.timeout = timeout
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self.session: ClientSession | None = None

    @classmethod
    def http(cls, url: str, token: str | None = None, headers: dict[str, str] | None = None, timeout: float = 30.0) -> MCPBridge:
        """Remote MCP over Streamable HTTP (Hero level). Usage: with MCPBridge.http(url, token) as mcp: ..."""
        b = cls([], timeout=timeout)
        b.url = url
        b.headers = {**(headers or {}), **({"Authorization": f"Bearer {token}"} if token else {})}
        return b

    async def _open_streams(self, stack: AsyncExitStack):
        if self.url is None:
            return await stack.enter_async_context(stdio_client(self.params))
        try:  # mcp 2.x: our own httpx client with headers
            import httpx2
            from mcp.client.streamable_http import streamable_http_client

            hc = await stack.enter_async_context(httpx2.AsyncClient(headers=self.headers, timeout=self.timeout))
            streams = await stack.enter_async_context(streamable_http_client(self.url, http_client=hc))
        except ImportError:  # mcp 1.x
            from mcp.client.streamable_http import streamablehttp_client

            streams = await stack.enter_async_context(streamablehttp_client(self.url, headers=self.headers))
        return streams[0], streams[1]

    def _run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(self.timeout)

    async def _lifetime(self, ready: asyncio.Future) -> None:
        """Opens and closes the session in THE SAME task (anyio requires it)."""
        try:
            async with AsyncExitStack() as stack:
                read, write = await self._open_streams(stack)
                self.session = await stack.enter_async_context(ClientSession(read, write))
                await self.session.initialize()
                self._closing = asyncio.Event()
                ready.set_result(True)
                await self._closing.wait()
        except BaseException as e:  # noqa: BLE001
            if not ready.done():
                ready.set_exception(e)
            else:
                raise

    async def _start(self) -> None:
        ready = asyncio.get_running_loop().create_future()
        self._task = asyncio.create_task(self._lifetime(ready))
        await ready

    async def _stop(self) -> None:
        self._closing.set()
        await self._task

    def __enter__(self) -> MCPBridge:
        self._thread.start()
        self._run(self._start())
        return self

    def __exit__(self, *exc: Any) -> None:
        try:
            self._run(self._stop())
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(timeout=5)

    def tools(self, prefix: str = "", risk: str = "exec") -> list[Tool]:
        assert self.session, "use MCPBridge as a context manager"
        listed = self._run(self.session.list_tools())
        out: list[Tool] = []
        for t in listed.tools:
            schema = getattr(t, "input_schema", None) or getattr(t, "inputSchema", None)  # mcp 2.x | 1.x
            out.append(self._wrap(t.name, t.description or t.name, schema, prefix, risk))
        return out

    def _wrap(self, mcp_name: str, description: str, input_schema: dict, prefix: str, risk: str = "exec") -> Tool:
        def fn(**kwargs: Any) -> str:
            res = self._run(self.session.call_tool(mcp_name, kwargs))
            text = "\n".join(getattr(c, "text", json.dumps(c.model_dump(), default=str)) for c in res.content)
            if getattr(res, "is_error", None) or getattr(res, "isError", False):
                raise RuntimeError(text)
            return text

        # Lax client-side validation: the MCP server does the real validation.
        args_model = create_model(f"{mcp_name}_mcp_args", __config__=ConfigDict(extra="allow"))
        t = MCPTool(name=prefix + mcp_name, description=description.strip().split("\n\n")[0], fn=fn, args_model=args_model, risk=risk)
        t.input_schema = input_schema
        return t
