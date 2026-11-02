# Lab 11 · Sesiones y deshacer

🇬🇧 [English](README.en.md) · Día 2 · 14:20–14:55

**Objetivo:** Retomar sesiones y deshacer lo que hizo el agente sin depender de git.

## Conceptos
- **Transcript JSONL append-only:** un mensaje por línea en `.forja/sessions/`. Reanudar, auditar y depurar. Tras compactar, una marca con el nuevo estado.
- **Checkpoints:** antes de que una tool modifique un fichero, se guarda su contenido original (o que no existía) — solo la primera vez por turno.
- **/undo:** restaura los ficheros del último turno con cambios. Funciona en carpetas sin git y no toca tus commits.
- **Límite:** los efectos de `bash` (instalar paquetes, borrar con `rm`) no se deshacen. Por eso bash pasa por permisos.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (con marcas de compactación) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

## Ejecuta
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> cambia el vencimiento por defecto a 60 días
/undo
/sessions
forja --cwd playground --resume <id>
```

## Checkpoint
`/undo` deja el fichero como estaba y `--resume` continúa la conversación anterior.

## Retos
1. `/undo N` para deshacer varios turnos.
2. `/rewind`: deshacer ficheros Y volver el historial al mismo punto.

**Tests:** `tests/test_l11_sesiones.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 12`

---
[← anterior](../L10_extensiones/README.md) · [siguiente →](../L12_evals/README.md)
