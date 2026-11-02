# Lab 08 · Plan before acting

Day 2 · 10:25–11:10

**Goal:** Visible task list and plan mode: the agent investigates, proposes and only executes once you approve.

## Concepts
- **todo_write:** the agent keeps its own list (pending / in_progress / completed). It forces decomposition and greatly improves small models' persistence on long tasks. One task in progress.
- **The list goes back into context** every turn (a system-prompt layer): the agent doesn't get lost.
- **Plan mode:** read-only via permissions, not via the model's goodwill. When it has a plan, it calls `exit_plan_mode`; if you approve, the harness switches to default mode.
- **When to use it:** multi-file changes, unfamiliar code, anything hard to undo.

## What you implement
| TODO | File | What |
|---|---|---|
| 08.1 | `forja/planning.py` | todo_write with validation |
| 08.2 | `forja/planning.py` | exit_plan_mode with user approval |

## Run
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> add percentage discounts to invoices (before VAT) with tests
/todos
```

## Checkpoint
In plan mode the agent investigates, presents a plan and, once approved, executes it ticking off tasks.

## Challenges
1. On approval switch to `accept_edits` instead of `default`. When is that a good idea?
2. Show the task list live under each answer.

**Tests:** `tests/test_l08_planning.py` · **Fallen behind?** `python scripts/tasks.py catchup 09`

---
[← previous](../L07_compaction/README.md) · [next →](../L09_subagents/README.md)
