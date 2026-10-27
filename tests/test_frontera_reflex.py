"""Comprobación de frontera de capas."""

from __future__ import annotations

import ast
from pathlib import Path


def test_no_modulos_reservas_importan_reflex():
    base = Path("src") / "reservas"
    for pyfile in base.rglob("*.py"):
        contenido = pyfile.read_text(encoding="utf-8")
        tree = ast.parse(contenido)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("reflex"):
                        raise AssertionError(f"{pyfile} importa reflex")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("reflex"):
                    raise AssertionError(f"{pyfile} importa reflex")
    assert True
