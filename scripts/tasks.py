"""Tareas del workshop, multiplataforma (Windows sin make incluido).

    python scripts/tasks.py setup              # dependencias + .env
    python scripts/tasks.py test 03            # tests del lab 03 contra TU código
    python scripts/tasks.py test               # todos
    python scripts/tasks.py catchup 05         # resuelve los labs 01-04 (necesita forja-solutions.zip del tutor)
    python scripts/tasks.py evals [args…]      # evals con tu agente
    python scripts/tasks.py reset              # deja playground/ como al principio (git)
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def sh(*args: str, env: dict | None = None, cwd: Path = ROOT) -> int:
    print("»", " ".join(args))
    return subprocess.call(list(args), cwd=cwd, env={**os.environ, **(env or {})})


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "setup":
        rc = sh(PY, "-m", "pip", "install", "-e", ".[dev]")
        if not (ROOT / ".env").exists():
            shutil.copy(ROOT / ".env.example", ROOT / ".env")
            print("creado .env (revísalo)")
        return rc
    if cmd == "test":
        files = sorted(glob.glob(str(ROOT / "tests" / f"test_l{rest[0].zfill(2)}_*.py"))) if rest else ["tests"]
        return sh(PY, "-m", "pytest", *files)
    if cmd == "catchup":
        return sh(PY, "scripts/catchup.py", *rest)
    if cmd == "evals":
        return sh(PY, "evals/run_evals.py", *rest)
    if cmd == "reset":
        sh("git", "checkout", "--", "playground")
        return sh("git", "clean", "-fdq", "playground")
    print(f"tarea desconocida: {cmd}\n{__doc__}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
