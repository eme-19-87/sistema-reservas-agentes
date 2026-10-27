"""Repositorio SQLite para unidades y reservas."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

from .inventario import cargar_inventario


def ruta_bd() -> Path:
    """Ruta a la base de datos SQLite."""
    ruta_env = os.environ.get("RESERVAS_DB")
    if ruta_env:
        return Path(ruta_env)
    return Path("data") / "reservas.db"


def obtener_conexion(ruta: Path | str | None = None) -> sqlite3.Connection:
    """Obtiene una conexión con claves foráneas activadas."""
    if ruta is None:
        ruta = ruta_bd()
    conn = sqlite3.connect(str(ruta))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


ESQUEMA_SQL = """
CREATE TABLE IF NOT EXISTS unidades (
  id TEXT PRIMARY KEY,
  equipo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reservas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unidad_id TEXT NOT NULL REFERENCES unidades(id),
  solicitante TEXT NOT NULL,
  inicio TEXT NOT NULL,
  fin TEXT NOT NULL,
  estado TEXT NOT NULL CHECK (estado IN ('ACTIVA','CANCELADA')),
  creada_en TEXT NOT NULL,
  cancelada_en TEXT,
  CHECK (inicio < fin)
);

CREATE INDEX IF NOT EXISTS idx_reservas_unidad_estado
ON reservas(unidad_id, estado, inicio);
"""


def crear_esquema(conn: sqlite3.Connection) -> None:
    """Crea el esquema si no existe."""
    conn.executescript(ESQUEMA_SQL)
    conn.commit()


def sembrar_unidades(
    conn: sqlite3.Connection, inventario: list[dict[str, Any]] | None = None
) -> None:
    """Siembra las unidades desde el inventario de forma idempotente."""
    if inventario is None:
        inventario = cargar_inventario()
    for unidad in inventario:
        if not isinstance(unidad, dict):
            continue
        unidad_id = unidad.get("id")
        equipo = unidad.get("equipo")
        if unidad_id is None or equipo is None:
            continue
        conn.execute(
            "INSERT OR IGNORE INTO unidades (id, equipo) VALUES (?, ?)",
            (str(unidad_id), str(equipo)),
        )
    conn.commit()


def inicializar_bd(
    ruta: Path | str | None = None, inventario: list[dict[str, Any]] | None = None
) -> Path:
    """Inicializa la base de datos creando esquema y sembrando unidades."""
    if ruta is None:
        ruta_bd_obj = ruta_bd()
    else:
        ruta_bd_obj = Path(ruta)
    ruta_bd_obj.parent.mkdir(parents=True, exist_ok=True)
    conn = obtener_conexion(ruta_bd_obj)
    try:
        crear_esquema(conn)
        sembrar_unidades(conn, inventario)
    finally:
        conn.close()
    return ruta_bd_obj


def obtener_unidades(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Obtiene todas las unidades."""
    cur = conn.execute("SELECT id, equipo FROM unidades ORDER BY id")
    return [dict(row) for row in cur.fetchall()]
