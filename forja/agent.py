"""LAB 03 — El bucle del agente.

    mientras no termine:
        respuesta = modelo(historial, tools)          # en streaming
        si no pide tools -> fin del turno
        ejecutar tools (lecturas en paralelo, el resto en orden) -> resultados al historial

El bucle no sabe de permisos, hooks ni interfaz: recibe una función `execute` (la puerta
del harness) y un objeto `events` para avisar a la interfaz. Así lo reutilizamos tal cual
para subagentes (lab 09) y para evals (lab 12).
"""
from __future__ import annotations

import threading
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Literal

from .tools import ToolRegistry, ToolResult
from .types import ChatModel, ChatResponse, Done, TextDelta, ToolCall

StopReason = Literal["final", "max_steps", "loop", "interrupted"]


class Events:
    """Callbacks para la interfaz (por defecto no hacen nada)."""

    def on_text(self, delta: str) -> None: ...
    def on_assistant(self, resp: ChatResponse) -> None: ...
    def on_tool_start(self, call: ToolCall) -> None: ...
    def on_tool_end(self, call: ToolCall, result: ToolResult) -> None: ...


@dataclass
class AgentResult:
    answer: str
    stop_reason: StopReason
    steps: int
    usage: dict[str, int] = field(default_factory=dict)
    tool_calls: int = 0


@dataclass
class Agent:
    llm: ChatModel
    tools: ToolRegistry
    execute: Callable[[ToolCall], ToolResult] | None = None  # por defecto, tools.execute (sin puerta)
    events: Events = field(default_factory=Events)
    max_steps: int = 40
    max_repeats: int = 3
    parallel_reads: bool = True
    cancel: threading.Event = field(default_factory=threading.Event)

    def _is_read(self, call: ToolCall) -> bool:
        t = self.tools.tools.get(call.name)
        return bool(t and t.risk == "read")

    # ---- TODO 03.1 : ejecutar un lote de tool calls ---------------------
    def _run_calls(self, calls: list[ToolCall]) -> list[ToolResult]:
        """Las llamadas de solo lectura consecutivas se ejecutan en paralelo; las demás, en orden.
        Los resultados se devuelven en el MISMO orden que las llamadas."""
        # TODO 03.1: results = [None]*len(calls). Agrupa lecturas CONSECUTIVAS (self._is_read) y ejecútalas con ThreadPoolExecutor; el resto en orden. Para cada una: events.on_tool_start, execute (self.execute o self.tools.execute), events.on_tool_end. Devuelve los resultados en el orden original.
        raise NotImplementedError("TODO 03.1")

    # ---- TODO 03.2 : el bucle -------------------------------------------
    def run(self, messages: list[dict[str, Any]]) -> AgentResult:
        """`messages` incluye system + historial + el mensaje nuevo del usuario.
        Se MODIFICA en sitio: al terminar contiene todo lo que pasó en el turno."""
        # TODO 03.2: Para step 1..max_steps: si self.cancel está activo -> 'interrupted'. Consume self.llm.stream(messages, tools=schemas or None): TextDelta -> events.on_text; Done -> resp. Acumula usage, añade resp.to_message(), events.on_assistant. Sin tool_calls -> 'final'. Detección de bucle (misma tool+args > max_repeats): cierra los tool_calls pendientes con un ToolResult de error y devuelve 'loop'. Si no, _run_calls y añade los mensajes tool. Al acabar: 'max_steps'.
        raise NotImplementedError("TODO 03.2")
