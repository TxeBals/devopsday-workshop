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

## Run
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # installs and creates .env
ollama pull qwen3:8b               # or the model for your hardware tier
python scripts/tasks.py test       # almost everything red: that's expected
cd playground && python -m pytest -q   # 3 tests fail: work for your agent
```

## Checkpoint
`ollama run qwen3:8b "hello"` answers and `python scripts/tasks.py test` runs (red, as it should). The tutor shows `python scripts/tasks.py demo`: that is what your agent will look like at the end of day 2.

## Challenges
1. Run `ollama ps` while the model answers: GPU or CPU? How much memory?
2. Skim `forja/harness.py`: find the “gate” every tool call goes through.

---
[next →](../L01_llm_streaming/README.md)
