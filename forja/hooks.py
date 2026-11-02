"""LAB 10a — Hooks: política determinista alrededor de un modelo probabilístico.

AGENTS.md *pide* ("ejecuta los tests"); un hook *garantiza*. Los hooks son comandos de
shell configurados en .forja/settings.json que el harness ejecuta en puntos fijos:

    PreToolUse        antes de ejecutar una tool          exit 2 => se BLOQUEA (stderr va al modelo)
    PostToolUse       después de ejecutarla               exit 2 => stderr se añade al resultado (feedback)
    UserPromptSubmit  al enviar un mensaje                exit 2 => se bloquea; stdout se añade como contexto
    Stop              cuando el agente cree que ha terminado  exit 2 => sigue trabajando con stderr como indicación

Cada hook recibe por stdin un JSON con el evento. Exit 0 = todo bien; exit 2 = bloquear;
cualquier otro código = error del hook (se avisa, no bloquea). Es la convención que ya usan
los agentes de código comerciales: si la conocéis, sirve en todos.

    "hooks": {
      "PreToolUse":  [{"matcher": "bash", "command": "python .forja/hooks/no_secrets.py"}],
      "PostToolUse": [{"matcher": "edit_file|write_file", "command": "ruff check --quiet ."}],
      "Stop":        [{"command": "pytest -q -x"}]
    }
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop")


@dataclass
class HookOutcome:
    block: bool = False
    message: str = ""  # stderr (bloqueo / feedback)
    context: str = ""  # stdout útil (UserPromptSubmit)
    errors: list[str] = field(default_factory=list)


@dataclass
class HookRunner:
    config: dict[str, list[dict[str, Any]]]
    cwd: Path
    timeout: int = 60

    # ---- TODO 10.1 : seleccionar hooks por evento y matcher -------------------
    def matching(self, event: str, tool_name: str | None = None) -> list[dict[str, Any]]:
        # TODO 10.1: De self.config[event]: sin matcher -> siempre; con matcher -> solo si hay tool_name y re.fullmatch(matcher, tool_name).
        raise NotImplementedError("TODO 10.1")

    # ---- TODO 10.2 : ejecutar y traducir códigos de salida ----------------------
    def run(self, event: str, payload: dict[str, Any], tool_name: str | None = None) -> HookOutcome:
        # TODO 10.2: Serializa {'hook_event_name', 'cwd', **payload} a JSON. Para cada hook que casa: subprocess.run(command, shell=True, cwd, input=json, capture_output, text, timeout). Exit 2 -> block=True y acumula stderr (o stdout) en message. Exit 0 -> stdout a context. Otro -> errors. TimeoutExpired -> errors.
        raise NotImplementedError("TODO 10.2")
