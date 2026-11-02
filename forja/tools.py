"""LAB 02a — The tool registry (@tool decorator, JSON Schema, safe execution).

Three risk classes, used by permissions (lab 04) and parallelism (lab 03):
  read  -> only reads (read_file, grep, glob): can run in parallel and without asking
  edit  -> modifies project files (write_file, edit_file)
  exec  -> arbitrary effects (bash, MCP): always goes through permissions
"""
from __future__ import annotations

import inspect
import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal, get_type_hints

from pydantic import BaseModel, ConfigDict, Field, ValidationError, create_model

from .types import ToolCall

Risk = Literal["read", "edit", "exec"]
MAX_OUTPUT_CHARS = 30_000


@dataclass
class ToolOutput:
    """What a tool returns when, besides the text for the model, it wants to pass
    metadata to the UI (e.g. the diff of an edit)."""

    text: str
    meta: dict[str, Any] = field(default_factory=dict)


def _param_docs(doc: str) -> dict[str, str]:
    out: dict[str, str] = {}
    m = re.search(r"Args:\s*\n(.*?)(\n\s*\n|\Z)", doc or "", re.S)
    for line in (m.group(1).splitlines() if m else []):
        lm = re.match(r"\s*(\w+)\s*(?:\(.*?\))?:\s*(.+)", line)
        if lm:
            out[lm.group(1)] = lm.group(2).strip()
    return out


def _description(doc: str) -> str:
    """The whole docstring up to 'Args:' — in a coding agent the long description matters."""
    return re.split(r"\n\s*Args:", (doc or "").strip())[0].strip()


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]
    args_model: type[BaseModel]
    risk: Risk = "read"

    # ---- TODO 02.1 : OpenAI schema from the pydantic model --------------
    def schema(self) -> dict[str, Any]:
        # TODO 02.1: self.args_model.model_json_schema(); remove 'title' from the root and from every property; additionalProperties=False. Return {'type':'function','function':{name, description, parameters}}.
        raise NotImplementedError("TODO 02.1")

    def subject(self, args: dict[str, Any]) -> str:
        """What is matched against permission rules: the command or the path."""
        for key in ("command", "path", "pattern", "name"):
            if key in args:
                return str(args[key])
        return ""


def tool(fn: Callable[..., Any] | None = None, *, name: str | None = None, risk: Risk = "read"):
    """@tool or @tool(risk="edit"). Type hints + docstring -> schema + validator."""

    def wrap(f: Callable[..., Any]) -> Tool:
        hints = get_type_hints(f)
        docs = _param_docs(f.__doc__ or "")
        fields: dict[str, Any] = {}
        for pname, p in inspect.signature(f).parameters.items():
            default = ... if p.default is inspect.Parameter.empty else p.default
            fields[pname] = (hints.get(pname, str), Field(default, description=docs.get(pname)))
        model = create_model(f"{f.__name__}_args", __config__=ConfigDict(extra="forbid"), **fields)
        return Tool(name or f.__name__, _description(f.__doc__ or f.__name__), f, model, risk)

    return wrap(fn) if fn else wrap


@dataclass
class ToolResult:
    call_id: str
    name: str
    ok: bool
    output: str
    meta: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0

    def to_message(self) -> dict[str, Any]:
        return {"role": "tool", "tool_call_id": self.call_id, "name": self.name, "content": self.output}


def _truncate(text: str) -> str:
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    half = MAX_OUTPUT_CHARS // 2
    return f"{text[:half]}\n\n…[{len(text) - MAX_OUTPUT_CHARS} characters omitted]…\n\n{text[-half:]}"


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, *tools: Tool) -> ToolRegistry:
        for t in tools:
            if t.name in self.tools:
                raise ValueError(f"duplicate tool: {t.name}")
            self.tools[t.name] = t
        return self

    def subset(self, names: list[str]) -> ToolRegistry:
        return ToolRegistry({n: self.tools[n] for n in names if n in self.tools})

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self.tools.values()]

    def parse_args(self, call: ToolCall) -> tuple[Tool | None, dict[str, Any] | None, str | None]:
        """(tool, validated args, error). Used by the permission gate BEFORE executing."""
        t = self.tools.get(call.name)
        if t is None:
            return None, None, f"ERROR: tool '{call.name}' does not exist. Available: {', '.join(self.tools)}"
        try:
            raw = json.loads(call.arguments or "{}")
            if not isinstance(raw, dict):
                raise ValueError("arguments must be a JSON object")
            return t, t.args_model.model_validate(raw).model_dump(), None
        except (json.JSONDecodeError, ValueError) as e:
            if isinstance(e, ValidationError):
                errs = "; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors())
                return t, None, f"Validation ERROR in '{t.name}': {errs}"
            return t, None, f"ERROR: arguments are not valid JSON ({e}). Retry with a JSON object."

    # ---- TODO 02.2 : execute without ever raising -----------------------
    def execute(self, call: ToolCall) -> ToolResult:
        # TODO 02.2: NEVER raises. t, args, err = self.parse_args(call); if err -> ToolResult(ok=False, err). Run t.fn(**args) catching any exception as 'ERROR in ...'. If it returns ToolOutput use .text and .meta; otherwise str or JSON. Use _truncate and measure duration_ms.
        raise NotImplementedError("TODO 02.2")
