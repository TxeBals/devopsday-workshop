# Ejemplos de extensibilidad (lab 10)

`project/.forja/` es una configuración completa para copiar a la raíz de **playground/**:

```bash
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
cd playground && forja
```

| Pieza | Fichero | Qué demuestra |
|---|---|---|
| Permisos | `settings.json` → `permissions` | allow/deny por tool y patrón |
| Hook PreToolUse | `hooks/bloquear_secretos.py` | bloquear comandos con secretos (exit 2) |
| Hook PostToolUse | `hooks/compilar.py` | feedback inmediato si una edición rompe la sintaxis |
| Hook Stop | `settings.json` → `Stop` | el agente no "termina" hasta que pasan los tests |
| Skill | `skills/conventional-commits/SKILL.md` | conocimiento bajo demanda |
| Subagente | `agents/revisor.md` | perfil propio con tools restringidas |
| MCP | `../mcp/issues_server.py` | issues como tools `mcp__issues__*` |

Prueba: *"Lista las issues abiertas, arregla la #12 y comenta en la issue qué cambiaste"*.
