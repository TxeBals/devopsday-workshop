# Lab 01 · Cliente LLM con streaming

🇬🇧 [English](README.en.md) · Día 1 · 09:30–10:15

**Objetivo:** Hablar con cualquier backend OpenAI-compatible en streaming y reconstruir las tool calls que llegan troceadas.

## Conceptos
- **Un protocolo, muchos backends:** Ollama, vLLM, LM Studio, llama.cpp y OpenRouter hablan Chat Completions. El SDK `openai` es solo un cliente HTTP; el modelo es abierto.
- **Streaming:** el texto llega token a token (la CLI se siente viva). Las **tool calls también llegan troceadas**: `index`, luego `id` y `name`, luego el JSON de argumentos en pedazos, a veces de varias llamadas intercaladas.
- **Rarezas de modelos locales:** bloques `<think>…</think>` que pueden partirse entre chunks; tool calls escritas como texto `<tool_call>{…}</tool_call>`.
- **Reintentos:** solo errores transitorios (conexión, 429, 5xx) con backoff exponencial. Un 400 no se arregla reintentando.

## Lo que implementas
| TODO | Fichero | Qué |
|---|---|---|
| 01.1 | `forja/llm.py` | ToolCallAccumulator: concatenar fragmentos por índice |
| 01.2 | `forja/llm.py` | ThinkFilter: quitar <think> aunque la etiqueta llegue partida |
| 01.3 | `forja/llm.py` | LLMClient.stream: reintentos, eventos TextDelta y Done |

## Ejecuta
```bash
python scripts/tasks.py test 01
forja doctor                      # ¿el modelo llama tools?
forja                             # ya es un chat en streaming (aún sin tools)
```

## Checkpoint
`forja doctor` dice ✔ y `forja` responde en streaming. Aparecen avisos «lab NN pendiente»: es normal.

## Retos
1. Mide el *time-to-first-token* local frente a OpenRouter.
2. ¿Qué pasa si el modelo emite dos tool calls con el mismo `index`? ¿Puede ocurrir?

**Tests:** `tests/test_l01_llm.py` · **¿Te has quedado atrás?** `python scripts/tasks.py catchup 02`

---
[← anterior](../L00_setup/README.md) · [siguiente →](../L02_tools_ficheros/README.md)
