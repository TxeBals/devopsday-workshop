"""LAB 05 — La interfaz: tu propio agente de terminal.

    forja                         # REPL interactivo en el directorio actual
    forja -p "arregla el test"    # modo headless (scripts, CI, evals): imprime la respuesta y sale
    forja --mode plan             # empezar en modo plan
    forja --resume <id>           # reanudar una sesión
    forja doctor                  # comprobar entorno y modelo

La mayor parte es "fontanería" de interfaz y viene dada. Los TODO de este lab son las
piezas que deciden la experiencia: cómo se resume una tool call, cómo se pinta un diff,
cómo se pide aprobación y qué hacen los comandos slash.
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


# ---- TODO 05.1 : resumir una tool call en una línea --------------------------
def summarize_call(name: str, args: dict[str, Any], width: int = 100) -> str:
    """read_file {path} -> 'Read src/app.py'; bash -> '$ pytest -q'; grep -> "Grep 'patrón' en src"…"""
    # TODO 05.1: Una línea legible por tool: 'Read ruta' (+ ' (desde línea N)' si offset != 1), 'Write ruta (N líneas)', 'Edit ruta', '$ comando', "Grep 'patrón' en ruta (include)", 'Glob patrón', 'Task[tipo] descripción', 'Todos (N)', resto 'nombre(k=v, …)'. Colapsa espacios y corta a `width` con '…'.
    raise NotImplementedError("TODO 05.1")


# ---- TODO 05.2 : estilos por línea de un diff unificado ----------------------
def diff_styles(diff: str) -> list[tuple[str, str]]:
    """[(línea, estilo rich)]: cabeceras en negrita, hunks en cian, + en verde, - en rojo, contexto atenuado."""
    # TODO 05.2: Por línea: '+++'/'---' -> 'bold'; '@@' -> 'cyan'; '+' -> 'green'; '-' -> 'red'; resto -> 'dim'. Devuelve [(línea, estilo)].
    raise NotImplementedError("TODO 05.2")


def parse_args_json(call: ToolCall) -> dict[str, Any]:
    try:
        v = json.loads(call.arguments or "{}")
        return v if isinstance(v, dict) else {}
    except json.JSONDecodeError:
        return {}


def _safe(fn, *a, default=None):
    """Mientras el lab 05 no esté hecho, la interfaz usa una versión mínima."""
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
            console.print(Text(f"{self.prefix}  ⎿ {first}" + (f"  (+{n - 1} líneas)" if n > 1 else ""), style="dim"))


# ---- TODO 05.3 : pedir aprobación ---------------------------------------------
def ask_approval(tool: Tool, args: dict[str, Any], reason: str, read: Any = input) -> Approval:
    """Muestra qué se va a hacer y pregunta. s/y = sí, n = no, a = siempre (añade regla). Vacío = no."""
    # TODO 05.3: Pinta un Panel con summarize_call y el motivo. Lee la respuesta con read(...): s/si/sí/y/yes -> 'yes'; a/always/siempre -> 'always'; cualquier otra cosa (incluido vacío) -> 'no'.
    raise NotImplementedError("TODO 05.3")


def ask_plan(plan: str, read: Any = input) -> bool:
    console.print(Panel(Markdown(plan), title="Plan propuesto", border_style="magenta"))
    return str(read("  ¿Aprobar el plan y empezar? [s/N] > ")).strip().lower() in ("s", "si", "sí", "y", "yes")


HELP = """/help                 esta ayuda
/mode [modo]          ver o cambiar modo: default | accept_edits | plan | bypass
/tools                tools disponibles
/todos                lista de tareas del agente
/context              tokens estimados del contexto
/compact              compactar ahora
/cost                 tokens consumidos en la sesión
/undo                 deshacer los cambios de ficheros del último turno
/sessions             sesiones guardadas
/clear                empezar conversación nueva
/exit                 salir"""


# ---- TODO 05.4 : comandos slash ------------------------------------------------
def handle_slash(app: Forja, line: str) -> str | None:
    """Devuelve el texto a mostrar, o None si el comando es /exit."""
    # TODO 05.4: Separa comando y argumento. /exit -> None. /help -> HELP. /mode [m] (app.set_mode). /tools (nombre [riesgo]). /todos (app.todos.render()). /context (app.context_tokens()). /compact (app.compact_now(force=True)). /cost (app.usage). /undo (app.undo()). /sessions (Transcript.list_sessions). /clear. Desconocido -> mensaje.
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
    """Comprueba backend y soporte de tools SIN depender del lab 01 (usa el SDK openai directamente)."""
    import time

    from openai import OpenAI

    b = backend_from_env(a.backend, a.model)
    console.print(f"backend={b.name} url={b.base_url} modelo={b.model}")
    tool = {"type": "function", "function": {"name": "ping", "description": "Responde pong", "parameters": {"type": "object", "properties": {}}}}
    client = OpenAI(base_url=b.base_url, api_key=b.api_key or "x", default_headers=b.extra_headers, timeout=300)
    t0 = time.time()
    try:
        r = client.chat.completions.create(model=b.model, messages=[{"role": "user", "content": "Llama a la tool ping."}],
                                           tools=[tool], extra_body=b.extra_body or None)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]✘ no se pudo hablar con el modelo: {type(e).__name__}: {e}[/red]")
        return 1
    dt = time.time() - t0
    msg = r.choices[0].message
    toks = getattr(r.usage, "completion_tokens", None) if r.usage else None
    speed = f" · {toks / dt:.0f} tok/s aprox. (incluye carga)" if toks else ""
    console.print(f"[dim]respuesta en {dt:.1f}s{speed}[/dim]")
    if msg.tool_calls:
        console.print(f"[green]✔ el modelo llama tools ({msg.tool_calls[0].function.name})[/green]")
        return 0
    console.print(f"[yellow]! el modelo respondió sin llamar a la tool: {msg.content!r}. Prueba otro modelo.[/yellow]")
    return 2


def repl(app: Forja) -> None:
    console.print(Panel(f"[bold]Forja {__version__}[/bold] · {app.llm.model} · modo [cyan]{app.mode}[/cyan]\n{app.root}\n/help para comandos · Ctrl+C interrumpe",
                        border_style="cyan", expand=False))

    def on_sigint(sig, frame):  # Ctrl+C durante un turno: parar en la siguiente frontera
        app.cancel.set()
        console.print("\n[yellow]interrumpiendo…[/yellow]")

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
        console.print(f"[dim]({r.steps} pasos · {r.tool_calls} tools)[/dim]")
    app.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="forja", description="Tu agente de código con modelos abiertos")
    ap.add_argument("command", nargs="?", choices=["doctor"], help="subcomando opcional")
    ap.add_argument("-p", "--print", dest="prompt", help="modo headless: ejecuta un prompt y sale")
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
