from forja.compaction import CLEARED, compact, estimate_tokens, microcompact
from forja.fake_llm import FakeLLM, call, say
from forja.config import Settings
from forja.harness import Forja


def history(turns=4, big=2000):
    h = []
    for i in range(turns):
        h += [{"role": "user", "content": f"question {i}"},
              {"role": "assistant", "content": "", "tool_calls": [{"id": f"c{i}", "type": "function", "function": {"name": "read_file", "arguments": "{}"}}]},
              {"role": "tool", "tool_call_id": f"c{i}", "name": "read_file", "content": "x" * big},
              {"role": "assistant", "content": f"answer {i}"}]
    return h


def valid_pairs(h):
    open_ids = set()
    for m in h:
        if m["role"] == "assistant":
            if open_ids:
                return False
            open_ids = {t["id"] for t in m.get("tool_calls", [])}
        elif m["role"] == "tool":
            if m["tool_call_id"] not in open_ids:
                return False
            open_ids.discard(m["tool_call_id"])
    return not open_ids


def test_microcompact():
    h = history()
    before = estimate_tokens(h)
    assert microcompact(h, keep_recent_turns=2) == 2
    tools = [m["content"] for m in h if m["role"] == "tool"]
    assert tools[:2] == [CLEARED, CLEARED] and tools[2:] == ["x" * 2000] * 2
    assert estimate_tokens(h) < before * 0.6 and valid_pairs(h)
    assert microcompact(h, keep_recent_turns=2) == 0


def test_compact_keeps_pairs_and_recent():
    h = history()
    llm = FakeLLM([say("SUMMARY: files were read")])
    new, done = compact(h, llm, keep_recent_turns=2)
    assert done and new[0]["content"].startswith("[Summary") and "SUMMARY" in new[0]["content"]
    assert new[2:] == h[8:] and valid_pairs(new)
    prompt = llm.calls[0]["messages"][1]["content"]
    assert "question 0" in prompt and "question 3" not in prompt
    assert compact(history(1), llm)[1] is False


def test_harness_autocompacts(project, home):
    script = []
    for i in range(4):
        script += [call("read_file", path="invoices/invoice.py"), say(f"ok {i}")]
    llm = FakeLLM(script + [say("SUMMARY"), say("end")])
    app = Forja(llm, project, home=home, persist=False, use_mcp=False, settings=Settings(context_window=1500))
    for i in range(4):
        app.turn(f"turn {i}")
    app.turn("last")
    assert any("compact" in n for n in app.notes)
    assert valid_pairs(app.history)
