# Lab 03 · The agent loop

🇪🇸 [Español](README.md) · Day 1 · 11:30–12:15

**Goal:** Write the loop that turns a model into an agent: think → act → observe, until done.

## Concepts
- **Ten lines:** ask for a response with tools → if no tools requested, done → execute → append results → repeat. Every agent framework is this with more layers.
- **History is the state:** each `assistant` with `tool_calls` is followed by one `tool` message per `tool_call_id`. Breaking the pair = HTTP 400 on almost any backend.
- **Parallel reads, ordered writes:** several `read_file`/`grep` calls run in parallel; an edit and a `pytest` never do.
- **Explicit stops:** final answer, max steps, loop detected (same tool + same args) and user interrupt (Ctrl+C).
- **The loop knows nothing about permissions or UI:** it gets an `execute` function (the harness gate) and `events`. That's why we reuse it for subagents and evals.

## What you implement
| TODO | File | What |
|---|---|---|
| 03.1 | `forja/agent.py` | _run_calls: consecutive reads in parallel, order preserved |
| 03.2 | `forja/agent.py` | run: the loop with streaming, stops and loop detection |

## Run
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explícame cómo se calcula el total de una factura
```

## Checkpoint
Forja explores the playground (glob, grep, read_file) and answers with `path:line` references. Edits still ask permission crudely: that's lab 04.

## Challenges
1. Make the agent warn the user after 15 steps.
2. What happens when the model requests 10 reads at once on a slow model? Measure.

**Tests:** `tests/test_l03_agent.py` · **Fallen behind?** `python scripts/tasks.py catchup 04`

---
[← previous](../L02_tools_ficheros/README.en.md) · [next →](../L04_bash_permisos/README.en.md)
