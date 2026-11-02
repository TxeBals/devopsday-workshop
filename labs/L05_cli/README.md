# Lab 05 · La CLI: tu agente de terminal

🇬🇧 [English](README.en.md) · Día 1 · 14:00–15:00

**Objetivo:** Convertir el harness en una herramienta agradable: streaming, resumen de acciones, diffs, aprobaciones y comandos slash.

## Conceptos
- **La experiencia es parte del producto:** el usuario tiene que ver QUÉ hace el agente (una línea por tool), CÓMO cambia el código (diff) y poder pararlo (Ctrl+C) o corregirlo.
- **Aprobaciones claras:** qué se va a ejecutar, por qué se pregunta (motivo de la decisión) y tres respuestas: sí, no, siempre.
- **Comandos slash:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. Operan sobre el harness sin pasar por el modelo.
- **Headless:** `forja -p "…"` ejecuta y sale: scripts, CI y evals (lab 12). Sin usuario, lo que pide permiso se deniega.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 05.1 | `forja/cli.py` | summarize_call: una línea legible por tool call |
| 05.2 | `forja/cli.py` | diff_styles: colorear el diff |
| 05.3 | `forja/cli.py` | ask_approval: sí / no / siempre |
| 05.4 | `forja/cli.py` | handle_slash: comandos slash |

## Ejecuta
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> arregla el bug del redondeo de importes y comprueba con los tests
/tools
/cost
```

## Checkpoint
**Hito del día 1** (15:15): Forja arregla los 3 tests que fallan en `playground/` con tu modelo local. Compara con el compañero que usa otro modelo.

## Retos
1. Añade `/model <nombre>` para cambiar de modelo en caliente.
2. Muestra en el prompt de la REPL el % de contexto usado.

**Tests:** `tests/test_l05_cli.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 06`

---
[← anterior](../L04_bash_permisos/README.md) · [siguiente →](../L06_contexto/README.md)
