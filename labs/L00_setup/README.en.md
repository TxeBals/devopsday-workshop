# Lab 00 · Setup and first contact

🇪🇸 [Español](README.md) · Day 1 · 09:00–09:30

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
python scripts/tasks.py setup      # instala y crea .env
ollama pull qwen3:8b               # o el modelo de tu nivel de hardware
python scripts/tasks.py test       # casi todo en rojo: es lo esperado
cd playground && python -m pytest -q   # 3 tests fallan: trabajo para tu agente
```

## Checkpoint
`ollama run qwen3:8b "hello"` answers. The tutor shows `python scripts/tasks.py demo`: that is what your agent will look like at the end.

## Challenges
1. Run `ollama ps` while the model answers: GPU or CPU? How much memory?
2. Skim `forja/harness.py`: find the “gate” every tool call goes through.

---
[next →](../L01_llm_streaming/README.en.md)
