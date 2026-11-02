# Lab 02 · Tools de ficheros

🇬🇧 [English](README.en.md) · Día 1 · 10:15–11:15

**Objetivo:** Dar al agente ojos y manos sobre el proyecto: leer, buscar, crear y editar ficheros con seguridad.

## Conceptos
- **El schema es el prompt:** nombre, docstring y type hints generan el JSON Schema que lee el modelo. Una buena descripción vale más que cualquier instrucción en el system prompt.
- **Las tools nunca lanzan:** cualquier error vuelve al modelo como texto accionable ("aparece 3 veces: añade contexto") para que se corrija solo.
- **edit_file = sustitución exacta de un texto único.** Es el formato más robusto con modelos pequeños (los diffs los generan mal). Errores frecuentes del modelo: incluir los números de línea de `read_file` o cambiar la indentación.
- **Leer antes de editar** y detectar cambios externos (mtime): el agente no pisa lo que no ha visto ni lo que tú has cambiado.
- **Sandbox:** todas las rutas se resuelven dentro del workspace. `../` y rutas absolutas fuera, rechazadas.
- **Explorar sin cargar el repo:** `grep` y `glob` devuelven rutas y líneas; el agente solo lee lo relevante.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: JSON Schema en formato OpenAI |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: ejecutar sin lanzar nunca |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: sandbox de rutas |
| 02.4 | `forja/fs_tools.py` | write_file: crear / reescribir con «leer antes» |
| 02.5 | `forja/fs_tools.py` | edit_file: sustitución exacta y única con errores útiles |
| 02.6 | `forja/fs_tools.py` | grep: búsqueda por regex en el workspace |

## Ejecuta
```bash
python scripts/tasks.py test 02
forja --cwd playground
> ¿qué hace la función vencimiento?        (aún no hay bucle: verás la primera tool call)
```

## Checkpoint
Tests del lab 02 en verde. Con el lab 03 todavía pendiente, Forja sigue siendo un chat: el bucle llega a continuación.

## Retos
1. Añade una tool `list_dir` con árbol de 2 niveles. ¿Mejora o empeora la exploración del modelo?
2. Pide al modelo que edite algo y fíjate en sus errores de `old_string`: ¿qué pista añadirías al mensaje de error?

**Tests:** `tests/test_l02_tools.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 03`

---
[← anterior](../L01_llm_streaming/README.md) · [siguiente →](../L03_bucle/README.md)
