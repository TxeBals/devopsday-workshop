# Lab 10 · Extensibility: hooks, skills and MCP

Day 2 · 12:10–13:20

**Goal:** Let the team extend the agent without touching its code: deterministic policy, on-demand knowledge and external tools.

## Concepts
- **Hooks = guarantees:** AGENTS.md *asks*, a hook *enforces*. Shell commands in `settings.json` that receive the event as JSON on stdin. Exit 2 blocks; exit 0 continues. It's the convention commercial agents use: what you learn here applies there.
- **Events:** `PreToolUse` (block), `PostToolUse` (feedback, e.g. a linter), `UserPromptSubmit` (filter or add context), `Stop` (don't finish until tests pass).
- **Skills = progressive disclosure:** only the catalogue (name + description) goes in the prompt; the body is loaded with the `skill` tool when needed. Portable `SKILL.md` format.
- **MCP:** servers that expose tools (issues, DB, wiki, CI). Forja starts them from `settings.json` and registers them as `mcp__server__tool`, with `exec` risk: they go through permissions.

## What you implement
| TODO | File | What |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks by event and matcher |
| 10.2 | `forja/hooks.py` | run: execute and map exit codes |
| 10.3 | `forja/skills.py` | discover_skills: SKILL.md catalogue |
| 10.4 | `forja/skills.py` | skill: load the body on demand |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: mcp__server__tool namespace |

## Run
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # if you didn't in lab 09
forja --cwd playground
> list the open issues, fix #12 and comment on the issue what you changed
> commit following the repo's convention
```

## Checkpoint
The Stop hook won't let it finish with red tests; the agent loads the `conventional-commits` skill before committing; `mcp__issues__*` tools show up in `/tools`.

## Challenges
1. A PostToolUse hook that runs `ruff` on the edited file.
2. Connect a real MCP server from your team.

**Tests:** `tests/test_l10_extensions.py` · **Fallen behind?** `python scripts/tasks.py catchup 11`

---
[← previous](../L09_subagents/README.md) · [next →](../L11_sessions/README.md)
