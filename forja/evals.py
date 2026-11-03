"""LAB 12 — Evals: measure your agent (and your models) with real tasks.

Each task = a prompt + an objective check, run on a clean COPY of the practice
project. Checks:
  * command          a command that must finish with exit 0 (usually tests)
  * hidden           HIDDEN tests copied in after the agent has worked
                     (so it can't "cheat" by reading or editing them)
  * answer_contains  the answer must contain certain facts (questions about the code)
  * forbid_changes   the task must not modify any file
The agent runs headless in bypass mode INSIDE the copy: the sandbox is the temp folder.
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
        if p.is_file() and not any(part in {".forja", ".git", "__pycache__", ".pytest_cache"} for part in p.parts):
            out[p.relative_to(root).as_posix()] = hashlib.sha1(p.read_bytes()).hexdigest()
    return out


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


# ---- TODO 12.1 : grade a task ---------------------------------------------------
def grade(task: EvalTask, workdir: Path, answer: str, before: dict[str, str], repo_root: Path) -> tuple[bool, str]:
    # TODO 12.1: In order: forbid_changes (different snapshot -> fail); answer_contains (compare with norm(), list what is missing); copy the hidden files into the workdir; run command in the workdir (timeout -> fail; exit != 0 -> fail with the last 3 lines). If all good: (True, 'ok').
    raise NotImplementedError("TODO 12.1")


def _git_baseline(work: Path) -> None:
    """Commit the clean copy so hooks/tools that look at `git status`/`git diff` see only the agent's changes."""
    git = ["git", "-c", "user.name=forja-eval", "-c", "user.email=eval@localhost", "-c", "commit.gpgsign=false"]
    try:
        for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "eval baseline"]):
            subprocess.run(git + cmd, cwd=work, capture_output=True, timeout=30, check=True)
    except (OSError, subprocess.SubprocessError):
        pass  # no git: hooks fall back to their non-git behaviour


def run_task(task: EvalTask, llm: ChatModel, playground: Path, repo_root: Path, max_steps: int = 30,
             config: Path | None = None, use_mcp: bool = False) -> TaskResult:
    """Runs one task on a clean copy of `playground` in bypass mode.

    config: a `.forja` folder (settings.json + hooks/ + skills/ + agents/) copied into the work copy, so the eval measures
            YOUR harness configuration (AGENTS.md is always part of the playground). Without it, no project config is used.
    use_mcp: also start the MCP servers from that settings.json (relative paths resolve from the work copy)."""
    with tempfile.TemporaryDirectory(prefix=f"forja-eval-{task.id}-") as tmp:
        work = Path(tmp) / "project"
        shutil.copytree(playground, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".forja"))
        if config:
            shutil.copytree(config, work / ".forja", ignore=shutil.ignore_patterns("__pycache__", "sessions"))
        _git_baseline(work)
        before = snapshot(work)
        home = Path(tmp) / "home"
        settings = Settings.load(work, home=home) if config else Settings()
        settings.max_steps = max_steps
        app = Forja(llm, work, mode="bypass", settings=settings, home=home, persist=False, use_mcp=use_mcp)
        t0 = time.time()
        try:
            r = app.turn(task.prompt)
            answer, steps, calls, stop = r.answer, r.steps, r.tool_calls, r.stop_reason
        except Exception as e:  # noqa: BLE001
            answer, steps, calls, stop = f"EXCEPTION {type(e).__name__}: {e}", 0, 0, "error"
        secs = round(time.time() - t0, 1)
        passed, reason = grade(task, work, answer, before, repo_root)
        return TaskResult(task.id, passed, reason, steps, calls, sum(app.usage.values()), secs, stop, answer[:500])


# ---- TODO 12.2 : summarise results -----------------------------------------------
def summarize(results: list[TaskResult], model: str) -> dict[str, Any]:
    # TODO 12.2: Group by id. Return model, runs, pass_rate (3 decimals), per_task (2 decimals), avg_steps and avg_seconds (1 decimal), total_tokens and results (asdict).
    raise NotImplementedError("TODO 12.2")
