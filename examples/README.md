# Extensibility examples (lab 10)

`project/.forja/` is a complete configuration to copy into the root of **playground/**:

```bash
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
cd playground && forja
```

| Piece | File | What it shows |
|---|---|---|
| Permissions | `settings.json` → `permissions` | allow/deny by tool and pattern |
| PreToolUse hook | `hooks/block_secrets.py` | block commands that touch secrets (exit 2) |
| PostToolUse hook | `hooks/compile_check.py` | immediate feedback if an edit breaks the syntax |
| Stop hook | `hooks/stop_tests.py` | if the agent changed files (git), it can't "finish" while the tests fail (max 3 extra rounds) |
| Skill | `skills/conventional-commits/SKILL.md` | on-demand knowledge |
| Subagent | `agents/reviewer.md` | custom profile with restricted tools |
| MCP | `../mcp/issues_server.py` | issues as `mcp__issues__*` tools |

Try: *"List the open issues, fix #12 and comment on the issue what you changed"*.
