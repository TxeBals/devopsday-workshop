# Lab 07 · Context management and compaction

Day 2 · 09:40–10:25

**Goal:** Make a long session fit a local model's window without breaking history.

## Concepts
- **The budget:** local models work with 16–32k effective tokens. A verbose `pytest` or a large file eats the window.
- **Level 1 — microcompaction (free):** blank old tool outputs. The model already used them; it can re-read if needed.
- **Level 2 — compaction (1 call):** summarise old turns (goal, files, commands, decisions, pending) and keep recent ones.
- **Invariant:** cut only before a `user` message. Never between `tool_calls` and their `tool` results.
- **It's lossy:** measure it with evals (lab 12) using a small window.

## What you implement
| TODO | File | What |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: blank old outputs |
| 07.2 | `forja/compaction.py` | compact: summary + recent turns, pairs intact |

## Run
```bash
python scripts/tasks.py test 07
forja --cwd playground
> read every file in the project and summarise them
/context
/compact
/context
```

## Checkpoint
`/context` drops after `/compact` and the agent still knows what it was doing.

## Challenges
1. Set `"contextWindow": 6000` in `.forja/settings.json` and work: when does it compact?
2. Compact with a smaller model than the main one.

**Tests:** `tests/test_l07_compaction.py` · **Fallen behind?** `python scripts/tasks.py catchup 08`

---
[← previous](../L06_context/README.md) · [next →](../L08_planning/README.md)
