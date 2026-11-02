# Lab 12 · Evals: measure your agent

🇪🇸 [Español](README.md) · Day 2 · 14:55–16:00

**Goal:** Compare models and harness changes with real tasks and objective checks.

## Concepts
- **Without measuring, it's all opinion.** Is `qwen3-coder:30b` better than `qwen3:8b`? Does your new prompt help? Measure it.
- **Task = prompt + objective check** on a CLEAN COPY of the project: tests (`command`), HIDDEN tests copied afterwards (`hidden`, so it can't cheat), answer content (`answer_contains`) and changing nothing (`forbid_changes`).
- **Headless + bypass inside the copy:** the sandbox is the temp folder.
- **Several repetitions:** models aren't deterministic. Look at pass rate, steps, time and tokens.

## What you implement
| TODO | File | What |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: apply the checks |
| 12.2 | `forja/evals.py` | summarize: pass rate, per task, steps, time, tokens |

## Run
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_redondeo
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
```

## Checkpoint
You have a report in `out/` and can say, with numbers, which model you'd use for which tasks.

## Challenges
1. Add your own task to `evals/tasks.yaml`.
2. Compare your harness with and without `todo_write` in the base prompt.

**Tests:** `tests/test_l12_evals.py` · **Fallen behind?** `python scripts/tasks.py catchup end`

---
[← previous](../L11_sesiones/README.en.md)
