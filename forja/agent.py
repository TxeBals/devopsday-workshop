"""LAB 03 — The agent loop.

    while not finished:
        response = model(history, tools)          # streaming
        if it requests no tools -> end of turn
        run tools (reads in parallel, the rest in order) -> results into history

The loop knows nothing about permissions, hooks or the UI: it receives an `execute` function
(the harness gate) and an `events` object to notify the UI. That way we reuse it as-is
for subagents (lab 09) and evals (lab 12).
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
    """Callbacks for the UI (no-ops by default)."""

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
    execute: Callable[[ToolCall], ToolResult] | None = None  # default: tools.execute (no gate)
    events: Events = field(default_factory=Events)
    max_steps: int = 40
    max_repeats: int = 3
    parallel_reads: bool = True
    cancel: threading.Event = field(default_factory=threading.Event)

    def _is_read(self, call: ToolCall) -> bool:
        t = self.tools.tools.get(call.name)
        return bool(t and t.risk == "read")

    # ---- TODO 03.1 : run a batch of tool calls ---------------------------
    def _run_calls(self, calls: list[ToolCall]) -> list[ToolResult]:
        """Consecutive read-only calls run in parallel; the rest, in order.
        Results are returned in the SAME order as the calls."""
        # TODO 03.1: results = [None]*len(calls). Group CONSECUTIVE reads (self._is_read) and run them with ThreadPoolExecutor; the rest in order. For each one: events.on_tool_start, execute (self.execute or self.tools.execute), events.on_tool_end. Return the results in the original order.
        raise NotImplementedError("TODO 03.1")

    # ---- TODO 03.2 : the loop --------------------------------------------
    def run(self, messages: list[dict[str, Any]]) -> AgentResult:
        """`messages` includes system + history + the new user message.
        It is MODIFIED in place: when done it contains everything that happened in the turn."""
        # TODO 03.2: For step 1..max_steps: if self.cancel is set -> 'interrupted'. Consume self.llm.stream(messages, tools=schemas or None): TextDelta -> events.on_text; Done -> resp. Accumulate usage, append resp.to_message(), events.on_assistant. No tool_calls -> 'final'. Loop detection (same tool+args > max_repeats): close the pending tool_calls with an error ToolResult and return 'loop'. Otherwise _run_calls and append the tool messages. At the end: 'max_steps'.
        raise NotImplementedError("TODO 03.2")
