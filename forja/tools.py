"""LAB 02a — El registro de tools (decorador @tool, JSON Schema, ejecución segura).

Tres clases de riesgo, que usan los permisos (lab 04) y el paralelismo (lab 03):
  read  -> solo lee (read_file, grep, glob): se puede ejecutar en paralelo y sin preguntar
  edit  -> modifica ficheros del proyecto (write_file, edit_file)
  exec  -> efectos arbitrarios (bash, MCP): siempre pasa por permisos
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
    """Lo que devuelve una tool cuando además del texto para el modelo quiere pasar
    metadatos a la interfaz (p. ej. el diff de una edición)."""

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
    """Todo el docstring hasta 'Args:' — en un agente de código la descripción larga importa."""
    return re.split(r"\n\s*Args:", (doc or "").strip())[0].strip()


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]
    args_model: type[BaseModel]
    risk: Risk = "read"

    # ---- TODO 02.1 : schema OpenAI desde el modelo pydantic -------------
    def schema(self) -> dict[str, Any]:
        # TODO 02.1: self.args_model.model_json_schema(); quita 'title' de la raíz y de cada property; additionalProperties=False. Devuelve {'type':'function','function':{name, description, parameters}}.
        raise NotImplementedError("TODO 02.1")

    def subject(self, args: dict[str, Any]) -> str:
        """Lo que se compara con las reglas de permisos: el comando o la ruta."""
        for key in ("command", "path", "pattern", "name"):
            if key in args:
                return str(args[key])
        return ""


def tool(fn: Callable[..., Any] | None = None, *, name: str | None = None, risk: Risk = "read"):
    """@tool o @tool(risk="edit"). Type hints + docstring -> schema + validador."""

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
    return f"{text[:half]}\n\n…[{len(text) - MAX_OUTPUT_CHARS} caracteres omitidos]…\n\n{text[-half:]}"


@dataclass
class ToolRegistry:
    tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, *tools: Tool) -> ToolRegistry:
        for t in tools:
            if t.name in self.tools:
                raise ValueError(f"tool duplicada: {t.name}")
            self.tools[t.name] = t
        return self

    def subset(self, names: list[str]) -> ToolRegistry:
        return ToolRegistry({n: self.tools[n] for n in names if n in self.tools})

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self.tools.values()]

    def parse_args(self, call: ToolCall) -> tuple[Tool | None, dict[str, Any] | None, str | None]:
        """(tool, args validados, error). Lo usa la puerta de permisos ANTES de ejecutar."""
        t = self.tools.get(call.name)
        if t is None:
            return None, None, f"ERROR: la tool '{call.name}' no existe. Disponibles: {', '.join(self.tools)}"
        try:
            raw = json.loads(call.arguments or "{}")
            if not isinstance(raw, dict):
                raise ValueError("los argumentos deben ser un objeto JSON")
            return t, t.args_model.model_validate(raw).model_dump(), None
        except (json.JSONDecodeError, ValueError) as e:
            if isinstance(e, ValidationError):
                errs = "; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors())
                return t, None, f"ERROR de validación en '{t.name}': {errs}"
            return t, None, f"ERROR: argumentos no son JSON válido ({e}). Reintenta con un objeto JSON."

    # ---- TODO 02.2 : ejecutar sin lanzar nunca --------------------------
    def execute(self, call: ToolCall) -> ToolResult:
        # TODO 02.2: NUNCA lanza. t, args, err = self.parse_args(call); si err -> ToolResult(ok=False, err). Ejecuta t.fn(**args) capturando cualquier excepción como 'ERROR en ...'. Si devuelve ToolOutput usa .text y .meta; si no, str o JSON. Usa _truncate y mide duration_ms.
        raise NotImplementedError("TODO 02.2")
