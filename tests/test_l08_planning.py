import json

from forja.fake_llm import FakeLLM, call, say
from forja.harness import Forja
from forja.planning import TodoStore, make_exit_plan_tool, make_todo_tool
from forja.tools import ToolRegistry
from forja.types import ToolCall


def test_todo_write_validation():
    store = TodoStore()
    reg = ToolRegistry().register(make_todo_tool(store))
    ok = reg.execute(ToolCall("c", "todo_write", json.dumps({"todos": [{"content": "read", "status": "completed"}, {"content": "edit", "status": "in_progress"}, {"content": "tests"}]})))
    assert ok.ok and "1/3" in ok.output and store.render().splitlines() == ["☑ read", "▶ edit", "☐ tests"]
    two = reg.execute(ToolCall("c", "todo_write", json.dumps({"todos": [{"content": "a", "status": "in_progress"}, {"content": "b", "status": "in_progress"}]})))
    assert not two.ok and "one task" in two.output and len(store.items) == 3


def test_exit_plan_tool():
    state = {}
    reg = ToolRegistry().register(make_exit_plan_tool(lambda p: "OK" in p, lambda: state.setdefault("approved", True)))
    no = reg.execute(ToolCall("c", "exit_plan_mode", json.dumps({"plan": "change things"})))
    assert "REJECTED" in no.output and not state
    yes = reg.execute(ToolCall("c", "exit_plan_mode", json.dumps({"plan": "OK: 1) edit 2) tests"})))
    assert "APPROVED" in yes.output and state["approved"]


def test_plan_mode_flow(project, home):
    llm = FakeLLM([call("edit_file", path="invoices/dates.py", old_string="a", new_string="b"),
                   call("exit_plan_mode", plan="1. fix due_date 2. tests"),
                   call("todo_write", todos=[{"content": "fix", "status": "in_progress"}]), say("done")])
    app = Forja(llm, project, mode="plan", home=home, persist=False, use_mcp=False, plan_approver=lambda p: True)
    app.turn("fix the due date")
    tools = [m["content"] for m in app.history if m["role"] == "tool"]
    assert "DENIED" in tools[0] and "plan mode" in tools[0]
    assert "APPROVED" in tools[1] and app.mode == "default"
    # the task list goes into the system prompt of the next step
    assert "▶ fix" in llm.calls[-1]["messages"][0]["content"] or "▶ fix" in app.system_prompt()
    assert "PLAN mode" in llm.calls[0]["messages"][0]["content"]
