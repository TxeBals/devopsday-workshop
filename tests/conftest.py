"""Por defecto los tests validan TU código (forja/ en la raíz).
Para validar la solución de referencia:  FORJA_SOLUTIONS=1 pytest"""
import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "solutions") if os.getenv("FORJA_SOLUTIONS") == "1" else str(ROOT))


@pytest.fixture()
def project(tmp_path):
    """Copia limpia del proyecto de prácticas."""
    dst = tmp_path / "proyecto"
    shutil.copytree(ROOT / "playground", dst, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", ".forja"))
    return dst


@pytest.fixture()
def home(tmp_path):
    h = tmp_path / "home"
    h.mkdir()
    return h
