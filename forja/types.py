"""Tipos compartidos (DADO)."""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str  # JSON crudo, tal cual lo genera el modelo


@dataclass
class ChatResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)
    model: str = ""
    finish_reason: str | None = None

    def to_message(self) -> dict[str, Any]:
        msg: dict[str, Any] = {"role": "assistant", "content": self.content or ""}
        if self.tool_calls:
            msg["tool_calls"] = [{"id": t.id, "type": "function", "function": {"name": t.name, "arguments": t.arguments}}
                                 for t in self.tool_calls]
        return msg


@dataclass
class TextDelta:
    """Evento de streaming: un trozo de texto visible."""

    text: str


@dataclass
class Done:
    """Evento de streaming: fin de la respuesta, con todo ensamblado."""

    response: ChatResponse


StreamEvent = TextDelta | Done


class ChatModel(Protocol):
    model: str

    def stream(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> Iterator[StreamEvent]: ...

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> ChatResponse: ...
