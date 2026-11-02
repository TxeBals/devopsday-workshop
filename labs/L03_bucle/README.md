# Lab 03 · El bucle del agente

🇬🇧 [English](README.en.md) · Día 1 · 11:30–12:15

**Objetivo:** Escribir el bucle que convierte un modelo en un agente: pensar → actuar → observar, hasta terminar.

## Conceptos
- **Diez líneas:** pedir respuesta con tools → si no pide tools, fin → ejecutar → añadir resultados → repetir. Todo framework de agentes es esto con más capas.
- **El historial es el estado:** cada `assistant` con `tool_calls` va seguido de un mensaje `tool` por cada `tool_call_id`. Romper ese par = error 400 en casi cualquier backend.
- **Lecturas en paralelo, escrituras en orden:** varias `read_file`/`grep` a la vez se ejecutan en paralelo; una edición y un `pytest` nunca.
- **Paradas explícitas:** respuesta final, máximo de pasos, bucle detectado (misma tool + mismos argumentos) e interrupción del usuario (Ctrl+C).
- **El bucle no sabe de permisos ni de interfaz:** recibe una función `execute` (la puerta del harness) y unos `events`. Por eso lo reutilizamos para subagentes y evals.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 03.1 | `forja/agent.py` | _run_calls: lecturas consecutivas en paralelo, orden preservado |
| 03.2 | `forja/agent.py` | run: el bucle con streaming, paradas y detección de bucles |

## Ejecuta
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explícame cómo se calcula el total de una factura
```

## Checkpoint
Forja explora el playground (glob, grep, read_file) y responde con referencias `ruta:línea`. Las ediciones aún piden permiso de forma rudimentaria: eso es el lab 04.

## Retos
1. Haz que el agente avise al usuario si lleva más de 15 pasos.
2. ¿Qué pasa si el modelo pide 10 lecturas a la vez con un modelo lento? Mide.

**Tests:** `tests/test_l03_agent.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 04`

---
[← anterior](../L02_tools_ficheros/README.md) · [siguiente →](../L04_bash_permisos/README.md)
