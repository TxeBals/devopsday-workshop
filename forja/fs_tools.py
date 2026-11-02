"""LAB 02b — Las tools de ficheros de un agente de código.

Reglas que separan un juguete de una herramienta usable:
  * Sandbox: toda ruta se resuelve DENTRO del workspace; `../` y symlinks hacia fuera, fuera.
  * read_file numera líneas (el modelo las cita) y pagina ficheros grandes (offset/limit).
  * edit_file = sustitución EXACTA de un texto ÚNICO. Nada de diffs que el modelo pequeño
    genera mal. Si el texto no aparece o aparece varias veces, error accionable.
  * Leer antes de editar: no se edita ni sobrescribe un fichero que el agente no ha leído,
    o que ha cambiado en disco desde que lo leyó (lo tocó el humano, un formatter…).
  * grep/glob para explorar: el agente NUNCA carga el repo entero en contexto.
"""
from __future__ import annotations

import difflib
import fnmatch
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from .tools import Tool, ToolOutput, tool

IGNORED_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", ".mypy_cache", ".pytest_cache", ".forja", "dist", "build"}
MAX_LINE = 2000
DEFAULT_LIMIT = 2000


@dataclass
class Workspace:
    root: Path
    read_state: dict[Path, float] = field(default_factory=dict)  # ruta -> mtime en la última lectura
    before_write: list = field(default_factory=list)  # callbacks(path) antes de modificar (checkpoints, lab 11)

    def __post_init__(self):
        self.root = Path(self.root).resolve()

    # ---- TODO 02.3 : sandbox de rutas -----------------------------------
    def resolve(self, path: str) -> Path:
        # TODO 02.3: Ruta relativa -> self.root / path; absoluta se respeta. .resolve() (sigue symlinks). Si no es self.root ni está dentro (is_relative_to) -> PermissionError('ruta fuera del workspace: …').
        raise NotImplementedError("TODO 02.3")

    def rel(self, p: Path) -> str:
        return str(p.relative_to(self.root)) if p != self.root else "."

    def mark_read(self, p: Path) -> None:
        self.read_state[p] = p.stat().st_mtime

    def check_fresh(self, p: Path) -> None:
        """Lanza si no se ha leído o si cambió en disco desde la lectura."""
        if p not in self.read_state:
            raise PermissionError(f"lee {self.rel(p)} con read_file antes de modificarlo")
        if p.stat().st_mtime != self.read_state[p]:
            raise PermissionError(f"{self.rel(p)} ha cambiado desde que lo leíste; vuelve a leerlo")

    def walk(self, base: Path):
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS and not d.startswith(".") or d == ".github")
            for f in sorted(filenames):
                yield Path(dirpath) / f


def unified_diff(before: str, after: str, path: str, context: int = 3) -> str:
    return "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), f"a/{path}", f"b/{path}", n=context))


def make_fs_tools(ws: Workspace) -> list[Tool]:
    @tool(risk="read")
    def read_file(path: str, offset: int = 1, limit: int = DEFAULT_LIMIT) -> str:
        """Lee un fichero de texto del proyecto y devuelve sus líneas numeradas (formato `  12→código`).
        Para ficheros grandes usa offset/limit. Lee SIEMPRE un fichero antes de editarlo.

        Args:
            path: Ruta relativa a la raíz del proyecto.
            offset: Primera línea a devolver (empieza en 1).
            limit: Número máximo de líneas.
        """
        p = ws.resolve(path)
        if not p.is_file():
            raise FileNotFoundError(f"no existe el fichero {path}")
        raw = p.read_bytes()
        if b"\x00" in raw[:8000]:
            raise ValueError(f"{path} parece binario")
        lines = raw.decode("utf-8", errors="replace").splitlines()
        ws.mark_read(p)
        if not lines:
            return f"({path} está vacío)"
        start = max(1, offset)
        chunk = lines[start - 1:start - 1 + limit]
        out = []
        for i, line in enumerate(chunk, start):
            if len(line) > MAX_LINE:
                line = line[:MAX_LINE] + "…[línea truncada]"
            out.append(f"{i:>6}→{line}")
        rest = len(lines) - (start - 1 + len(chunk))
        if rest > 0:
            out.append(f"…({rest} líneas más; usa offset={start + len(chunk)})")
        return "\n".join(out)

    # ---- TODO 02.4 : write_file con "leer antes de sobrescribir" ------
    @tool(risk="edit")
    def write_file(path: str, content: str) -> ToolOutput:
        """Crea un fichero nuevo o reescribe uno entero. Para cambios parciales usa edit_file.
        Si el fichero ya existe, debes haberlo leído antes.

        Args:
            path: Ruta relativa a la raíz del proyecto.
            content: Contenido completo del fichero.
        """
        # TODO 02.4: p = ws.resolve(path). Si existe: ws.check_fresh(p) y guarda el contenido anterior. Llama a cada cb de ws.before_write(p). Crea carpetas, escribe, ws.mark_read(p). Devuelve ToolOutput(texto corto, {'path': ws.rel(p), 'diff': unified_diff(antes, después, ruta)}).
        raise NotImplementedError("TODO 02.4")

    # ---- TODO 02.5 : edit_file por sustitución exacta y única -------------
    @tool(risk="edit")
    def edit_file(path: str, old_string: str, new_string: str, replace_all: bool = False) -> ToolOutput:
        """Sustituye un fragmento EXACTO de un fichero (incluida la indentación) por otro.
        old_string debe aparecer UNA sola vez; si aparece varias, añade líneas de contexto o usa replace_all.
        No incluyas los números de línea de read_file en old_string.

        Args:
            path: Ruta relativa a la raíz del proyecto.
            old_string: Texto exacto a sustituir.
            new_string: Texto nuevo.
            replace_all: Sustituir todas las apariciones.
        """
        # TODO 02.5: Debe existir; ws.check_fresh(p); old != new. n = text.count(old_string): 0 -> ValueError con pista (¿números de línea ' 12→'? ¿espacios?); n>1 sin replace_all -> ValueError 'aparece N veces'. Sustituye (1 o todas), before_write, escribe, mark_read. ToolOutput con línea del cambio y diff.
        raise NotImplementedError("TODO 02.5")

    @tool(risk="read")
    def glob(pattern: str, path: str = ".") -> str:
        """Busca ficheros por patrón (p. ej. `**/*.py`, `src/**/test_*.py`). Devuelve rutas, las modificadas más recientemente primero.

        Args:
            pattern: Patrón glob relativo a `path`.
            path: Directorio desde el que buscar.
        """
        base = ws.resolve(path)
        hits = [f for f in ws.walk(base) if fnmatch.fnmatch(str(f.relative_to(base)), pattern)
                or fnmatch.fnmatch(f.name, pattern)]
        hits.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        if not hits:
            return "(sin resultados)"
        lines = [ws.rel(f) for f in hits[:200]]
        if len(hits) > 200:
            lines.append(f"…({len(hits) - 200} más; afina el patrón)")
        return "\n".join(lines)

    # ---- TODO 02.6 : grep sobre el workspace --------------------------------
    @tool(risk="read")
    def grep(pattern: str, path: str = ".", include: str | None = None, ignore_case: bool = False, show_content: bool = True) -> str:
        """Busca una expresión regular en el contenido de los ficheros. Úsalo para localizar definiciones,
        usos y mensajes de error antes de leer ficheros enteros.

        Args:
            pattern: Expresión regular (sintaxis Python).
            path: Fichero o directorio donde buscar.
            include: Filtro de nombre de fichero, p. ej. `*.py`.
            ignore_case: Ignorar mayúsculas/minúsculas.
            show_content: true = líneas `ruta:nº: texto`; false = solo rutas.
        """
        # TODO 02.6: re.compile(pattern, re.I si ignore_case). Si path es fichero, solo ese; si no, ws.walk(base). Filtra por include (fnmatch sobre el nombre). Lee como UTF-8 (salta binarios). show_content: 'ruta:nº: línea'; si no, solo rutas. Corta en 300 resultados. Sin nada: '(sin coincidencias)'.
        raise NotImplementedError("TODO 02.6")

    return [read_file, write_file, edit_file, glob, grep]
