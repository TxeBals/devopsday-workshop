from forja.fake_llm import FakeLLM, call, say
from forja.harness import Forja
from forja.subagents import BUILTIN, load_profiles


def test_load_profiles(tmp_path):
    d = tmp_path / "agents"
    d.mkdir()
    (d / "revisor.md").write_text("---\nname: revisor\ndescription: Revisa diffs.\ntools: read_file, grep\nmax_steps: 5\n---\nEres un revisor.")
    (d / "roto.md").write_text("sin frontmatter")
    (d / "incompleto.md").write_text("---\nname: x\n---\ncuerpo")
    p = load_profiles(d)
    assert set(p) == {"explore", "revisor"}
    assert p["revisor"].tools == ["read_file", "grep"] and p["revisor"].max_steps == 5 and p["revisor"].system == "Eres un revisor."
    assert load_profiles(tmp_path / "no_existe") == BUILTIN


def test_task_isolated_context(project, home):
    # El MISMO FakeLLM sirve al principal y al subagente (en orden de llamada).
    llm = FakeLLM([
        call("task", description="dónde está el IVA", prompt="Encuentra dónde se calcula el IVA", subagent_type="explore"),
        call("grep", pattern="def calcular_iva"),            # subagente
        call("read_file", path="facturas/importes.py"),      # subagente
        say("calcular_iva en facturas/importes.py:12"),      # subagente: conclusión
        say("Está en facturas/importes.py:12"),              # principal
    ])
    app = Forja(llm, project, home=home, persist=False, use_mcp=False)
    r = app.turn("¿dónde se calcula el IVA?")
    assert r.answer == "Está en facturas/importes.py:12"
    task_out = next(m["content"] for m in app.history if m["role"] == "tool")
    assert "subagente explore" in task_out and "importes.py:12" in task_out
    # el historial del principal NO contiene las lecturas del subagente
    assert [m.get("name") for m in app.history if m["role"] == "tool"] == ["task"]
    # el subagente empezó con contexto limpio y solo con sus tools
    sub_call = llm.calls[1]
    assert sub_call["messages"][0]["content"].startswith("Eres un subagente") and len(sub_call["messages"]) == 2
    assert {t["function"]["name"] for t in sub_call["tools"]} == {"read_file", "grep", "glob"}


def test_unknown_subagent(project, home):
    app = Forja(FakeLLM([call("task", description="x", prompt="y", subagent_type="pirata"), say("vale")]), project,
                home=home, persist=False, use_mcp=False)
    app.turn("x")
    assert "desconocido" in next(m["content"] for m in app.history if m["role"] == "tool")
