# Lab 11 · Sessions and undo

Day 2 · 14:20–14:55

**Goal:** Resume sessions and undo what the agent did without relying on git.

## Concepts
- **Append-only JSONL transcript:** one message per line in `.forja/sessions/`. Resume, audit and debug. After compaction, a marker with the new state.
- **Checkpoints:** before a tool modifies a file, its original content (or that it didn't exist) is saved — only the first time per turn.
- **/undo:** restores the files from the last turn with changes. Works without git and doesn't touch your commits.
- **Limit:** `bash` side effects (installing packages, `rm`) can't be undone. That's why bash goes through permissions.

## What you implement
| TODO | File | What |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (with compaction markers) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

## Before you start
- Open `forja/session.py`. Two independent classes: `Transcript` (11.1, 11.2: a JSONL file per session in `<project>/.forja/sessions/<id>.jsonl`) and `Checkpoints` (11.3, 11.4: an in-memory stack of turns, each `{Path: original bytes | None}`). `mark_compaction` and `list_sessions` are already written: read them, they tell you the line format (`{"ts": ..., "message": m}` and `{"ts": ..., "compacted": [...]}`).
- How the harness uses them: at the end of `Forja.turn` it calls `self.transcript.append(*self.history[start:])` (only the NEW messages); `resume(id)` calls `Transcript.load(folder, id)`. `Forja.turn` calls `self.checkpoints.begin_turn()`, and `Workspace` calls `checkpoints.before_write(path)` right BEFORE `write_file`/`edit_file` touch a file (see `forja/fs_tools.py`). `/undo` calls `Checkpoints.undo()`.
- Stdlib: `json.dumps(obj, ensure_ascii=False)`, `json.loads(line)`, `Path.open("a", encoding="utf-8")` (append mode), `Path.read_bytes()` / `write_bytes()` (bytes, so encodings and line endings are restored exactly), `Path.unlink(missing_ok=True)`, `Path.mkdir(parents=True, exist_ok=True)`.
- Limit to keep in mind: only file tools create checkpoints. Whatever `bash` does (`rm`, `pip install`, `sed -i`) cannot be undone.

## Step by step
11.1 and 11.2 together (one round-trip test: `test_transcript_roundtrip`), then 11.3 and 11.4 together (`test_checkpoints`). Finish with `test_harness_resume_and_undo`, which exercises everything through the real harness (needs labs 02-04 for `edit_file` in `accept_edits`).

### TODO 11.1 · `forja/session.py` · `Transcript.append(self, *messages: dict) -> None`

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

### TODO 11.2 · `forja/session.py` · `Transcript.load(folder: Path, session_id: str) -> list[dict]` (staticmethod)

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

### TODO 11.3 · `forja/session.py` · `Checkpoints.before_write(self, path: Path) -> None`

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

### TODO 11.4 · `forja/session.py` · `Checkpoints.undo(self) -> list[Path]`

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

## Run
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> change the default due-date period to 60 days
/undo
/sessions
forja --cwd playground --resume <id>
```

## Try it in your agent
1. `forja --cwd playground --mode accept_edits` and type `change the default due-date period to 60 days`. Expected: an `edit_file invoices/dates.py` with a diff panel (`days: int = 30` → `60`), no approval prompt (accept_edits).
2. `/undo` → `restored: invoices/dates.py`. Check the file: it says `30` again. `/undo` once more → `nothing to undo`.
3. Ask a plain question (`what does due_date do?`), make another edit, ask another question, then `/undo`: it still reverts the last turn WITH changes (empty turns are skipped).
4. `/sessions` → lines like `20261103-143012-a1b2  change the default due-date period to 60 days`. Look at the raw file: macOS/Linux `cat playground/.forja/sessions/<id>.jsonl` · PowerShell `Get-Content playground\.forja\sessions\<id>.jsonl` — one JSON object per line.
5. `/exit`, then `forja --cwd playground --resume <id>` and ask `what did you change before?` → the agent answers from the restored history.
6. Note what is NOT undone: ask the agent to `create a file tmp.txt using bash` and `/undo` → `tmp.txt` is still there (`/undo` says `nothing to undo`, or reverts an OLDER edit turn instead). Clean up with `python scripts/tasks.py reset` if needed.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `json.decoder.JSONDecodeError: Extra data` in `load` | Two records on the same line → add `"\n"` after each `json.dumps` in `append`. |
| Round-trip returns only the last message | You opened the file with `"w"` → use append mode `"a"`. |
| `test_checkpoints`: `a.txt` restores to `v1` instead of `original` | `before_write` overwrites the stored original → only store it the first time the path appears in the turn. |
| `/undo` always says `nothing to undo` after a follow-up question | Empty turns on top of the stack are not skipped → pop empty turns before popping the real one. |
| `test_harness_resume_and_undo`: `app2.history == app.history` fails | Messages are being changed on the way (e.g. you saved `str(m)` or only `content`) → dump the whole dict as JSON and load it back unchanged. |
| `UnicodeEncodeError` / garbled text in `.jsonl` on Windows | Default codepage is not UTF-8 → pass `encoding="utf-8"` when opening and reading, keep `ensure_ascii=False`. |
| `--resume` says the session does not exist | Sessions live in `<project>/.forja/sessions/` → resume with the same `--cwd` you used when creating it, and copy the id from `/sessions`. |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 11` → 3 passed.
- [ ] [ ] `/undo` restores a file edited by the agent and deletes a file it created, without git.
- [ ] [ ] `forja --cwd playground --resume <id>` continues the previous conversation.

## Checkpoint
`/undo` restores the file and `--resume` continues the previous conversation.

## Challenges
1. `/undo N` to undo several turns.
2. `/rewind`: undo files AND roll history back to the same point.

**Tests:** `tests/test_l11_sessions.py` · **Fallen behind?** `python scripts/tasks.py catchup 12`

---
[← previous](../L10_extensions/README.md) · [next →](../L12_evals/README.md)
