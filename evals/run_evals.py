"""Runs the Forja evals against a model.

    python evals/run_evals.py                                   # backend/model from .env
    python evals/run_evals.py --model qwen3-coder:30b --repeat 3
    python evals/run_evals.py --backend openrouter --model deepseek/deepseek-v3.2
    python evals/run_evals.py --only fix_rounding
    python evals/run_evals.py --config examples/project/.forja --label with-config   # measure your hooks/skills/subagents
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "solutions") if os.getenv("FORJA_SOLUTIONS") == "1" else str(ROOT))

from forja.config import backend_from_env  # noqa: E402
from forja.evals import load_tasks, run_task, summarize  # noqa: E402
from forja.llm import LLMClient  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["ollama", "openai_compat", "openrouter"])
    ap.add_argument("--model")
    ap.add_argument("--repeat", type=int, default=1, help="models are not deterministic: use 3 to compare")
    ap.add_argument("--only")
    ap.add_argument("--max-steps", type=int, default=30)
    ap.add_argument("--config", help="a .forja folder to use in every task (settings, hooks, skills, agents)")
    ap.add_argument("--mcp", action="store_true", help="also start the MCP servers from --config")
    ap.add_argument("--label", default="", help="suffix for the report file, e.g. 'with-config'")
    a = ap.parse_args()
    llm = LLMClient(backend_from_env(a.backend, a.model))
    tasks = [t for t in load_tasks(ROOT / "evals" / "tasks.yaml") if not a.only or t.id == a.only]
    results = []
    for t in tasks:
        for i in range(a.repeat):
            r = run_task(t, llm, ROOT / "playground", ROOT, a.max_steps,
                         config=(ROOT / a.config).resolve() if a.config else None, use_mcp=a.mcp)
            results.append(r)
            print(f"{'PASS' if r.passed else 'FAIL'}  {t.id:<20} {r.seconds:>6}s {r.steps:>3} steps  {'' if r.passed else r.reason}")
    rep = summarize(results, llm.model)
    rep["config"] = a.config or None
    label = f"_{a.label}" if a.label else ""
    out = ROOT / "out" / f"evals_{llm.model.replace('/', '_').replace(':', '_')}{label}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{rep['model']}: pass_rate {rep['pass_rate']:.0%} · {rep['avg_steps']} steps · {rep['avg_seconds']}s/task · {rep['total_tokens']} tokens")
    print(f"per task: {rep['per_task']}\n-> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
