# Lab 09 · Subagentes

🇬🇧 [English](README.en.md) · Día 2 · 11:25–12:10

**Objetivo:** Delegar exploraciones y revisiones en agentes con contexto propio y tools restringidas.

## Conceptos
- **El problema:** explorar un repo cuesta 20 lecturas y 30k tokens que se quedan en el contexto del agente principal para siempre.
- **La solución:** la tool `task` lanza un subagente con contexto LIMPIO (system + prompt) que devuelve solo la conclusión. El principal paga ~300 tokens.
- **Mismo bucle, otras tools:** reutilizamos `Agent` del lab 03 con un subconjunto de tools y la MISMA puerta de permisos. Un subagente no lanza subagentes.
- **Perfiles en Markdown:** `.forja/agents/revisor.md` con frontmatter (name, description, tools). La descripción es lo que lee el modelo para decidir cuándo delegar.
- **El prompt del subagente debe ser autocontenido:** no ve la conversación.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: perfiles desde Markdown |
| 09.2 | `forja/subagents.py` | task: lanzar un subagente con contexto limpio |

## Ejecuta
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> usa un subagente para averiguar todos los sitios donde se redondea
> pide al revisor que revise mis cambios sin commitear
```

## Checkpoint
Ves las tool calls del subagente con prefijo `[explore]` y el contexto del principal apenas crece (`/context`).

## Retos
1. Crea un subagente `tester` que solo pueda ejecutar `python -m pytest*`.
2. Ejecuta el subagente con un modelo más pequeño y rápido.

**Tests:** `tests/test_l09_subagentes.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 10`

---
[← anterior](../L08_planificacion/README.md) · [siguiente →](../L10_extensiones/README.md)
