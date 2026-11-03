# Lab 09 · Subagents

Day 2 · 11:25–12:10

**Goal:** Delegate exploration and reviews to agents with their own context and restricted tools.

## Concepts
- **The problem:** exploring a repo costs 20 reads and 30k tokens that stay in the main agent's context forever.
- **The solution:** the `task` tool launches a subagent with a CLEAN context (system + prompt) that returns only its conclusion. The main agent pays ~300 tokens.
- **Same loop, other tools:** we reuse lab 03's `Agent` with a subset of tools and the SAME permission gate. A subagent can't spawn subagents.
- **Profiles in Markdown:** `.forja/agents/reviewer.md` with frontmatter (name, description, tools). The description is what the model reads to decide when to delegate.
- **The subagent prompt must be self-contained:** it doesn't see the conversation.

## What you implement
| TODO | File | What |
|---|---|---|
| 09.1 | `forja/subagents.py` | load_profiles: profiles from Markdown |
| 09.2 | `forja/subagents.py` | task: launch a subagent with a clean context |

## Before you start
- Open `forja/subagents.py` (your TODOs) and keep `forja/agent.py` (lab 03) and `forja/harness.py` (`_build_registry`) open next to it. The harness already calls `subagents.load_profiles(root / ".forja" / "agents")` and registers `subagents.make_task_tool(self.llm, reg, profiles, execute=self.gate, events_factory=self.sub_events)`: you only fill in the two functions.
- What you reuse: `Agent(llm, tools, execute=..., events=..., max_steps=...)` and its `run(messages) -> AgentResult` (fields `answer`, `stop_reason`, `steps`, `tool_calls`, `usage`). `ToolRegistry.subset(names)` builds a registry with only the names that exist (unknown names are silently skipped).
- Stdlib / libs used: `Path.glob("*.md")`, `Path.read_text(encoding="utf-8")`, the precompiled regex `FRONTMATTER` (group 1 = YAML between the `---` lines, group 2 = body) and `yaml.safe_load` (returns a dict, or `None` for empty YAML). `tools: read_file, grep` in YAML is a *string*; `tools: [read_file, grep]` is a *list*.
- Key idea: the subagent starts from a NEW `messages` list (system + user prompt). It never sees the main history; the main agent only gets back the string your `task` tool returns. Every subagent tool call still goes through `execute` = the harness gate (hooks, permissions, approvals, checkpoints).
- Look at `examples/project/.forja/agents/reviewer.md` for a real profile (it has `tools` and `max_steps`).

## Step by step
Do 09.1 first: it is pure parsing, has its own isolated test (`test_load_profiles`) and the harness needs it to build the list of subagents that appears in the `task` tool description. Then 09.2, whose tests (`test_task_isolated_context`, `test_unknown_subagent`) run through the full harness, so labs 02-04 must already pass.

### TODO 09.1 · `forja/subagents.py` · `load_profiles(folder: Path) -> dict[str, AgentProfile]`

**What it must do:** Receives the agents folder (it may not exist). Returns a dict `name -> AgentProfile` that ALWAYS contains the built-in `explore` profile (start from a copy of `BUILTIN`, never mutate `BUILTIN` itself). For each `*.md` file with valid frontmatter that has both `name` and `description`, add `AgentProfile(name, description, system=<body stripped>, tools=<list[str]>, max_steps=<int, default 25>)`. Files without frontmatter or missing `name`/`description` are skipped silently. The test checks: `set(p) == {"explore", "reviewer"}`, `tools == ["read_file", "grep"]` (from the string `read_file, grep`), `max_steps == 5`, `system == "You are a reviewer."`, and that a missing folder returns exactly `BUILTIN`.

**Steps:**
1. Create `profiles = dict(BUILTIN)`; if the folder is not a directory, return it right away.
2. Loop over the `*.md` files in a stable order (`sorted`). Read each one as UTF-8 and apply `FRONTMATTER.match`.
3. No match → skip. Match → `yaml.safe_load(group 1)`, and treat `None` as `{}`.
4. Skip if `name` or `description` is missing or empty.
5. Normalise `tools`: default `["read_file", "grep", "glob"]`; if it is a string, split on commas and strip each item, dropping empties; if it is already a list, keep it.
6. Build the profile: the body (group 2) `.strip()`ped is the system prompt; `max_steps` via `int(...)` with default 25. Store it under its `name` (a file can override `explore` if it uses that name).

**Watch out for:**
- Returning `BUILTIN` itself and then adding to it mutates the module constant: the next test (`load_profiles(missing) == BUILTIN`) or the next harness instance will see stale profiles. Copy it.
- `tools: read_file, grep` is the string `'read_file, grep'`. Forgetting to split gives `['r','e','a',...]` if you iterate it, or a single unknown tool name — and `subset()` silently drops unknown names, so the subagent ends up with NO tools.
- `system` must be the body *without* the frontmatter and stripped: the test compares it exactly.
- `yaml.safe_load` on a frontmatter that only contains comments returns `None`: `.get` on it raises `AttributeError`.

<details><summary>💡 Hint 1</summary>

It is the same "frontmatter + body" parsing you will do again for skills in lab 10. The regex is already compiled for you.

</details>

<details><summary>💡 Hint 2</summary>

`m = FRONTMATTER.match(text)`; `meta = yaml.safe_load(m.group(1)) or {}`; `m.group(2).strip()` is the system prompt. `isinstance(tools, str)` tells you when to split.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
profiles = dict(BUILTIN)
if not folder.is_dir(): return profiles
for f in sorted(folder.glob("*.md")):
    m = ...            # FRONTMATTER.match on the file text
    if not m: continue
    meta = ...         # yaml, never None
    if <missing name or description>: continue
    tools = ...        # default list; split 'a, b' strings
    profiles[meta["name"]] = AgentProfile(...)
return profiles
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l09_subagents.py -k load_profiles -v
```

### TODO 09.2 · `forja/subagents.py` · `make_task_tool(...)` → inner tool `task(description, prompt, subagent_type="explore") -> str`

**What it must do:** `make_task_tool` is already written except the body of `task`. Inside `task`: look up `profiles[subagent_type]`; if it does not exist raise `ValueError` whose message contains `unknown` and lists the available names (the registry turns it into a failed tool result; `test_unknown_subagent` checks `"unknown"` is in it). Build the subagent's registry with `parent_tools.subset(...)` using the profile's tools MINUS `"task"`. Create an `Agent` with the same `llm`, that sub-registry, `execute=execute`, `max_steps=prof.max_steps` and `events=events_factory(prof.name)` if a factory was given, else `Events()`. Run it on a BRAND-NEW list `[{"role": "system", "content": prof.system}, {"role": "user", "content": prompt}]`. Return a header that contains `subagent <name>` (the test looks for `"subagent explore"`), e.g. `[subagent explore · <description> · N steps · M tools · <stop_reason>]`, then a newline and `res.answer`. The test also checks that the subagent's first LLM call had exactly 2 messages starting with the explore system prompt, that it was offered exactly `{read_file, grep, glob}`, and that the main history only contains ONE tool message (`task`).

**Steps:**
1. Look up the profile; if missing, `raise ValueError(f"unknown subagent: ... Available: ...")`.
2. Compute the allowed tool names: the profile's `tools` without `"task"` (no recursion).
3. `sub_tools = parent_tools.subset(those names)`.
4. Pick the events object: `events_factory(prof.name)` when the factory is not `None`, otherwise `Events()`. In the CLI this factory prints the subagent's tool calls with the `[explore]` prefix.
5. Wrap `execute` in a small `sub_execute(call)`: if `call.name` is not in `sub_tools.tools`, return `ToolResult(call.id, call.name, False, "ERROR: tool '...' is not available to subagent '...'")`; otherwise delegate to `execute` (or `sub_tools.execute` when `execute` is `None`). The schema list only *offers* tools; the model can still call others.
6. Create the `Agent` (same `llm`, `execute=sub_execute`, `max_steps=prof.max_steps`) and call `run` with a NEW two-message list.
7. Format and return the header line + the subagent's `answer` (use `res.steps`, `res.tool_calls`, `res.stop_reason`).

**Watch out for:**
- Reusing or copying the parent's history: the subagent must start clean (`len(messages) == 2` on its first call).
- Passing `parent_tools` instead of the subset: the subagent would get `write_file`, `bash`, `task`… and `test_task_isolated_context` fails on the tool set.
- Forgetting to route through `execute`: the subagent would bypass the gate (no permissions, no hooks, no checkpoints).
- Trusting the offered tool list: `test_subagent_cannot_use_tools_outside_its_profile` makes the model call `write_file` from `explore`; your wrapper must refuse it and the file must not exist.
- The same `FakeLLM` serves main agent and subagent in call order: if your `task` makes an extra LLM call (or none), every scripted reply shifts and the assertions fail in confusing ways.
- Do not touch `task.description`: it is set after the function and includes the catalogue the model reads to choose a subagent.

<details><summary>💡 Hint 1</summary>

The whole subagent is just lab 03's `Agent` with a smaller registry and a fresh message list.

</details>

<details><summary>💡 Hint 2</summary>

`parent_tools.subset([t for t in prof.tools if t != "task"])`; `Agent(llm, sub_tools, execute=sub_execute, max_steps=..., events=...)`; `res = agent.run(messages)`.

</details>

<details><summary>💡 Hint 3 · skeleton</summary>

```python
prof = profiles.get(subagent_type)
if prof is None: raise ValueError(...)  # 'unknown', list names
sub_tools = ...                 # subset, never 'task'
def sub_execute(call): ...     # refuse names not in sub_tools.tools
events = ...                    # factory(name) or Events()
agent = Agent(...)
res = agent.run([...])         # system + user ONLY
return f"[subagent {prof.name} · ...]\n{res.answer}"
```

</details>

**Check just this TODO:**
```bash
python -m pytest tests/test_l09_subagents.py -k "task_isolated or unknown_subagent or outside_its_profile" -v
```

## Run
```bash
python scripts/tasks.py test 09
cp -r examples/project/.forja playground/      # Windows: xcopy /E /I examples\project\.forja playground\.forja
forja --cwd playground
> use a subagent to find every place where amounts are rounded
> ask the reviewer subagent to review my uncommitted changes
```

## Try it in your agent
1. Copy the example project config into the playground. macOS/Linux: `cp -r examples/project/.forja playground/` · PowerShell: `Copy-Item -Recurse examples\project\.forja playground\.forja` · cmd: `xcopy /E /I examples\project\.forja playground\.forja`.
2. `forja --cwd playground`, then `/tools`: you should see `task [read]` at the end of the list, and no `subagents: lab 09 pending` note at startup.
3. Type `use a subagent to find every place where amounts are rounded`. Expected: `⏺ task …`, then indented lines `  [explore] ⏺ grep …` / `  [explore] ⏺ read_file …` (the subagent's calls; its text is not streamed), and finally the main agent's answer listing `path:line` locations.
4. Run `/context` before and after: the main context grows by a few hundred tokens, not by the size of every file the subagent read.
5. Edit something in `playground/invoices/` by hand, then: `ask the reviewer subagent to review my uncommitted changes`. You should see `  [reviewer] ⏺ bash git diff …` (allowed by `bash(git diff*)` in settings) and a review with numbered sections.

## If something goes wrong
| Symptom | Cause → fix |
|---|---|
| `test_task_isolated_context` fails with `StopIteration` / FakeLLM 'no more responses' | Your `task` calls the LLM a different number of times (e.g. you ran `agent.run` twice, or the main loop from lab 03 is broken) → one `Agent.run` per task call; run `tests/test_l03_agent.py` first. |
| Assertion on `{t['function']['name'] ...} == {'read_file','grep','glob'}` | You passed the whole parent registry, or included `task` → use `parent_tools.subset(...)` with `task` filtered out. |
| Subagent has no tools / answers without reading anything | In 09.1 `tools` was not split (string `'read_file, grep'`), so `subset()` dropped every name → split on commas and strip. |
| `reviewer` does not appear in the `task` description / 'unknown subagent: reviewer' | The profile file has no `---` frontmatter on the very first line, or lacks `description` → fix the file; profiles are read from `<project>/.forja/agents/`, so check you copied `.forja` into `playground/`. |
| No `[explore]` prefix in the CLI, subagent calls look like main calls | You ignored `events_factory` and always used `Events()` (then you see nothing) or passed the main events → use `events_factory(prof.name)` when it is not `None`. |
| The small model never delegates | 8B models often prefer doing it themselves → ask explicitly ('use a subagent…'); the `task` description is all it reads to decide. |
| Windows: `cp -r` fails in cmd.exe | `cp` only exists in PowerShell (as an alias) → use `xcopy /E /I examples\project\.forja playground\.forja` in cmd. |

## You're done when
- [ ] [ ] `python scripts/tasks.py test 09` → 3 passed.
- [ ] [ ] In the CLI you see `[explore]`-prefixed tool calls and `/context` barely grows after a delegated search.
- [ ] [ ] The `reviewer` profile from `.forja/agents/` is listed in the `task` tool description and can be invoked by name.

## Checkpoint
You see the subagent's tool calls prefixed `[explore]` and the main context barely grows (`/context`).

## Challenges
1. Create a `tester` subagent that can only run `python -m pytest*`.
2. Run the subagent on a smaller, faster model.

**Tests:** `tests/test_l09_subagents.py` · **Fallen behind?** `python scripts/tasks.py catchup 10`

---
[← previous](../L08_planning/README.md) · [next →](../L10_extensions/README.md)
