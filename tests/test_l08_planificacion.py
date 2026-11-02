import json

from forja.fake_llm import FakeLLM, call, say
from forja.harness import Forja
from forja.planning import TodoStore, make_exit_plan_tool, make_todo_tool
from forja.tools import ToolRegistry
from forja.types import ToolCall


def test_todo_write_validation():
    store = TodoStore()
    reg = ToolRegistry().register(make_todo_tool(store))
    ok = reg.execute(ToolCall("c", "todo_write", json.dumps({"todos": [{"content": "leer", "status": "completed"}, {"content": "editar", "status": "in_progress"}, {"content": "tests"}]})))
    assert ok.ok and "1/3" in ok.output and store.render().splitlines() == ["☑ leer", "▶ editar", "☐ tests"]
    two = reg.execute(ToolCall("c", "todo_write", json.dumps({"todos": [{"content": "a", "status": "in_progress"}, {"content": "b", "status": "in_progress"}]})))
    assert not two.ok and "una tarea" in two.output and len(store.items) == 3


def test_exit_plan_tool():
    state = {}
    reg = ToolRegistry().register(make_exit_plan_tool(lambda p: "OK" in p, lambda: state.setdefault("approved", True)))
    no = reg.execute(ToolCall("c", "exit_plan_mode", json.dumps({"plan": "cambiar cosas"})))
    assert "RECHAZÓ" in no.output and not state
    yes = reg.execute(ToolCall("c", "exit_plan_mode", json.dumps({"plan": "OK: 1) editar 2) tests"})))
    assert "APROBÓ" in yes.output and state["approved"]


def test_plan_mode_flow(project, home):
    llm = FakeLLM([call("edit_file", path="facturas/fechas.py", old_string="a", new_string="b"),
                   call("exit_plan_mode", plan="1. arreglar vencimiento 2. tests"),
                   call("todo_write", todos=[{"content": "arreglar", "status": "in_progress"}]), say("listo")])
    app = Forja(llm, project, mode="plan", home=home, persist=False, use_mcp=False, plan_approver=lambda p: True)
    app.turn("arregla el vencimiento")
    tools = [m["content"] for m in app.history if m["role"] == "tool"]
    assert "DENEGADO" in tools[0] and "modo plan" in tools[0]
    assert "APROBÓ" in tools[1] and app.mode == "default"
    # la lista de tareas entra en el system prompt del siguiente paso
    assert "▶ arreglar" in llm.calls[-1]["messages"][0]["content"] or "▶ arreglar" in app.system_prompt()
    assert "Modo PLAN" in llm.calls[0]["messages"][0]["content"]
