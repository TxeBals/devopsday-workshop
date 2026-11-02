"""El harness de Forja (DADO — se lee en clase, no es un TODO).

Une todas las piezas que construís en los labs:

    turno del usuario
      ├─ hook UserPromptSubmit (10)          ├─ expandir @menciones (06)
      ├─ compactar si hace falta (07)        ├─ system prompt por capas (06) + skills (10)
      └─ bucle del agente (03) ──► cada tool call pasa por la PUERTA:
             parsear y validar (02) → hook PreToolUse (10) → permisos (04) → aprobación humana (05)
             → checkpoint (11) → ejecutar (02/04/08/09/10) → hook PostToolUse (10)
      ├─ hook Stop: ¿de verdad ha terminado? (10)
      └─ guardar transcript (11)

Diseño "progresivo": si una pieza aún lanza NotImplementedError porque su lab no está
hecho, el harness sigue funcionando sin ella y lo avisa una vez. Cada lab que terminéis
enciende una capacidad nueva en vuestra CLI.
"""
from __future__ import annotations

import threading
from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from . import compaction, context, hooks, permissions, planning, session, skills, subagents
from .agent import Agent, AgentResult, Events
from .config import Settings
from .fs_tools import Workspace, make_fs_tools
from .mcp_tools import connect_servers
from .shell import make_shell_tool
from .tools import Tool, ToolRegistry, ToolResult
from .types import ChatModel, ToolCall

Approval = Literal["yes", "no", "always"]
FALLBACK_PROMPT = "Eres Forja, un agente de código. Usa las tools para explorar y modificar el proyecto. Sé conciso."

LAB_OF = {"context": "06", "compaction": "07", "permissions": "04", "hooks": "10", "skills": "10", "session": "11",
          "planning": "08", "subagents": "09", "mcp": "10", "tools": "02"}


@dataclass
class Forja:
    llm: ChatModel
    root: Path
    mode: permissions.Mode = "default"
    settings: Settings | None = None
    approver: Callable[[Tool, dict[str, Any], str], Approval] | None = None  # None = nadie para aprobar -> deniega
    plan_approver: Callable[[str], bool] | None = None
    events: Events = field(default_factory=Events)
    sub_events: Callable[[str], Events] | None = None
    home: Path | None = None
    persist: bool = True
    use_mcp: bool = True
    notes: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0})
    cancel: threading.Event = field(default_factory=threading.Event)

    def __post_init__(self) -> None:
        self.root = Path(self.root).resolve()
        self.home = self.home or Path.home()
        self.settings = self.settings or Settings.load(self.root, self.home)
        self.ws = Workspace(self.root)
        self.todos = planning.TodoStore()
        self.checkpoints = session.Checkpoints()
        self.ws.before_write.append(lambda p: self._opt("session", lambda: self.checkpoints.before_write(p), None))
        self.transcript = session.Transcript(self.root / ".forja" / "sessions")
        self.hooks = hooks.HookRunner(self.settings.hooks, self.root)
        self._stack = ExitStack()
        self._warned: set[str] = set()
        self.skills = self._opt("skills", lambda: skills.discover_skills(self.home / ".forja" / "skills", self.root / ".forja" / "skills"), {})
        self.registry = self._build_registry()

    # ------------------------------------------------------------------ utilidades
    def _opt(self, piece: str, fn: Callable[[], Any], fallback: Any) -> Any:
        try:
            return fn()
        except NotImplementedError:
            if piece not in self._warned:
                self._warned.add(piece)
                self.notes.append(f"{piece}: lab {LAB_OF.get(piece, '?')} pendiente — funcionando sin esta capacidad")
            return fallback

    def _build_registry(self) -> ToolRegistry:
        reg = ToolRegistry()
        reg.register(*make_fs_tools(self.ws), make_shell_tool(self.ws))
        reg.register(planning.make_todo_tool(self.todos),
                     planning.make_exit_plan_tool(self._approve_plan, lambda: self.set_mode("default")))
        if self.skills:
            reg.register(skills.make_skill_tool(self.skills))
        if self.use_mcp and self.settings.mcp_servers:
            tools, errors = connect_servers(self.settings.mcp_servers, self._stack)
            reg.register(*tools)
            self.notes += errors
        profiles = self._opt("subagents", lambda: subagents.load_profiles(self.root / ".forja" / "agents"), dict(subagents.BUILTIN))
        reg.register(subagents.make_task_tool(self.llm, reg, profiles, execute=self.gate, events_factory=self.sub_events))
        return reg

    def _approve_plan(self, plan: str) -> bool:
        return bool(self.plan_approver and self.plan_approver(plan))

    def set_mode(self, mode: permissions.Mode) -> None:
        if mode not in permissions.MODES:
            raise ValueError(f"modo desconocido: {mode}")
        self.mode = mode

    def close(self) -> None:
        self._stack.close()

    # ------------------------------------------------------------------ la puerta
    def gate(self, call: ToolCall) -> ToolResult:
        tool, args, err = self.registry.parse_args(call)
        if err:
            return ToolResult(call.id, call.name, False, err)
        pre = self._opt("hooks", lambda: self.hooks.run("PreToolUse", {"tool_name": tool.name, "tool_input": args}, tool.name), hooks.HookOutcome())
        if pre.block:
            return ToolResult(call.id, call.name, False, f"BLOQUEADO por hook: {pre.message}")
        fallback = ("allow", "lab 04 pendiente") if tool.risk == "read" else ("ask", "lab 04 pendiente")
        decision, why = self._opt("permissions", lambda: permissions.decide(tool, args, self.mode, self.settings.allow, self.settings.deny), fallback)
        if decision == "deny":
            return ToolResult(call.id, call.name, False, f"DENEGADO ({why}). No lo reintentes; busca otra forma o pregunta al usuario.")
        if decision == "ask":
            try:
                answer: Approval = self.approver(tool, args, why) if self.approver else "no"
            except NotImplementedError:  # lab 05 pendiente: pregunta mínima
                answer = "yes" if input(f"¿Permitir {tool.name} {args}? [s/N] ").strip().lower() in ("s", "y") else "no"
            if answer == "always":
                rule = self._opt("permissions", lambda: permissions.suggest_rule(tool, args), tool.name)
                self.settings.allow.append(rule)
                self.notes.append(f"regla añadida para esta sesión: allow {rule}")
            elif answer != "yes":
                return ToolResult(call.id, call.name, False, "DENEGADO por el usuario. No lo reintentes; pregunta qué prefiere.")
        try:
            result = self.registry.execute(call)
        except NotImplementedError as e:
            return ToolResult(call.id, call.name, False, f"ERROR: {e} (lab pendiente)")
        post = self._opt("hooks", lambda: self.hooks.run("PostToolUse", {"tool_name": tool.name, "tool_input": args,
                                                                          "tool_response": result.output[:5000]}, tool.name), hooks.HookOutcome())
        if post.block:
            result.output += f"\n\n[hook PostToolUse] {post.message}"
        return result

    # ------------------------------------------------------------------ contexto
    def system_prompt(self) -> str:
        cat = self._opt("skills", lambda: skills.catalog(self.skills), "")
        todos = f"## Tu lista de tareas actual\n{self.todos.render()}" if self.todos.items else ""
        return self._opt("context", lambda: context.build_system_prompt(self.ws, self.mode, self.llm.model, self.home, cat, [todos]),
                         FALLBACK_PROMPT)

    def context_tokens(self) -> int:
        return compaction.estimate_tokens([{"role": "system", "content": self.system_prompt()}, *self.history])

    def compact_now(self, force: bool = False) -> str:
        system = self.system_prompt()
        if not force and not self._opt("compaction", lambda: compaction.should_compact(system, self.history, self.settings.context_window), False):
            return ""
        n = self._opt("compaction", lambda: compaction.microcompact(self.history), 0)
        if not force and not compaction.should_compact(system, self.history, self.settings.context_window):
            return f"microcompactación: {n} salidas antiguas vaciadas"
        new, done = self._opt("compaction", lambda: compaction.compact(self.history, self.llm), (self.history, False))
        if done:
            self.history = new
            if self.persist:
                self._opt("session", lambda: self.transcript.mark_compaction(self.history), None)
            return f"compactado: resumen + últimos turnos ({compaction.estimate_tokens(self.history)} tokens aprox.)"
        return f"microcompactación: {n} salidas antiguas vaciadas" if n else "nada que compactar"

    # ------------------------------------------------------------------ un turno
    def turn(self, text: str) -> AgentResult:
        self.cancel.clear()
        hook = self._opt("hooks", lambda: self.hooks.run("UserPromptSubmit", {"prompt": text}), hooks.HookOutcome())
        if hook.block:
            return AgentResult(f"Mensaje bloqueado por hook: {hook.message}", "final", 0)
        content = self._opt("context", lambda: context.expand_mentions(text, self.ws), text)
        if hook.context:
            content += f"\n\n<contexto-hook>\n{hook.context}\n</contexto-hook>"
        note = self.compact_now()
        if note:
            self.notes.append(note)
        self.checkpoints.begin_turn()
        start = len(self.history)
        messages = [{"role": "system", "content": self.system_prompt()}, *self.history, {"role": "user", "content": content}]
        agent = Agent(self.llm, self._registry_for_turn(), execute=self.gate, events=self.events,
                      max_steps=self.settings.max_steps, cancel=self.cancel)
        try:
            result = agent.run(messages)
        except NotImplementedError:  # lab 03 pendiente: chat simple, sin tools
            self._warned.add("agent") or self.notes.append("agent: lab 03 pendiente — modo chat sin tools")
            result = self._chat_only(messages)
        for _ in range(3):  # hooks Stop: puertas de finalización ("no termines hasta que pasen los tests")
            if result.stop_reason != "final":
                break
            stop = self._opt("hooks", lambda: self.hooks.run("Stop", {"last_assistant_message": result.answer}), hooks.HookOutcome())
            if not stop.block:
                break
            messages.append({"role": "user", "content": f"[hook Stop] Aún no has terminado:\n{stop.message}"})
            result = agent.run(messages)
        for k, v in result.usage.items():
            self.usage[k] = self.usage.get(k, 0) + v
        self.history = messages[1:]
        if self.persist:
            self._opt("session", lambda: self.transcript.append(*self.history[start:]), None)
        return result

    def _chat_only(self, messages: list[dict[str, Any]]) -> AgentResult:
        from .types import Done, TextDelta

        resp = None
        for ev in self.llm.stream(messages):
            if isinstance(ev, TextDelta):
                self.events.on_text(ev.text)
            elif isinstance(ev, Done):
                resp = ev.response
        self.events.on_assistant(resp)
        messages.append({"role": "assistant", "content": resp.content or ""})
        return AgentResult(resp.content or "", "final", 1, resp.usage, 0)

    def _registry_for_turn(self) -> ToolRegistry:
        """Antes del lab 02 (schema sin implementar) el agente funciona como chat sin tools."""
        ok = self._opt("tools", lambda: self.registry.schemas() is not None, False)
        return self.registry if ok else ToolRegistry()

    # ------------------------------------------------------------------ sesiones
    def resume(self, session_id: str) -> None:
        self.history = session.Transcript.load(self.transcript.folder, session_id)
        self.transcript = session.Transcript(self.transcript.folder, session_id)

    def undo(self) -> list[Path]:
        return self._opt("session", self.checkpoints.undo, [])
