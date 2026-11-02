"""Configuración de Forja (DADO — no es un TODO).

* Backends: Ollama local, vLLM/LM Studio (cualquier endpoint OpenAI-compatible) y OpenRouter.
* Política: solo modelos open-weight. Se bloquean ids de Anthropic y OpenAI en código.
* Settings en capas: ~/.forja/settings.json (usuario) + <proyecto>/.forja/settings.json.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

BLOCKED_MODEL_PATTERNS = ("anthropic/", "openai/", "~anthropic", "~openai", "claude", "gpt-", "gpt-oss", "codex", "o1", "o3", "o4")


class ModelPolicyError(ValueError):
    """Se intentó usar un modelo fuera de la política del workshop (solo open-weight)."""


def check_model_allowed(model: str) -> str:
    m = model.lower().strip()
    name = m.split("/", 1)[-1]
    for pat in BLOCKED_MODEL_PATTERNS:
        if len(pat) <= 2:
            if name == pat or name.startswith((pat + "-", pat + ":")):
                raise ModelPolicyError(f"modelo '{model}' bloqueado por política (solo open-weight)")
        elif pat in m:
            raise ModelPolicyError(f"modelo '{model}' bloqueado por política (solo open-weight)")
    return model


@dataclass(frozen=True)
class Backend:
    name: str
    base_url: str
    api_key: str
    model: str
    extra_headers: dict[str, str] = field(default_factory=dict)
    extra_body: dict = field(default_factory=dict)


def backend_from_env(kind: str | None = None, model: str | None = None) -> Backend:
    """FORJA_BACKEND = ollama | openai_compat | openrouter."""
    kind = kind or os.getenv("FORJA_BACKEND", "ollama")
    if kind == "ollama":
        return Backend("ollama", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"), "ollama",
                       check_model_allowed(model or os.getenv("FORJA_MODEL", "qwen3:8b")))
    if kind == "openai_compat":  # vLLM, LM Studio, llama.cpp server, LiteLLM…
        return Backend("openai_compat", os.environ["FORJA_BASE_URL"], os.getenv("FORJA_API_KEY", "x"),
                       check_model_allowed(model or os.environ["FORJA_MODEL"]))
    if kind == "openrouter":
        return Backend("openrouter", "https://openrouter.ai/api/v1", os.getenv("OPENROUTER_API_KEY", ""),
                       check_model_allowed(model or os.getenv("FORJA_MODEL", "deepseek/deepseek-v3.2")),
                       extra_headers={"X-Title": "forja-workshop"}, extra_body={"provider": {"data_collection": "deny"}})
    raise ValueError(f"backend desconocido: {kind}")


DEFAULT_DENY = [
    "bash(sudo *)", "bash(rm -rf /*)", "bash(rm -rf ~*)", "bash(*| sh*)", "bash(*| bash*)",
    "bash(git push*--force*)", "bash(mkfs*)", "bash(dd *of=/dev/*)", "bash(*> /dev/sd*)",
]


@dataclass
class Settings:
    allow: list[str] = field(default_factory=list)
    deny: list[str] = field(default_factory=lambda: list(DEFAULT_DENY))
    hooks: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    mcp_servers: dict[str, dict[str, Any]] = field(default_factory=dict)
    context_window: int = 32768
    max_steps: int = 40

    @classmethod
    def load(cls, project_root: Path, home: Path | None = None) -> Settings:
        s = cls()
        for p in [(home or Path.home()) / ".forja" / "settings.json", project_root / ".forja" / "settings.json"]:
            if not p.is_file():
                continue
            d = json.loads(p.read_text(encoding="utf-8"))
            perms = d.get("permissions", {})
            s.allow += perms.get("allow", [])
            s.deny += perms.get("deny", [])
            for ev, items in d.get("hooks", {}).items():
                s.hooks.setdefault(ev, []).extend(items)
            s.mcp_servers.update(d.get("mcpServers", {}))
            s.context_window = d.get("contextWindow", s.context_window)
            s.max_steps = d.get("maxSteps", s.max_steps)
        return s
