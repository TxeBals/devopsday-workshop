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

## Before you start
- Open `forja/context.py`. Read the provided parts first: `BASE_PROMPT`, `MODE_REMINDERS` (a dict mode -> text), `INSTRUCTION_FILES = ("AGENTS.md", "FORJA.md")`, `MENTION_RE` and `git_info(root)`. You write three functions.
- Look at `Forja.system_prompt()` and `Forja.turn()` in `forja/harness.py`: the harness calls `build_system_prompt(self.ws, self.mode, self.llm.model, self.home, cat, [todos])` EVERY step, and `expand_mentions(text, self.ws)` on every user message. Until this lab is done it uses the one-line `FALLBACK_PROMPT`, so your agent has never seen `AGENTS.md`.
- Stdlib you need: `pathlib.Path` (`/`, `.is_file()`, `.resolve()`, `.parent`, `.read_text(encoding="utf-8")`, `.is_relative_to()`), `re.Pattern.findall`, `dict.fromkeys(...)` (order-preserving de-duplication), `platform.system()`, `datetime.date.today().isoformat()`.
- From lab 02 you reuse the `Workspace` (`forja/fs_tools.py`): `ws.root`, `ws.resolve(path)` (raises `PermissionError` outside the sandbox), `ws.rel(p)` and `ws.mark_read(p)` (records the file in `ws.read_state` so a later `edit_file` does not complain that it was not read).

## Step by step
06.1 first: 06.2 calls it to get the instruction files. Then 06.2, the layered prompt, which is what turns AGENTS.md on in your CLI. 06.3 is independent; leave it for last. After 06.2 passes, lab 08's `test_plan_mode_flow` also depends on it (it checks `PLAN mode` and the task list in the system prompt).

### TODO 06.1 · `forja/context.py` · `find_instruction_files(cwd, home=None, stop=None) -> list[Path]`

**What it must do:** Returns the instruction files that apply to `cwd`, in the order they must appear in the prompt: first the user's global `home/.forja/AGENTS.md` (only if `home` is given and the file exists), then every `AGENTS.md`/`FORJA.md` found walking UP from `cwd`, returned from the HIGHEST folder down to `cwd` (most specific last). The walk stops after checking `stop` (inclusive) or at the filesystem root. `test_find_instruction_files_order` builds `home/.forja/AGENTS.md`, `repo/AGENTS.md`, `repo/pkg/AGENTS.md` and expects the contents `["global", "root", "package"]` when called with `cwd=repo/pkg, stop=tmp_path`.

**Steps:**
1. Start a `found` list with the global file if `home` is set and `home / ".forja" / "AGENTS.md"` is a file.
2. Set `d = cwd.resolve()` and loop: for each name in `INSTRUCTION_FILES`, if `d / name` is a file, add it to a `chain` list.
3. Stop the loop when `d` equals the resolved `stop`, or when `d.parent == d` (you are at the root); otherwise move to `d.parent`.
4. `chain` is now lowest-first; reverse it so the highest folder comes first.
5. Return `found + reversed chain`.

**Watch out for:**
- Resolve BOTH `cwd` and `stop` before comparing. On macOS `tmp_path` lives under `/var`, which is a symlink to `/private/var`: comparing a resolved and an unresolved path never matches, and you walk to `/`.
- Root detection: `d.parent == d` works on Windows too (`C:\` is its own parent). Do not compare with `Path("/")`.
- Check `stop` AFTER collecting files in that folder: `stop` is inclusive.
- The global file goes first, before the reversed chain, not mixed into it.

<details><summary>💡 Hint 1</summary>

It is a `while True` walk from `cwd` up to the root, collecting files, then a reverse.

</details>

<details><summary>💡 Hint 2</summary>

Collect bottom-up (natural for a walk upwards) and reverse once at the end, instead of inserting at index 0.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
found = []
if home and (home / ".forja" / "AGENTS.md").is_file():
    found.append(...)
chain, d = [], cwd.resolve()
while True:
    # collect INSTRUCTION_FILES present in d
    if ... or d.parent == d:   # reached stop (resolved) or root
        break
    d = d.parent
return found + ...
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l06_context.py -k find_instruction -v
```

### TODO 06.2 · `forja/context.py` · `build_system_prompt(ws, mode, model, home=None, skills_catalog="", extra=None) -> str`

**What it must do:** Returns the full system prompt: non-empty layers joined with a blank line (`"\n\n"`), in this order: `BASE_PROMPT`; `MODE_REMINDERS[mode]`; one block per file from `find_instruction_files(ws.root, home=home)`, each with a `## ... instructions` heading followed by the file content; `skills_catalog` if non-empty; each non-empty string in `extra` (the harness passes the task list here); and finally a `## Environment` block with the working directory (`ws.root`), `git_info(ws.root)`, OS (`platform.system()`), date (`date.today().isoformat()`) and `model`. `test_system_prompt_layers` checks that `You are Forja`, `PLAN mode`, `half-up` (from `playground/AGENTS.md`), `## Skills`, `## Extra`, the model name and `str(project)` are present, and that `PLAN mode` comes before `half-up`, which comes before `## Environment`.

**Steps:**
1. Start a `layers` list with `BASE_PROMPT` and the reminder for `mode` (`MODE_REMINDERS.get(mode, "")` is safe).
2. For each file from `find_instruction_files(ws.root, home=home)`, add `"## <label>\n<content>"`. A useful label: `User global instructions` for the file under `home/.forja`, `Project instructions (<relative path>)` for the others.
3. Append `skills_catalog` if not empty, then each non-empty element of `extra or []`.
4. Append the `## Environment` block (directory, `git_info(ws.root)`, OS, date, model) as one multi-line string.
5. Return `"\n\n".join(...)` over the non-empty layers.

**Watch out for:**
- Read files with `read_text(encoding="utf-8")`. On Windows the default encoding is cp1252 and AGENTS.md files with accents or `—` raise `UnicodeDecodeError` or come out garbled.
- `extra` may be `None` and may contain `""` (the test passes `["## Extra", ""]`, the harness passes `[""]` when there are no todos): filter empty strings so you do not get stray blank sections.
- Call `find_instruction_files` with `ws.root`, not `Path.cwd()`: with `forja --cwd playground` the process cwd is the repo root.
- `f.relative_to(ws.root)` raises `ValueError` for files above the workspace or in home: guard with `f.is_relative_to(ws.root)`.
- The test needs `str(project)` in the prompt: print `ws.root` itself (absolute), not `.`.

<details><summary>💡 Hint 1</summary>

Build a list of strings in order and join it once; do not concatenate with `+=` and forget separators.

</details>

<details><summary>💡 Hint 2</summary>

The harness already gives you everything: `ws.root`, `mode`, `model`, `skills_catalog`, `extra`. You only add the files and the environment.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
layers = [BASE_PROMPT, MODE_REMINDERS.get(mode, "")]
for f in find_instruction_files(ws.root, home=home):
    label = ...   # global vs project (relative path)
    layers.append(f"## {label}\n{...}")
# skills_catalog, extra (non-empty only)
layers.append(f"## Environment\nWorking directory: {ws.root}\n{git_info(ws.root)}\n...")
return "\n\n".join(x for x in layers if x)
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l06_context.py -k system_prompt -v
```

### TODO 06.3 · `forja/context.py` · `expand_mentions(text, ws, max_chars=20_000) -> str`

**What it must do:** Finds `@path` mentions with `MENTION_RE` (it already ignores e-mail addresses like `joe@mail.com`). For each UNIQUE mention that resolves inside the workspace to an existing FILE: read it (at most `max_chars` characters), call `ws.mark_read(p)`, and append a block `<file path="<relative path>">\n<content>\n</file>` at the END of the original text (the text itself is not modified). Mentions outside the sandbox (`@../../etc/passwd` -> `PermissionError`), missing files (`@nobody`) and folders are skipped silently. With no valid mention, return `text` unchanged (`expand_mentions("no mentions", ws) == "no mentions"`). `test_expand_mentions` expects exactly one `<file` block with `path="invoices/dates.py"`, the file content (`def due_date`) and the path in `ws.read_state`.

**Steps:**
1. Get the mentions with `MENTION_RE.findall(text)` and de-duplicate keeping order (`dict.fromkeys(...)`).
2. Strip trailing punctuation from each mention: the regex stops at `,` but it allows `.`, so `look at @src/app.py.` captures `src/app.py.`. Use `ref.rstrip(".,;:")`.
3. Resolve with `ws.resolve(ref)` inside `try/except PermissionError: continue`; skip if `not p.is_file()`.
4. Read with `read_text(encoding="utf-8", errors="replace")`, cut to `max_chars` (add a `…[truncated]` marker), `ws.mark_read(p)`, and build the `<file path=...>` block.
5. If you have blocks, return `text + "\n\n" + "\n\n".join(blocks)`; otherwise return `text`.

**Watch out for:**
- A mention at the end of a sentence (`look at @src/app.py.`) captures the final dot: strip trailing `.,;:` or the file is not found.
- Use `ws.rel(p)` for the `path` attribute: it already returns a POSIX path (`invoices/dates.py`) on Windows too, which is what the test looks for.
- Call `ws.mark_read(p)` for every included file: the test checks `ws.read_state`, and in the CLI it lets the model `edit_file` right away without a `read_file` round-trip.
- Do not replace the mention inside the text: keep the user's sentence intact and append blocks after it.
- Do not let one bad mention abort the others: `continue`, never `return` inside the loop.

<details><summary>💡 Hint 1</summary>

Loop over mentions, filter the valid ones, build a list of blocks, append them at the end.

</details>

<details><summary>💡 Hint 2</summary>

The sandbox is already done (lab 02): `ws.resolve` raising `PermissionError` is your filter for `../` paths.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
blocks = []
for ref in dict.fromkeys(MENTION_RE.findall(text)):
    try:
        p = ws.resolve(ref.rstrip(".,;:"))
    except PermissionError:
        continue
    # skip non-files; read (cap max_chars); ws.mark_read(p)
    blocks.append(f'<file path="{...}">\n{...}\n</file>')
return ...  # text unchanged if no blocks
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l06_context.py -k mentions -v
```

## Run
```bash
python scripts/tasks.py test 06
forja --cwd playground
> review @invoices/amounts.py and tell me whether it follows AGENTS.md
```

## Try it in your agent
1. Reset first: `python scripts/tasks.py reset`. Start `forja --cwd playground`. The dim note `context: lab 06 pending ...` should NO LONGER appear.
2. Ask: `review @invoices/amounts.py and tell me whether it follows AGENTS.md`. Expected: NO `⏺ Read invoices/amounts.py` line (the file came with the message) and an answer that quotes the rules: half-up rounding with `decimal`, not `round()` on floats, don't change tests.
3. Ask without mentioning the rules: `what are the rules of this project?`. The agent answers from `AGENTS.md` without calling any tool.
4. Type `/context` before and after a message with a big `@` mention: the token count grows by roughly the file size / 4.
5. Optional: create `~/.forja/AGENTS.md` (Windows: `%USERPROFILE%\.forja\AGENTS.md`) with `Always answer in Spanish.`; restart Forja and say hello. The answer language changes: the global layer works.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_find_instruction_files_order` returns `['global', 'package', 'root']` | You did not reverse the walk (or reversed the global file too) → collect bottom-up, reverse only the chain, then prepend the global file. |
| `test_find_instruction_files_order` finds extra files or never stops (macOS) | Comparing resolved `cwd` with unresolved `stop` (`/var` vs `/private/var`) → resolve `stop` too. |
| `test_system_prompt_layers` fails on `half-up` in sp | The playground AGENTS.md was not included → call `find_instruction_files(ws.root, home=home)` and append the file CONTENT, not just its path. |
| `UnicodeDecodeError: 'charmap' codec can't decode` (Windows) | `read_text()` without encoding → `read_text(encoding="utf-8")` (and `errors="replace"` for mentioned files). |
| `test_expand_mentions`: `out.count("<file") == 2` or a crash on `@../../etc/passwd` | Missing `except PermissionError` or missing `is_file()` check → skip invalid mentions with `continue`. |
| In the CLI the agent still ignores AGENTS.md | You ran Forja from another folder, or the AGENTS.md is not under `--cwd` → start with `forja --cwd playground`; small models may also need the rule repeated in the prompt (less is more: keep AGENTS.md short). |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 06` → 3 passed.
- [ ] [ ] In the CLI the agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told.
- [ ] [ ] An `@file` mention is answered without an extra `⏺ Read` line.

## Checkpoint
The agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told.

## Challenges
1. Write your `~/.forja/AGENTS.md` with your preferences (language, style).
2. Add the Python version and last 3 commits to the environment.

**Tests:** `tests/test_l06_context.py` · **Fallen behind?** `python scripts/tasks.py catchup 07`

---
[← previous](../L05_cli/README.md) · [next →](../L07_compaction/README.md)
