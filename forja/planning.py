"""LAB 08 — Planificar antes de actuar: lista de tareas y modo plan.

* todo_write: el agente mantiene una lista de tareas visible para el usuario. Obliga al
  modelo a descomponer, y al usuario le permite ver el progreso. Con modelos locales
  pequeños mejora mucho la constancia en tareas largas.
* Modo plan: solo lectura. El agente investiga y propone un plan con exit_plan_mode; si
  el usuario lo aprueba, el harness pasa a modo default (o accept_edits) y se ejecuta.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel

from .tools import Tool, tool

Status = Literal["pending", "in_progress", "completed"]
ICON = {"pending": "☐", "in_progress": "▶", "completed": "☑"}


class TodoItem(BaseModel):
    content: str
    status: Status = "pending"


@dataclass
class TodoStore:
    items: list[TodoItem] = field(default_factory=list)

    def render(self) -> str:
        if not self.items:
            return "(lista vacía)"
        return "\n".join(f"{ICON[i.status]} {i.content}" for i in self.items)


# ---- TODO 08.1 : la tool todo_write con validación ---------------------------
def make_todo_tool(store: TodoStore) -> Tool:
    @tool(risk="read")
    def todo_write(todos: list[TodoItem]) -> str:
        """Crea o actualiza tu lista de tareas (sustituye la lista completa). Úsala en tareas de 3+ pasos:
        al empezar, divide el trabajo; marca una tarea in_progress antes de empezarla y completed al terminarla.
        Solo puede haber UNA tarea in_progress a la vez.

        Args:
            todos: Lista completa de tareas con content y status (pending, in_progress, completed).
        """
        # TODO 08.1: Convierte cada elemento a TodoItem (pueden llegar dicts). Más de una in_progress -> ValueError. content vacío -> ValueError. store.items = items. Devuelve 'Lista actualizada (X/N completadas):' + store.render().
        raise NotImplementedError("TODO 08.1")

    return todo_write


# ---- TODO 08.2 : salir del modo plan con aprobación del usuario --------------
def make_exit_plan_tool(approve: Callable[[str], bool], on_approved: Callable[[], None]) -> Tool:
    @tool(risk="read")
    def exit_plan_mode(plan: str) -> str:
        """En modo plan, presenta al usuario tu plan de implementación (markdown: ficheros a tocar, cambios,
        cómo verificar) y pide aprobación para empezar a ejecutarlo.

        Args:
            plan: El plan, concreto y breve.
        """
        # TODO 08.2: Plan vacío -> ValueError. Si approve(plan): on_approved() y devuelve un texto que diga que el usuario APROBÓ y que implemente. Si no: que RECHAZÓ y sigue en modo plan.
        raise NotImplementedError("TODO 08.2")

    return exit_plan_mode
