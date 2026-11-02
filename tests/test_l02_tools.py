import json
import os
import time

import pytest

from forja.fs_tools import Workspace, make_fs_tools
from forja.tools import ToolRegistry, tool
from forja.types import ToolCall


def run(reg, name, **args):
    return reg.execute(ToolCall("c1", name, json.dumps(args)))


@pytest.fixture()
def reg(project):
    ws = Workspace(project)
    return ToolRegistry().register(*make_fs_tools(ws)), ws


def test_schema_from_type_hints():
    @tool(risk="edit")
    def f(path: str, n: int = 3) -> str:
        """Does something.

        Args:
            path: Path.
            n: Number.
        """
        return path

    s = f.schema()["function"]
    assert s["name"] == "f" and s["description"] == "Does something."
    assert s["parameters"]["required"] == ["path"] and s["parameters"]["properties"]["n"]["default"] == 3
    assert s["parameters"]["properties"]["path"]["description"] == "Path." and s["parameters"]["additionalProperties"] is False
    assert "title" not in s["parameters"]


def test_execute_never_raises(reg):
    r, _ = reg
    assert "does not exist" in run(r, "nope").output
    assert not r.execute(ToolCall("c", "read_file", "{bad")).ok
    assert "Validation" in run(r, "read_file", path="x", offset="a").output
    assert not run(r, "read_file", path="x", extra=1).ok


def test_read_numbered_and_paging(reg):
    r, _ = reg
    out = run(r, "read_file", path="invoices/amounts.py").output
    assert out.splitlines()[0].strip().startswith("1→") and "def round_amount" in out
    page = run(r, "read_file", path="invoices/amounts.py", offset=2, limit=2).output
    assert page.splitlines()[0].strip().startswith("2→") and "more lines" in page


def test_sandbox(reg):
    r, _ = reg
    for bad in ["../secret.txt", "/etc/passwd"]:
        res = run(r, "read_file", path=bad)
        assert not res.ok and "outside the workspace" in res.output


def test_edit_requires_read_and_unique(reg):
    r, ws = reg
    res = run(r, "edit_file", path="invoices/amounts.py", old_string="round(value, 2)", new_string="X")
    assert not res.ok and "before modifying" in res.output
    run(r, "read_file", path="invoices/amounts.py")
    dup = run(r, "edit_file", path="invoices/amounts.py", old_string="return", new_string="return ")
    assert not dup.ok and "times" in dup.output
    miss = run(r, "edit_file", path="invoices/amounts.py", old_string="     9→    return round(value, 2)", new_string="x")
    assert not miss.ok and "line numbers" in miss.output
    ok = run(r, "edit_file", path="invoices/amounts.py", old_string="    return round(value, 2)", new_string="    return round(value + 1e-9, 2)")
    assert ok.ok and ok.meta["diff"].count("\n+    return round(value + 1e-9, 2)") == 1
    assert "1e-9" in (ws.root / "invoices/amounts.py").read_text()


def test_edit_detects_external_change(reg):
    r, ws = reg
    run(r, "read_file", path="invoices/dates.py")
    p = ws.root / "invoices/dates.py"
    time.sleep(0.01)
    p.write_text(p.read_text() + "\n# touched by the human\n")
    os.utime(p, (time.time() + 5, time.time() + 5))
    res = run(r, "edit_file", path="invoices/dates.py", old_string="days: int = 30", new_string="days: int = 60")
    assert not res.ok and "has changed" in res.output


def test_write_new_and_overwrite_rules(reg):
    r, ws = reg
    assert run(r, "write_file", path="docs/note.md", content="hello\n").ok
    assert (ws.root / "docs/note.md").read_text() == "hello\n"
    res = run(r, "write_file", path="invoices/dates.py", content="x")
    assert not res.ok and "before modifying" in res.output


def test_grep_and_glob(reg):
    r, _ = reg
    g = run(r, "grep", pattern=r"def (round_amount|due_date)", include="*.py").output
    assert "invoices/amounts.py:7:" in g and "invoices/dates.py" in g
    assert run(r, "grep", pattern="calculate_vat", show_content=False).output.splitlines()[0].endswith(".py")
    files = run(r, "glob", pattern="tests/test_*.py").output.splitlines()
    assert set(files) == {"tests/test_amounts.py", "tests/test_dates.py", "tests/test_invoice.py"}
    assert run(r, "glob", pattern="*.rs").output == "(no results)"
