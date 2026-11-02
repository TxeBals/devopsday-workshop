# Forja · Construye tu propio agente de código con modelos locales

🇬🇧 [English](README.en.md)

Workshop práctico de 2 días (o 1 día comprimido) en el que cada asistente construye **Forja**, un agente de código de terminal —del tipo de Claude Code, Codex CLI u OpenCode— desde cero, en Python y con **modelos abiertos en local** (Ollama, vLLM, LM Studio) u OpenRouter con modelos open-weight. No se usan modelos de Anthropic ni OpenAI: el código los bloquea.

Cada lab rellena una pieza; el harness es **progresivo**: la CLI funciona desde el lab 01 y gana capacidades a medida que completas labs.

## Por dónde empiezo
1. [Checklist de setup](docs/checklist_setup.md) — **antes del día**.
2. [Cuaderno del alumno](docs/alumno/cuaderno_alumno.md).
3. Los labs, en orden.

## Labs
| Lab | Día · hora | Tema |
|---|---|---|
| [L00](labs/L00_setup/README.md) | 1 · 09:00–09:30 | Setup y primer contacto |
| [L01](labs/L01_llm_streaming/README.md) | 1 · 09:30–10:15 | Cliente LLM con streaming |
| [L02](labs/L02_tools_ficheros/README.md) | 1 · 10:15–11:15 | Tools de ficheros |
| [L03](labs/L03_bucle/README.md) | 1 · 11:30–12:15 | El bucle del agente |
| [L04](labs/L04_bash_permisos/README.md) | 1 · 12:15–13:00 | Bash y permisos |
| [L05](labs/L05_cli/README.md) | 1 · 14:00–15:00 | La CLI: tu agente de terminal |
| [L06](labs/L06_contexto/README.md) | 2 · 09:00–09:40 | Ingeniería de contexto |
| [L07](labs/L07_compactacion/README.md) | 2 · 09:40–10:25 | Gestión de contexto y compactación |
| [L08](labs/L08_planificacion/README.md) | 2 · 10:25–11:10 | Planificar antes de actuar |
| [L09](labs/L09_subagentes/README.md) | 2 · 11:25–12:10 | Subagentes |
| [L10](labs/L10_extensiones/README.md) | 2 · 12:10–13:20 | Extensibilidad: hooks, skills y MCP |
| [L11](labs/L11_sesiones/README.md) | 2 · 14:20–14:55 | Sesiones y deshacer |
| [L12](labs/L12_evals/README.md) | 2 · 14:55–16:00 | Evals: medir tu agente |
| — | 2 · 16:00 | Proyecto final (ver cuaderno) |

## Comandos (Windows, macOS y Linux)
```bash
python scripts/tasks.py setup          # instalar y crear .env
python scripts/tasks.py test 03        # tests del lab 03 contra tu código
python scripts/tasks.py catchup 05     # ponerte al día: resuelve los labs 01–04 (con forja-solutions.zip del tutor)
forja                                  # tu agente, sobre el directorio actual
python scripts/tasks.py evals          # evals con tu agente
```

## Estructura
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

## Notas
- Datos y proyecto de práctica sintéticos.
- No se basa en OpenClaude (fork del código filtrado de Claude Code): Forja es una implementación propia con la misma arquitectura, documentada públicamente.
- Los tests no necesitan modelo ni GPU (FakeLLM). Los tags de modelos cambian: verifícalos antes del workshop.
