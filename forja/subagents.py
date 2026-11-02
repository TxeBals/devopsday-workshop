"""LAB 09 — Subagentes: delegar con contexto limpio.

Explorar un repo para responder "¿dónde se calcula el IVA?" puede costar 20 lecturas y
30k tokens. Si lo hace el agente principal, esas lecturas se quedan en SU contexto para
siempre. Un subagente hace la exploración en un contexto propio y devuelve solo la
conclusión: el principal paga ~300 tokens.

Perfiles de subagente: ficheros Markdown con frontmatter en .forja/agents/*.md
    ---
    name: revisor
    description: Revisa un diff buscando bugs y problemas de estilo.
    tools: read_file, grep, glob
    ---
    Eres un revisor de código exigente…
"""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .agent import Agent, Events
from .tools import Tool, ToolRegistry, ToolResult, tool
from .types import ChatModel, ToolCall

EXPLORE = """Eres un subagente de exploración de código. Tu trabajo es investigar el repositorio con read_file, grep y glob
y devolver una respuesta concreta para la tarea que te encargan. NO modificas nada.
Responde con: conclusión en 2-4 frases + lista de ficheros relevantes con líneas (ruta:línea) + fragmentos clave si ayudan."""


@dataclass
class AgentProfile:
    name: str
    description: str
    system: str
    tools: list[str] = field(default_factory=list)
    max_steps: int = 25


BUILTIN = {"explore": AgentProfile("explore", "Explora el código (solo lectura) y responde preguntas sobre él: dónde está X, cómo funciona Y.",
                                   EXPLORE, ["read_file", "grep", "glob"])}
FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


# ---- TODO 09.1 : cargar perfiles desde Markdown con frontmatter ----------------
def load_profiles(folder: Path) -> dict[str, AgentProfile]:
    # TODO 09.1: Empieza con dict(BUILTIN). Para cada *.md de la carpeta (si existe): FRONTMATTER.match; yaml.safe_load del frontmatter; exige name y description; tools puede ser lista o 'a, b'; max_steps opcional. El cuerpo es el system prompt.
    raise NotImplementedError("TODO 09.1")


# ---- TODO 09.2 : la tool `task` que lanza un subagente -------------------------
def make_task_tool(llm: ChatModel, parent_tools: ToolRegistry, profiles: dict[str, AgentProfile],
                   execute: Callable[[ToolCall], ToolResult] | None = None, events_factory: Callable[[str], Events] | None = None) -> Tool:
    catalog = "\n".join(f"- {p.name}: {p.description}" for p in profiles.values())

    @tool(risk="read")
    def task(description: str, prompt: str, subagent_type: str = "explore") -> str:
        """placeholder"""
        # TODO 09.2: Busca el perfil (ValueError si no existe). sub_tools = parent_tools.subset(tools del perfil, sin 'task'). Agent(llm, sub_tools, execute=execute, max_steps, events=events_factory(nombre) o Events()). Mensajes NUEVOS: [system del perfil, user prompt]. Devuelve '[subagente …] ' + la respuesta.
        raise NotImplementedError("TODO 09.2")

    task.description = ("Lanza un subagente con contexto propio para una tarea autocontenida (sobre todo búsquedas y exploración "
                        "del código que requieren muchas lecturas). Devuelve solo su conclusión. Escribe un prompt completo: "
                        "el subagente no ve esta conversación.\nSubagentes disponibles:\n" + catalog)
    return task
