"""¿Te has quedado atrás? Copia las soluciones de los labs ANTERIORES al que indiques.

Las soluciones NO están en el repo: el tutor te pasa `forja-solutions.zip` cuando lo necesites.
Déjalo en la raíz del repo (o indica dónde está con --from).

    python scripts/catchup.py 05                      # resuelve 01-04 y tú sigues con el 05
    python scripts/catchup.py 05 --from D:/forja-solutions.zip
    python scripts/catchup.py 05 --dry-run
    python scripts/catchup.py end                     # todo resuelto

Antes de sobrescribir guarda tus ficheros en .catchup_backup/<hora>/.
"""
from __future__ import annotations

import argparse
import shutil
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB_FILES = {
    "01": ["llm.py"],
    "02": ["tools.py", "fs_tools.py"],
    "03": ["agent.py"],
    "04": ["shell.py", "permissions.py"],
    "05": ["cli.py"],
    "06": ["context.py"],
    "07": ["compaction.py"],
    "08": ["planning.py"],
    "09": ["subagents.py"],
    "10": ["hooks.py", "skills.py", "mcp_tools.py"],
    "11": ["session.py"],
    "12": ["evals.py"],
}
ORDER = list(LAB_FILES) + ["end"]


def find_source(explicit: str | None):
    """Devuelve una función nombre_fichero -> bytes, buscando las soluciones en este orden:
    --from, $FORJA_SOLUTIONS_SRC, ./forja-solutions.zip, ./solutions/forja/."""
    import os
    candidates = [explicit, os.getenv("FORJA_SOLUTIONS_SRC"), str(ROOT / "forja-solutions.zip"), str(ROOT / "solutions" / "forja")]
    for c in candidates:
        if not c:
            continue
        p = Path(c)
        if p.is_file() and p.suffix == ".zip":
            z = zipfile.ZipFile(p)
            names = {Path(n).name: n for n in z.namelist() if n.endswith(".py")}
            return str(p), lambda f: z.read(names[f])
        if p.is_dir():
            d = p / "forja" if (p / "forja").is_dir() else p
            return str(d), lambda f: (d / f).read_bytes()
    raise SystemExit("No encuentro las soluciones. Pide al tutor `forja-solutions.zip` y déjalo en la raíz "
                     "del repo, o usa --from <ruta al zip o carpeta>.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("lab", help="lab en el que empiezas (01-12) o 'end'")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--from", dest="src", help="zip o carpeta con las soluciones")
    a = ap.parse_args()
    target = a.lab.zfill(2) if a.lab.isdigit() else a.lab.lower()
    if target not in ORDER:
        raise SystemExit(f"lab desconocido: {a.lab}. Opciones: {', '.join(ORDER)}")
    where, read = find_source(a.src)
    print(f"soluciones: {where}")
    backup = ROOT / ".catchup_backup" / time.strftime("%H%M%S")
    for lab in ORDER[: ORDER.index(target)]:
        for f in LAB_FILES[lab]:
            dst = ROOT / "forja" / f
            print(f"lab {lab}: {f} -> {dst.relative_to(ROOT)}")
            if a.dry_run:
                continue
            backup.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                shutil.copy2(dst, backup / f)
            dst.write_bytes(read(f))
    if backup.exists():
        print(f"tus versiones anteriores: {backup.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
