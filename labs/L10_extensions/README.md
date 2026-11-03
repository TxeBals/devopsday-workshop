# Lab 10 · Extensibility: hooks, skills and MCP

Day 2 · 12:10–13:20

**Goal:** Let the team extend the agent without touching its code: deterministic policy, on-demand knowledge and external tools.

## Concepts
- **Hooks = guarantees:** AGENTS.md *asks*, a hook *enforces*. Shell commands in `settings.json` that receive the event as JSON on stdin. Exit 2 blocks; exit 0 continues. It's the convention commercial agents use: what you learn here applies there.
- **Events:** `PreToolUse` (block), `PostToolUse` (feedback, e.g. a linter), `UserPromptSubmit` (filter or add context), `Stop` (don't finish until tests pass).
- **Skills = progressive disclosure:** only the catalogue (name + description) goes in the prompt; the body is loaded with the `skill` tool when needed. Portable `SKILL.md` format.
- **MCP:** servers that expose tools (issues, DB, wiki, CI). Forja starts them from `settings.json` and registers them as `mcp__server__tool`, with `exec` risk: they go through permissions.

## What you implement
| TODO | File | What |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks by event and matcher |
| 10.2 | `forja/hooks.py` | run: execute and map exit codes |
| 10.3 | `forja/skills.py` | discover_skills: SKILL.md catalogue |
| 10.4 | `forja/skills.py` | skill: load the body on demand |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: mcp__server__tool namespace |

## Before you start
- Three small files, three ideas: `forja/hooks.py` (10.1, 10.2), `forja/skills.py` (10.3, 10.4) and `forja/mcp_tools.py` (10.5). The harness (`forja/harness.py`) already calls them: `self.hooks.run("PreToolUse", {...}, tool.name)` in `gate`, `"PostToolUse"` after executing, `"UserPromptSubmit"` and `"Stop"` in `turn`; `skills.discover_skills(home/.forja/skills, root/.forja/skills)` at startup; `mcp_tool_name` inside `connect_servers`.
- Hooks API: `subprocess.run(cmd, shell=True, cwd=..., input=<json str>, capture_output=True, text=True, timeout=...)` returns a `CompletedProcess` with `returncode`, `stdout`, `stderr`; it raises `subprocess.TimeoutExpired` on timeout. `re.fullmatch(pattern, s)` matches the WHOLE string (so `edit_file|write_file` works as an alternation). With `shell=True` the shell is cmd.exe on Windows and `/bin/sh` on macOS/Linux.
- Exit-code convention (same as commercial agents): `0` = OK (stdout may be useful context), `2` = BLOCK (stderr, or stdout if empty, is the message for the model), anything else = hook error (recorded, never blocks). `HookOutcome` has `block`, `message`, `context`, `errors`.
- Skills reuse the frontmatter parsing you wrote in 09.1 (`FRONTMATTER` + `yaml.safe_load`). `catalog()` is already written: it only needs `Skill.name` and `Skill.description`.
- Look at `examples/project/.forja/settings.json` and `examples/project/.forja/hooks/*.py`: a real PreToolUse hook reads the event with `json.load(sys.stdin)` and exits 2 with a message on stderr.

## Step by step
10.1 → 10.2 (one test covers both: `test_hook_matching_and_exit_codes`; then `test_hooks_in_harness` checks the integration), then 10.5 (one line, quick win), then 10.3 → 10.4 (both checked by `test_skills`). Leave `test_mcp_end_to_end` for last: it starts a real MCP server subprocess and needs labs 02-04 working.

### TODO 10.1 · `forja/hooks.py` · `HookRunner.matching(event: str, tool_name: str | None = None) -> list[dict]`

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

### TODO 10.2 · `forja/hooks.py` · `HookRunner.run(event: str, payload: dict, tool_name: str | None = None) -> HookOutcome`

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

### TODO 10.3 · `forja/skills.py` · `discover_skills(*folders: Path) -> dict[str, Skill]`

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

### TODO 10.4 · `forja/skills.py` · `make_skill_tool(skills)` → inner tool `skill(name: str) -> str`

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

### TODO 10.5 · `forja/mcp_tools.py` · `mcp_tool_name(server: str, tool: str) -> str`

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

## Run
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # if you didn't in lab 09
forja --cwd playground
> list the open issues, fix #12 and comment on the issue what you changed
> commit following the repo's convention
```

## Try it in your agent
1. Make sure `playground/.forja/` exists (copied in lab 09). The MCP server path in `settings.json` (`../examples/mcp/issues_server.py`) is resolved from the project root (`playground/`), so `forja --cwd playground` from the repo root works. If the server fails you get a startup note `· MCP 'issues': …` and no MCP tools.
2. `/tools` → you should see `mcp__issues__list_issues`, `mcp__issues__get_issue`, `mcp__issues__comment_issue` with `[exec]`, and `skill [read]`.
3. `list the open issues, fix #12 and comment on the issue what you changed`. Expected: `⏺ mcp__issues__list_issues` (no approval prompt: `mcp__issues__*` is in `allow`), reads/edits in `invoices/amounts.py`, a PostToolUse compile check after each edit, and finally `mcp__issues__comment_issue`.
4. Watch the Stop hook (`.forja/hooks/stop_tests.py`): it only runs when there are uncommitted changes in the project (git), so plain questions are not affected. If the agent edited files and says it is done while tests are red, you will see it keep working (a `[Stop hook] You are not done yet…` user message is injected with the pytest tail). It gives up after 3 extra rounds.
5. `commit following the repo's convention` → the first call should be `⏺ skill conventional-commits`, then `git status`/`git diff`, then a commit message like `fix(amounts): …`. (You will be asked to approve `git commit`: it is not in `allow`.)
6. Try the PreToolUse hook: `run cat .env` → the result shows `BLOCKED by hook: Command blocked by policy: it may expose secrets…`.

## If something goes wrong
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

## You're done when
- [ ] [ ] `python scripts/tasks.py test 10` → 5 passed (including `test_mcp_end_to_end`).
- [ ] [ ] In the CLI: `cat .env` is blocked by the PreToolUse hook, and the Stop hook makes the agent continue while tests are red.
- [ ] [ ] `/tools` lists `skill` and the `mcp__issues__*` tools, and the agent loads `conventional-commits` before committing.

## Checkpoint
The Stop hook won't let it finish with red tests; the agent loads the `conventional-commits` skill before committing; `mcp__issues__*` tools show up in `/tools`.

## Challenges
1. A PostToolUse hook that runs `ruff` on the edited file.
2. Connect a real MCP server from your team.

**Tests:** `tests/test_l10_extensions.py` · **Fallen behind?** `python scripts/tasks.py catchup 11`

---
[← previous](../L09_subagents/README.md) · [next →](../L11_sessions/README.md)
