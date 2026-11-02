# Lab 09 · Subagents

🇪🇸 [Español](README.md) · Day 2 · 11:25–12:10

**Goal:** Delegate exploration and reviews to agents with their own context and restricted tools.

## Concepts
- **The problem:** exploring a repo costs 20 reads and 30k tokens that stay in the main agent's context forever.
- **The solution:** the `task` tool launches a subagent with a CLEAN context (system + prompt) that returns only its conclusion. The main agent pays ~300 tokens.
- **Same loop, other tools:** we reuse lab 03's `Agent` with a subset of tools and the SAME permission gate. A subagent can't spawn subagents.
- **Profiles in Markdown:** `.forja/agents/reviewer.md` with frontmatter (name, description, tools). The description is what the model reads to decide when to delegate.
- **The subagent prompt must be self-contained:** it doesn't see the conversation.

## What you implement
| TODO | File | What |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: profiles from Markdown |
| 09.2 | `forja/subagents.py` | task: launch a subagent with a clean context |

## Run
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> usa un subagente para averiguar todos los sitios donde se redondea
> pide al revisor que revise mis cambios sin commitear
```

## Checkpoint
You see the subagent's tool calls prefixed `[explore]` and the main context barely grows (`/context`).

## Challenges
1. Create a `tester` subagent that can only run `python -m pytest*`.
2. Run the subagent on a smaller, faster model.

**Tests:** `tests/test_l09_subagentes.py` · **Fallen behind?** `python scripts/tasks.py catchup 10`

---
[← previous](../L08_planificacion/README.en.md) · [next →](../L10_extensiones/README.en.md)
