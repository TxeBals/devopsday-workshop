# Lab 03 · The agent loop

Day 1 · 11:30–12:15

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

## Before you start
- Open `forja/agent.py` (`Events`, `AgentResult`, `Agent` and your two TODOs), `forja/fake_llm.py` (`FakeLLM`, `say`, `call`, `calls`: the scripted model the tests use) and `tests/test_l03_agent.py`.
- Message protocol (Chat Completions): an assistant message with `tool_calls` must be followed by one `{"role": "tool", "tool_call_id": …}` message per call, before the next assistant message. `ChatResponse.to_message()` and `ToolResult.to_message()` (provided) build those dicts for you.
- `self.llm.stream(messages, tools=...)` yields `TextDelta` and a final `Done` (your lab 01, or `FakeLLM` in tests, which yields text in 8-character pieces). `self.tools.schemas()` (lab 02) is the `tools` list.
- Stdlib: `concurrent.futures.ThreadPoolExecutor` (`ex.map(fn, iterable)`), `collections.Counter`, `threading.Event.is_set()`.
- How it connects: the harness creates `Agent(llm, registry, execute=self.gate, events=RichEvents(), …)`. The loop never knows about permissions or UI — it only calls `execute` and `events`. The same class is reused for subagents (lab 09) and evals (lab 12).

## Step by step
Start with the no-tools path of 03.2 (stream, append the assistant message, return `"final"`, plus the cancel check): that makes `test_final_answer`, `test_streaming_events` and `test_cancel` green. Then write 03.1 `_run_calls`, then complete 03.2 with tool execution, `max_steps` and loop detection. All 03.1 tests run through `run`, so you need both.

### TODO 03.1 · `forja/agent.py` · `Agent._run_calls(calls)`

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

### TODO 03.2 · `forja/agent.py` · `Agent.run(messages)`

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

## Run
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explain how an invoice total is calculated
```

## Try it in your agent
1. `python scripts/tasks.py test 03` → `6 passed`.
2. `forja --cwd playground` and ask `explain how an invoice total is calculated`. You should SEE blue lines per tool call, e.g. `⏺ grep {"pattern": "def total", …}` followed by dim `⎿ invoices/invoice.py:…` (raw JSON args until lab 05 makes them pretty), then a streamed answer with `path:line` references and `(N steps · M tools)`.
3. Ask `read amounts.py and dates.py and summarise both`: if the model requests both reads in one response, they run in parallel (both `⏺` lines appear before the results).
4. Ask it to change something, e.g. `add a docstring to total_with_vat`. Until lab 04/05 you get a crude prompt `Allow edit_file {…}? [y/N]` — answer `n` and see the model react to `DENIED by the user`.
5. Press Ctrl+C while it works: `interrupting…`, then the turn stops at the next step with `(interrupted by the user)`.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_parallel_reads_keep_order` fails on time (≈0.6 s or more) | Reads are running sequentially → check `_is_read` grouping and that you use the pool for blocks > 1. |
| `test_parallel_reads_keep_order` fails on order (`['r2', 'r1', …]`) | Results appended as threads finish → write into `results[i]`. |
| `AssertionError: assert not open_ids` in `test_max_steps_and_loop` | On `"loop"` you returned without answering the pending tool_calls → append a failed tool message for each. |
| Real backend: `400 … tool_call_id … not found` / `messages with role 'tool' must be a response…` | History broken: assistant message built by hand, or tool messages missing/out of order → use the `to_message()` helpers and keep the order. |
| The CLI calls tools but `bash` answers `ERROR in 'bash': NotImplementedError: TODO 04.2` | Expected: the bash tool is lab 04. The model will usually retry with read tools. |
| The model answers without calling any tool, or writes `<tool_call>{…}` as text | Small model or tools not sent → check `tools=self.tools.schemas() or None`; try `forja doctor`; `qwen3:8b` sometimes needs an explicit prompt like `use grep to find…`. |
| The agent repeats the same `read_file` again and again | That's what loop detection is for → it should stop with `I stopped: I repeated read_file…` after `max_repeats` (3). |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 03` → all 6 tests green.
- [ ] [ ] In `forja --cwd playground` the agent explores with glob/grep/read_file and answers with `path:line` references.
- [ ] [ ] You can explain why every `tool_call` needs a `tool` message, even when the loop stops.

## Checkpoint
Forja explores the playground (glob, grep, read_file) and answers with `path:line` references. Edits still ask permission crudely: that's lab 04.

## Challenges
1. Make the agent warn the user after 15 steps.
2. What happens when the model requests 10 reads at once on a slow model? Measure.

**Tests:** `tests/test_l03_agent.py` · **Fallen behind?** `python scripts/tasks.py catchup 04`

---
[← previous](../L02_file_tools/README.md) · [next →](../L04_bash_permissions/README.md)
