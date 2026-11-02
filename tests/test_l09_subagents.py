from forja.fake_llm import FakeLLM, call, say
from forja.harness import Forja
from forja.subagents import BUILTIN, load_profiles


def test_load_profiles(tmp_path):
    d = tmp_path / "agents"
    d.mkdir()
    (d / "reviewer.md").write_text("---\nname: reviewer\ndescription: Reviews diffs.\ntools: read_file, grep\nmax_steps: 5\n---\nYou are a reviewer.")
    (d / "broken.md").write_text("no frontmatter")
    (d / "incomplete.md").write_text("---\nname: x\n---\nbody")
    p = load_profiles(d)
    assert set(p) == {"explore", "reviewer"}
    assert p["reviewer"].tools == ["read_file", "grep"] and p["reviewer"].max_steps == 5 and p["reviewer"].system == "You are a reviewer."
    assert load_profiles(tmp_path / "missing") == BUILTIN


def test_task_isolated_context(project, home):
    # The SAME FakeLLM serves the main agent and the subagent (in call order).
    llm = FakeLLM([
        call("task", description="where VAT is", prompt="Find where VAT is calculated", subagent_type="explore"),
        call("grep", pattern="def calculate_vat"),           # subagent
        call("read_file", path="invoices/amounts.py"),       # subagent
        say("calculate_vat in invoices/amounts.py:12"),      # subagent: conclusion
        say("It is in invoices/amounts.py:12"),              # main agent
    ])
    app = Forja(llm, project, home=home, persist=False, use_mcp=False)
    r = app.turn("where is VAT calculated?")
    assert r.answer == "It is in invoices/amounts.py:12"
    task_out = next(m["content"] for m in app.history if m["role"] == "tool")
    assert "subagent explore" in task_out and "amounts.py:12" in task_out
    # the main agent's history does NOT contain the subagent's reads
    assert [m.get("name") for m in app.history if m["role"] == "tool"] == ["task"]
    # the subagent started with a clean context and only its own tools
    sub_call = llm.calls[1]
    assert sub_call["messages"][0]["content"].startswith("You are a code exploration subagent") and len(sub_call["messages"]) == 2
    assert {t["function"]["name"] for t in sub_call["tools"]} == {"read_file", "grep", "glob"}


def test_unknown_subagent(project, home):
    app = Forja(FakeLLM([call("task", description="x", prompt="y", subagent_type="pirate"), say("ok")]), project,
                home=home, persist=False, use_mcp=False)
    app.turn("x")
    assert "unknown" in next(m["content"] for m in app.history if m["role"] == "tool")
