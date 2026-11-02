"""LAB 11 — Sesiones y checkpoints: retomar el trabajo y deshacer lo que hizo el agente.

* Transcript JSONL append-only en .forja/sessions/<id>.jsonl: un mensaje por línea.
  Sirve para reanudar (`forja --resume <id>`), para auditar y para depurar.
* Checkpoints: antes de que una tool modifique un fichero, guardamos su contenido
  original (o que no existía). `/undo` restaura los ficheros tocados en el último turno.
  No depende de git: funciona también en carpetas sin repositorio.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Transcript:
    folder: Path
    session_id: str = field(default_factory=lambda: time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4])

    @property
    def path(self) -> Path:
        return self.folder / f"{self.session_id}.jsonl"

    # ---- TODO 11.1 : append-only ---------------------------------------
    def append(self, *messages: dict[str, Any]) -> None:
        # TODO 11.1: Crea la carpeta; abre self.path en modo 'a' y escribe una línea JSON por mensaje: {'ts': ..., 'message': m} (ensure_ascii=False).
        raise NotImplementedError("TODO 11.1")

    def mark_compaction(self, history: list[dict[str, Any]]) -> None:
        """Tras compactar, el historial "vivo" ya no es la suma de líneas: guardamos una marca con el nuevo estado."""
        self.folder.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": round(time.time(), 3), "compacted": history}, ensure_ascii=False) + "\n")

    # ---- TODO 11.2 : reconstruir el historial --------------------------------
    @staticmethod
    def load(folder: Path, session_id: str) -> list[dict[str, Any]]:
        # TODO 11.2: FileNotFoundError si no existe. Recorre las líneas: 'compacted' -> sustituye todo el historial; 'message' -> añade.
        raise NotImplementedError("TODO 11.2")

    @staticmethod
    def list_sessions(folder: Path) -> list[tuple[str, str]]:
        """[(id, primer mensaje del usuario)] de la más reciente a la más antigua."""
        out = []
        for p in sorted(folder.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True):
            first = ""
            for line in p.read_text(encoding="utf-8").splitlines():
                m = json.loads(line).get("message", {})
                if m.get("role") == "user":
                    first = (m.get("content") or "")[:80]
                    break
            out.append((p.stem, first))
        return out


@dataclass
class Checkpoints:
    """Pila de turnos; cada turno guarda {ruta: contenido_original | None (no existía)}."""

    stack: list[dict[Path, bytes | None]] = field(default_factory=list)

    def begin_turn(self) -> None:
        self.stack.append({})

    # ---- TODO 11.3 : guardar el original la PRIMERA vez que se toca ------------
    def before_write(self, path: Path) -> None:
        # TODO 11.3: Si no hay turno, begin_turn(). Solo la PRIMERA vez que se toca una ruta en el turno: guarda path.read_bytes() o None si no existía.
        raise NotImplementedError("TODO 11.3")

    # ---- TODO 11.4 : deshacer el último turno con cambios ----------------------
    def undo(self) -> list[Path]:
        # TODO 11.4: Descarta turnos vacíos del final. Saca el último: restaura cada fichero (write_bytes, creando carpetas) o bórralo si era None. Devuelve las rutas ordenadas; [] si no hay nada.
        raise NotImplementedError("TODO 11.4")
