"""LAB 06 — Ingeniería de contexto: qué ve el modelo en cada turno.

El system prompt se ensambla por capas, cada turno:
  1. Prompt base del agente de código (cómo trabajar)
  2. Recordatorio del modo de permisos
  3. Instrucciones de proyecto: AGENTS.md (convención abierta compartida por varias herramientas),
     buscadas desde el directorio actual hacia arriba, más la global del usuario
  4. Catálogo de skills (lab 10)
  5. Entorno: directorio, rama y estado de git, SO, fecha, modelo
Y en el mensaje del usuario, las menciones `@ruta` se expanden con el contenido del fichero.
"""
from __future__ import annotations

import platform
import re
import subprocess
from datetime import date
from pathlib import Path

from .fs_tools import Workspace

BASE_PROMPT = """Eres Forja, un agente de ingeniería de software que trabaja en el terminal del usuario sobre su proyecto.

Cómo trabajas:
- Explora antes de cambiar: usa glob y grep para localizar código y read_file para leerlo. No supongas contenidos.
- Lee un fichero antes de editarlo. Para cambios parciales usa edit_file (texto exacto y único); write_file solo para ficheros nuevos o reescrituras completas.
- Sigue el estilo y las convenciones del código existente. No añadas dependencias sin necesidad.
- Verifica tu trabajo: ejecuta los tests o el comando relevante con bash y revisa la salida.
- Si una tool devuelve ERROR, lee el mensaje, corrige y reintenta; no repitas la misma llamada.
- Para tareas de varios pasos, mantén una lista con todo_write y actualízala según avances.
- Sé conciso: explica en pocas frases qué has hecho y qué queda. Cita ficheros como ruta:línea.
- Nunca inventes resultados de tests ni de comandos."""

MODE_REMINDERS = {
    "default": "Modo DEFAULT: puedes leer libremente; las ediciones y comandos pedirán aprobación al usuario.",
    "accept_edits": "Modo ACCEPT_EDITS: puedes leer y editar ficheros; los comandos de shell piden aprobación.",
    "plan": ("Modo PLAN: SOLO LECTURA. Investiga el código y, cuando tengas un plan concreto (ficheros, cambios, cómo verificar), "
             "preséntalo con la tool exit_plan_mode. No intentes editar ni ejecutar comandos."),
    "bypass": "Modo BYPASS: todas las acciones permitidas salvo las denegadas por política. Actúa con cuidado.",
}

INSTRUCTION_FILES = ("AGENTS.md", "FORJA.md")
MENTION_RE = re.compile(r"(?<![\w/])@([\w./\-]+)")


# ---- TODO 06.1 : encontrar instrucciones de proyecto ------------------------
def find_instruction_files(cwd: Path, home: Path | None = None, stop: Path | None = None) -> list[Path]:
    """Global del usuario primero (~/.forja/AGENTS.md) y luego desde la raíz MÁS ALTA hasta `cwd`,
    para que las instrucciones más cercanas (más específicas) aparezcan las últimas y pesen más."""
    # TODO 06.1: Primero home/.forja/AGENTS.md si existe. Después sube desde cwd hasta `stop` o la raíz del disco recogiendo AGENTS.md/FORJA.md, y devuélvelos de la carpeta MÁS ALTA a la más baja (lo más específico al final).
    raise NotImplementedError("TODO 06.1")


def git_info(root: Path) -> str:
    def run(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=5).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            return ""

    branch = run("rev-parse", "--abbrev-ref", "HEAD")
    if not branch:
        return "Repositorio git: no"
    status = run("status", "--short").splitlines()
    shown = "\n".join(status[:20]) + (f"\n…({len(status) - 20} más)" if len(status) > 20 else "")
    return f"Repositorio git: sí · rama {branch}\nCambios sin commit:\n{shown or '(ninguno)'}"


# ---- TODO 06.2 : ensamblar el system prompt ---------------------------------
def build_system_prompt(ws: Workspace, mode: str, model: str, home: Path | None = None, skills_catalog: str = "",
                        extra: list[str] | None = None) -> str:
    # TODO 06.2: Capas unidas por '\n\n': BASE_PROMPT, MODE_REMINDERS[mode], cada fichero de instrucciones con un título '## Instrucciones …', skills_catalog, extra (no vacíos) y '## Entorno' con directorio, git_info(ws.root), SO, fecha y modelo.
    raise NotImplementedError("TODO 06.2")


# ---- TODO 06.3 : expandir menciones @fichero -------------------------------
def expand_mentions(text: str, ws: Workspace, max_chars: int = 20_000) -> str:
    """`Revisa @src/app.py` -> el mensaje original + un bloque con el contenido del fichero.
    Las menciones que no son ficheros del workspace se dejan como están."""
    # TODO 06.3: Para cada @ruta única (MENTION_RE): ws.resolve (ignora PermissionError), solo si es fichero; lee (máx. max_chars), ws.mark_read y añade <fichero ruta="…">contenido</fichero> al final del texto. Sin menciones válidas, el texto tal cual.
    raise NotImplementedError("TODO 06.3")
