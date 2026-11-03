from pathlib import Path

from forja.evals import EvalTask, grade, load_tasks, run_task, snapshot, summarize, TaskResult
from forja.fake_llm import FakeLLM, call, say

ROOT = Path(__file__).resolve().parents[1]
FIX = "    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))"


def solver():
    return FakeLLM([
        call("read_file", path="invoices/amounts.py"),
        call("edit_file", path="invoices/amounts.py", old_string="from decimal import Decimal", new_string="from decimal import ROUND_HALF_UP, Decimal"),
        call("edit_file", path="invoices/amounts.py", old_string="    return round(value, 2)", new_string=FIX),
        call("bash", command="python -m pytest -q tests/test_amounts.py"),
        say("Fixed."),
    ])


def test_tasks_file():
    ids = [t.id for t in load_tasks(ROOT / "evals/tasks.yaml")]
    assert ids[:2] == ["fix_rounding", "fix_due_date"] and "feature_discount" in ids


def test_run_task_pass_and_fail():
    t = EvalTask("fix_rounding", "fix it", {"command": "python -m pytest -q tests/test_amounts.py"})
    ok = run_task(t, solver(), ROOT / "playground", ROOT)
    assert ok.passed and ok.steps == 5 and ok.tool_calls == 4
    bad = run_task(t, FakeLLM([say("done (a lie)")]), ROOT / "playground", ROOT)
    assert not bad.passed and "failed" in bad.reason
    # the original playground has not been touched
    assert "round(value, 2)" in (ROOT / "playground/invoices/amounts.py").read_text()


def test_grade_answer_and_forbid_changes(project):
    before = snapshot(project)
    t = EvalTask("q", "p", {"answer_contains": ["amounts.py", "VAT"], "forbid_changes": True})
    assert grade(t, project, "In invoices/amounts.py, calculate_vat (the vat)", before, ROOT) == (True, "ok")
    assert not grade(t, project, "I don't know", before, ROOT)[0]
    (project / "new.txt").write_text("x")
    assert "modified" in grade(t, project, "amounts.py vat", before, ROOT)[1]


def test_hidden_tests_copied_after(project):
    t = EvalTask("h", "p", {"command": "python -m pytest -q tests/test_discount_hidden.py",
                            "hidden": {"evals/hidden/test_discount.py": "tests/test_discount_hidden.py"}})
    passed, reason = grade(t, project, "", snapshot(project), ROOT)
    assert not passed and (project / "tests/test_discount_hidden.py").exists()


def test_summarize():
    rs = [TaskResult("a", True, "ok", 4, 3, 100, 2.0, "final"), TaskResult("a", False, "x", 6, 5, 200, 4.0, "final"),
          TaskResult("b", True, "ok", 2, 1, 50, 1.0, "final")]
    s = summarize(rs, "m")
    assert s["pass_rate"] == 0.667 and s["per_task"] == {"a": 0.5, "b": 1.0}
    assert s["avg_steps"] == 4.0 and s["total_tokens"] == 350 and len(s["results"]) == 3


def test_run_task_uses_config(tmp_path):
    # --config: the eval copies your .forja (settings + hooks) into the work copy and loads it.
    cfg = tmp_path / ".forja"
    (cfg / "hooks").mkdir(parents=True)
    (cfg / "hooks" / "deny_edits.py").write_text("import sys\nprint('edits are frozen', file=sys.stderr)\nsys.exit(2)\n")
    (cfg / "settings.json").write_text(
        '{"hooks": {"PreToolUse": [{"matcher": "edit_file", "command": "python .forja/hooks/deny_edits.py"}]}}')
    t = EvalTask("fix_rounding", "fix it", {"command": "python -m pytest -q tests/test_amounts.py"})
    assert run_task(t, solver(), ROOT / "playground", ROOT).passed           # no config: the hook doesn't exist
    blocked = run_task(t, solver(), ROOT / "playground", ROOT, config=cfg)   # with config: edits are blocked
    assert not blocked.passed
