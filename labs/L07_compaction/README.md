# Lab 07 · Context management and compaction

Day 2 · 09:40–10:25

**Goal:** Make a long session fit a local model's window without breaking history.

## Concepts
- **The budget:** local models work with 16–32k effective tokens. A verbose `pytest` or a large file eats the window.
- **Level 1 — microcompaction (free):** blank old tool outputs. The model already used them; it can re-read if needed.
- **Level 2 — compaction (1 call):** summarise old turns (goal, files, commands, decisions, pending) and keep recent ones.
- **Invariant:** cut only before a `user` message. Never between `tool_calls` and their `tool` results.
- **It's lossy:** measure it with evals (lab 12) using a small window.

## What you implement
| TODO | File | What |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: blank old outputs |
| 07.2 | `forja/compaction.py` | compact: summary + recent turns, pairs intact |

## Before you start
- Open `forja/compaction.py`. Provided: `SUMMARY_PROMPT`, `CLEARED = "[old tool result cleared]"`, `estimate_tokens(messages)` (~4 chars per token), `user_turn_starts(history)` (indices of the `user` messages) and `should_compact(...)` (true above 80% of the window). You write `microcompact` and `compact`.
- Know the history format (OpenAI chat): `{"role": "user", "content": ...}`, `{"role": "assistant", "content": ..., "tool_calls": [{"id", "type", "function": {"name", "arguments"}}]}`, `{"role": "tool", "tool_call_id": ..., "name": ..., "content": ...}`. An assistant message with `tool_calls` MUST be followed by one `tool` message per call: breaking that pair makes the API reject the request.
- A "turn" starts at a `user` message. Cutting only at `user_turn_starts(...)` indices is what guarantees you never separate a `tool_calls` message from its results.
- How it connects: `Forja.compact_now()` in `forja/harness.py` runs before every turn: if `should_compact` → `microcompact(self.history)` (free); if still too big → `compact(self.history, self.llm)` (one LLM call). `/compact` calls `compact_now(force=True)`. The LLM call is `llm.chat(messages, temperature=0)` and returns a `ChatResponse` whose `.content` is the text (in tests, `FakeLLM` records it in `llm.calls`).

## Step by step
07.1 first: it is a pure in-place loop, no LLM, and it teaches you the cut point (`starts[-keep_recent_turns]`) that 07.2 reuses. Then 07.2. `test_harness_autocompacts` (run with 07.2) exercises both through the harness with a tiny window, so it only passes when both are right.

### TODO 07.1 · `forja/compaction.py` · `microcompact(history, keep_recent_turns=2, min_chars=500) -> int`

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

### TODO 07.2 · `forja/compaction.py` · `compact(history, llm, keep_recent_turns=2) -> tuple[list, bool]`

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

## Run
```bash
python scripts/tasks.py test 07
forja --cwd playground
> read every file in the project and summarise them
/context
/compact
/context
```

## Try it in your agent
1. `python scripts/tasks.py reset`, then `forja --cwd playground`. Ask: `read every file in the project and summarise them` (approve with `y` if asked; reads should not ask).
2. Type `/context`: something like `~6000 tokens of 32768 (N messages)`. Ask two more short questions (e.g. `which function computes VAT?`, `where is the due date logic?`) so you have at least 3 turns: compaction always keeps the last 2.
3. Type `/compact`. Expected: `compacted: summary + recent turns (~N tokens)`. If you only had 1–2 turns you get `nothing to compact` (or `microcompaction: N old outputs cleared`): that is correct behaviour.
4. Type `/context` again: the number drops clearly. Ask `what were we doing?`: the agent still knows the files and the goal (it reads them from the summary).
5. Optional: create `playground/.forja/settings.json` with `{"contextWindow": 6000}`, restart and work for a few turns: a dim note `· microcompaction: ...` or `· compacted: ...` appears automatically before a turn. Delete the file afterwards.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_microcompact`: `assert 4 == 2` (everything cleared) | You loop over the whole history → only `history[:starts[-keep_recent_turns]]`. |
| `test_microcompact`: second call returns 2 instead of 0, or the count is right but contents unchanged | Not checking `!= CLEARED`, or modifying a copy (`dict(m)`) → mutate the original dicts and skip already-cleared ones. |
| `test_compact_keeps_pairs_and_recent`: `question 3` found in the prompt | You summarise the whole history → only `old = history[:cut]`. |
| `test_compact_keeps_pairs_and_recent`: `KeyError: 'tool_calls'` or `TypeError: can only concatenate str (not "NoneType")` | Use `m.get("tool_calls", [])` and `m.get("content") or ""`. |
| `test_harness_autocompacts`: `assert any("compact" in n for n in app.notes)` fails | `compact` returns `(history, False)` too often, or 07.1 raises → check both functions with the 07.1 test first; the harness only adds the note when something was compacted. |
| Real model: after `/compact` the agent forgets which files it changed | Compaction is lossy → make sure your transcript text includes tool names and arguments (paths!), not just contents; measure it later with evals (lab 12). |
| Real model: `/compact` takes a long time | It is one full LLM call over up to 60k characters → normal on a laptop; a smaller cap on the transcript makes it faster. |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 07` → 3 passed.
- [ ] [ ] `/context` drops after `/compact` and the agent still knows what it was doing.

## Checkpoint
`/context` drops after `/compact` and the agent still knows what it was doing.

## Challenges
1. Set `"contextWindow": 6000` in `.forja/settings.json` and work: when does it compact?
2. Compact with a smaller model than the main one.

**Tests:** `tests/test_l07_compaction.py` · **Fallen behind?** `python scripts/tasks.py catchup 08`

---
[← previous](../L06_context/README.md) · [next →](../L08_planning/README.md)
