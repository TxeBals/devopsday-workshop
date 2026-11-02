"""LAB 12 — Evals: medir tu agente (y tus modelos) con tareas reales.

Cada tarea = un prompt + una comprobación objetiva, ejecutada en una COPIA limpia del
proyecto de prácticas. Comprobaciones:
  * command          un comando que debe terminar con exit 0 (normalmente tests)
  * hidden           tests OCULTOS que se copian después de que trabaje el agente
                     (así no puede "hacer trampa" leyéndolos o editándolos)
  * answer_contains  la respuesta debe contener ciertos datos (preguntas sobre el código)
  * forbid_changes   la tarea no debe modificar ningún fichero
El agente corre headless en modo bypass DENTRO de la copia: el sandbox es la carpeta temporal.
"""
from __future__ import annotations

import hashlib
import shutil
import statistics
import subprocess
import tempfile
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .config import Settings
from .harness import Forja
from .types import ChatModel


@dataclass
class EvalTask:
    id: str
    prompt: str
    check: dict[str, Any]


@dataclass
class TaskResult:
    id: str
    passed: bool
    reason: str
    steps: int
    tool_calls: int
    tokens: int
    seconds: float
    stop_reason: str
    answer: str = ""


def load_tasks(path: Path) -> list[EvalTask]:
    return [EvalTask(t["id"], t["prompt"], t.get("check", {})) for t in yaml.safe_load(path.read_text(encoding="utf-8"))]


def snapshot(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and not any(part in {".forja", "__pycache__", ".pytest_cache"} for part in p.parts):
            out[str(p.relative_to(root))] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# ---- TODO 12.1 : corregir una tarea --------------------------------------------
def grade(task: EvalTask, workdir: Path, answer: str, before: dict[str, str], repo_root: Path) -> tuple[bool, str]:
    # TODO 12.1: En orden: forbid_changes (snapshot distinto -> falla); answer_contains (comparar con norm(), lista lo que falta); copiar los hidden al workdir; ejecutar command en el workdir (timeout -> falla; exit != 0 -> falla con las 3 últimas líneas). Si todo bien: (True, 'ok').
    raise NotImplementedError("TODO 12.1")


def run_task(task: EvalTask, llm: ChatModel, playground: Path, repo_root: Path, max_steps: int = 30) -> TaskResult:
    with tempfile.TemporaryDirectory(prefix=f"forja-eval-{task.id}-") as tmp:
        work = Path(tmp) / "proyecto"
        shutil.copytree(playground, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".forja"))
        before = snapshot(work)
        app = Forja(llm, work, mode="bypass", settings=Settings(max_steps=max_steps), home=Path(tmp) / "home",
                    persist=False, use_mcp=False)
        t0 = time.time()
        try:
            r = app.turn(task.prompt)
            answer, steps, calls, stop = r.answer, r.steps, r.tool_calls, r.stop_reason
        except Exception as e:  # noqa: BLE001
            answer, steps, calls, stop = f"EXCEPCIÓN {type(e).__name__}: {e}", 0, 0, "error"
        secs = round(time.time() - t0, 1)
        passed, reason = grade(task, work, answer, before, repo_root)
        return TaskResult(task.id, passed, reason, steps, calls, sum(app.usage.values()), secs, stop, answer[:500])


# ---- TODO 12.2 : resumir resultados -----------------------------------------------
def summarize(results: list[TaskResult], model: str) -> dict[str, Any]:
    # TODO 12.2: Agrupa por id. Devuelve model, runs, pass_rate (3 decimales), per_task (2 decimales), avg_steps y avg_seconds (1 decimal), total_tokens y results (asdict).
    raise NotImplementedError("TODO 12.2")
