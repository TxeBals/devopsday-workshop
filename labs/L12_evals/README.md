# Lab 12 · Evals: medir tu agente

🇬🇧 [English](README.en.md) · Día 2 · 14:55–16:00

**Objetivo:** Comparar modelos y cambios del harness con tareas reales y comprobaciones objetivas.

## Conceptos
- **Sin medir, todo es opinión.** ¿Es mejor `qwen3-coder:30b` que `qwen3:8b`? ¿Tu nuevo prompt ayuda? Se mide.
- **Tarea = prompt + comprobación objetiva** sobre una COPIA limpia del proyecto: tests (`command`), tests OCULTOS que se copian después (`hidden`, para que no haga trampa), contenido de la respuesta (`answer_contains`) y no modificar nada (`forbid_changes`).
- **Headless + bypass dentro de la copia:** el sandbox es la carpeta temporal.
- **Varias repeticiones:** los modelos no son deterministas. Mira pass rate, pasos, tiempo y tokens.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: aplicar las comprobaciones |
| 12.2 | `forja/evals.py` | summarize: pass rate, por tarea, pasos, tiempo, tokens |

## Ejecuta
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_redondeo
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
```

## Checkpoint
Tienes un informe en `out/` y puedes decir, con números, qué modelo usarías y para qué tareas.

## Retos
1. Añade una tarea propia a `evals/tasks.yaml`.
2. Compara tu harness con y sin `todo_write` en el prompt base.

**Tests:** `tests/test_l12_evals.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup end`

---
[← anterior](../L11_sesiones/README.md)
