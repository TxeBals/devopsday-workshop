# Lab 05 · The CLI: your terminal agent

Day 1 · 14:00–15:00

**Goal:** Turn the harness into a pleasant tool: streaming, action summaries, diffs, approvals and slash commands.

## Concepts
- **Experience is part of the product:** the user must see WHAT the agent does (one line per tool), HOW the code changes (diff) and be able to stop it (Ctrl+C) or correct it.
- **Clear approvals:** what will run, why it's being asked (decision reason) and three answers: `y` (yes), `n` (no), `a` (always).
- **Slash commands:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. They act on the harness without going through the model.
- **Headless:** `forja -p "…"` runs and exits: scripts, CI and evals (lab 12). With no user, anything needing approval is denied.

## What you implement
| TODO | File | What |
|---|---|---|
| 05.1 | `forja/cli.py` | summarize_call: one readable line per tool call |
| 05.2 | `forja/cli.py` | diff_styles: colour the diff |
| 05.3 | `forja/cli.py` | ask_approval: y / n / a (yes / no / always) |
| 05.4 | `forja/cli.py` | handle_slash: slash commands |

## Run
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> fix the amount rounding bug and check with the tests
/tools
/cost
```

## Checkpoint
**Day 1 milestone** (15:15): Forja fixes the 3 failing tests in `playground/` with your local model. Compare with a neighbour using another model.

## Challenges
1. Add `/model <name>` to switch models on the fly.
2. Show the % of context used in the REPL prompt.

**Tests:** `tests/test_l05_cli.py` · **Fallen behind?** `python scripts/tasks.py catchup 06`

---
[← previous](../L04_bash_permissions/README.md) · [next →](../L06_context/README.md)
