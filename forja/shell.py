"""LAB 04a — La tool bash: el poder (y el riesgo) de un agente de código.

Con bash el agente ejecuta tests, instala dependencias, usa git… y también podría
borrar tu disco. Esta tool solo ejecuta: QUIÉN puede ejecutar QUÉ lo decide permissions.py.

Decisiones de diseño:
  * cwd = raíz del workspace en cada llamada ("fresh exec"): `cd` no persiste. Predecible.
  * timeout duro; salida truncada por cabeza y cola (los errores suelen estar al final).
  * entorno saneado: no heredamos secretos (*_KEY, *_TOKEN, *_SECRET).
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
    env["PAGER"] = "cat"  # sin paginadores interactivos
    env["GIT_PAGER"] = "cat"
    env["PYTHONUNBUFFERED"] = "1"
    return env


# ---- TODO 04.1 : truncar por cabeza y cola ---------------------------------
def head_tail(text: str, limit: int = MAX_SHELL_OUTPUT) -> str:
    # TODO 04.1: Si cabe, tal cual. Si no: 1/4 del límite del principio + 3/4 del final, con un aviso de cuántos caracteres se omiten en medio.
    raise NotImplementedError("TODO 04.1")


def make_shell_tool(ws: Workspace, default_timeout: int = 120) -> Tool:
    # ---- TODO 04.2 : ejecutar con timeout y salida combinada ------------
    @tool(risk="exec")
    def bash(command: str, timeout: int = default_timeout) -> ToolOutput:
        """Ejecuta un comando de shell en la raíz del proyecto (cada llamada empieza ahí: `cd` no persiste,
        encadena con `&&`). Úsalo para tests, git, instalar dependencias o ejecutar scripts.
        No lo uses para leer o buscar ficheros: para eso tienes read_file, grep y glob.

        Args:
            command: Comando a ejecutar.
            timeout: Segundos máximos (por defecto 120, máximo 600).
        """
        # TODO 04.2: subprocess.run(command, shell=True, cwd=ws.root, capture_output, text, timeout (1..600), env=clean_env(), stdin=DEVNULL). TimeoutExpired -> 'TIMEOUT tras Ns'. Devuelve ToolOutput('exit_code=N\n' + head_tail(stdout + [stderr]), {'exit_code': N}).
        raise NotImplementedError("TODO 04.2")

    shell = "cmd.exe (Windows: usa sintaxis de cmd o invoca `powershell -Command ...`)" if os.name == "nt" else "/bin/sh"
    bash.description += f"\nShell del sistema: {shell}."
    return bash
