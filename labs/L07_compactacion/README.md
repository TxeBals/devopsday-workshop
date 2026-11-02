# Lab 07 · Gestión de contexto y compactación

🇬🇧 [English](README.en.md) · Día 2 · 09:40–10:25

**Objetivo:** Que una sesión larga quepa en la ventana de un modelo local sin romper el historial.

## Conceptos
- **El presupuesto:** modelos locales trabajan con 16–32k tokens efectivos. Un `pytest` verboso o un fichero grande se comen la ventana.
- **Nivel 1 — microcompactación (gratis):** vaciar salidas de tools antiguas. El modelo ya las usó; si las necesita, vuelve a leer.
- **Nivel 2 — compactación (1 llamada):** resumir los turnos antiguos (objetivo, ficheros, comandos, decisiones, pendientes) y conservar los recientes.
- **Invariante:** solo se corta antes de un mensaje `user`. Nunca entre un `tool_calls` y sus `tool`.
- **Es con pérdida:** mídelo con evals (lab 12) usando una ventana pequeña.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: vaciar salidas antiguas |
| 07.2 | `forja/compaction.py` | compact: resumen + turnos recientes, sin romper pares |

## Ejecuta
```bash
python scripts/tasks.py test 07
forja --cwd playground
> lee todos los ficheros del proyecto y resúmelos
/context
/compact
/context
```

## Checkpoint
`/context` baja tras `/compact` y el agente sigue sabiendo qué estaba haciendo.

## Retos
1. Pon `"contextWindow": 6000` en `.forja/settings.json` y trabaja: ¿cuándo compacta?
2. Compacta con un modelo más pequeño que el principal.

**Tests:** `tests/test_l07_compactacion.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 08`

---
[← anterior](../L06_contexto/README.md) · [siguiente →](../L08_planificacion/README.md)
