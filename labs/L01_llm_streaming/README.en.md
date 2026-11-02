# Lab 01 · Streaming LLM client

🇪🇸 [Español](README.md) · Day 1 · 09:30–10:15

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

## Run
```bash
python scripts/tasks.py test 01
forja doctor                      # ¿el modelo llama tools?
forja                             # ya es un chat en streaming (aún sin tools)
```

## Checkpoint
`forja doctor` shows ✔ and `forja` answers in streaming. “lab NN pending” notes are expected.

## Challenges
1. Measure local time-to-first-token against OpenRouter.
2. What if the model emits two tool calls with the same `index`? Can it happen?

**Tests:** `tests/test_l01_llm.py` · **Fallen behind?** `python scripts/tasks.py catchup 02`

---
[← previous](../L00_setup/README.en.md) · [next →](../L02_tools_ficheros/README.en.md)
