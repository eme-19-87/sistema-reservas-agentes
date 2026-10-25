"""Carga del inventario desde data/inventario.json (solo lectura)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ruta_inventario() -> Path:
    """Ruta por defecto al inventario."""
    return Path("data") / "inventario.json"


def cargar_inventario(ruta: Path | None = None) -> list[dict[str, Any]]:
    """Carga el inventario. Devuelve una lista de unidades."""
    ruta_efectiva = ruta if ruta is not None else ruta_inventario()
    with ruta_efectiva.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return datos


def obtener_inventario() -> dict[str, dict[str, Any]]:
    """Devuelve el inventario indexado por id de unidad."""
    inventario = cargar_inventario()
    resultado: dict[str, dict[str, Any]] = {}
    for unidad in inventario:
        if isinstance(unidad, dict) and "id" in unidad:
            resultado[str(unidad["id"])] = unidad
    return resultado
