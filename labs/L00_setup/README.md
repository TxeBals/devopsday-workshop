# Lab 00 · Setup y primer contacto

🇬🇧 [English](README.en.md) · Día 1 · 09:00–09:30

**Objetivo:** Tener Ollama con un modelo que sepa usar tools, el repo instalado y los tests ejecutándose.

## Conceptos
- **Qué vamos a construir:** *Forja*, un agente de código de terminal como los comerciales: lee y edita tu proyecto, ejecuta comandos, pide permiso, planifica, delega en subagentes y se extiende con hooks, skills y MCP. Funciona con modelos abiertos en tu máquina.
- **Agente = modelo + tools + bucle. Harness = todo lo demás** (permisos, contexto, interfaz, sesiones…). El modelo es una pieza intercambiable: el harness es lo que construimos.
- **Cómo funcionan los labs:** cada lab tiene funciones con `TODO` en `forja/` y tests en `tests/`. Cuando los tests pasan, la capacidad se enciende sola en tu CLI. ¿Te quedas atrás? `python scripts/tasks.py catchup NN`.
- **Modelos:** `qwen3:8b` (portátil de 16 GB), `qwen3-coder:30b` (Mac de 32 GB o GPU de 24 GB), o el servidor compartido del aula. OpenRouter solo con modelos open-weight.

## Lo que implementas
Este lab no tiene TODOs.

## Ejecuta
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # instala y crea .env
ollama pull qwen3:8b               # o el modelo de tu nivel de hardware
python scripts/tasks.py test       # casi todo en rojo: es lo esperado
cd playground && python -m pytest -q   # 3 tests fallan: trabajo para tu agente
```

## Checkpoint
`ollama run qwen3:8b "hola"` responde y `python scripts/tasks.py test` se ejecuta (en rojo, como debe ser). El tutor enseña `python scripts/tasks.py demo`: así será tu agente al final del día 2.

## Retos
1. Ejecuta `ollama ps` mientras el modelo responde: ¿va en GPU o CPU? ¿Cuánta memoria usa?
2. Lee `forja/harness.py` por encima: localiza la «puerta» por la que pasa cada tool call.

---
[siguiente →](../L01_llm_streaming/README.md)
