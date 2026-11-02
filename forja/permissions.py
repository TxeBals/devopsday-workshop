"""LAB 04b — Permisos: autonomía graduable con reglas.

Modos (los mismos conceptos que usan los agentes de código comerciales):
  default      -> lecturas libres; ediciones y bash preguntan
  accept_edits -> lecturas y ediciones libres; bash pregunta
  plan         -> SOLO lectura; editar o ejecutar se deniega (lab 08)
  bypass       -> todo permitido salvo las reglas deny (para sandbox/CI, nunca en tu portátil)

Reglas:  "nombre_tool"  o  "nombre_tool(patrón)"  — el patrón (fnmatch) se compara con el
"subject" de la llamada: el comando en bash, la ruta en las tools de ficheros.
  allow: ["bash(pytest*)", "bash(git status*)", "edit_file(src/*)"]
  deny:  ["bash(sudo *)", "read_file(.env*)"]
Orden de evaluación: deny > modo plan > allow > riesgo/modo > preguntar.
"""
from __future__ import annotations

import fnmatch
import re
import shlex
from typing import Any, Literal

from .tools import Tool

Mode = Literal["default", "accept_edits", "plan", "bypass"]
Decision = Literal["allow", "ask", "deny"]
MODES: tuple[Mode, ...] = ("default", "accept_edits", "plan", "bypass")
RULE_RE = re.compile(r"^([\w.\-*?]+)(?:\((.*)\))?$")


def parse_rule(rule: str) -> tuple[str, str | None]:
    m = RULE_RE.match(rule.strip())
    if not m:
        raise ValueError(f"regla inválida: {rule!r}")
    return m.group(1), m.group(2)


# ---- TODO 04.3 : ¿una regla casa con una llamada? -------------------------
def rule_matches(rule: str, tool: Tool, args: dict[str, Any]) -> bool:
    # TODO 04.3: name, pattern = parse_rule(rule). El nombre de tool se compara con fnmatchcase (permite 'mcp__issues__*'). Sin patrón: casa. Con patrón: fnmatchcase(tool.subject(args), pattern); en bash normaliza espacios (' '.join(split())).
    raise NotImplementedError("TODO 04.3")


def split_commands(command: str) -> list[str]:
    """`pytest -q && rm -rf /` son DOS comandos: una regla allow para pytest no debe colar el segundo."""
    parts = re.split(r"\s*(?:&&|\|\||;|\|)\s*", command.strip())
    return [p for p in parts if p]


# ---- TODO 04.4 : la decisión ---------------------------------------------
def decide(tool: Tool, args: dict[str, Any], mode: Mode, allow: list[str], deny: list[str]) -> tuple[Decision, str]:
    # TODO 04.4: 1) deny (también por cada subcomando de bash con split_commands) -> 'deny'. 2) plan y riesgo != read -> 'deny'. 3) allow: en bash TODOS los subcomandos deben casar con alguna regla; en el resto, alguna regla. 4) riesgo read o modo bypass -> allow. 5) accept_edits y riesgo edit -> allow. 6) 'ask'. Devuelve (decisión, motivo).
    raise NotImplementedError("TODO 04.4")


# ---- TODO 04.5 : sugerir una regla para "aprobar siempre" ---------------------
def suggest_rule(tool: Tool, args: dict[str, Any]) -> str:
    """Al responder 'siempre', guardamos una regla razonable, no el comando literal:
    bash `pytest -q tests/x.py` -> `bash(pytest *)`; edit_file -> `edit_file`."""
    # TODO 04.5: bash: shlex.split; 'python -m X' -> bash(python -m X*); git/npm/uv/pip/docker… -> bash(<cmd> <subcmd>*); resto -> bash(<cmd>*). Otras tools: su nombre.
    raise NotImplementedError("TODO 04.5")
