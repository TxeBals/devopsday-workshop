"""LAB 01 — Cliente LLM con streaming (Ollama, vLLM, LM Studio, OpenRouter).

Un agente de código se siente "vivo" porque el texto llega token a token. Pero en
streaming las tool calls también llegan troceadas: primero el id y el nombre, luego
los argumentos JSON en pedazos, a veces de varias llamadas intercaladas por índice.
Ensamblarlas bien es la primera pieza seria del harness.
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


# ---- TODO 01.1 : ensamblar tool calls que llegan troceadas -------------
@dataclass
class ToolCallAccumulator:
    """Recibe los `delta.tool_calls` de cada chunk y reconstruye las llamadas completas.

    Cada fragmento trae `index` (qué llamada), y opcionalmente `id`, `function.name`
    y un trozo de `function.arguments` que hay que CONCATENAR.
    """

    _parts: dict[int, dict[str, str]] = field(default_factory=dict)

    def add(self, deltas: list[Any] | None) -> None:
        # TODO 01.1: Para cada delta: slot = self._parts.setdefault(d.index, {'id': '', 'name': '', 'arguments': ''}). Si d.id, guárdalo. Si d.function: CONCATENA name y arguments (llegan troceados).
        raise NotImplementedError("TODO 01.1")

    def finish(self) -> list[ToolCall]:
        # TODO 01.1: Recorre los índices en orden; ignora los que no tienen name; crea ToolCall(id o uno generado, name, arguments o '{}').
        raise NotImplementedError("TODO 01.1")


# ---- TODO 01.2 : filtrar <think>…</think> en streaming --------------------
@dataclass
class ThinkFilter:
    """Los modelos que razonan (qwen3, deepseek-r1) emiten <think>…</think>. En streaming
    las etiquetas pueden partirse entre chunks ("<thi" + "nk>"): hay que tener un búfer."""

    in_think: bool = False
    buf: str = ""

    def feed(self, text: str) -> str:
        # TODO 01.2: Añade el texto a self.buf. Fuera de <think>: emite hasta la etiqueta de apertura (y retén al final un posible principio de '<think>', p. ej. '<thi'). Dentro: descarta hasta '</think>' (reteniendo un posible cierre partido). Devuelve el texto visible.
        raise NotImplementedError("TODO 01.2")

    def flush(self) -> str:
        rest, self.buf = ("" if self.in_think else self.buf), ""
        return rest


def rescue_text_tool_calls(text: str) -> tuple[str, list[ToolCall]]:
    """Algunos modelos locales escriben la llamada como texto <tool_call>{…}</tool_call>."""
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

    # ---- TODO 01.3 : streaming con reintentos y ensamblado final --------
    def stream(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> Iterator[StreamEvent]:
        # TODO 01.3: params = self._params(...). Crea el stream con reintentos (RETRYABLE, backoff 1,2,4 s; los 4xx no). Por cada chunk: usage si viene; delta.content -> ThinkFilter -> yield TextDelta; delta.tool_calls -> acumulador. Al final: flush, si no hay tool calls prueba rescue_text_tool_calls, y yield Done(ChatResponse(...)).
        raise NotImplementedError("TODO 01.3")

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kw: Any) -> ChatResponse:
        for ev in self.stream(messages, tools, **kw):
            if isinstance(ev, Done):
                return ev.response
        raise RuntimeError("stream sin evento Done")
