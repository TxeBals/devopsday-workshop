"""LAB 07 — Gestión de contexto: que una sesión larga quepa en una ventana pequeña.

Un modelo local típico trabaja con 16–32k tokens. Un agente de código los llena rápido:
cada read_file, cada salida de pytest… Dos niveles, del más barato al más caro:

  1. Microcompactación (sin LLM): vaciar las salidas de tools ANTIGUAS. El modelo ya las usó;
     si las necesita, puede volver a leer el fichero.
  2. Compactación completa (1 llamada al LLM): resumir los turnos antiguos y conservar los recientes.

Invariante sagrado: nunca separar un mensaje assistant con tool_calls de sus mensajes tool.
Solo se corta justo antes de un mensaje 'user'.
"""
from __future__ import annotations

import json
from typing import Any

from .types import ChatModel

SUMMARY_PROMPT = """Resume esta sesión de trabajo de un agente de código para poder continuarla sin el historial.
Incluye, en este orden y sin inventar nada:
1. Objetivo del usuario y peticiones explícitas.
2. Ficheros relevantes y qué se ha cambiado en cada uno (rutas exactas).
3. Comandos ejecutados y su resultado (tests que pasan/fallan, errores importantes).
4. Decisiones tomadas y por qué.
5. Tareas pendientes y siguiente paso.
Máximo 300 palabras."""

CLEARED = "[salida antigua eliminada para ahorrar contexto; vuelve a ejecutar la tool si la necesitas]"


def estimate_tokens(messages: list[dict[str, Any]]) -> int:
    """~4 caracteres por token. Barato y suficiente para decidir cuándo compactar."""
    return sum(len(json.dumps(m, ensure_ascii=False)) for m in messages) // 4


def user_turn_starts(history: list[dict[str, Any]]) -> list[int]:
    return [i for i, m in enumerate(history) if m["role"] == "user"]


# ---- TODO 07.1 : microcompactación ---------------------------------------
def microcompact(history: list[dict[str, Any]], keep_recent_turns: int = 2, min_chars: int = 500) -> int:
    """Vacía (en sitio) las salidas de tools largas anteriores a los últimos `keep_recent_turns` turnos.
    Devuelve cuántas ha vaciado."""
    # TODO 07.1: starts = user_turn_starts(history). Si hay <= keep_recent_turns turnos, 0. Si no, para los mensajes ANTERIORES a starts[-keep_recent_turns]: los 'tool' con contenido >= min_chars y no vaciados -> content = CLEARED. Devuelve cuántos.
    raise NotImplementedError("TODO 07.1")


# ---- TODO 07.2 : compactación completa con resumen ---------------------------
def compact(history: list[dict[str, Any]], llm: ChatModel, keep_recent_turns: int = 2) -> tuple[list[dict[str, Any]], bool]:
    """Devuelve (nuevo_historial, compactado?). Resume todo lo anterior a los últimos turnos."""
    # TODO 07.2: Corta SOLO en un inicio de turno de usuario dejando keep_recent_turns turnos. Convierte lo antiguo en texto (rol, contenido, tools llamadas, resultados truncados), pide el resumen con SUMMARY_PROMPT (temperature=0) y devuelve ([user: '[Resumen de la sesión anterior]\n…', assistant: ack, *recientes], True).
    raise NotImplementedError("TODO 07.2")


def should_compact(system: str, history: list[dict[str, Any]], window: int, threshold: float = 0.8) -> bool:
    return estimate_tokens([{"role": "system", "content": system}, *history]) > window * threshold
