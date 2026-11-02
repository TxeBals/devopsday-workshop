# Forja · Build your own coding agent with local models

Hands-on workshop where you build **Forja**, a terminal coding agent —like Claude Code, Codex CLI or OpenCode— from scratch,
in Python, on **local open models** (Ollama, vLLM, LM Studio) or OpenRouter with open-weight models.
Anthropic and OpenAI models are blocked in code.

Each lab fills in one piece. The harness is **progressive**: the CLI works from lab 01 and gains capabilities as you complete labs.

## Where to start
1. [Setup checklist](docs/setup_checklist.md) — **before the day**.
2. [Student workbook](docs/student_workbook.md).
3. The labs, in order.

## Labs
| Lab | Day · time | Topic |
|---|---|---|
| [L00](labs/L00_setup/README.md) | 1 · 09:00–09:30 | Setup and first contact |
| [L01](labs/L01_llm_streaming/README.md) | 1 · 09:30–10:15 | Streaming LLM client |
| [L02](labs/L02_file_tools/README.md) | 1 · 10:15–11:15 | File tools |
| [L03](labs/L03_loop/README.md) | 1 · 11:30–12:15 | The agent loop |
| [L04](labs/L04_bash_permissions/README.md) | 1 · 12:15–13:00 | Bash and permissions |
| [L05](labs/L05_cli/README.md) | 1 · 14:00–15:00 | The CLI: your terminal agent |
| [L06](labs/L06_context/README.md) | 2 · 09:00–09:40 | Context engineering |
| [L07](labs/L07_compaction/README.md) | 2 · 09:40–10:25 | Context management and compaction |
| [L08](labs/L08_planning/README.md) | 2 · 10:25–11:10 | Plan before acting |
| [L09](labs/L09_subagents/README.md) | 2 · 11:25–12:10 | Subagents |
| [L10](labs/L10_extensions/README.md) | 2 · 12:10–13:20 | Extensibility: hooks, skills and MCP |
| [L11](labs/L11_sessions/README.md) | 2 · 14:20–14:55 | Sessions and undo |
| [L12](labs/L12_evals/README.md) | 2 · 14:55–16:00 | Evals: measure your agent |
| — | 2 · 16:00 | Final project (see the workbook) |

## Commands (Windows, macOS and Linux)
```bash
python scripts/tasks.py setup          # install and create .env
python scripts/tasks.py test 03        # lab 03 tests against your code
forja                                  # your agent, on the current directory
python scripts/tasks.py evals          # evals with your agent
python scripts/tasks.py catchup 05     # catch up: solves labs 01–04 (needs the tutor's forja-solutions.zip)
python scripts/tasks.py reset          # restore playground/ (git)
```

## Layout
```
devopsday-workshop/
├── docs/          setup_checklist.md · student_workbook.md · hardware.png
├── labs/          L00…L12, one README per lab
├── forja/         your code: functions with TODO NN.x
├── tests/         test_lNN_*.py (offline, FakeLLM: no GPU needed)
├── playground/    small invoices project with bugs for your agent
├── examples/      settings, hooks, skill, subagent, MCP server
├── evals/         tasks.yaml · hidden/ · run_evals.py
└── scripts/       tasks.py · catchup.py
```

## Notes
- Synthetic data and practice project.
- Forja is an independent implementation of the publicly documented architecture of coding agents.
- Tests need no model or GPU. Model tags change: check them before the workshop.
