"""LAB 10b — Skills: conocimiento bajo demanda (divulgación progresiva).

Meter todas las guías del equipo en el system prompt gasta contexto en cada turno.
Una skill es una carpeta con SKILL.md (frontmatter name + description + cuerpo). En el
prompt solo va el CATÁLOGO (una línea por skill); el cuerpo se carga con la tool `skill`
cuando el modelo decide que lo necesita. Mismo formato que usan otras herramientas: las
skills son portables.

    .forja/skills/conventional-commits/SKILL.md
    ---
    name: conventional-commits
    description: Cómo escribir mensajes de commit en este repo. Úsala antes de hacer git commit.
    ---
    Formato: <tipo>(<ámbito>): <resumen en imperativo>…
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from .tools import Tool, tool

FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


@dataclass
class Skill:
    name: str
    description: str
    path: Path


# ---- TODO 10.3 : descubrir skills ------------------------------------------
def discover_skills(*folders: Path) -> dict[str, Skill]:
    """Busca <carpeta>/<skill>/SKILL.md. Si dos carpetas definen la misma skill, gana la última (proyecto > usuario)."""
    # TODO 10.3: Para cada carpeta existente: */SKILL.md ordenados; FRONTMATTER + yaml; exige name y description (normaliza espacios). Las carpetas posteriores sobrescriben a las anteriores.
    raise NotImplementedError("TODO 10.3")


def catalog(skills: dict[str, Skill]) -> str:
    if not skills:
        return ""
    lines = "\n".join(f"- {s.name}: {s.description}" for s in skills.values())
    return f"## Skills disponibles (cárgalas con la tool skill cuando apliquen)\n{lines}"


# ---- TODO 10.4 : la tool que carga una skill ---------------------------------
def make_skill_tool(skills: dict[str, Skill]) -> Tool:
    @tool(risk="read")
    def skill(name: str) -> str:
        """Carga las instrucciones completas de una skill del catálogo.

        Args:
            name: Nombre de la skill.
        """
        # TODO 10.4: Skill desconocida -> ValueError con las disponibles. Devuelve '# Skill: nombre', la carpeta y el CUERPO sin frontmatter.
        raise NotImplementedError("TODO 10.4")

    return skill
