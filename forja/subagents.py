"""LAB 09 — Subagents: delegate with a clean context.

Exploring a repo to answer "where is VAT calculated?" can cost 20 reads and
30k tokens. If the main agent does it, those reads stay in ITS context forever.
A subagent does the exploration in its own context and returns only the
conclusion: the main agent pays ~300 tokens.

Subagent profiles: Markdown files with frontmatter in .forja/agents/*.md
    ---
    name: reviewer
    description: Reviews a diff looking for bugs and style problems.
    tools: read_file, grep, glob
    ---
    You are a demanding code reviewer…
"""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .agent import Agent, Events
from .tools import Tool, ToolRegistry, ToolResult, tool
from .types import ChatModel, ToolCall

EXPLORE = """You are a code exploration subagent. Your job is to investigate the repository with read_file, grep and glob
and return a concrete answer for the task you are given. You do NOT modify anything.
Answer with: a 2-4 sentence conclusion + a list of relevant files with lines (path:line) + key snippets if they help."""


@dataclass
class AgentProfile:
    name: str
    description: str
    system: str
    tools: list[str] = field(default_factory=list)
    max_steps: int = 25


BUILTIN = {"explore": AgentProfile("explore", "Explores the code (read-only) and answers questions about it: where X is, how Y works.",
                                   EXPLORE, ["read_file", "grep", "glob"])}
FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.S)


# ---- TODO 09.1 : load profiles from Markdown with frontmatter ------------------
def load_profiles(folder: Path) -> dict[str, AgentProfile]:
    # TODO 09.1: Start with dict(BUILTIN). For each *.md in the folder (if it exists): FRONTMATTER.match; yaml.safe_load the frontmatter; require name and description; tools may be a list or 'a, b'; max_steps optional. The body is the system prompt.
    raise NotImplementedError("TODO 09.1")


# ---- TODO 09.2 : the `task` tool that launches a subagent -----------------------
def make_task_tool(llm: ChatModel, parent_tools: ToolRegistry, profiles: dict[str, AgentProfile],
                   execute: Callable[[ToolCall], ToolResult] | None = None, events_factory: Callable[[str], Events] | None = None) -> Tool:
    catalog = "\n".join(f"- {p.name}: {p.description}" for p in profiles.values())

    @tool(risk="read")
    def task(description: str, prompt: str, subagent_type: str = "explore") -> str:
        """placeholder"""
        # TODO 09.2: Look up the profile (ValueError if missing). sub_tools = parent_tools.subset(the profile's tools, without 'task'). Wrap execute so a call to a tool NOT in sub_tools returns ToolResult(ok=False, 'ERROR: tool ... is not available to subagent ...') instead of running. Agent(llm, sub_tools, execute=<wrapper>, max_steps, events=events_factory(name) or Events()). NEW messages: [profile system, user prompt]. Return '[subagent …] ' + the answer.
        raise NotImplementedError("TODO 09.2")

    task.description = ("Launches a subagent with its own context for a self-contained task (especially code searches and "
                        "exploration that need many reads). Returns only its conclusion. Write a complete prompt: "
                        "the subagent does not see this conversation.\nAvailable subagents:\n" + catalog)
    return task
