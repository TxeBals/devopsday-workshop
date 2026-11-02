import json
import sys
from pathlib import Path

from forja.config import Settings
from forja.fake_llm import FakeLLM, call, say
from forja.harness import Forja
from forja.hooks import HookRunner
from forja.mcp_tools import mcp_tool_name
from forja.skills import catalog, discover_skills

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable.replace("\\", "/")


def hook(code: str) -> str:
    return f'"{PY}" -c "{code}"'


def test_hook_matching_and_exit_codes(tmp_path):
    cfg = {"PreToolUse": [{"matcher": "bash", "command": hook("import sys; print('no', file=sys.stderr); sys.exit(2)")},
                          {"matcher": "edit_file|write_file", "command": hook("import sys; sys.exit(0)")},
                          {"command": hook("import sys; sys.exit(1)")}]}
    runner = HookRunner(cfg, tmp_path)
    # sin matcher = aplica a todas las tools
    assert [h.get("matcher") for h in runner.matching("PreToolUse", "bash")] == ["bash", None]
    assert len(runner.matching("PreToolUse", "write_file")) == 2 and runner.matching("Stop") == []
    out = runner.run("PreToolUse", {"tool_input": {"command": "ls"}}, "bash")
    assert out.block and out.message == "no" and len(out.errors) == 1
    cfg2 = {"UserPromptSubmit": [{"command": hook("import sys, json; d=json.load(sys.stdin); print('ctx:' + d['prompt'])")},
                                 {"command": hook("import sys; sys.exit(1)")}]}
    out2 = HookRunner(cfg2, tmp_path).run("UserPromptSubmit", {"prompt": "hola"})
    assert not out2.block and out2.context == "ctx:hola" and len(out2.errors) == 1


def test_hooks_in_harness(project, home):
    s = Settings(hooks={
        "PreToolUse": [{"matcher": "bash", "command": hook("import sys, json; d=json.load(sys.stdin); c=d['tool_input']['command']; sys.exit(2 if 'rm ' in c else 0)")}],
        "Stop": [{"command": hook("import sys, pathlib; sys.exit(0 if pathlib.Path('HECHO').exists() else 2)")}],
    })
    llm = FakeLLM([call("bash", command="rm -rf facturas"), say("he terminado"),
                   call("write_file", path="HECHO", content="ok"), say("ahora sí")])
    app = Forja(llm, project, mode="bypass", home=home, settings=s, persist=False, use_mcp=False)
    r = app.turn("x")
    tools = [m["content"] for m in app.history if m["role"] == "tool"]
    assert "BLOQUEADO por hook" in tools[0] and (project / "facturas").exists()
    assert r.answer == "ahora sí"  # el hook Stop le obligó a seguir
    assert any(m["role"] == "user" and "[hook Stop]" in m["content"] for m in app.history)


def test_skills(tmp_path, project, home):
    d = project / ".forja" / "skills" / "commits"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("---\nname: commits\ndescription: Cómo hacer\n  commits aquí.\n---\nUsa conventional commits.")
    (project / ".forja" / "skills" / "rota").mkdir()
    (project / ".forja" / "skills" / "rota" / "SKILL.md").write_text("sin frontmatter")
    sk = discover_skills(home / ".forja" / "skills", project / ".forja" / "skills")
    assert list(sk) == ["commits"] and sk["commits"].description == "Cómo hacer commits aquí."
    assert "- commits: Cómo hacer commits aquí." in catalog(sk) and catalog({}) == ""
    llm = FakeLLM([call("skill", name="commits"), say("ok")])
    app = Forja(llm, project, home=home, persist=False, use_mcp=False)
    app.turn("haz commit")
    assert "commits" in llm.calls[0]["messages"][0]["content"]
    out = next(m["content"] for m in app.history if m["role"] == "tool")
    assert "Usa conventional commits." in out and "---" not in out


def test_mcp_name():
    assert mcp_tool_name("issues", "get_issue") == "mcp__issues__get_issue"
    assert mcp_tool_name("mi-wiki", "buscar.docs") == "mcp__mi_wiki__buscar_docs"


def test_mcp_end_to_end(project, home, tmp_path):
    data = tmp_path / "issues.json"
    data.write_text((ROOT / "examples/mcp/issues.json").read_text(encoding="utf-8"), encoding="utf-8")
    server = tmp_path / "issues_server.py"
    server.write_text((ROOT / "examples/mcp/issues_server.py").read_text(encoding="utf-8"), encoding="utf-8")
    s = Settings(mcp_servers={"issues": {"command": [sys.executable, str(server)]}}, allow=["mcp__issues__get_issue"])
    llm = FakeLLM([call("mcp__issues__get_issue", id=12), call("mcp__issues__comment_issue", id=12, texto="hola"), say("ok")])
    app = Forja(llm, project, home=home, settings=s, persist=False)
    try:
        assert {"mcp__issues__list_issues", "mcp__issues__get_issue"} <= set(app.registry.tools)
        app.turn("mira la issue 12")
        tools = [m["content"] for m in app.history if m["role"] == "tool"]
        assert "céntimo" in tools[0]
        assert "DENEGADO" in tools[1]  # exec sin allow y sin nadie para aprobar
    finally:
        app.close()
