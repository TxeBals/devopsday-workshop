# Lab 00 · Setup and first contact

Day 1 · 09:00–09:30

**Goal:** Have Ollama running a tool-capable model, the repo installed and the tests running.

## Concepts
- **What we will build:** *Forja*, a terminal coding agent like the commercial ones: it reads and edits your project, runs commands, asks for permission, plans, delegates to subagents and is extended with hooks, skills and MCP. It runs on open models on your machine.
- **Agent = model + tools + loop. Harness = everything else** (permissions, context, UI, sessions…). The model is a swappable part: the harness is what we build.
- **How the labs work:** each lab has `TODO` functions in `forja/` and tests in `tests/`. When the tests pass, the capability lights up in your CLI. Falling behind? `python scripts/tasks.py catchup NN`.
- **Models:** `qwen3:8b` (16 GB laptop), `qwen3-coder:30b` (32 GB Mac or 24 GB GPU), or the room's shared server. OpenRouter with open-weight models only.

## What you implement
This lab has no TODOs.

## Before you start
- You need **Python 3.11+**, **git** and **Ollama** installed (or the address of the room's shared server). Check with `python --version` (macOS/Linux: `python3 --version`), `git --version` and `ollama --version`.
- Everything is run **from the repo root** through `python scripts/tasks.py …` so the same commands work on Windows (PowerShell/cmd) and macOS/Linux, without `make`.
- Map of the repo: `forja/` = YOUR code (stub functions raising `NotImplementedError("TODO NN.x")` with a hint comment above), `tests/test_lNN_*.py` = offline tests per lab (they use `forja/fake_llm.py`, no model needed), `playground/` = small invoices project with 3 bugs that your agent will fix, `labs/LNN_*/` = lab sheets.
- Forja is **progressive**: `forja/harness.py` catches `NotImplementedError` and keeps running without the missing piece, printing a note like `· tools: lab 02 pending — running without this capability`. Every lab you finish lights up a capability in the CLI.

## Setup step by step
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

## Run
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # installs and creates .env
ollama pull qwen3:8b               # or the model for your hardware tier
python scripts/tasks.py test       # almost everything red: that's expected
cd playground && python -m pytest -q   # 3 tests fail: work for your agent
```

## Try it in your agent
1. Watch the tutor run `python scripts/tasks.py demo`: the reference agent on `playground/`. That is your agent at the end of day 2.
2. Run `ollama ps` while `ollama run qwen3:8b "write a haiku"` is answering: note GPU vs CPU and the memory used.
3. Skim `forja/harness.py`, method `Forja.gate`: every tool call goes parse → PreToolUse hook → permissions → approval → execute → PostToolUse hook. Each step is a lab.
4. Open `forja/llm.py` and find the first `# TODO 01.1:` comment: this is what a starter stub looks like.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled` | Execution policy → `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, or use cmd.exe with `.venv\Scripts\activate.bat`. |
| `forja` is not recognized / `command not found: forja` | The venv isn't active or `setup` failed → activate it and re-run `python scripts/tasks.py setup`. `python -m forja` works as a fallback. |
| `ERROR: Package 'forja' requires a different Python` | Your Python is older than 3.11 → install 3.11+ and recreate `.venv` with it (Windows: `py -3.12 -m venv .venv`). |
| `forja doctor` → `✘ could not talk to the model: APIConnectionError` | Ollama is not running or `OLLAMA_BASE_URL` is wrong → start the Ollama app (or `ollama serve`) and check `http://localhost:11434` in a browser says *Ollama is running*. |
| `forja doctor` → `ModelPolicyError: model '…' blocked by policy` | You chose a closed model id (anthropic/openai/gpt-oss/o3…) → use an open-weight model. |
| `forja doctor` is very slow the first time (30–90 s) | The model is being loaded into memory → normal; the second call is fast. If it stays slow, `ollama ps` probably shows CPU: use a smaller model or the shared server. |
| macOS: `python: command not found` | Outside the venv macOS only has `python3` → create the venv with `python3 -m venv .venv`; once it is active, `python` works. |

## You're done when
- [ ] [ ] `ollama run <your model> "hello"` answers (or the shared server answers `forja doctor`).
- [ ] [ ] `forja doctor` prints `✔ the model calls tools`.
- [ ] [ ] `python scripts/tasks.py test` runs and shows red `NotImplementedError: TODO …` failures.
- [ ] [ ] `playground` tests show exactly 3 failures.

## Checkpoint
`ollama run qwen3:8b "hello"` answers and `python scripts/tasks.py test` runs (red, as it should). The tutor shows `python scripts/tasks.py demo`: that is what your agent will look like at the end of day 2.

## Challenges
1. Run `ollama ps` while the model answers: GPU or CPU? How much memory?
2. Skim `forja/harness.py`: find the “gate” every tool call goes through.

---
[next →](../L01_llm_streaming/README.md)
