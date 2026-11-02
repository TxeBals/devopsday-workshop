# Lab 02 · File tools

Day 1 · 10:15–11:15

**Goal:** Give the agent eyes and hands on the project: read, search, create and edit files safely.

## Concepts
- **The schema is the prompt:** name, docstring and type hints generate the JSON Schema the model reads. A good description beats any system-prompt instruction.
- **Tools never raise:** every error goes back to the model as actionable text (“appears 3 times: add context”) so it can self-correct.
- **edit_file = exact replacement of a unique string.** The most robust format for small models (they produce bad diffs). Typical model mistakes: including `read_file` line numbers or changing indentation.
- **Read before edit** and detect external changes (mtime): the agent doesn't overwrite what it hasn't seen or what you just changed.
- **Sandbox:** every path resolves inside the workspace. `../` and outside absolute paths are rejected.
- **Explore without loading the repo:** `grep` and `glob` return paths and lines; the agent reads only what's relevant.

## What you implement
| TODO | File | What |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: OpenAI-format JSON Schema |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: run without ever raising |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: path sandbox |
| 02.4 | `forja/fs_tools.py` | write_file: create / overwrite with read-first |
| 02.5 | `forja/fs_tools.py` | edit_file: exact, unique replacement with useful errors |
| 02.6 | `forja/fs_tools.py` | grep: regex search across the workspace |

## Run
```bash
python scripts/tasks.py test 02
forja --cwd playground
> what does the due_date function do?        (no loop yet: you'll see the first tool call)
```

## Checkpoint
Lab 02 tests green. With lab 03 still pending, Forja is still a chat: the loop comes next.

## Challenges
1. Add a `list_dir` tool with a 2-level tree. Does it help or hurt the model's exploration?
2. Ask the model to edit something and watch its `old_string` mistakes: which hint would you add to the error message?

**Tests:** `tests/test_l02_tools.py` · **Fallen behind?** `python scripts/tasks.py catchup 03`

---
[← previous](../L01_llm_streaming/README.md) · [next →](../L03_loop/README.md)
