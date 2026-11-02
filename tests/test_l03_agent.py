import threading
import time

from forja.agent import Agent, Events
from forja.fake_llm import FakeLLM, call, calls, say
from forja.tools import ToolRegistry, tool


@tool(risk="read")
def lento(n: int) -> str:
    """Tarda."""
    time.sleep(0.2)
    return f"r{n}"


@tool(risk="edit")
def escribe(x: str) -> str:
    """Escribe."""
    return f"w{x}"


def reg():
    return ToolRegistry().register(lento, escribe)


def test_final_answer():
    msgs = [{"role": "user", "content": "hola"}]
    r = Agent(FakeLLM([say("hola!")]), reg()).run(msgs)
    assert (r.answer, r.stop_reason, r.steps) == ("hola!", "final", 1) and msgs[-1]["role"] == "assistant"


def test_streaming_events():
    got = []

    class E(Events):
        def on_text(self, d):
            got.append(d)

    Agent(FakeLLM([say("un texto bastante largo")]), reg(), events=E()).run([{"role": "user", "content": "x"}])
    assert "".join(got) == "un texto bastante largo" and len(got) > 1


def test_parallel_reads_keep_order():
    msgs = [{"role": "user", "content": "x"}]
    llm = FakeLLM([calls(("lento", {"n": 1}), ("lento", {"n": 2}), ("lento", {"n": 3}), ("escribe", {"x": "a"})), say("ok")])
    t0 = time.time()
    r = Agent(llm, reg()).run(msgs)
    assert time.time() - t0 < 0.5  # 3 lecturas de 0,2 s en paralelo
    tools = [m["content"] for m in msgs if m["role"] == "tool"]
    assert tools == ["r1", "r2", "r3", "wa"] and r.tool_calls == 4
    ids = [tc["id"] for tc in msgs[1]["tool_calls"]]
    assert [m["tool_call_id"] for m in msgs if m["role"] == "tool"] == ids


def test_custom_execute_gate():
    seen = []

    def gate(c):
        seen.append(c.name)
        return reg().execute(c)

    Agent(FakeLLM([call("escribe", x="b"), say("ok")]), reg(), execute=gate).run([{"role": "user", "content": "x"}])
    assert seen == ["escribe"]


def test_max_steps_and_loop():
    r = Agent(FakeLLM([call("escribe", x=str(i)) for i in range(10)]), reg(), max_steps=3).run([{"role": "user", "content": "x"}])
    assert r.stop_reason == "max_steps"
    msgs = [{"role": "user", "content": "x"}]
    r = Agent(FakeLLM([call("escribe", x="1") for _ in range(10)]), reg(), max_repeats=2).run(msgs)
    assert r.stop_reason == "loop"
    # el historial queda válido: cada tool_call tiene su respuesta
    last_calls = [tc["id"] for tc in msgs[-2 if msgs[-1]["role"] == "tool" else -1].get("tool_calls", [])] if False else None
    open_ids = set()
    for m in msgs:
        if m["role"] == "assistant":
            assert not open_ids
            open_ids = {tc["id"] for tc in m.get("tool_calls", [])}
        elif m["role"] == "tool":
            open_ids.discard(m["tool_call_id"])
    assert not open_ids


def test_cancel():
    ev = threading.Event()
    ev.set()
    r = Agent(FakeLLM([say("x")]), reg(), cancel=ev).run([{"role": "user", "content": "x"}])
    assert r.stop_reason == "interrupted"
