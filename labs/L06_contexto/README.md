# Lab 06 · Ingeniería de contexto

🇬🇧 [English](README.en.md) · Día 2 · 09:00–09:40

**Objetivo:** Decidir qué ve el modelo en cada turno: prompt por capas, AGENTS.md, entorno y menciones @fichero.

## Conceptos
- **El system prompt se reconstruye cada turno** por capas: base del agente, recordatorio del modo, instrucciones del proyecto, skills, lista de tareas y entorno (git, SO, fecha, modelo).
- **AGENTS.md:** convención abierta para instrucciones de proyecto que leen varias herramientas. Global del usuario + desde la carpeta más alta hasta la actual: lo más específico, al final.
- **Entorno = verdad barata:** rama y cambios de git, directorio, fecha. Evita que el modelo adivine.
- **@menciones:** `@src/app.py` mete el fichero en el mensaje (y cuenta como leído). Ahorra una vuelta del bucle.
- **Menos es más con modelos locales:** cada token de prompt compite con el código. Instrucciones cortas y concretas.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 06.1 | `forja/context.py` | find_instruction_files: AGENTS.md del usuario y de la jerarquía |
| 06.2 | `forja/context.py` | build_system_prompt: capas en orden |
| 06.3 | `forja/context.py` | expand_mentions: @ruta → contenido |

## Ejecuta
```bash
python scripts/tasks.py test 06
forja --cwd playground
> revisa @facturas/importes.py y dime si cumple lo que dice AGENTS.md
```

## Checkpoint
El agente cita reglas del `playground/AGENTS.md` (half-up, no tocar tests) sin que se las digas.

## Retos
1. Escribe tu `~/.forja/AGENTS.md` con tus preferencias (idioma, estilo).
2. Añade al entorno la versión de Python y los últimos 3 commits.

**Tests:** `tests/test_l06_contexto.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 07`

---
[← anterior](../L05_cli/README.md) · [siguiente →](../L07_compactacion/README.md)
