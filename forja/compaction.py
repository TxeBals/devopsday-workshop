"""LAB 07 — Context management: fitting a long session into a small window.

A typical local model works with 16–32k tokens. A coding agent fills them fast:
every read_file, every pytest output… Two levels, from cheapest to most expensive:

  1. Microcompaction (no LLM): blank OLD tool outputs. The model already used them;
     if it needs them, it can read the file again.
  2. Full compaction (1 LLM call): summarise the old turns and keep the recent ones.

Sacred invariant: never separate an assistant message with tool_calls from its tool messages.
Only cut right before a 'user' message.
"""
from __future__ import annotations

import json
from typing import Any

from .types import ChatModel

SUMMARY_PROMPT = """Summarise this coding-agent work session so it can be continued without the history.
Include, in this order and without inventing anything:
1. The user's goal and explicit requests.
2. Relevant files and what was changed in each (exact paths).
3. Commands run and their results (passing/failing tests, important errors).
4. Decisions taken and why.
5. Pending tasks and the next step.
300 words maximum."""

CLEARED = "[old tool result cleared]"


def estimate_tokens(messages: list[dict[str, Any]]) -> int:
    """~4 characters per token. Cheap and good enough to decide when to compact."""
    return sum(len(json.dumps(m, ensure_ascii=False)) for m in messages) // 4


def user_turn_starts(history: list[dict[str, Any]]) -> list[int]:
    return [i for i, m in enumerate(history) if m["role"] == "user"]


# ---- TODO 07.1 : microcompaction -----------------------------------------
def microcompact(history: list[dict[str, Any]], keep_recent_turns: int = 2, min_chars: int = 500) -> int:
    """Blanks (in place) long tool outputs older than the last `keep_recent_turns` turns.
    Returns how many were blanked."""
    # TODO 07.1: starts = user_turn_starts(history). If there are <= keep_recent_turns turns, 0. Otherwise, for the messages BEFORE starts[-keep_recent_turns]: 'tool' messages with content >= min_chars not yet cleared -> content = CLEARED. Return how many.
    raise NotImplementedError("TODO 07.1")


# ---- TODO 07.2 : full compaction with a summary ------------------------------
def compact(history: list[dict[str, Any]], llm: ChatModel, keep_recent_turns: int = 2) -> tuple[list[dict[str, Any]], bool]:
    """Returns (new_history, compacted?). Summarises everything before the last turns."""
    # TODO 07.2: Cut ONLY at the start of a user turn, keeping keep_recent_turns turns. Turn the old part into text (role, content, tools called, truncated results), ask for the summary with SUMMARY_PROMPT (temperature=0) and return ([user: '[Summary of the previous session]\n…', assistant: ack, *recent], True).
    raise NotImplementedError("TODO 07.2")


def should_compact(system: str, history: list[dict[str, Any]], window: int, threshold: float = 0.8) -> bool:
    return estimate_tokens([{"role": "system", "content": system}, *history]) > window * threshold
