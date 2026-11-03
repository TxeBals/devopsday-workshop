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

## Before you start
- Open `forja/cli.py`. Almost everything in it is provided UI plumbing (`RichEvents`, `repl`, `main`, `doctor`). You only write four small functions: `summarize_call`, `diff_styles`, `ask_approval` and `handle_slash`. Read `RichEvents.on_tool_start` / `on_tool_end` first: they show exactly where your functions are called.
- The UI calls your functions through `_safe(...)`, which only swallows `NotImplementedError`. Any other exception (e.g. a `KeyError` because the model omitted an argument) would crash the turn, so be defensive with `dict.get`.
- Libraries used: `rich` (`console.print`, `Panel`, `Text`), already imported. You do not need to learn rich in depth: `console.print(Panel(Text("..."), title="...", border_style="yellow"))` is all 05.3 needs.
- How it connects to the harness: `Forja.gate` (in `forja/harness.py`) calls `self.approver(tool, args, why)` when permissions answer `ask`; `build_app` passes your `ask_approval` as that approver. `handle_slash` receives the `Forja` object, so read the attributes it uses: `app.mode`, `app.set_mode()`, `app.registry.tools`, `app.todos`, `app.context_tokens()`, `app.compact_now()`, `app.usage`, `app.undo()`, `app.transcript.folder`, `app.history`, `app.settings.context_window`.
- This lab ends with the **day-1 milestone** (see the milestone section): your own agent fixes the 3 failing tests in `playground/`. Keep 15 minutes for it.

## Step by step
Do 05.2 first (5 minutes, pure string logic, builds confidence), then 05.1 (string formatting with many cases, and 05.3 reuses it), then 05.3 (tiny once 05.1 exists), and finish with 05.4, which is the longest and needs a quick read of `Forja` in `forja/harness.py`. Run each TODO's test as you go; then run the whole lab with `python scripts/tasks.py test 05` and go to the milestone.

### TODO 05.1 · `forja/cli.py` · `summarize_call(name, args, width=100) -> str`

**What it must do:** Receives the tool name and the (raw, possibly incomplete) argument dict the model sent. Returns ONE line, at most `width` characters. Exact formats checked by `test_summarize_call`:
- `read_file` -> `Read a.py`; with `offset` different from 1 -> `Read a.py (from line 50)`
- `write_file` -> `Write n.md (2 lines)` (number of lines of `content`)
- `edit_file` -> `Edit path`
- `bash` -> `$ pytest -q` (the command, whitespace collapsed)
- `grep` -> `Grep 'def x' in src (*.py)` (path defaults to `.`; ` (include)` only if include is set)
- `glob` -> `Glob pattern`
- `task` -> `Task[explore] find VAT` (`subagent_type` defaults to `explore`)
- `todo_write` -> `Todos (N)` (number of items)
- anything else -> `name(k=v, k2=v2)`, e.g. `mcp__x__y(id=3)`
All runs of whitespace (spaces, newlines) become a single space. If the line is longer than `width`, cut it so the result is exactly `width` characters long, ending in `…`.

**Steps:**
1. Branch on `name` with an `if/elif` chain and build a string `s` for each known tool, reading arguments with `args.get(key, default)`.
2. For `read_file`, start with `Read <path>` and append ` (from line N)` only when `args.get("offset", 1) != 1`.
3. For `write_file`, count lines with `str(content).splitlines()`; for `grep`, add the ` (<include>)` suffix only when include is truthy.
4. For the fallback, join `f"{k}={v}"` pairs with `", "` inside `name(...)` (optionally trim long values to ~30 chars each).
5. Collapse whitespace on the final string: `" ".join(s.split())`.
6. Truncate last: if `len(s) > width`, keep the first `width - 1` characters and add `…`.

**Watch out for:**
- Collapse whitespace BEFORE truncating, otherwise the length check uses the wrong string (`test_summarize_call` checks `len(...) == 50` with `width=50`).
- The cut must give exactly `width` characters including the `…` (one character), not `width + 1` and not `...` (three dots).
- `args` comes straight from the model's JSON (not validated): keys may be missing. Use `.get()` everywhere; a `KeyError` here crashes the turn.
- `bash` with `"pytest  -q\n"` must become `$ pytest -q`: double spaces and the trailing newline disappear.

<details><summary>💡 Hint 1</summary>

Think of it as a lookup of 9 formats plus two post-processing steps (collapse, truncate) applied to whatever you built.

</details>

<details><summary>💡 Hint 2</summary>

The default values matter for the expected strings: grep path `'.'`, task type `'explore'`, read offset `1`, todos `[]`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
if name == "read_file":
    s = f"Read {args.get('path')}"
    # if offset != 1: append " (from line N)"
elif name == "bash":
    s = ...
# elif ... write_file / edit_file / grep / glob / task / todo_write
else:
    s = f"{name}(...)"   # k=v pairs
s = ...                  # collapse whitespace
return ...               # truncate to width with '…'
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k summarize -v
```

### TODO 05.2 · `forja/cli.py` · `diff_styles(diff: str) -> list[tuple[str, str]]`

**What it must do:** Receives a unified diff as one string (the `diff` that `write_file`/`edit_file` put in `ToolResult.meta`). Returns one `(line, style)` tuple per line, in order, with the line text unchanged (no newline). Styles: `'+++'` or `'---'` -> `'bold'`; `'@@'` -> `'cyan'`; `'+'` -> `'green'`; `'-'` -> `'red'`; everything else -> `'dim'`. `test_diff_styles` expects `["bold", "bold", "cyan", "red", "green", "dim"]` for a 6-line diff.

**Steps:**
1. Split the diff into lines with `str.splitlines()`.
2. For each line, test the prefixes from most specific to least specific: headers (`+++`, `---`), then hunk (`@@`), then `+`, then `-`.
3. Append `(line, style)` to the output list; default style is `dim`.
4. Return the list (an empty diff gives `[]`).

**Watch out for:**
- Order matters: `'--- a/x'` also starts with `'-'`. If you test `'-'` first, headers come out red and the test fails.
- `str.startswith` accepts a tuple: `line.startswith(("+++", "---"))`.
- Do not strip lines: a context line starts with a space, and the UI prints it as-is.

<details><summary>💡 Hint 1</summary>

It is a loop with an `if/elif` chain over prefixes.

</details>

<details><summary>💡 Hint 2</summary>

Check the 3-character prefixes before the 1-character ones.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
out = []
for line in diff.splitlines():
    if line.startswith(("+++", "---")):
        style = "bold"
    # elif '@@' ... elif '+' ... elif '-' ...
    else:
        style = "dim"
    out.append(...)
return out
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k diff_styles -v
```

### TODO 05.3 · `forja/cli.py` · `ask_approval(tool, args, reason, read=input) -> Approval`

**What it must do:** Called by `Forja.gate` when the permission decision is `ask`. Shows the user what is about to run (a `Panel` with `summarize_call(tool.name, args, ...)`) and why it is being asked (`reason`, e.g. `requires approval`). Reads ONE answer by calling `read(prompt_text)`. Returns the literal string `"yes"` for `y`/`yes`, `"always"` for `a`/`always`, and `"no"` for anything else, including an empty answer. `test_ask_approval` passes `read=lambda _: "y"`, `"a"` and `""`. With `always`, the harness (not you) adds a rule via `permissions.suggest_rule`.

**Steps:**
1. Build the summary with `summarize_call(tool.name, args, width=...)`; use a large width (e.g. 400) so the user sees the full command before approving it.
2. Print it with `console.print(Panel(Text(summary), title=..., border_style="yellow"))`; put `tool.name` and `reason` in the title.
3. Call `read("  [y]es / [n]o / [a]lways this session > ")` and normalise the answer with `str(...).strip().lower()`.
4. Map the answer to `"yes"`, `"always"` or `"no"` and return it.

**Watch out for:**
- Use the `read` parameter, never `input()` or `console.input()` directly: the tests inject `read`, and under pytest a real `input()` fails because stdin is captured.
- Return exactly `"yes"` / `"no"` / `"always"` (the `Approval` literal), not booleans and not `"y"`.
- Default is NO: an empty answer (just Enter), `nope` or anything unknown -> `"no"`. Safe by default. Normalise first, so ` Y ` still counts as yes.
- Wrap the summary in `Text(...)`: if you pass a raw string, rich interprets `[brackets]` in commands as markup.

<details><summary>💡 Hint 1</summary>

Two parts: print something, then translate one answer into one of three strings.

</details>

<details><summary>💡 Hint 2</summary>

Membership tests are enough: `ans in ("y", "yes")`, `ans in ("a", "always")`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
summary = summarize_call(tool.name, args, width=400)
console.print(Panel(Text(summary), title=f"Allow {tool.name}? (...)", border_style="yellow"))
ans = ...  # read(...) normalised
if ...:
    return "yes"
# always?
return "no"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k approval -v
```

### TODO 05.4 · `forja/cli.py` · `handle_slash(app: Forja, line: str) -> str | None`

**What it must do:** Receives the raw line typed in the REPL (starts with `/`). Returns the text to print, or `None` for `/exit`. It acts on the harness directly, never calls the model. Checked by `test_slash_commands`:
- `/exit` -> `None`; `/help` -> `HELP` (contains `/mode`)
- `/mode` alone -> current mode and the list `MODES`; `/mode plan` -> exactly `mode -> plan` and `app.mode == "plan"` (use `app.set_mode`, which raises `ValueError` for unknown modes; the REPL catches it and prints `error: ...`)
- `/tools` -> one line per tool with its risk in brackets, e.g. `bash   [exec]`
- `/todos` -> `app.todos.render()` (contains `▶ a` for an in-progress item)
- `/context` -> text containing `tokens` (use `app.context_tokens()`, optionally `app.settings.context_window` and `len(app.history)`)
- `/compact` -> `app.compact_now(force=True)` (or a fallback text if it returns empty)
- `/cost` -> text containing `input` (from `app.usage['prompt_tokens']` and `['completion_tokens']`)
- `/undo` -> `app.undo()` returns a list of `Path`; show them relative (`app.ws.rel(p)`) or say nothing to undo
- `/sessions` -> `Transcript.list_sessions(app.transcript.folder)` gives `[(id, first_message)]`
- `/clear` -> empties `app.history` (and the todo list) and returns exactly `new conversation`
- anything else -> a message containing `unknown`

**Steps:**
1. Split the line into command and argument: `line.strip().split(maxsplit=1)`; the argument is the rest (or `""`).
2. Handle `/exit` and `/help` first (trivial returns).
3. `/mode`: without argument describe the current mode; with argument call `app.set_mode(arg)` and return `f"mode -> {app.mode}"`.
4. Read-only commands: `/tools` (iterate `app.registry.tools.values()`, each `Tool` has `.name` and `.risk`), `/todos`, `/context`, `/cost`, `/sessions`; build a string for each.
5. Commands with effects: `/compact`, `/undo`, `/clear` (assign `app.history = []` and `app.todos.items = []`).
6. End with the fallback for unknown commands, suggesting `/help`.

**Watch out for:**
- `/mode plan` must return exactly `mode -> plan` (ASCII `->`, one space each side).
- `/clear` must return exactly `new conversation` and leave `app.history == []` (assign a new list).
- Do not catch the `ValueError` of `set_mode` yourself and return `None`: `None` means exit and would close the REPL. Let it propagate or return an error text.
- `app.compact_now(force=True)` may return `""` (nothing to compact); return a readable fallback instead of an empty line.
- `/undo` and `/compact` depend on labs 11 and 07: until then the harness falls back quietly (empty list / nothing compacted). That is fine.

<details><summary>💡 Hint 1</summary>

A flat sequence of `if cmd == "/...": return ...` reads better than a dict of lambdas here.

</details>

<details><summary>💡 Hint 2</summary>

Everything you need is already on `app`: `app.registry.tools`, `app.todos.render()`, `app.context_tokens()`, `app.usage`, `app.transcript.folder`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
cmd, *rest = line.strip().split(maxsplit=1)
arg = rest[0].strip() if rest else ""
if cmd == "/exit":
    return None
if cmd == "/mode":
    if not arg:
        return ...            # current mode + MODES
    app.set_mode(arg)
    return f"mode -> {app.mode}"
# /help /tools /todos /context /compact /cost /undo /sessions /clear
return f"unknown command: {cmd} (/help)"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l05_cli.py -k slash -v
```

## Run
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> fix the amount rounding bug and check with the tests
/tools
/cost
```

## Try it in your agent
1. Check the model first: `forja doctor`. Expected: `backend=ollama url=... model=...`, `answered in N.Ns`, then `✔ the model calls tools (ping)`.
2. Start the REPL on the playground: `forja --cwd playground --mode accept_edits`. You see a cyan panel `Forja <version> · <model> · mode accept_edits` and the prompt `accept_edits ›`.
3. Type `/tools`: one line per tool, e.g. `read_file   [read]`, `edit_file   [edit]`, `bash   [exec]`. Then `/mode`: `current mode: accept_edits (available: default, accept_edits, plan, bypass)`.
4. Ask: `fix the amount rounding bug and check with the tests`. You should see one blue line per action (`⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`), a framed green/red diff after every edit, and a yellow `Allow bash? (requires approval)` panel before each command. Answer `a` once: a dim note `rule added for this session: allow bash(python -m pytest*)` appears and later pytest runs no longer ask.
5. After the turn: `(N steps · M tools)` in grey. Type `/cost` (`input ... · output ... tokens`) and `/context` (`~N tokens of 32768 (M messages)`).
6. Press Ctrl+C during a long answer: `interrupting…` and the agent stops at the next step boundary. Then `/exit`.

## Day-1 milestone
1. **Goal (15:15):** with YOUR Forja and YOUR local model, the 3 failing tests in `playground/` pass. Then compare results with a pair using a different model.
2. **1. Reset the playground.** From the repo root: `python scripts/tasks.py reset` (same command on Windows and macOS/Linux). Check the starting point: `cd playground` then `python -m pytest -q`, then `cd ..`. Expected summary: `3 failed, 4 passed` (`test_round_half_up`, `test_total_with_vat_cent`, `test_due_date_sunday_moves_to_monday`).
3. **2. Check the model.** `forja doctor` must end with `✔ the model calls tools`. If it prints `! the model answered without calling the tool`, switch model (`FORJA_MODEL` in `.env`) or use the classroom server before you go on.
4. **3. Start the agent.** `forja --cwd playground --mode accept_edits` (edits are auto-approved, commands ask). Start a stopwatch when you press Enter on the prompt.
5. **4. Prompt to use** (paste it as one line). Lab 06 is not done yet, so the agent does NOT see `playground/AGENTS.md`: the prompt carries the project rules itself:
> Run the tests with `python -m pytest -q`, find why 3 tests fail and fix the code in `invoices/` (never change the tests). Amounts have 2 decimals with half-up rounding using `decimal`, never `round()` on floats. Due dates falling on Saturday or Sunday move to the next Monday. When you finish, run the tests again and show me the result.
6. **5. Approvals.** When the yellow `Allow bash?` panel shows `$ python -m pytest -q`, answer `a` (always): only pytest gets a session rule. Answer `n` to anything you would not run on your own machine (installing packages, deleting files).
7. **6. What a GOOD run looks like:** `⏺ $ python -m pytest -q` (3 failures) → `⏺ Read invoices/amounts.py` / `⏺ Read invoices/dates.py` → `⏺ Edit invoices/amounts.py` with a diff that rounds through `Decimal(str(value))` + `ROUND_HALF_UP` → `⏺ Edit invoices/dates.py` with a diff that also handles Sunday → `⏺ $ python -m pytest -q` showing `7 passed` → a short summary citing the files. Typically 6–15 steps, one turn, no edits under `tests/`.
8. **7. What a BAD run looks like** (record it, it is data, not failure): the model edits `tests/` to make them pass; uses `Decimal(value)` on the float (2.675 stays 2.67) or adds `+ 0.0001` hacks; claims `all tests pass` without running pytest again; repeats the same failing `edit_file` until the loop detector stops it; rewrites a whole file with `write_file` and drops functions; answers with a code block instead of calling tools; reaches `max_steps`. Give at most two corrective follow-up prompts (e.g. `the tests still fail, run them and read the error`) and count them.
9. **8. Verify outside the agent.** `/exit`, then `cd playground` and `python -m pytest -q` → `7 passed`. Check that only `invoices/` changed: `git status playground` (or `git diff --stat playground`). If a test file changed, the run does not count as a success.
10. **9. Record your result** (in your workbook or the shared sheet): **model** (exact tag, e.g. `qwen3:8b`, plus backend: local Ollama / classroom server / OpenRouter), **success** (yes/no and tests passing out of 7; note if you needed follow-up prompts), **steps** (the grey `(N steps · M tools)` line; add them up if there were several turns), **time** (stopwatch from Enter to the final answer; optionally `/cost` tokens). Then compare with a neighbour who used another model: who needed fewer steps, who broke a rule?
11. **10. Optional: a reproducible headless run.** `python scripts/tasks.py reset`, then time it: PowerShell `Measure-Command { forja --cwd playground --mode bypass -p "<same prompt>" }`, macOS/Linux `time forja --cwd playground --mode bypass -p "<same prompt>"`. Headless has no user: in `accept_edits` every command would be DENIED, hence `bypass` (deny rules still apply). Exit code 0 means the agent finished with a final answer, not that tests pass: run pytest yourself.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_ask_approval` hangs or fails with `OSError: pytest: reading from stdin while output is captured` | You called `input()`/`console.input()` instead of the `read` parameter → call `read(prompt)`. |
| `test_summarize_call` fails on the length assertion (51 != 50) or on `$ pytest  -q` | Truncation adds `…` without removing a character, or you truncate before collapsing whitespace → collapse first, then `s[:width - 1] + "…"`. |
| `test_diff_styles` gives `['red', 'green', ...]` for the headers | You test `-`/`+` before `---`/`+++` → check the 3-character prefixes first. |
| The REPL closes when you type `/mode foo` | `handle_slash` returned `None` for an error → only `/exit` returns `None`; let `set_mode`'s `ValueError` propagate (the REPL prints `error: unknown mode: foo`). |
| `KeyError` / crash on `⏺` lines when the model sends odd arguments | `summarize_call` uses `args['x']` → use `args.get('x', default)`; arguments come unvalidated from the model. |
| `forja` is not recognised (Windows) / `command not found` (macOS/Linux) | The venv is not active or setup was not run → PowerShell `.venv\Scripts\Activate.ps1` (if blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`), macOS/Linux `source .venv/bin/activate`, then `python scripts/tasks.py setup`. `python -m forja ...` also works. |
| Windows: the agent runs `ls`, `cat` or `python3` and gets errors | The bash tool uses `cmd.exe` on Windows → normal; the model should adapt after the error. Tell it: `use python -m pytest -q; this is Windows cmd`. |
| Colours or `⏺` show as garbage in old Windows consoles | Use Windows Terminal (or VS Code's terminal) instead of the legacy `cmd.exe` window; `chcp 65001` helps for UTF-8. |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 05` → 4 passed.
- [ ] [ ] In the REPL you see one-line summaries, coloured diffs and the y/n/a approval panel; `/tools`, `/mode`, `/cost`, `/context` work.
- [ ] [ ] Day-1 milestone: your agent made the 3 failing playground tests pass, and you recorded model, success, steps and time.

## Checkpoint
**Day 1 milestone** (15:15): Forja fixes the 3 failing tests in `playground/` with your local model. Compare with a neighbour using another model.

## Challenges
1. Add `/model <name>` to switch models on the fly.
2. Show the % of context used in the REPL prompt.

**Tests:** `tests/test_l05_cli.py` · **Fallen behind?** `python scripts/tasks.py catchup 06`

---
[← previous](../L04_bash_permissions/README.md) · [next →](../L06_context/README.md)
