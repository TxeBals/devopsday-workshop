# Forja · Build your own coding agent with local models

🇪🇸 [Español](README.md)

Hands-on 2-day workshop (or a compressed 1-day version) where every attendee builds **Forja**, a terminal coding agent —like Claude Code, Codex CLI or OpenCode— from scratch, in Python, on **local open models** (Ollama, vLLM, LM Studio) or OpenRouter with open-weight models. Anthropic and OpenAI models are not used: the code blocks them.

Each lab fills in one piece; the harness is **progressive**: the CLI works from lab 01 and gains capabilities as you complete labs.

> Code, prompts and the practice project are in Spanish; READMEs, workbooks, guides and decks exist in both languages.

## Where do I start
1. [Setup checklist](docs/setup_checklist.md) — **before the day**.
2. [Student workbook](docs/student/student_workbook.md).
3. The labs, in order.

## Labs
| Lab | Day · time | Topic |
|---|---|---|
| [L00](labs/L00_setup/README.en.md) | 1 · 09:00–09:30 | Setup and first contact |
| [L01](labs/L01_llm_streaming/README.en.md) | 1 · 09:30–10:15 | Streaming LLM client |
| [L02](labs/L02_tools_ficheros/README.en.md) | 1 · 10:15–11:15 | File tools |
| [L03](labs/L03_bucle/README.en.md) | 1 · 11:30–12:15 | The agent loop |
| [L04](labs/L04_bash_permisos/README.en.md) | 1 · 12:15–13:00 | Bash and permissions |
| [L05](labs/L05_cli/README.en.md) | 1 · 14:00–15:00 | The CLI: your terminal agent |
| [L06](labs/L06_contexto/README.en.md) | 2 · 09:00–09:40 | Context engineering |
| [L07](labs/L07_compactacion/README.en.md) | 2 · 09:40–10:25 | Context management and compaction |
| [L08](labs/L08_planificacion/README.en.md) | 2 · 10:25–11:10 | Plan before acting |
| [L09](labs/L09_subagentes/README.en.md) | 2 · 11:25–12:10 | Subagents |
| [L10](labs/L10_extensiones/README.en.md) | 2 · 12:10–13:20 | Extensibility: hooks, skills and MCP |
| [L11](labs/L11_sesiones/README.en.md) | 2 · 14:20–14:55 | Sessions and undo |
| [L12](labs/L12_evals/README.en.md) | 2 · 14:55–16:00 | Evals: measure your agent |
| — | 2 · 16:00 | Final project (see workbook) |

## Commands (Windows, macOS and Linux)
```bash
python scripts/tasks.py setup          # install and create .env
python scripts/tasks.py test 03        # lab 03 tests against your code
python scripts/tasks.py catchup 05     # catch up: solves labs 01–04 (with the tutor's forja-solutions.zip)
forja                                  # your agent, on the current directory
python scripts/tasks.py evals          # evals with your agent
```

## Layout
```
devopsday-workshop/
├── docs/
│   ├── alumno/         cuaderno_alumno.md                    ← alumno (ES)
│   ├── student/        student_workbook.md                   ← student (EN)
│   ├── checklist_setup.md · setup_checklist.md · hardware.png
├── labs/L00…L12/       README.md (ES) · README.en.md (EN)
├── forja/              código del alumno con TODOs  / student code with TODOs
├── tests/              test_lNN_*.py  (offline, FakeLLM)
├── playground/         proyecto con bugs para el agente / buggy practice project
├── examples/           settings, hooks, skills, subagente, servidor MCP
├── evals/              tasks.yaml · hidden/ · run_evals.py
└── scripts/            tasks.py · catchup.py
```

## Notes
- Synthetic data and practice project.
- Not based on OpenClaude (a fork of the leaked Claude Code source): Forja is an independent implementation of the same, publicly documented architecture.
- Tests need no model or GPU (FakeLLM). Model tags change: check them before the workshop.
