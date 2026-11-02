# Lab 08 · Planificar antes de actuar

🇬🇧 [English](README.en.md) · Día 2 · 10:25–11:10

**Objetivo:** Lista de tareas visible y modo plan: el agente investiga, propone y solo ejecuta cuando apruebas.

## Conceptos
- **todo_write:** el agente mantiene su lista (pending / in_progress / completed). Obliga a descomponer y mejora mucho la constancia de modelos pequeños en tareas largas. Una sola tarea en curso.
- **La lista vuelve al contexto** cada turno (capa del system prompt): el agente no se pierde.
- **Modo plan:** solo lectura por permisos, no por buena voluntad del modelo. Cuando tiene un plan, llama a `exit_plan_mode`; si lo apruebas, el harness cambia a modo default.
- **Cuándo usarlo:** cambios de varios ficheros, código que no conoces, cualquier cosa difícil de deshacer.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 08.1 | `forja/planning.py` | todo_write con validación |
| 08.2 | `forja/planning.py` | exit_plan_mode con aprobación del usuario |

## Ejecuta
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> añade descuentos porcentuales a las facturas (antes del IVA) con tests
/todos
```

## Checkpoint
En modo plan el agente investiga, presenta un plan y, al aprobarlo, lo ejecuta marcando tareas.

## Retos
1. Al aprobar, pasa a `accept_edits` en vez de `default`. ¿Cuándo es buena idea?
2. Muestra la lista de tareas en vivo bajo cada respuesta.

**Tests:** `tests/test_l08_planificacion.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 09`

---
[← anterior](../L07_compactacion/README.md) · [siguiente →](../L09_subagentes/README.md)
