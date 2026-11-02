"""Scripted LLM for tests and GPU-less demos (PROVIDED)."""
from __future__ import annotations

import json
import uuid
from collections.abc import Callable, Iterator
from typing import Any

from .types import ChatResponse, Done, StreamEvent, TextDelta, ToolCall


def call(name: str, /, **args: Any) -> ChatResponse:
    return ChatResponse(None, [ToolCall(f"call_{uuid.uuid4().hex[:6]}", name, json.dumps(args, ensure_ascii=False))], finish_reason="tool_calls")


def calls(*pairs: tuple[str, dict]) -> ChatResponse:
    """Several tool calls in one response (parallel calls)."""
    return ChatResponse(None, [ToolCall(f"call_{uuid.uuid4().hex[:6]}", n, json.dumps(a, ensure_ascii=False)) for n, a in pairs],
                        finish_reason="tool_calls")


def say(text: str) -> ChatResponse:
    return ChatResponse(text, finish_reason="stop")


Step = ChatResponse | Callable[[list[dict], list[dict] | None], ChatResponse]


class FakeLLM:
    def __init__(self, script: list[Step], model: str = "fake"):
        self.script = list(script)
        self.model = model
        self.calls: list[dict] = []

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> ChatResponse:
        self.calls.append({"messages": [dict(m) for m in messages], "tools": tools, "kw": kw})
        if not self.script:
            return say("(end of script)")
        step = self.script.pop(0)
        r = step(messages, tools) if callable(step) else step
        r.model = self.model
        r.usage = r.usage or {"prompt_tokens": sum(len(str(m.get("content") or "")) for m in messages) // 4 + 50, "completion_tokens": 20}
        return r

    def stream(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> Iterator[StreamEvent]:
        r = self.chat(messages, tools, **kw)
        text = r.content or ""
        for i in range(0, len(text), 8):
            yield TextDelta(text[i:i + 8])
        yield Done(r)
