# Lab 12 · Evals: measure your agent

Day 2 · 14:55–16:00

**Goal:** Compare models and harness changes with real tasks and objective checks.

## Concepts
- **Without measuring, it's all opinion.** Is `qwen3-coder:30b` better than `qwen3:8b`? Does your new prompt help? Measure it.
- **Task = prompt + objective check** on a CLEAN COPY of the project: tests (`command`), HIDDEN tests copied afterwards (`hidden`, so it can't cheat), answer content (`answer_contains`) and changing nothing (`forbid_changes`).
- **Headless + bypass inside the copy:** the sandbox is the temp folder.
- **Several repetitions:** models aren't deterministic. Look at pass rate, steps, time and tokens.

## What you implement
| TODO | File | What |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: apply the checks |
| 12.2 | `forja/evals.py` | summarize: pass rate, per task, steps, time, tokens |

## Before you start
- Open `forja/evals.py` (your TODOs: `grade` and `summarize`) and `evals/tasks.yaml` (the tasks). Already written for you: `load_tasks`, `snapshot(root)` (dict `relative path -> sha1`, ignoring `.forja`, `.git`, `__pycache__`, `.pytest_cache`), `norm(s)` (lowercase + strip accents) and `run_task`, which copies `playground/` into a temp dir, runs ONE headless turn in `bypass` mode, then calls your `grade(task, work, answer, before, repo_root)`.
- The runner is `evals/run_evals.py` (via `python scripts/tasks.py evals ...`): flags `--model`, `--backend`, `--repeat N`, `--only <id>`, `--max-steps`, `--config <.forja folder>` (use your settings, hooks, skills and subagents in every task), `--mcp` and `--label <suffix>` for the report name. It prints one `PASS`/`FAIL` line per run, calls your `summarize` and writes `out/evals_<model>.json` (`/` and `:` in the model name become `_`).
- Stdlib: `subprocess.run(cmd, shell=True, cwd=workdir, capture_output=True, text=True, timeout=...)` and `subprocess.TimeoutExpired`; `shutil.copy(src, dst)`; `statistics.mean`; `dataclasses.asdict`. `TaskResult` fields: `id, passed, reason, steps, tool_calls, tokens, seconds, stop_reason, answer`.
- A task's `check` dict may contain: `command` (exit 0 = pass, optional `timeout`, default 120 s), `hidden` (`{repo-relative source: workdir-relative destination}`, copied AFTER the agent finished), `answer_contains` (list of strings), `forbid_changes` (bool).
- Evals use YOUR whole agent (labs 01-11). `test_run_task_pass_and_fail` drives `read_file`, `edit_file` and `bash` through the harness, so those labs must pass.

## Step by step
12.1 first (`test_grade_answer_and_forbid_changes`, `test_hidden_tests_copied_after`, then `test_run_task_pass_and_fail`), because `run_task` and the runner depend on it. 12.2 is independent arithmetic (`test_summarize`). Then run real evals: start with `--only vat_question` (fast, read-only).

### TODO 12.1 · `forja/evals.py` · `grade(task, workdir, answer, before, repo_root) -> tuple[bool, str]`

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

### TODO 12.2 · `forja/evals.py` · `summarize(results: list[TaskResult], model: str) -> dict`

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

## Run
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_rounding
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
python scripts/tasks.py evals --repeat 3 --config playground/.forja --label config   # with your hooks, skills and subagents
```

## Try it in your agent
1. `python scripts/tasks.py evals --only vat_question` (read-only, fastest). Expected: `» …run_evals.py --only vat_question`, then a line like `PASS  vat_question           18.4s   4 steps` (or `FAIL … the answer is missing: ['calculate_vat']`), then the summary `qwen3:8b: pass_rate 100% · 4.0 steps · 18.4s/task · 9123 tokens`, `per task: {...}` and `-> out/evals_qwen3_8b.json`.
2. `python scripts/tasks.py evals --only fix_rounding` → a FAIL line shows the last 3 lines of pytest output as the reason. Note that your real `playground/` is never modified.
3. `python scripts/tasks.py evals --repeat 3` (all 5 tasks × 3; this takes a while on a laptop — start it and keep reading). Look at `per_task`: which tasks are flaky (0.33, 0.67)?
4. If you have a second model: `python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3` (or the classroom server via `--backend openai_compat`). Open both `out/evals_*.json` files and compare `pass_rate`, `avg_steps`, `avg_seconds`, `total_tokens`.
5. Inspect a failure: in the JSON, `results[i].answer` (first 500 chars) and `stop_reason` (`max_steps`, `loop`, `error`…) usually tell you why.

## If something goes wrong
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

## You're done when
- [ ] [ ] `python scripts/tasks.py test 12` → 5 passed.
- [ ] [ ] You have at least one `out/evals_<model>.json` produced with `--repeat 3`.
- [ ] [ ] You can state, with numbers (pass rate, steps, seconds, tokens), which model you would use for which tasks.

## Final project step by step

Final project (16:00–17:00): customise Forja for the way YOU work and prove it with numbers. Five deliverables, each small. Work in `playground/` (or a real repo of yours for 1–4) and keep a short `NOTES` list of what you changed for the 3-minute demo. Budget: ~10 min per deliverable, 15 min for the evals.

### AGENTS.md: global preferences + one per repo

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

### A team skill

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

### A hook that guarantees something you now ask for politely

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

### A specialised subagent profile

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

### An eval task for your daily work + a 2-model report

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

### 3-minute demo
1. 3 minutes per person/pair: 30 s what you added (show the files), 90 s one live prompt where a skill/hook/subagent visibly kicks in, 60 s the eval table and your conclusion.
2. Bring numbers, not impressions: 'pass rate on my task went from 0.33 to 1.0 with qwen3-coder:30b at 2× the time'.

### You're done when
- [ ] [ ] Global and project `AGENTS.md` exist and the agent can quote them.
- [ ] [ ] One skill is loaded by the agent (`⏺ skill <name>`) when relevant.
- [ ] [ ] One hook visibly blocks or feeds back (`BLOCKED by hook` / `[hook PostToolUse]`).
- [ ] [ ] One subagent profile is listed in the `task` description and used (`[<name>]` calls).
- [ ] [ ] One new task in `evals/tasks.yaml`, `python scripts/tasks.py test 12` still passes, and two `out/evals_*.json` reports compared in a table.

## Checkpoint
You have a report in `out/` and can say, with numbers, which model you'd use for which tasks.

## Challenges
1. Add your own task to `evals/tasks.yaml`.
2. Compare your harness with and without `todo_write` in the base prompt.

**Tests:** `tests/test_l12_evals.py` · **Fallen behind?** `python scripts/tasks.py catchup end`

---
[← previous](../L11_sessions/README.md)
