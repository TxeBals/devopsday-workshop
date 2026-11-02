# Lab 10 · Extensibilidad: hooks, skills y MCP

🇬🇧 [English](README.en.md) · Día 2 · 12:10–13:20

**Objetivo:** Que el equipo extienda el agente sin tocar su código: política determinista, conocimiento bajo demanda y herramientas externas.

## Conceptos
- **Hooks = garantías:** AGENTS.md *pide*, un hook *impide*. Comandos de shell en `settings.json` que reciben el evento como JSON por stdin. Exit 2 bloquea; exit 0 sigue. Es la convención que usan los agentes comerciales: lo que aprendáis aquí os sirve allí.
- **Eventos:** `PreToolUse` (bloquear), `PostToolUse` (feedback, p. ej. linter), `UserPromptSubmit` (filtrar o añadir contexto), `Stop` (no terminar hasta que pasen los tests).
- **Skills = divulgación progresiva:** en el prompt solo va el catálogo (nombre + descripción); el cuerpo se carga con la tool `skill` cuando hace falta. Formato portable `SKILL.md`.
- **MCP:** servidores que exponen tools (issues, BD, wiki, CI). Forja los arranca desde `settings.json` y los registra como `mcp__servidor__tool`, con riesgo `exec`: pasan por permisos.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks por evento y matcher |
| 10.2 | `forja/hooks.py` | run: ejecutar y traducir códigos de salida |
| 10.3 | `forja/skills.py` | discover_skills: catálogo de SKILL.md |
| 10.4 | `forja/skills.py` | skill: cargar el cuerpo bajo demanda |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: espacio de nombres mcp__server__tool |

## Ejecuta
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # si no lo hiciste en el lab 09
forja --cwd playground
> lista las issues abiertas, arregla la #12 y comenta en la issue qué cambiaste
> haz commit siguiendo la convención del repo
```

## Checkpoint
El hook Stop no deja terminar con tests en rojo; el agente carga la skill `conventional-commits` antes de hacer commit; las tools `mcp__issues__*` aparecen en `/tools`.

## Retos
1. Hook PostToolUse que ejecute `ruff` sobre el fichero editado.
2. Conecta un servidor MCP real de tu equipo (o el de seguros del workshop de nivel 3).

**Tests:** `tests/test_l10_extensiones.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 11`

---
[← anterior](../L09_subagentes/README.md) · [siguiente →](../L11_sesiones/README.md)
