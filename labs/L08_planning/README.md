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

## Before you start
- Open `forja/planning.py`. Provided: `TodoItem` (pydantic model with `content: str` and `status: "pending" | "in_progress" | "completed"`, default `pending`), `ICON` and `TodoStore` with `.items` and `.render()` (one line `☐/▶/☑ content` per item, or `(empty list)`). You write the BODIES of two tools, inside factory functions.
- Both tools are created with `@tool(risk="read")` from lab 02: the docstring and type hints become the JSON schema the model reads, so do not change them. Raising an exception inside a tool is the right way to reject bad input: `ToolRegistry.execute` turns it into `ERROR in '<tool>': ValueError: <message>` and the model can correct itself.
- Arguments reach your function AFTER pydantic validation and `model_dump()`, so `todos` normally arrives as a list of plain dicts; but code may also call the function with `TodoItem` objects. Accept both (`TodoItem.model_validate(d)`).
- How it connects: `Forja._build_registry` registers `make_todo_tool(self.todos)` and `make_exit_plan_tool(self._approve_plan, lambda: self.set_mode("default"))`. The task list goes back into the system prompt every step via `extra` in `build_system_prompt` (lab 06). Plan mode is read-only because `permissions.decide` (lab 04) denies non-read tools in `plan`, not because the model behaves.

## Step by step
08.1 first (validation logic, fully unit-tested by `test_todo_write_validation`), then 08.2 (short). `test_plan_mode_flow`, selected with 08.2, drives a whole plan-mode turn through the harness and needs 08.1, 08.2, lab 04 (plan-mode deny) and lab 06 (the prompt layers) all working.

### TODO 08.1 · `forja/planning.py` · `make_todo_tool(store)` → inner `todo_write(todos: list[TodoItem]) -> str`

**What it must do:** Replaces the WHOLE list in `store.items` with the given items, after validating: each item converted to `TodoItem`; more than one `in_progress` → `ValueError` (its message must contain `one task`, e.g. `only one task can be in_progress at a time`); an item with empty/blank `content` → `ValueError`. Validation happens BEFORE touching the store: on error the previous list stays. Returns `"List updated (X/N completed):\n" + store.render()` (X = completed, N = total). `test_todo_write_validation` expects `1/3` in the output, render lines `["☑ read", "▶ edit", "☐ tests"]`, and after the double-`in_progress` call: `ok` false, `one task` in the output and still 3 items in the store.

**Steps:**
1. Convert: `items = [t if isinstance(t, TodoItem) else TodoItem.model_validate(t) for t in todos]`.
2. Count items with `status == "in_progress"`; if more than 1, raise `ValueError` with a message the model can act on.
3. If any item has `not t.content.strip()`, raise `ValueError`.
4. Only now assign `store.items = items`.
5. Count completed items and return the header line plus `store.render()`.

**Watch out for:**
- Assign `store.items` only after all checks pass: the test checks that a rejected call leaves the old 3 items.
- The error text must contain `one task` (the test does `"one task" in two.output`).
- `content` of only spaces is also empty: use `.strip()`.
- Raise, do not return an error string: a returned string counts as success (`ok=True`) and the test expects `not two.ok`.
- Keep the factory shape: `todo_write` must stay an inner function that closes over `store` and is returned at the end.

<details><summary>💡 Hint 1</summary>

Three phases: normalise, validate, commit. Commit last.

</details>

<details><summary>💡 Hint 2</summary>

`sum(t.status == "in_progress" for t in items)` counts booleans.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
items = [...]               # dict or TodoItem -> TodoItem
if sum(...) > 1:
    raise ValueError("only one task can be in_progress at a time")
if any(...):                # blank content
    raise ValueError(...)
store.items = items
done = ...
return f"List updated ({done}/{len(items)} completed):\n{store.render()}"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l08_planning.py -k todo_write -v
```

### TODO 08.2 · `forja/planning.py` · `make_exit_plan_tool(approve, on_approved)` → inner `exit_plan_mode(plan: str) -> str`

**What it must do:** Empty/blank `plan` → `ValueError`. Otherwise call `approve(plan)` exactly once (in the CLI it shows the plan as Markdown and asks `Approve the plan and start? [y/N]`; headless or in tests it is a function returning `bool`). If approved: call `on_approved()` (the harness switches to `default` mode) and return a text containing `APPROVED` that tells the model it is no longer in plan mode and must implement the plan step by step and verify. If rejected: do NOT call `on_approved`, and return a text containing `REJECTED` saying it is still in plan mode and should ask what to change or propose an alternative. `test_exit_plan_tool` checks both branches and that the callback ran only on approval; `test_plan_mode_flow` checks that after approval `app.mode == "default"`.

**Steps:**
1. Validate `plan.strip()`; raise `ValueError` if empty.
2. Call `approve(plan)` once and keep the boolean.
3. If true: call `on_approved()`, then return the APPROVED instruction.
4. If false: return the REJECTED instruction.

**Watch out for:**
- The words `APPROVED` and `REJECTED` must be uppercase in the text: the tests look for them, and uppercase also helps small models notice the state change.
- Call `on_approved()` only in the approved branch, and only once.
- The return text is an instruction for the MODEL, not for the user: say clearly what to do next (implement + verify, or ask/propose). A vague `ok` makes small models re-plan forever.
- Do not change the mode yourself here: the tool does not know the harness; the `on_approved` callback does it.

<details><summary>💡 Hint 1</summary>

It is a guard clause plus an if/else around a callback.

</details>

<details><summary>💡 Hint 2</summary>

The two callbacks are injected so the tool is testable without a UI or a harness.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
if not plan.strip():
    raise ValueError(...)
if approve(plan):
    ...                     # callback
    return "The user APPROVED the plan. ..."
return "The user REJECTED the plan. ..."
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l08_planning.py -k "exit_plan or plan_mode_flow" -v
```

## Run
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> add percentage discounts to invoices (before VAT) with tests
/todos
```

## Try it in your agent
1. `python scripts/tasks.py reset`, then `forja --cwd playground --mode plan`. The prompt reads `plan ›`.
2. Ask: `add percentage discounts to invoices (before VAT) with tests`. Expected: only read actions (`⏺ Read ...`, `⏺ Grep ...`, `⏺ Glob ...`). If the model tries an edit you see a red `⎿ DENIED (plan mode: read-only) ...` and it goes back to investigating.
3. A magenta `Proposed plan` panel appears with files to touch, changes and how to verify, followed by `Approve the plan and start? [y/N] >`. Answer `n` once: the model gets `REJECTED` and asks what to change. Tell it what to adjust and approve with `y` the next time.
4. After `y`: the REPL mode becomes `default` (the next prompt shows `default ›`), edits now ask for approval, and you see `⏺ Todos (N)` lines as the agent ticks tasks off. Type `/todos` any time: `☑ ...`, `▶ ...`, `☐ ...`.
5. At the end the agent runs the tests; check yourself with `cd playground` and `python -m pytest -q`. Then `python scripts/tasks.py reset` to clean up.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_todo_write_validation`: `assert len(store.items) == 3` fails (it is 2) | You assigned `store.items` before validating → validate first, commit last. |
| `test_todo_write_validation`: `not two.ok` fails | You returned an error string instead of raising → `raise ValueError(...)`. |
| `AttributeError: 'dict' object has no attribute 'status'` | The registry passes dicts → convert with `TodoItem.model_validate(d)` (keep `TodoItem` instances as they are). |
| `test_plan_mode_flow`: `assert "PLAN mode" in llm.calls[0]["messages"][0]["content"]` fails | Lab 06 is not done, so the harness uses `FALLBACK_PROMPT` → finish 06.2 (or run `python scripts/tasks.py catchup 07`). |
| `test_plan_mode_flow`: the first tool result is not `DENIED` | Lab 04's `decide` does not deny non-read tools in plan mode → check TODO 04.x; the message must contain `plan mode`. |
| Real model never calls `exit_plan_mode` and just writes the plan as text | Small models do that → say it explicitly: `when you have the plan, present it with exit_plan_mode`; or try a stronger model. |
| Real model sets several tasks `in_progress` and loops on the error | Make the `ValueError` message actionable (`only one task can be in_progress at a time`); the model reads it and retries with one. |
| Headless (`forja -p ... --mode plan`) always rejects the plan | With no user, `plan_approver` is `None` → expected; plan mode is meant for interactive use. |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 08` → 3 passed.
- [ ] [ ] In plan mode the agent investigates, presents a plan with `exit_plan_mode`, and after `y` executes it ticking off tasks (`/todos` shows progress).
- [ ] [ ] You saw at least one `DENIED (plan mode: read-only)` or one `REJECTED` and the agent recovered.

## Checkpoint
In plan mode the agent investigates, presents a plan and, once approved, executes it ticking off tasks.

## Challenges
1. On approval switch to `accept_edits` instead of `default`. When is that a good idea?
2. Show the task list live under each answer.

**Tests:** `tests/test_l08_planning.py` · **Fallen behind?** `python scripts/tasks.py catchup 09`

---
[← previous](../L07_compaction/README.md) · [next →](../L09_subagents/README.md)
