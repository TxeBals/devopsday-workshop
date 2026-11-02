# Lab 11 · Sessions and undo

Day 2 · 14:20–14:55

**Goal:** Resume sessions and undo what the agent did without relying on git.

## Concepts
- **Append-only JSONL transcript:** one message per line in `.forja/sessions/`. Resume, audit and debug. After compaction, a marker with the new state.
- **Checkpoints:** before a tool modifies a file, its original content (or that it didn't exist) is saved — only the first time per turn.
- **/undo:** restores the files from the last turn with changes. Works without git and doesn't touch your commits.
- **Limit:** `bash` side effects (installing packages, `rm`) can't be undone. That's why bash goes through permissions.

## What you implement
| TODO | File | What |
|---|---|---|
| 11.1 | `forja/session.py` | Transcript.append |
| 11.2 | `forja/session.py` | Transcript.load (with compaction markers) |
| 11.3 | `forja/session.py` | Checkpoints.before_write |
| 11.4 | `forja/session.py` | Checkpoints.undo |

## Run
```bash
python scripts/tasks.py test 11
forja --cwd playground --mode accept_edits
> change the default due-date period to 60 days
/undo
/sessions
forja --cwd playground --resume <id>
```

## Checkpoint
`/undo` restores the file and `--resume` continues the previous conversation.

## Challenges
1. `/undo N` to undo several turns.
2. `/rewind`: undo files AND roll history back to the same point.

**Tests:** `tests/test_l11_sessions.py` · **Fallen behind?** `python scripts/tasks.py catchup 12`

---
[← previous](../L10_extensions/README.md) · [next →](../L12_evals/README.md)
