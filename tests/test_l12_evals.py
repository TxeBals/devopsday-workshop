from pathlib import Path

from forja.evals import EvalTask, grade, load_tasks, run_task, snapshot, summarize, TaskResult
from forja.fake_llm import FakeLLM, call, say

ROOT = Path(__file__).resolve().parents[1]
FIX = "    return float(Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))"


def solver():
    return FakeLLM([
        call("read_file", path="facturas/importes.py"),
        call("edit_file", path="facturas/importes.py", old_string="from decimal import Decimal", new_string="from decimal import ROUND_HALF_UP, Decimal"),
        call("edit_file", path="facturas/importes.py", old_string="    return round(valor, 2)", new_string=FIX),
        call("bash", command="python -m pytest -q tests/test_importes.py"),
        say("Arreglado."),
    ])


def test_tasks_file():
    ids = [t.id for t in load_tasks(ROOT / "evals/tasks.yaml")]
    assert ids[:2] == ["fix_redondeo", "fix_vencimiento"] and "feature_descuento" in ids


def test_run_task_pass_and_fail():
    t = EvalTask("fix_redondeo", "arregla", {"command": "python -m pytest -q tests/test_importes.py"})
    ok = run_task(t, solver(), ROOT / "playground", ROOT)
    assert ok.passed and ok.steps == 5 and ok.tool_calls == 4
    bad = run_task(t, FakeLLM([say("ya está (mentira)")]), ROOT / "playground", ROOT)
    assert not bad.passed and "falló" in bad.reason
    # el playground original no se ha tocado
    assert "round(valor, 2)" in (ROOT / "playground/facturas/importes.py").read_text()


def test_grade_answer_and_forbid_changes(project):
    before = snapshot(project)
    t = EvalTask("q", "p", {"answer_contains": ["importes.py", "IVA"], "forbid_changes": True})
    assert grade(t, project, "En facturas/importes.py, calcular_iva (el iva)", before, ROOT) == (True, "ok")
    assert not grade(t, project, "no lo sé", before, ROOT)[0]
    (project / "nuevo.txt").write_text("x")
    assert "modificó" in grade(t, project, "importes.py iva", before, ROOT)[1]


def test_hidden_tests_copied_after(project):
    t = EvalTask("h", "p", {"command": "python -m pytest -q tests/test_descuento_oculto.py",
                            "hidden": {"evals/hidden/test_descuento.py": "tests/test_descuento_oculto.py"}})
    passed, reason = grade(t, project, "", snapshot(project), ROOT)
    assert not passed and (project / "tests/test_descuento_oculto.py").exists()


def test_summarize():
    rs = [TaskResult("a", True, "ok", 4, 3, 100, 2.0, "final"), TaskResult("a", False, "x", 6, 5, 200, 4.0, "final"),
          TaskResult("b", True, "ok", 2, 1, 50, 1.0, "final")]
    s = summarize(rs, "m")
    assert s["pass_rate"] == 0.667 and s["per_task"] == {"a": 0.5, "b": 1.0}
    assert s["avg_steps"] == 4.0 and s["total_tokens"] == 350 and len(s["results"]) == 3
