# Lab 06 · Context engineering

Day 2 · 09:00–09:40

**Goal:** Decide what the model sees each turn: layered prompt, AGENTS.md, environment and @file mentions.

## Concepts
- **The system prompt is rebuilt every turn** in layers: agent base, mode reminder, project instructions, skills, todo list and environment (git, OS, date, model).
- **AGENTS.md:** an open convention for project instructions read by several tools. User global + from the highest folder down to the current one: most specific last.
- **Environment = cheap truth:** git branch and changes, directory, date. Stops the model guessing.
- **@mentions:** `@src/app.py` puts the file in the message (and marks it read). Saves a loop iteration.
- **Less is more with local models:** every prompt token competes with code. Short, concrete instructions.

## What you implement
| TODO | File | What |
|---|---|---|
| 06.1 | `forja/context.py` | find_instruction_files: user and hierarchy AGENTS.md |
| 06.2 | `forja/context.py` | build_system_prompt: layers in order |
| 06.3 | `forja/context.py` | expand_mentions: @path → content |

## Run
```bash
python scripts/tasks.py test 06
forja --cwd playground
> review @invoices/amounts.py and tell me whether it follows AGENTS.md
```

## Checkpoint
The agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told.

## Challenges
1. Write your `~/.forja/AGENTS.md` with your preferences (language, style).
2. Add the Python version and last 3 commits to the environment.

**Tests:** `tests/test_l06_context.py` · **Fallen behind?** `python scripts/tasks.py catchup 07`

---
[← previous](../L05_cli/README.md) · [next →](../L07_compaction/README.md)
