"""LAB 10a — Hooks: deterministic policy around a probabilistic model.

AGENTS.md *asks* ("run the tests"); a hook *guarantees*. Hooks are shell commands
configured in .forja/settings.json that the harness runs at fixed points:

    PreToolUse        before running a tool                 exit 2 => BLOCKED (stderr goes to the model)
    PostToolUse       after running it                      exit 2 => stderr is appended to the result (feedback)
    UserPromptSubmit  when a message is sent                exit 2 => blocked; stdout is added as context
    Stop              when the agent thinks it is done      exit 2 => keeps working with stderr as guidance

Each hook receives a JSON with the event on stdin. Exit 0 = all good; exit 2 = block;
any other code = hook error (reported, doesn't block). It's the convention commercial
coding agents already use: once you know it, it works in all of them.

    "hooks": {
      "PreToolUse":  [{"matcher": "bash", "command": "python .forja/hooks/no_secrets.py"}],
      "PostToolUse": [{"matcher": "edit_file|write_file", "command": "ruff check --quiet ."}],
      "Stop":        [{"command": "pytest -q -x"}]
    }
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

EVENTS = ("PreToolUse", "PostToolUse", "UserPromptSubmit", "Stop")


@dataclass
class HookOutcome:
    block: bool = False
    message: str = ""  # stderr (block / feedback)
    context: str = ""  # useful stdout (UserPromptSubmit)
    errors: list[str] = field(default_factory=list)


@dataclass
class HookRunner:
    config: dict[str, list[dict[str, Any]]]
    cwd: Path
    timeout: int = 60

    # ---- TODO 10.1 : select hooks by event and matcher -------------------------
    def matching(self, event: str, tool_name: str | None = None) -> list[dict[str, Any]]:
        # TODO 10.1: From self.config[event]: no matcher -> always; with a matcher -> only if there is a tool_name and re.fullmatch(matcher, tool_name).
        raise NotImplementedError("TODO 10.1")

    # ---- TODO 10.2 : run and map exit codes -------------------------------------
    def run(self, event: str, payload: dict[str, Any], tool_name: str | None = None) -> HookOutcome:
        # TODO 10.2: Serialise {'hook_event_name', 'cwd', **payload} to JSON. For each matching hook: subprocess.run(command, shell=True, cwd, input=json, capture_output, text, timeout). Exit 2 -> block=True and accumulate stderr (or stdout) in message. Exit 0 -> stdout to context. Other -> errors. TimeoutExpired -> errors.
        raise NotImplementedError("TODO 10.2")
