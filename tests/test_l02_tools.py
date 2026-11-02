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
        """Hace algo.

        Args:
            path: Ruta.
            n: Número.
        """
        return path

    s = f.schema()["function"]
    assert s["name"] == "f" and s["description"] == "Hace algo."
    assert s["parameters"]["required"] == ["path"] and s["parameters"]["properties"]["n"]["default"] == 3
    assert s["parameters"]["properties"]["path"]["description"] == "Ruta." and s["parameters"]["additionalProperties"] is False
    assert "title" not in s["parameters"]


def test_execute_never_raises(reg):
    r, _ = reg
    assert "no existe" in run(r, "nope").output
    assert not r.execute(ToolCall("c", "read_file", "{malo")).ok
    assert "validación" in run(r, "read_file", path="x", offset="a").output
    assert not run(r, "read_file", path="x", extra=1).ok


def test_read_numbered_and_paging(reg):
    r, _ = reg
    out = run(r, "read_file", path="facturas/importes.py").output
    assert out.splitlines()[0].strip().startswith("1→") and "def redondear" in out
    page = run(r, "read_file", path="facturas/importes.py", offset=2, limit=2).output
    assert page.splitlines()[0].strip().startswith("2→") and "líneas más" in page


def test_sandbox(reg):
    r, _ = reg
    for bad in ["../secret.txt", "/etc/passwd"]:
        res = run(r, "read_file", path=bad)
        assert not res.ok and "fuera del workspace" in res.output


def test_edit_requires_read_and_unique(reg):
    r, ws = reg
    res = run(r, "edit_file", path="facturas/importes.py", old_string="round(valor, 2)", new_string="X")
    assert not res.ok and "lee" in res.output
    run(r, "read_file", path="facturas/importes.py")
    dup = run(r, "edit_file", path="facturas/importes.py", old_string="return", new_string="return ")
    assert not dup.ok and "veces" in dup.output
    miss = run(r, "edit_file", path="facturas/importes.py", old_string="     9→    return round(valor, 2)", new_string="x")
    assert not miss.ok and "números de línea" in miss.output
    ok = run(r, "edit_file", path="facturas/importes.py", old_string="    return round(valor, 2)", new_string="    return round(valor + 1e-9, 2)")
    assert ok.ok and ok.meta["diff"].count("\n+    return round(valor + 1e-9, 2)") == 1
    assert "1e-9" in (ws.root / "facturas/importes.py").read_text()


def test_edit_detects_external_change(reg):
    r, ws = reg
    run(r, "read_file", path="facturas/fechas.py")
    p = ws.root / "facturas/fechas.py"
    time.sleep(0.01)
    p.write_text(p.read_text() + "\n# tocado por el humano\n")
    os.utime(p, (time.time() + 5, time.time() + 5))
    res = run(r, "edit_file", path="facturas/fechas.py", old_string="dias: int = 30", new_string="dias: int = 60")
    assert not res.ok and "ha cambiado" in res.output


def test_write_new_and_overwrite_rules(reg):
    r, ws = reg
    assert run(r, "write_file", path="docs/nota.md", content="hola\n").ok
    assert (ws.root / "docs/nota.md").read_text() == "hola\n"
    res = run(r, "write_file", path="facturas/fechas.py", content="x")
    assert not res.ok and "lee" in res.output


def test_grep_and_glob(reg):
    r, _ = reg
    g = run(r, "grep", pattern=r"def (redondear|vencimiento)", include="*.py").output
    assert "facturas/importes.py:7:" in g and "facturas/fechas.py" in g
    assert run(r, "grep", pattern="calcular_iva", show_content=False).output.splitlines()[0].endswith(".py")
    files = run(r, "glob", pattern="tests/test_*.py").output.splitlines()
    assert set(files) == {"tests/test_importes.py", "tests/test_fechas.py", "tests/test_factura.py"}
    assert run(r, "glob", pattern="*.rs").output == "(sin resultados)"
