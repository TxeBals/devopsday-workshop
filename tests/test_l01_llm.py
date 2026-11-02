import json

import httpx
import pytest

from forja.config import Backend, ModelPolicyError, check_model_allowed
from forja.llm import LLMClient, ThinkFilter, ToolCallAccumulator, rescue_text_tool_calls
from forja.types import Done, TextDelta


class D:  # imita los objetos delta del SDK
    def __init__(self, index, id=None, name=None, arguments=None):
        self.index, self.id = index, id
        self.function = type("F", (), {"name": name, "arguments": arguments})()


def test_accumulator_interleaved():
    acc = ToolCallAccumulator()
    acc.add([D(0, id="a", name="read_file", arguments='{"pa')])
    acc.add([D(1, id="b", name="grep", arguments="")])
    acc.add([D(0, arguments='th": "x.py"}'), D(1, arguments='{"pattern": "def"}')])
    acc.add(None)
    calls = acc.finish()
    assert [(c.id, c.name, json.loads(c.arguments)) for c in calls] == [("a", "read_file", {"path": "x.py"}), ("b", "grep", {"pattern": "def"})]


def test_accumulator_empty_args_and_missing_id():
    acc = ToolCallAccumulator()
    acc.add([D(0, name="glob")])
    [c] = acc.finish()
    assert c.arguments == "{}" and c.id


@pytest.mark.parametrize("chunks", [["<think>razono</think>Hola"], ["<thi", "nk>razono</th", "ink>Ho", "la"], ["Ho", "la<", "think>x</think>"]])
def test_think_filter_split_tags(chunks):
    f = ThinkFilter()
    out = "".join(f.feed(c) for c in chunks) + f.flush()
    assert out.replace("\n", "") == "Hola"


def test_think_filter_keeps_normal_lt():
    f = ThinkFilter()
    assert f.feed("a < b") + f.flush() == "a < b"


def test_rescue_text_tool_calls():
    rest, calls = rescue_text_tool_calls('Voy.<tool_call>{"name": "glob", "arguments": {"pattern": "*.py"}}</tool_call>')
    assert rest == "Voy." and calls[0].name == "glob"


def sse(*chunks) -> bytes:
    return "".join(f"data: {json.dumps(c)}\n\n" for c in chunks).encode() + b"data: [DONE]\n\n"


def chunk(delta=None, finish=None, usage=None):
    c = {"id": "x", "object": "chat.completion.chunk", "created": 0, "model": "qwen3:8b",
         "choices": [] if delta is None else [{"index": 0, "delta": delta, "finish_reason": finish}]}
    if usage:
        c["usage"] = usage
    return c


def client(handler) -> LLMClient:
    b = Backend("ollama", "http://fake/v1", "k", "qwen3:8b", extra_body={"provider": {"data_collection": "deny"}})
    return LLMClient(b, max_retries=2, http_client=httpx.Client(transport=httpx.MockTransport(handler)))


def test_stream_text_and_tool_calls():
    seen = {}

    def handler(req):
        seen.update(json.loads(req.content))
        body = sse(chunk({"role": "assistant", "content": "<think>x</think>Mira"}), chunk({"content": "ndo…"}),
                   chunk({"tool_calls": [{"index": 0, "id": "c1", "type": "function", "function": {"name": "read_file", "arguments": '{"path":'}}]}),
                   chunk({"tool_calls": [{"index": 0, "function": {"arguments": ' "a.py"}'}}]}, finish="tool_calls"),
                   chunk(usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}))
        return httpx.Response(200, content=body, headers={"content-type": "text/event-stream"})

    events = list(client(handler).stream([{"role": "user", "content": "hola"}], tools=[{"type": "function", "function": {"name": "read_file", "parameters": {}}}]))
    text = "".join(e.text for e in events if isinstance(e, TextDelta))
    done = events[-1]
    assert isinstance(done, Done) and text == "Mirando…"
    r = done.response
    assert r.content == "Mirando…" and r.tool_calls[0].name == "read_file" and json.loads(r.tool_calls[0].arguments) == {"path": "a.py"}
    assert r.usage == {"prompt_tokens": 10, "completion_tokens": 5}
    assert seen["stream"] is True and seen["tool_choice"] == "auto" and seen["provider"] == {"data_collection": "deny"}


def test_retries_on_503(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    n = {"i": 0}

    def handler(req):
        n["i"] += 1
        if n["i"] < 3:
            return httpx.Response(503, json={"error": "busy"})
        return httpx.Response(200, content=sse(chunk({"content": "ok"}, finish="stop")), headers={"content-type": "text/event-stream"})

    assert client(handler).chat([{"role": "user", "content": "x"}]).content == "ok" and n["i"] == 3


def test_no_retry_on_400(monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    n = {"i": 0}

    def handler(req):
        n["i"] += 1
        return httpx.Response(400, json={"error": "bad"})

    with pytest.raises(Exception):
        client(handler).chat([{"role": "user", "content": "x"}])
    assert n["i"] == 1


@pytest.mark.parametrize("m", ["anthropic/claude-sonnet-4.5", "openai/gpt-5", "gpt-oss:20b", "o3-mini"])
def test_policy(m):
    with pytest.raises(ModelPolicyError):
        check_model_allowed(m)
    assert check_model_allowed("qwen3-coder:30b") == "qwen3-coder:30b"
