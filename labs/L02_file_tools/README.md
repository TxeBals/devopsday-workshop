# Lab 02 · File tools

Day 1 · 10:15–11:15

**Goal:** Give the agent eyes and hands on the project: read, search, create and edit files safely.

## Concepts
- **The schema is the prompt:** name, docstring and type hints generate the JSON Schema the model reads. A good description beats any system-prompt instruction.
- **Tools never raise:** every error goes back to the model as actionable text (“appears 3 times: add context”) so it can self-correct.
- **edit_file = exact replacement of a unique string.** The most robust format for small models (they produce bad diffs). Typical model mistakes: including `read_file` line numbers or changing indentation.
- **Read before edit** and detect external changes (mtime): the agent doesn't overwrite what it hasn't seen or what you just changed.
- **Sandbox:** every path resolves inside the workspace. `../` and outside absolute paths are rejected.
- **Explore without loading the repo:** `grep` and `glob` return paths and lines; the agent reads only what's relevant.

## What you implement
| TODO | File | What |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: OpenAI-format JSON Schema |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: run without ever raising |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: path sandbox |
| 02.4 | `forja/fs_tools.py` | write_file: create / overwrite with read-first |
| 02.5 | `forja/fs_tools.py` | edit_file: exact, unique replacement with useful errors |
| 02.6 | `forja/fs_tools.py` | grep: regex search across the workspace |

## Before you start
- Open `forja/tools.py` (TODOs 02.1–02.2), `forja/fs_tools.py` (02.3–02.6) and `tests/test_l02_tools.py`. Read the provided parts first: the `@tool` decorator builds a pydantic model from type hints + docstring (`Tool.args_model`), `ToolRegistry.parse_args(call)` validates JSON arguments, and `read_file` / `glob` are complete examples of tools.
- Stdlib/APIs you will use: pydantic `Model.model_json_schema()`; `json.dumps`; `time.perf_counter()`; `pathlib.Path.resolve()`, `.is_absolute()`, `.is_relative_to()`; `str.count`, `str.replace(old, new, 1)`; `re.compile`, `fnmatch.fnmatch`.
- Provided `Workspace` helpers you must use: `ws.resolve(path)` (your 02.3), `ws.rel(p)` (relative string), `ws.mark_read(p)` (remember mtime), `ws.check_fresh(p)` (raises `PermissionError` if not read or changed on disk), `ws.walk(base)` (files, skipping `.git`, `.venv`, `__pycache__`…), `ws.before_write` (callbacks, used by checkpoints in lab 11) and `unified_diff(before, after, path)`.
- Key idea: tools **raise** normal Python exceptions with helpful messages; `ToolRegistry.execute` (02.2) catches everything and returns the message to the model as `ToolResult(ok=False, …)`. So the test assertions like `"before modifying" in res.output` check YOUR error text passed through `execute`.
- How it connects: `schemas()` is what the model sees as `tools=[…]`; `execute` is called by the harness gate for every call the model makes.

## Step by step
02.1 → 02.2 → 02.3 first: every file-tool test goes through `registry.execute` and `ws.resolve`, so nothing else can pass before them. Then 02.4 (`write_file`), 02.5 (`edit_file`, the biggest one) and 02.6 (`grep`). Keep `read_file` open as your model of how a tool is written.

### TODO 02.1 · `forja/tools.py` · `Tool.schema()`

**What it must do:** Returns `{"type": "function", "function": {"name": self.name, "description": self.description, "parameters": params}}` where `params` is the pydantic JSON Schema of `self.args_model` with: no `"title"` at the root, no `"title"` inside any property, `"additionalProperties": False`, and a `"properties"` key even for tools without arguments. `test_schema_from_type_hints` checks name, description `"Does something."`, `required == ["path"]`, `n` default `3`, `path` description `"Path."`.

**Steps:**
1. Get the schema dict from `self.args_model.model_json_schema()`.
2. Remove the root `title` (use `pop` with a default so it never fails).
3. Loop over the values of `params["properties"]` (may be missing) and remove each `title`.
4. Make sure `properties` exists and set `additionalProperties` to `False`.
5. Wrap it in the OpenAI function format and return.

**Watch out for:**
- pydantic adds titles like `"Path"`, `"N"` to each property: small models get confused by them, and the test asserts there is no root title.
- A tool with no parameters has no `properties` key: some backends reject a schema without it.
- Descriptions and `required` are already produced by pydantic from the `@tool` decorator: don't rebuild them by hand.

<details><summary>💡 Hint 1</summary>

Print it first: `python -c "from forja.fs_tools import *; from pathlib import Path; print(make_fs_tools(Workspace(Path('.')))[0].args_model.model_json_schema())"`.

</details>

<details><summary>💡 Hint 2</summary>

`dict.pop("title", None)` and `dict.setdefault("properties", {})` do most of the work.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
params = self.args_model.model_json_schema()
# drop root title
for prop in params.get("properties", {}).values():
    ...
# ensure properties, additionalProperties
return {"type": "function", "function": {...}}
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k schema -v
```

### TODO 02.2 · `forja/tools.py` · `ToolRegistry.execute(call)`

**What it must do:** `execute(call: ToolCall) -> ToolResult` and it **never raises**. Uses `self.parse_args(call)` → `(tool, args, err)`; if `err`, return `ToolResult(call.id, call.name, False, err)`. Otherwise call `tool.fn(**args)`; any `Exception` becomes `ok=False` with output `"ERROR in '<tool>': <ExceptionType>: <message>"`. Success: a `ToolOutput` gives `.text` and `.meta`; a `str` is used as is; anything else is `json.dumps(..., ensure_ascii=False, default=str)`. Output always goes through `_truncate`; `duration_ms` is measured.

**Steps:**
1. Take `t0 = time.perf_counter()` at the start.
2. Call `self.parse_args(call)`; on error return a failed `ToolResult` with that message.
3. In a `try`, call the tool function with the validated args; on `Exception` return a failed result with type name and message.
4. Convert the return value to `(text, meta)` according to its type.
5. Return `ToolResult(call.id, call.name, ok, _truncate(text), meta, duration_ms)`.

**Watch out for:**
- When the tool doesn't exist, `parse_args` returns `t = None`: use `call.name`, not `t.name`, in the result (`test_execute_never_raises` calls a tool named `nope`).
- Include the exception MESSAGE in the output: later tests look for `"outside the workspace"`, `"before modifying"`, `"times"`, `"line numbers"`, `"has changed"` in `res.output`.
- Catch `Exception`, not bare `except:` (you don't want to swallow Ctrl+C / `KeyboardInterrupt`).
- A small helper closure `done(ok, out, meta=None)` avoids repeating the `ToolResult(...)` construction.

<details><summary>💡 Hint 1</summary>

The ordered field list of `ToolResult` is `call_id, name, ok, output, meta, duration_ms`.

</details>

<details><summary>💡 Hint 2</summary>

`isinstance(res, ToolOutput)` / `isinstance(res, str)`; the message format is `f"ERROR in '{t.name}': {type(e).__name__}: {e}"`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
t0 = time.perf_counter()
t, args, err = self.parse_args(call)
if err:
    return ...
try:
    res = t.fn(**args)
except Exception as e:
    return ...
# ToolOutput? str? other -> json
return ToolResult(..., _truncate(text), meta, int((time.perf_counter() - t0) * 1000))
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k execute_never_raises -v
```

### TODO 02.3 · `forja/fs_tools.py` · `Workspace.resolve(path)`

**What it must do:** `resolve(path: str) -> Path`: a relative path is joined to `self.root`, an absolute one is kept; the result is `.resolve()`d (removes `..`, follows symlinks). If it is neither `self.root` nor inside it, raise `PermissionError(f"path outside the workspace: {path}")`. Returns the absolute resolved `Path`. `self.root` is already resolved in `__post_init__`.

**Steps:**
1. Wrap the string in a `Path`.
2. Build the candidate: the path itself if absolute, otherwise `self.root / path`.
3. Call `.resolve()` on the candidate.
4. If it equals `self.root` or `is_relative_to(self.root)`, return it; otherwise raise the `PermissionError`.

**Watch out for:**
- Check AFTER resolving: `"invoices/../../secret.txt"` looks relative but escapes.
- Don't compare strings with `startswith`: `/home/me/proj2` starts with `/home/me/proj`. `Path.is_relative_to` compares path components.
- `test_sandbox` checks both `"../secret.txt"` and `"/etc/passwd"` and that the message contains `"outside the workspace"` (on Windows `/etc/passwd` becomes `C:\etc\passwd`: still outside).

<details><summary>💡 Hint 1</summary>

Three lines of logic: build, resolve, check.

</details>

<details><summary>💡 Hint 2</summary>

`Path.is_absolute()`, `Path.resolve()`, `Path.is_relative_to(other)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
p = Path(path)
target = (...).resolve()
if target != self.root and not ...:
    raise PermissionError(...)
return target
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k "sandbox or read_numbered" -v
```

### TODO 02.4 · `forja/fs_tools.py` · `make_fs_tools` → inner `write_file(path, content)`

**What it must do:** Returns `ToolOutput(text, {"path": ws.rel(p), "diff": unified_diff(before, content, ws.rel(p))})`. New file: creates parent folders and writes. Existing file: `ws.check_fresh(p)` first (raises `"read … with read_file before modifying it"`), keep the old content as `before`. Call every callback in `ws.before_write` with `p` before writing. After writing, `ws.mark_read(p)`. Text like `"docs/note.md created (1 lines)"` / `"… updated (N lines)"`. Write UTF-8.

**Steps:**
1. `p = ws.resolve(path)`; `before = ""`.
2. If `p` exists: `ws.check_fresh(p)` and read the old text into `before`.
3. Call each `cb(p)` in `ws.before_write`.
4. Create `p.parent` (parents, exist_ok) and write `content` with `encoding="utf-8"`.
5. `ws.mark_read(p)` and return the `ToolOutput` with path and diff.

**Watch out for:**
- `test_write_new_and_overwrite_rules` writes to `docs/note.md` — the `docs` folder doesn't exist yet.
- Overwriting a file that was never read must fail with `"before modifying"` in the output: let `check_fresh` raise, don't catch it.
- Without `mark_read` after writing, the next `edit_file` on the same file fails with `"has changed since you read it"` (your own write changed the mtime).
- Always pass `encoding="utf-8"`: on Windows the default encoding is not UTF-8.

<details><summary>💡 Hint 1</summary>

Mirror the structure of the provided `read_file`: resolve first, then work with `p`.

</details>

<details><summary>💡 Hint 2</summary>

`p.parent.mkdir(parents=True, exist_ok=True)`, `p.write_text(content, encoding="utf-8")`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
p = ws.resolve(path)
before = ""
if p.exists():
    ...  # fresh check + old content
for cb in ws.before_write:
    ...
...  # mkdir, write, mark_read
return ToolOutput(f"...", {"path": ..., "diff": ...})
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k write_new -v
```

### TODO 02.5 · `forja/fs_tools.py` · `make_fs_tools` → inner `edit_file(path, old_string, new_string, replace_all=False)`

**What it must do:** Returns `ToolOutput("<rel> edited (N replacement(s), from line L)", {"path": ws.rel(p), "diff": …})`. Raises (in this order): `FileNotFoundError` if it isn't a file (suggest `write_file`); `check_fresh` errors; `ValueError` if `old_string == new_string`; `ValueError` `"old_string not found in <path>."` + a hint when the count is 0; `ValueError` `"old_string appears N times in <path>: …"` when the count is >1 and not `replace_all`. Replaces one occurrence (or all), calls `ws.before_write` callbacks, writes, `mark_read`.

**Steps:**
1. Resolve the path; if it is not a file, raise `FileNotFoundError` mentioning `write_file`.
2. `ws.check_fresh(p)`; reject identical old/new strings.
3. Read the text and count `old_string` occurrences.
4. Count 0: build a hint — if `old_string` has lines starting with digits + `→` (regex `r"^\s*\d+→"` with `re.M`), say it contains read_file **line numbers**; else if its stripped version exists in the text, say whitespace/indentation differ. Raise `ValueError`.
5. Count >1 without `replace_all`: raise `ValueError` saying it appears N times and how to fix it.
6. Replace (once with `str.replace(old, new, 1)` or all), call `before_write` callbacks, write UTF-8, `mark_read`.
7. Compute the line of the first match (`text[:text.index(old_string)].count("\n") + 1`) and return the `ToolOutput` with the diff.

**Watch out for:**
- Order matters: `test_edit_requires_read_and_unique` first edits an UNREAD file and expects `"before modifying"` — `check_fresh` must run before counting.
- The duplicate test uses `old_string="return"` and checks `"times"` in the output.
- The line-number test passes `"     9→    return round(value, 2)"` and checks `"line numbers"` in the output: the `→` is the character `read_file` prints.
- `test_edit_detects_external_change` touches the file after reading: just calling `check_fresh` gives `"has changed"`.
- The diff must contain the new line exactly once → replace only the first occurrence by default.

<details><summary>💡 Hint 1</summary>

These error messages are prompts for the model: say what went wrong AND what to do next.

</details>

<details><summary>💡 Hint 2</summary>

`text.count(old_string)`, `text.replace(old, new, 1)`, `re.search(pattern, old_string, re.M)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
p = ws.resolve(path)
if not p.is_file(): raise FileNotFoundError(...)
ws.check_fresh(p)
if old_string == new_string: raise ValueError(...)
text = ...
n = text.count(old_string)
if n == 0: ...   # hint: line numbers? whitespace?
if n > 1 and not replace_all: ...
new_text = ...
# before_write, write, mark_read, line, return ToolOutput
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k "edit_requires or external_change" -v
```

### TODO 02.6 · `forja/fs_tools.py` · `make_fs_tools` → inner `grep(pattern, path=".", include=None, ignore_case=False, show_content=True)`

**What it must do:** Returns a `str`. With `show_content=True`: one line per match, `"<rel>:<lineno>: <line stripped, max 300 chars>"`. With `show_content=False`: one line per matching file (its relative path). `include` filters by file NAME with `fnmatch` (e.g. `*.py`). Searches a single file if `path` is a file, otherwise `ws.walk(base)`. Skips files that are not UTF-8. Stops at 300 results with a note. Nothing found: `"(no matches)"`.

**Steps:**
1. Compile the regex with `re.I` when `ignore_case`.
2. Resolve `path`; the file list is `[base]` if it is a file, else `ws.walk(base)`.
3. For each file: skip it if `include` is given and the name doesn't match.
4. Read it as UTF-8 inside `try/except (UnicodeDecodeError, OSError)` and skip on error.
5. Enumerate lines from 1; on `rx.search(line)`: append the formatted line, or (paths-only mode) append the path once and stop reading that file.
6. Stop with a note when you reach 300 results; return the joined lines or `"(no matches)"`.

**Watch out for:**
- Line numbers start at 1: `test_grep_and_glob` expects `"invoices/amounts.py:7:"` for `def round_amount`.
- Use `ws.rel(f)` for the path, not the absolute path.
- `include` is matched against `f.name`, not the full path.
- In paths-only mode each file must appear once even if many lines match.
- An invalid regex raises `re.error`; that's fine — `execute` turns it into an error message for the model.

<details><summary>💡 Hint 1</summary>

Look at the provided `glob` tool right above: same walk, different filter.

</details>

<details><summary>💡 Hint 2</summary>

`enumerate(text.splitlines(), 1)`, `fnmatch.fnmatch(f.name, include)`, `rx.search(line)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
rx = re.compile(pattern, re.I if ignore_case else 0)
base = ws.resolve(path)
files = [base] if base.is_file() else ws.walk(base)
out = []
for f in files:
    ...  # include filter, read (skip binaries), match lines
    if len(out) >= 300: ...
return "\n".join(out) or "(no matches)"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l02_tools.py -k grep -v
```

## Run
```bash
python scripts/tasks.py test 02
forja --cwd playground
> what does the due_date function do?        (no loop yet: it answers as a chat; tools arrive in lab 03)
```

## Try it in your agent
1. `python scripts/tasks.py test 02` → `8 passed`.
2. Drive the tools by hand from a Python REPL at the repo root (`python`, then type):
```python
import json; from pathlib import Path
from forja.fs_tools import Workspace, make_fs_tools
from forja.tools import ToolRegistry; from forja.types import ToolCall
r = ToolRegistry().register(*make_fs_tools(Workspace(Path("playground"))))
x = lambda name, **a: print(r.execute(ToolCall("1", name, json.dumps(a))).output)
x("grep", pattern="def ", include="*.py")
```
You should SEE lines like `invoices/amounts.py:7: def round_amount(value: float) -> float:`.
3. In the same REPL: `x("read_file", path="../README.md")` → `ERROR in 'read_file': PermissionError: path outside the workspace: ../README.md`; `x("edit_file", path="invoices/dates.py", old_string="a", new_string="b")` → `… read invoices/dates.py with read_file before modifying it`.
4. See what the model will read: `print(json.dumps(r.schemas()[2], indent=2))` → the `edit_file` schema, with its long description, `required` and `"additionalProperties": false`, and no `title` keys.
5. `forja --cwd playground`: the note `tools: lab 02 pending` is gone. It is still a chat (`agent: lab 03 pending — chat mode without tools`), so the model cannot call your tools yet — that's lab 03.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| Every file-tool test fails with `NotImplementedError: TODO 02.2` or `TODO 02.3` | All tests go through `registry.execute` and `ws.resolve` → finish 02.2 and 02.3 first. |
| `AttributeError: 'NoneType' object has no attribute 'name'` in `execute` | Unknown tool → `t` is `None` → use `call.name` when building the error result. |
| Test expects `"before modifying"` but output says `"old_string not found"` | You count occurrences before `ws.check_fresh(p)` → move the freshness check up. |
| `edit_file` works once, then the next edit says `has changed since you read it` | Missing `ws.mark_read(p)` after writing → call it at the end of write_file and edit_file. |
| `AssertionError: 'line numbers' in …` in the edit test | Your hint regex doesn't match `"     9→    return …"` → use `^\s*\d+→` with `re.M`, and copy the `→` character from `read_file`'s code. |
| `UnicodeDecodeError` / mojibake when writing on Windows | Missing `encoding="utf-8"` in `write_text`/`read_text` → always pass it. |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 02` → all 8 tests green.
- [ ] [ ] From the REPL you get a numbered `read_file`, a `grep` with `path:line:` hits and a sandbox error for `../`.
- [ ] [ ] Your `edit_file` error messages tell the model how to fix its call.

## Checkpoint
Lab 02 tests green. With lab 03 still pending, Forja is still a chat: the loop comes next.

## Challenges
1. Add a `list_dir` tool with a 2-level tree. Does it help or hurt the model's exploration?
2. Ask the model to edit something and watch its `old_string` mistakes: which hint would you add to the error message?

**Tests:** `tests/test_l02_tools.py` · **Fallen behind?** `python scripts/tasks.py catchup 03`

---
[← previous](../L01_llm_streaming/README.md) · [next →](../L03_loop/README.md)
