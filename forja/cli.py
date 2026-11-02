"""LAB 05 — The interface: your own terminal agent.

    forja                         # interactive REPL in the current directory
    forja -p "fix the test"       # headless mode (scripts, CI, evals): prints the answer and exits
    forja --mode plan             # start in plan mode
    forja --resume <id>           # resume a session
    forja doctor                  # check environment and model

Most of this is UI "plumbing" and is provided. The TODOs in this lab are the pieces
that shape the experience: how a tool call is summarised, how a diff is rendered,
how approval is requested and what the slash commands do.
"""
from __future__ import annotations

import argparse
import json
import signal
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .agent import Events
from .config import backend_from_env
from .harness import Approval, Forja
from .permissions import MODES
from .session import Transcript
from .tools import Tool, ToolResult
from .types import ChatResponse, ToolCall

console = Console(highlight=False)


# ---- TODO 05.1 : summarise a tool call in one line ----------------------------
def summarize_call(name: str, args: dict[str, Any], width: int = 100) -> str:
    """read_file {path} -> 'Read src/app.py'; bash -> '$ pytest -q'; grep -> "Grep 'pattern' in src"…"""
    # TODO 05.1: One readable line per tool: 'Read path' (+ ' (from line N)' if offset != 1), 'Write path (N lines)', 'Edit path', '$ command', "Grep 'pattern' in path (include)", 'Glob pattern', 'Task[type] description', 'Todos (N)', others 'name(k=v, …)'. Collapse whitespace and cut to `width` with '…'.
    raise NotImplementedError("TODO 05.1")


# ---- TODO 05.2 : per-line styles for a unified diff ---------------------------
def diff_styles(diff: str) -> list[tuple[str, str]]:
    """[(line, rich style)]: headers bold, hunks cyan, + green, - red, context dimmed."""
    # TODO 05.2: Per line: '+++'/'---' -> 'bold'; '@@' -> 'cyan'; '+' -> 'green'; '-' -> 'red'; the rest -> 'dim'. Return [(line, style)].
    raise NotImplementedError("TODO 05.2")


def parse_args_json(call: ToolCall) -> dict[str, Any]:
    try:
        v = json.loads(call.arguments or "{}")
        return v if isinstance(v, dict) else {}
    except json.JSONDecodeError:
        return {}


def _safe(fn, *a, default=None):
    """Until lab 05 is done, the UI uses a minimal version."""
    try:
        return fn(*a)
    except NotImplementedError:
        return default


class RichEvents(Events):
    def __init__(self, prefix: str = "", show_diffs: bool = True):
        self.prefix = prefix
        self.show_diffs = show_diffs
        self._streaming = False

    def on_text(self, delta: str) -> None:
        if not self.prefix:
            if not self._streaming:
                console.print()
                self._streaming = True
            console.print(delta, end="", markup=False, highlight=False)

    def on_assistant(self, resp: ChatResponse) -> None:
        if self._streaming:
            console.print()
            self._streaming = False

    def on_tool_start(self, call: ToolCall) -> None:
        label = _safe(summarize_call, call.name, parse_args_json(call), default=f"{call.name} {call.arguments[:80]}")
        console.print(Text(f"{self.prefix}⏺ {label}", style="bold blue" if not self.prefix else "blue"))

    def on_tool_end(self, call: ToolCall, result: ToolResult) -> None:
        first = (result.output.splitlines() or [""])[0][:160]
        if not result.ok:
            console.print(Text(f"{self.prefix}  ⎿ {first}", style="red"))
            return
        styled = _safe(diff_styles, result.meta.get("diff", ""), default=None) if result.meta.get("diff") else None
        if self.show_diffs and styled:
            body = Text()
            for line, style in styled[:80]:
                body.append(line + "\n", style=style)
            console.print(Panel(body, title=result.meta.get("path"), border_style="dim", expand=False))
        else:
            n = len(result.output.splitlines())
            console.print(Text(f"{self.prefix}  ⎿ {first}" + (f"  (+{n - 1} lines)" if n > 1 else ""), style="dim"))


# ---- TODO 05.3 : ask for approval ---------------------------------------------
def ask_approval(tool: Tool, args: dict[str, Any], reason: str, read: Any = input) -> Approval:
    """Shows what is about to happen and asks. y = yes, n = no, a = always (adds a rule). Empty = no."""
    # TODO 05.3: Draw a Panel with summarize_call and the reason. Read the answer with read(...): y/yes -> 'yes'; a/always -> 'always'; anything else (including empty) -> 'no'.
    raise NotImplementedError("TODO 05.3")


def ask_plan(plan: str, read: Any = input) -> bool:
    console.print(Panel(Markdown(plan), title="Proposed plan", border_style="magenta"))
    return str(read("  Approve the plan and start? [y/N] > ")).strip().lower() in ("y", "yes")


HELP = """/help                 this help
/mode [mode]          show or change mode: default | accept_edits | plan | bypass
/tools                available tools
/todos                the agent's task list
/context              estimated context tokens
/compact              compact now
/cost                 tokens used in this session
/undo                 undo the file changes from the last turn
/sessions             saved sessions
/clear                start a new conversation
/exit                 quit"""


# ---- TODO 05.4 : slash commands ------------------------------------------------
def handle_slash(app: Forja, line: str) -> str | None:
    """Returns the text to display, or None if the command is /exit."""
    # TODO 05.4: Split command and argument. /exit -> None. /help -> HELP. /mode [m] (app.set_mode). /tools (name [risk]). /todos (app.todos.render()). /context (app.context_tokens()). /compact (app.compact_now(force=True)). /cost (app.usage). /undo (app.undo()). /sessions (Transcript.list_sessions). /clear. Unknown -> message.
    raise NotImplementedError("TODO 05.4")


def build_app(a: argparse.Namespace, interactive: bool) -> Forja:
    from .llm import LLMClient

    llm = LLMClient(backend_from_env(a.backend, a.model))
    app = Forja(llm, Path(a.cwd), mode=a.mode, events=RichEvents(), sub_events=lambda n: RichEvents(prefix=f"  [{n}] "),
                approver=ask_approval if interactive else None, plan_approver=ask_plan if interactive else None)
    if a.resume:
        app.resume(a.resume)
    return app


def doctor(a: argparse.Namespace) -> int:
    """Checks the backend and tool support WITHOUT depending on lab 01 (uses the openai SDK directly)."""
    import time

    from openai import OpenAI

    b = backend_from_env(a.backend, a.model)
    console.print(f"backend={b.name} url={b.base_url} model={b.model}")
    tool = {"type": "function", "function": {"name": "ping", "description": "Replies pong", "parameters": {"type": "object", "properties": {}}}}
    client = OpenAI(base_url=b.base_url, api_key=b.api_key or "x", default_headers=b.extra_headers, timeout=300)
    t0 = time.time()
    try:
        r = client.chat.completions.create(model=b.model, messages=[{"role": "user", "content": "Call the ping tool."}],
                                           tools=[tool], extra_body=b.extra_body or None)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]✘ could not talk to the model: {type(e).__name__}: {e}[/red]")
        return 1
    dt = time.time() - t0
    msg = r.choices[0].message
    toks = getattr(r.usage, "completion_tokens", None) if r.usage else None
    speed = f" · ~{toks / dt:.0f} tok/s (includes loading)" if toks else ""
    console.print(f"[dim]answered in {dt:.1f}s{speed}[/dim]")
    if msg.tool_calls:
        console.print(f"[green]✔ the model calls tools ({msg.tool_calls[0].function.name})[/green]")
        return 0
    console.print(f"[yellow]! the model answered without calling the tool: {msg.content!r}. Try another model.[/yellow]")
    return 2


def repl(app: Forja) -> None:
    console.print(Panel(f"[bold]Forja {__version__}[/bold] · {app.llm.model} · mode [cyan]{app.mode}[/cyan]\n{app.root}\n/help for commands · Ctrl+C interrupts",
                        border_style="cyan", expand=False))

    def on_sigint(sig, frame):  # Ctrl+C during a turn: stop at the next boundary
        app.cancel.set()
        console.print("\n[yellow]interrupting…[/yellow]")

    while True:
        for n in app.notes:
            console.print(f"[dim]· {n}[/dim]")
        app.notes.clear()
        try:
            line = console.input(f"\n[bold cyan]{app.mode}[/bold cyan] › ")
        except (EOFError, KeyboardInterrupt):
            break
        if not line.strip():
            continue
        if line.strip() == "/exit":
            break
        if line.startswith("/"):
            try:
                out = handle_slash(app, line)
            except (ValueError, NotImplementedError) as e:
                out = f"error: {e}"
            if out is None:
                break
            console.print(out)
            continue
        old = signal.signal(signal.SIGINT, on_sigint)
        try:
            r = app.turn(line)
        except Exception as e:  # noqa: BLE001
            console.print(f"[red]{type(e).__name__}: {e}[/red]")
            continue
        finally:
            signal.signal(signal.SIGINT, old)
        if r.stop_reason != "final":
            console.print(f"[yellow]{r.answer}[/yellow]")
        console.print(f"[dim]({r.steps} steps · {r.tool_calls} tools)[/dim]")
    app.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="forja", description="Your coding agent on open models")
    ap.add_argument("command", nargs="?", choices=["doctor"], help="optional subcommand")
    ap.add_argument("-p", "--print", dest="prompt", help="headless mode: run one prompt and exit")
    ap.add_argument("--mode", choices=MODES, default="default")
    ap.add_argument("--backend", choices=["ollama", "openai_compat", "openrouter"])
    ap.add_argument("--model")
    ap.add_argument("--resume")
    ap.add_argument("--cwd", default=".")
    a = ap.parse_args(argv)
    if a.command == "doctor":
        return doctor(a)
    if a.prompt:
        app = build_app(a, interactive=False)
        app.events = Events()
        r = app.turn(a.prompt)
        print(r.answer)
        app.close()
        return 0 if r.stop_reason == "final" else 1
    repl(build_app(a, interactive=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
