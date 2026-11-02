from forja.context import build_system_prompt, expand_mentions, find_instruction_files
from forja.fs_tools import Workspace


def test_find_instruction_files_order(tmp_path, home):
    (home / ".forja").mkdir()
    (home / ".forja" / "AGENTS.md").write_text("global")
    repo = tmp_path / "repo"
    sub = repo / "pkg"
    sub.mkdir(parents=True)
    (repo / "AGENTS.md").write_text("root")
    (sub / "AGENTS.md").write_text("package")
    files = find_instruction_files(sub, home=home, stop=tmp_path)
    assert [f.read_text() for f in files] == ["global", "root", "package"]


def test_system_prompt_layers(project, home):
    ws = Workspace(project)
    sp = build_system_prompt(ws, "plan", "qwen3:8b", home=home, skills_catalog="## Skills\n- x", extra=["## Extra", ""])
    assert "You are Forja" in sp and "PLAN mode" in sp
    assert "half-up" in sp  # comes from the playground's AGENTS.md
    assert "## Skills" in sp and "## Extra" in sp and "qwen3:8b" in sp and str(project) in sp
    assert sp.index("PLAN mode") < sp.index("half-up") < sp.index("## Environment")


def test_expand_mentions(project):
    ws = Workspace(project)
    out = expand_mentions("Review @invoices/dates.py, and @nobody or @../../etc/passwd. Write to joe@mail.com", ws)
    assert out.count("<file") == 1 and 'path="invoices/dates.py"' in out and "def due_date" in out
    assert ws.root / "invoices/dates.py" in ws.read_state  # counts as read
    assert expand_mentions("no mentions", ws) == "no mentions"
