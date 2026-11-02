"""LAB 08 — Plan before acting: task list and plan mode.

* todo_write: the agent keeps a task list visible to the user. It forces the model
  to decompose the work, and lets the user see progress. With small local models
  it greatly improves persistence on long tasks.
* Plan mode: read-only. The agent investigates and proposes a plan with exit_plan_mode; if
  the user approves it, the harness switches to default mode (or accept_edits) and it is executed.
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
            return "(empty list)"
        return "\n".join(f"{ICON[i.status]} {i.content}" for i in self.items)


# ---- TODO 08.1 : the todo_write tool with validation --------------------------
def make_todo_tool(store: TodoStore) -> Tool:
    @tool(risk="read")
    def todo_write(todos: list[TodoItem]) -> str:
        """Creates or updates your task list (replaces the whole list). Use it for tasks with 3+ steps:
        at the start, split the work; mark a task in_progress before starting it and completed when done.
        Only ONE task can be in_progress at a time.

        Args:
            todos: Full list of tasks with content and status (pending, in_progress, completed).
        """
        # TODO 08.1: Convert each item to TodoItem (dicts may arrive). More than one in_progress -> ValueError. Empty content -> ValueError. store.items = items. Return 'List updated (X/N completed):' + store.render().
        raise NotImplementedError("TODO 08.1")

    return todo_write


# ---- TODO 08.2 : leave plan mode with user approval --------------------------
def make_exit_plan_tool(approve: Callable[[str], bool], on_approved: Callable[[], None]) -> Tool:
    @tool(risk="read")
    def exit_plan_mode(plan: str) -> str:
        """In plan mode, presents your implementation plan to the user (markdown: files to touch, changes,
        how to verify) and asks for approval to start executing it.

        Args:
            plan: The plan, concrete and brief.
        """
        # TODO 08.2: Empty plan -> ValueError. If approve(plan): on_approved() and return a text saying the user APPROVED and it should implement it. Otherwise: that they REJECTED it and it is still in plan mode.
        raise NotImplementedError("TODO 08.2")

    return exit_plan_mode
