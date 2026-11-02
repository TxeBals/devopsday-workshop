from forja.context import build_system_prompt, expand_mentions, find_instruction_files
from forja.fs_tools import Workspace


def test_find_instruction_files_order(tmp_path, home):
    (home / ".forja").mkdir()
    (home / ".forja" / "AGENTS.md").write_text("global")
    repo = tmp_path / "repo"
    sub = repo / "pkg"
    sub.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("raíz")
    (sub / "AGENTS.md").write_text("paquete")
    files = find_instruction_files(sub, home=home, stop=tmp_path)
    assert [f.read_text() for f in files] == ["global", "raíz", "paquete"]


def test_system_prompt_layers(project, home):
    ws = Workspace(project)
    sp = build_system_prompt(ws, "plan", "qwen3:8b", home=home, skills_catalog="## Skills\n- x", extra=["## Extra", ""])
    assert "Eres Forja" in sp and "Modo PLAN" in sp
    assert "half-up" in sp  # viene del AGENTS.md del playground
    assert "## Skills" in sp and "## Extra" in sp and "qwen3:8b" in sp and str(project) in sp
    assert sp.index("Modo PLAN") < sp.index("half-up") < sp.index("## Entorno")


def test_expand_mentions(project):
    ws = Workspace(project)
    out = expand_mentions("Revisa @facturas/fechas.py, y @nadie o @../../etc/passwd. Escribe a pepe@correo.com", ws)
    assert out.count("<fichero") == 1 and 'ruta="facturas/fechas.py"' in out and "def vencimiento" in out
    assert ws.root / "facturas/fechas.py" in ws.read_state  # cuenta como leído
    assert expand_mentions("sin menciones", ws) == "sin menciones"
