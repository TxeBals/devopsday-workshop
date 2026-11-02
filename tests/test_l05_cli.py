from forja.cli import ask_approval, diff_styles, handle_slash, summarize_call
from forja.fake_llm import FakeLLM, say
from forja.harness import Forja


def test_summarize_call():
    assert summarize_call("read_file", {"path": "a.py"}) == "Read a.py"
    assert summarize_call("read_file", {"path": "a.py", "offset": 50}) == "Read a.py (from line 50)"
    assert summarize_call("bash", {"command": "pytest  -q\n"}) == "$ pytest -q"
    assert summarize_call("grep", {"pattern": "def x", "path": "src", "include": "*.py"}) == "Grep 'def x' in src (*.py)"
    assert summarize_call("write_file", {"path": "n.md", "content": "a\nb"}) == "Write n.md (2 lines)"
    assert summarize_call("task", {"description": "find VAT"}) == "Task[explore] find VAT"
    assert summarize_call("mcp__x__y", {"id": 3}) == "mcp__x__y(id=3)"
    assert len(summarize_call("bash", {"command": "x" * 500}, width=50)) == 50


def test_diff_styles():
    d = "--- a/x\n+++ b/x\n@@ -1 +1 @@\n-old\n+new\n ctx"
    assert [s for _, s in diff_styles(d)] == ["bold", "bold", "cyan", "red", "green", "dim"]


def test_ask_approval(project):
    app = Forja(FakeLLM([]), project, persist=False, use_mcp=False)
    t = app.registry.tools["bash"]
    assert ask_approval(t, {"command": "ls"}, "x", read=lambda _: "y") == "yes"
    assert ask_approval(t, {"command": "ls"}, "x", read=lambda _: "a") == "always"
    assert ask_approval(t, {"command": "ls"}, "x", read=lambda _: "") == "no"


def test_slash_commands(project, home):
    from forja.planning import TodoItem

    app = Forja(FakeLLM([say("done")]), project, home=home, persist=False, use_mcp=False)
    app.turn("do things")
    app.todos.items = [TodoItem(content="a", status="in_progress")]
    assert handle_slash(app, "/exit") is None
    assert "/mode" in handle_slash(app, "/help")
    assert handle_slash(app, "/mode plan") == "mode -> plan" and app.mode == "plan"
    assert "bash" in handle_slash(app, "/tools") and "[exec]" in handle_slash(app, "/tools")
    assert "▶ a" in handle_slash(app, "/todos")
    assert "tokens" in handle_slash(app, "/context") and "input" in handle_slash(app, "/cost")
    assert handle_slash(app, "/clear") == "new conversation" and app.history == []
    assert "unknown" in handle_slash(app, "/nope")
