"""LAB 04a — The bash tool: the power (and the risk) of a coding agent.

With bash the agent runs tests, installs dependencies, uses git… and could also
wipe your disk. This tool only executes: WHO may run WHAT is decided by permissions.py.

Design decisions:
  * cwd = workspace root on every call ("fresh exec"): `cd` doesn't persist. Predictable.
  * hard timeout; output truncated head and tail (errors are usually at the end).
  * sanitised environment: we don't inherit secrets (*_KEY, *_TOKEN, *_SECRET).
"""
from __future__ import annotations

import os
import re
import subprocess

from .fs_tools import Workspace
from .tools import Tool, ToolOutput, tool

SECRET_ENV = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL)", re.I)
MAX_SHELL_OUTPUT = 20_000


def clean_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not SECRET_ENV.search(k)}
    env["PAGER"] = "cat"  # no interactive pagers
    env["GIT_PAGER"] = "cat"
    env["PYTHONUNBUFFERED"] = "1"
    return env


# ---- TODO 04.1 : truncate head and tail ------------------------------------
def head_tail(text: str, limit: int = MAX_SHELL_OUTPUT) -> str:
    # TODO 04.1: If it fits, unchanged. Otherwise: 1/4 of the limit from the start + 3/4 from the end, with a note saying how many characters are omitted in the middle.
    raise NotImplementedError("TODO 04.1")


def make_shell_tool(ws: Workspace, default_timeout: int = 120) -> Tool:
    # ---- TODO 04.2 : run with timeout and combined output --------------
    @tool(risk="exec")
    def bash(command: str, timeout: int = default_timeout) -> ToolOutput:
        """Runs a shell command at the project root (every call starts there: `cd` doesn't persist,
        chain with `&&`). Use it for tests, git, installing dependencies or running scripts.
        Don't use it to read or search files: use read_file, grep and glob for that.

        Args:
            command: Command to run.
            timeout: Maximum seconds (default 120, maximum 600).
        """
        # TODO 04.2: subprocess.run(command, shell=True, cwd=ws.root, capture_output, text, encoding='utf-8', errors='replace', timeout (1..600), env=clean_env(), stdin=DEVNULL). TimeoutExpired -> 'TIMEOUT after Ns'. Return ToolOutput('exit_code=N\n' + head_tail(stdout + [stderr]), {'exit_code': N}).
        raise NotImplementedError("TODO 04.2")

    shell = "cmd.exe (Windows: use cmd syntax or invoke `powershell -Command ...`)" if os.name == "nt" else "/bin/sh"
    bash.description += f"\nShell: {shell}."
    return bash
