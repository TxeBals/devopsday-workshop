"""LAB 02b — A coding agent's file tools.

Rules that separate a toy from a usable tool:
  * Sandbox: every path resolves INSIDE the workspace; `../` and symlinks pointing outside are rejected.
  * read_file numbers lines (the model cites them) and pages large files (offset/limit).
  * edit_file = EXACT replacement of a UNIQUE string. No diffs, which small models
    produce badly. If the text doesn't appear or appears several times, an actionable error.
  * Read before edit: a file the agent hasn't read, or that changed on disk since it read it
    (touched by the human, a formatter…), is not edited or overwritten.
  * grep/glob to explore: the agent NEVER loads the whole repo into context.
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
    read_state: dict[Path, float] = field(default_factory=dict)  # path -> mtime at last read
    before_write: list = field(default_factory=list)  # callbacks(path) before modifying (checkpoints, lab 11)

    def __post_init__(self):
        self.root = Path(self.root).resolve()

    # ---- TODO 02.3 : path sandbox ---------------------------------------
    def resolve(self, path: str) -> Path:
        # TODO 02.3: Relative path -> self.root / path; absolute is kept. .resolve() (follows symlinks). If it is neither self.root nor inside it (is_relative_to) -> PermissionError('path outside the workspace: …').
        raise NotImplementedError("TODO 02.3")

    def rel(self, p: Path) -> str:
        return p.relative_to(self.root).as_posix() if p != self.root else "."

    def mark_read(self, p: Path) -> None:
        self.read_state[p] = p.stat().st_mtime

    def check_fresh(self, p: Path) -> None:
        """Raises if it hasn't been read or if it changed on disk since it was read."""
        if p not in self.read_state:
            raise PermissionError(f"read {self.rel(p)} with read_file before modifying it")
        if p.stat().st_mtime != self.read_state[p]:
            raise PermissionError(f"{self.rel(p)} has changed since you read it; read it again")

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
        """Reads a text file from the project and returns its numbered lines (format `  12→code`).
        For large files use offset/limit. ALWAYS read a file before editing it.

        Args:
            path: Path relative to the project root.
            offset: First line to return (starts at 1).
            limit: Maximum number of lines.
        """
        p = ws.resolve(path)
        if not p.is_file():
            raise FileNotFoundError(f"file {path} does not exist")
        raw = p.read_bytes()
        if b"\x00" in raw[:8000]:
            raise ValueError(f"{path} looks binary")
        lines = raw.decode("utf-8", errors="replace").splitlines()
        ws.mark_read(p)
        if not lines:
            return f"({path} is empty)"
        start = max(1, offset)
        chunk = lines[start - 1:start - 1 + limit]
        out = []
        for i, line in enumerate(chunk, start):
            if len(line) > MAX_LINE:
                line = line[:MAX_LINE] + "…[line truncated]"
            out.append(f"{i:>6}→{line}")
        rest = len(lines) - (start - 1 + len(chunk))
        if rest > 0:
            out.append(f"…({rest} more lines; use offset={start + len(chunk)})")
        return "\n".join(out)

    # ---- TODO 02.4 : write_file with "read before overwrite" ----------
    @tool(risk="edit")
    def write_file(path: str, content: str) -> ToolOutput:
        """Creates a new file or rewrites a whole one. For partial changes use edit_file.
        If the file already exists, you must have read it first.

        Args:
            path: Path relative to the project root.
            content: Full content of the file.
        """
        # TODO 02.4: p = ws.resolve(path). If it exists: ws.check_fresh(p) and keep the previous content. Call every cb in ws.before_write(p). Create folders, write, ws.mark_read(p). Return ToolOutput(short text, {'path': ws.rel(p), 'diff': unified_diff(before, after, path)}).
        raise NotImplementedError("TODO 02.4")

    # ---- TODO 02.5 : edit_file by exact, unique replacement ---------------
    @tool(risk="edit")
    def edit_file(path: str, old_string: str, new_string: str, replace_all: bool = False) -> ToolOutput:
        """Replaces an EXACT fragment of a file (including indentation) with another.
        old_string must appear exactly ONCE; if it appears several times, add context lines or use replace_all.
        Don't include read_file line numbers in old_string.

        Args:
            path: Path relative to the project root.
            old_string: Exact text to replace.
            new_string: New text.
            replace_all: Replace every occurrence.
        """
        # TODO 02.5: Must exist; ws.check_fresh(p); old != new. n = text.count(old_string): 0 -> ValueError with a hint (line numbers ' 12→'? whitespace?); n>1 without replace_all -> ValueError 'appears N times'. Replace (1 or all), before_write, write, mark_read. ToolOutput with the line of the change and the diff.
        raise NotImplementedError("TODO 02.5")

    @tool(risk="read")
    def glob(pattern: str, path: str = ".") -> str:
        """Finds files by pattern (e.g. `**/*.py`, `src/**/test_*.py`). Returns paths, most recently modified first.

        Args:
            pattern: Glob pattern relative to `path`.
            path: Directory to search from.
        """
        base = ws.resolve(path)
        hits = [f for f in ws.walk(base) if fnmatch.fnmatch(f.relative_to(base).as_posix(), pattern)
                or fnmatch.fnmatch(f.name, pattern)]
        hits.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        if not hits:
            return "(no results)"
        lines = [ws.rel(f) for f in hits[:200]]
        if len(hits) > 200:
            lines.append(f"…({len(hits) - 200} more; narrow the pattern)")
        return "\n".join(lines)

    # ---- TODO 02.6 : grep over the workspace --------------------------------
    @tool(risk="read")
    def grep(pattern: str, path: str = ".", include: str | None = None, ignore_case: bool = False, show_content: bool = True) -> str:
        """Searches file contents for a regular expression. Use it to locate definitions,
        usages and error messages before reading whole files.

        Args:
            pattern: Regular expression (Python syntax).
            path: File or directory to search in.
            include: File name filter, e.g. `*.py`.
            ignore_case: Case-insensitive search.
            show_content: true = `path:line: text` lines; false = paths only.
        """
        # TODO 02.6: re.compile(pattern, re.I if ignore_case). If path is a file, only that one; otherwise ws.walk(base). Filter by include (fnmatch on the name). Read as UTF-8 (skip binaries). show_content: 'path:n: line'; otherwise paths only. Stop at 300 results. Nothing found: '(no matches)'.
        raise NotImplementedError("TODO 02.6")

    return [read_file, write_file, edit_file, glob, grep]
