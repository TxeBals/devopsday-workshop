# Lab 01 · Streaming LLM client

Day 1 · 09:30–10:15

**Goal:** Talk to any OpenAI-compatible backend in streaming mode and rebuild tool calls that arrive in pieces.

## Concepts
- **One protocol, many backends:** Ollama, vLLM, LM Studio, llama.cpp and OpenRouter all speak Chat Completions. The `openai` SDK is just an HTTP client; the model is open.
- **Streaming:** text arrives token by token (the CLI feels alive). **Tool calls arrive in pieces too**: `index`, then `id` and `name`, then the argument JSON in fragments, sometimes interleaved across calls.
- **Local-model quirks:** `<think>…</think>` blocks that may be split across chunks; tool calls written as text `<tool_call>{…}</tool_call>`.
- **Retries:** only transient errors (connection, 429, 5xx) with exponential backoff. A 400 isn't fixed by retrying.

## What you implement
| TODO | File | What |
|---|---|---|
| 01.1 | `forja/llm.py` | ToolCallAccumulator: concatenate fragments by index |
| 01.2 | `forja/llm.py` | ThinkFilter: strip <think> even when the tag is split |
| 01.3 | `forja/llm.py` | LLMClient.stream: retries, TextDelta and Done events |

## Before you start
- Open `forja/llm.py` (your three TODOs), `forja/types.py` (`ToolCall`, `ChatResponse`, `TextDelta`, `Done` — provided) and `tests/test_l01_llm.py`.
- The `openai` SDK is only an HTTP client here. With `stream=True`, `client.chat.completions.create(**params)` returns an iterator of *chunks*. Each chunk has `.model`, `.usage` (usually only on the LAST chunk, which has `choices == []`) and `.choices[0].delta` with `.content` (a text piece or `None`) and `.tool_calls` (a list of fragments or `None`). `.choices[0].finish_reason` is set on the last content chunk.
- A tool-call fragment has `.index` (which call), `.id` and `.function.name` (usually only in the first fragment) and `.function.arguments` (a *piece* of a JSON string). The test fakes them with class `D`.
- How it connects: `LLMClient.stream()` is the generator the agent loop (lab 03) consumes. It yields `TextDelta(text)` for the UI while streaming and ends with ONE `Done(ChatResponse(...))` with everything assembled. `chat()` (provided) just returns the `Done` response.
- Provided helpers you will reuse: `self._params(messages, tools, **kw)` (builds the request body, including `stream`, `stream_options`, `tools`, `tool_choice` and `extra_body`), `RETRYABLE` (the transient exception classes) and `rescue_text_tool_calls(text)`.

## Step by step
Do 01.1 (accumulator) first: it is small, pure and tested in isolation. Then 01.2 (think filter), also pure but trickier — draw the buffer states on paper. Finish with 01.3, which wires both into the real stream; its tests use an `httpx.MockTransport`, so you still need no model. Run each TODO's test command before moving on.

### TODO 01.1 · `forja/llm.py` · `ToolCallAccumulator.add(deltas)` / `ToolCallAccumulator.finish()`

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

### TODO 01.2 · `forja/llm.py` · `ThinkFilter.feed(text)` (`flush()` is provided)

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

### TODO 01.3 · `forja/llm.py` · `LLMClient.stream(messages, tools=None, **kw)`

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

## Run
```bash
python scripts/tasks.py test 01
forja doctor                      # does the model call tools?
forja                             # already a streaming chat (no tools yet)
```

## Try it in your agent
1. `python scripts/tasks.py test 01` → `14 passed`.
2. `forja --cwd playground` and ask `explain in 3 lines what an invoice due date is`. You should SEE the answer appear progressively (token by token) and then a dim `(1 steps · 0 tools)`. No `<think>` text should be printed.
3. Before the prompt you will see dim notes such as `· tools: lab 02 pending — running without this capability` and `· agent: lab 03 pending — chat mode without tools`: expected, it is a plain chat for now.
4. Check the retries: point to a dead port and watch it wait 1+2+4 s before failing.
  - PowerShell: `$env:OLLAMA_BASE_URL="http://localhost:9999/v1"; forja --cwd playground` (then `Remove-Item Env:OLLAMA_BASE_URL`)
  - macOS/Linux: `OLLAMA_BASE_URL=http://localhost:9999/v1 forja --cwd playground`
  - Type `hi` → after ~7 s, red `APIConnectionError: Connection error.`
5. `forja doctor` still prints `✔ the model calls tools` (it doesn't use your client, so it is your baseline when something looks wrong).

## If something goes wrong
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

## You're done when
- [ ] [ ] `python scripts/tasks.py test 01` → all 14 tests green.
- [ ] [ ] `forja --cwd playground` answers in streaming without `<think>` text.
- [ ] [ ] You can explain why a 400 is not retried and a 503 is.

## Checkpoint
`forja doctor` shows ✔ and `forja` answers in streaming. “lab NN pending” notes are expected.

## Challenges
1. Measure local time-to-first-token against OpenRouter.
2. What if the model emits two tool calls with the same `index`? Can it happen?

**Tests:** `tests/test_l01_llm.py` · **Fallen behind?** `python scripts/tasks.py catchup 02`

---
[← previous](../L00_setup/README.md) · [next →](../L02_file_tools/README.md)
