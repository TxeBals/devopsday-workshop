"""LAB 01 — Streaming LLM client (Ollama, vLLM, LM Studio, OpenRouter).

A coding agent feels "alive" because text arrives token by token. But when
streaming, tool calls also arrive in pieces: first the id and the name, then
the JSON arguments in fragments, sometimes from several calls interleaved by index.
Assembling them correctly is the first serious piece of the harness.
"""
from __future__ import annotations

import json
import re
import time
import uuid
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx
import openai
from openai import OpenAI

from .config import Backend, check_model_allowed
from .types import ChatResponse, Done, StreamEvent, TextDelta, ToolCall

RETRYABLE = (openai.APIConnectionError, openai.APITimeoutError, openai.RateLimitError, openai.InternalServerError)
TEXT_TOOLCALL_RE = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.S)


# ---- TODO 01.1 : assemble tool calls that arrive in pieces ------------
@dataclass
class ToolCallAccumulator:
    """Receives each chunk's `delta.tool_calls` and rebuilds the complete calls.

    Each fragment carries `index` (which call), and optionally `id`, `function.name`
    and a piece of `function.arguments` that must be CONCATENATED.
    """

    _parts: dict[int, dict[str, str]] = field(default_factory=dict)

    def add(self, deltas: list[Any] | None) -> None:
        # TODO 01.1: For each delta: slot = self._parts.setdefault(d.index, {'id': '', 'name': '', 'arguments': ''}). If d.id, store it. If d.function: CONCATENATE name and arguments (they arrive in pieces).
        raise NotImplementedError("TODO 01.1")

    def finish(self) -> list[ToolCall]:
        # TODO 01.1: Walk the indices in order; skip those without a name; build ToolCall(id or a generated one, name, arguments or '{}').
        raise NotImplementedError("TODO 01.1")


# ---- TODO 01.2 : filter <think>…</think> while streaming ------------------
@dataclass
class ThinkFilter:
    """Reasoning models (qwen3, deepseek-r1) emit <think>…</think>. When streaming,
    the tags can be split across chunks ("<thi" + "nk>"): a buffer is needed."""

    in_think: bool = False
    buf: str = ""

    def feed(self, text: str) -> str:
        # TODO 01.2: Append the text to self.buf. Outside <think>: emit up to the opening tag (and hold back at the end a possible start of '<think>', e.g. '<thi'). Inside: discard up to '</think>' (holding back a possible split closing tag). Return the visible text.
        raise NotImplementedError("TODO 01.2")

    def flush(self) -> str:
        rest, self.buf = ("" if self.in_think else self.buf), ""
        return rest


def rescue_text_tool_calls(text: str) -> tuple[str, list[ToolCall]]:
    """Some local models write the call as text: <tool_call>{…}</tool_call>."""
    calls = []
    for raw in TEXT_TOOLCALL_RE.findall(text or ""):
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if obj.get("name"):
            args = obj.get("arguments", {})
            calls.append(ToolCall(f"txt_{uuid.uuid4().hex[:8]}", obj["name"], args if isinstance(args, str) else json.dumps(args)))
    return TEXT_TOOLCALL_RE.sub("", text or "").strip(), calls


class LLMClient:
    def __init__(self, backend: Backend, *, timeout: float = 300.0, max_retries: int = 3, temperature: float = 0.2,
                 max_tokens: int = 8192, http_client: httpx.Client | None = None):
        check_model_allowed(backend.model)
        self.backend = backend
        self.model = backend.model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self._client = OpenAI(base_url=backend.base_url, api_key=backend.api_key or "x", timeout=timeout, max_retries=0,
                              default_headers=backend.extra_headers or None, http_client=http_client)

    def _params(self, messages: list[dict], tools: list[dict] | None, **kw: Any) -> dict[str, Any]:
        p: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": kw.pop("temperature", self.temperature),
                             "max_tokens": kw.pop("max_tokens", self.max_tokens), "stream": True,
                             "stream_options": {"include_usage": True}}
        if tools:
            p["tools"] = tools
            p["tool_choice"] = "auto"
        if self.backend.extra_body:
            p["extra_body"] = self.backend.extra_body
        p.update(kw)
        return p

    # ---- TODO 01.3 : streaming with retries and final assembly ---------
    def stream(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> Iterator[StreamEvent]:
        # TODO 01.3: params = self._params(...). Create the stream with retries (RETRYABLE, backoff 1, 2, 4 s; not for 4xx). For each chunk: usage if present; delta.content -> ThinkFilter -> yield TextDelta; delta.tool_calls -> accumulator. At the end: flush, if there are no tool calls try rescue_text_tool_calls, and yield Done(ChatResponse(...)).
        raise NotImplementedError("TODO 01.3")

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> ChatResponse:
        for ev in self.stream(messages, tools, **kw):
            if isinstance(ev, Done):
                return ev.response
        raise RuntimeError("stream without a Done event")
