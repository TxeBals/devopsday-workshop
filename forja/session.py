"""LAB 11 — Sessions and checkpoints: resume work and undo what the agent did.

* Append-only JSONL transcript in .forja/sessions/<id>.jsonl: one message per line.
  Used to resume (`forja --resume <id>`), to audit and to debug.
* Checkpoints: before a tool modifies a file, we save its original content
  (or the fact that it didn't exist). `/undo` restores the files touched in the last turn.
  It doesn't depend on git: it also works in folders without a repository.
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
        # TODO 11.1: Create the folder; open self.path in 'a' mode and write one JSON line per message: {'ts': ..., 'message': m} (ensure_ascii=False).
        raise NotImplementedError("TODO 11.1")

    def mark_compaction(self, history: list[dict[str, Any]]) -> None:
        """After compaction the "live" history is no longer the sum of the lines: we save a marker with the new state."""
        self.folder.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": round(time.time(), 3), "compacted": history}, ensure_ascii=False) + "\n")

    # ---- TODO 11.2 : rebuild the history -------------------------------------
    @staticmethod
    def load(folder: Path, session_id: str) -> list[dict[str, Any]]:
        # TODO 11.2: FileNotFoundError if it doesn't exist. Walk the lines: 'compacted' -> replaces the whole history; 'message' -> append.
        raise NotImplementedError("TODO 11.2")

    @staticmethod
    def list_sessions(folder: Path) -> list[tuple[str, str]]:
        """[(id, first user message)] from newest to oldest."""
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
    """Stack of turns; each turn stores {path: original_content | None (did not exist)}."""

    stack: list[dict[Path, bytes | None]] = field(default_factory=list)

    def begin_turn(self) -> None:
        self.stack.append({})

    # ---- TODO 11.3 : save the original the FIRST time it is touched -------------
    def before_write(self, path: Path) -> None:
        # TODO 11.3: If there is no turn, begin_turn(). Only the FIRST time a path is touched in the turn: store path.read_bytes() or None if it didn't exist.
        raise NotImplementedError("TODO 11.3")

    # ---- TODO 11.4 : undo the last turn with changes ---------------------------
    def undo(self) -> list[Path]:
        # TODO 11.4: Drop empty turns from the end. Pop the last one: restore each file (write_bytes, creating folders) or delete it if it was None. Return the sorted paths; [] if there is nothing.
        raise NotImplementedError("TODO 11.4")
