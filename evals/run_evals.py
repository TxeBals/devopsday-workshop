"""Ejecuta las evals de Forja contra un modelo.

    python evals/run_evals.py                                   # backend/modelo de .env
    python evals/run_evals.py --model qwen3-coder:30b --repeat 3
    python evals/run_evals.py --backend openrouter --model deepseek/deepseek-v3.2
    python evals/run_evals.py --only fix_redondeo
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
    ap.add_argument("--repeat", type=int, default=1, help="los modelos no son deterministas: usa 3 para comparar")
    ap.add_argument("--only")
    ap.add_argument("--max-steps", type=int, default=30)
    a = ap.parse_args()
    llm = LLMClient(backend_from_env(a.backend, a.model))
    tasks = [t for t in load_tasks(ROOT / "evals" / "tasks.yaml") if not a.only or t.id == a.only]
    results = []
    for t in tasks:
        for i in range(a.repeat):
            r = run_task(t, llm, ROOT / "playground", ROOT, a.max_steps)
            results.append(r)
            print(f"{'PASS' if r.passed else 'FAIL'}  {t.id:<20} {r.seconds:>6}s {r.steps:>3} pasos  {'' if r.passed else r.reason}")
    rep = summarize(results, llm.model)
    out = ROOT / "out" / f"evals_{llm.model.replace('/', '_').replace(':', '_')}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{rep['model']}: pass_rate {rep['pass_rate']:.0%} · {rep['avg_steps']} pasos · {rep['avg_seconds']}s/tarea · {rep['total_tokens']} tokens")
    print(f"por tarea: {rep['per_task']}\n-> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
