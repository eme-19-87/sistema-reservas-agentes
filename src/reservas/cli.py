"""CLI de mantenimiento."""
from __future__ import annotations

import sys

from .repositorio import inicializar_bd, obtener_conexion


def _confirmar_reset() -> bool:
    """Solicita confirmación para reset."""
    try:
        respuesta = input("¿Borrar todas las reservas? [y/N]: ")
    except EOFError:
        return False
    return respuesta.strip().lower() in {"y", "yes", "s", "si"}


def cmd_init_db(reset: bool = False, yes: bool = False) -> int:
    """Inicializa la base de datos."""
    try:
        if reset:
            if not yes and not _confirmar_reset():
                return 1
            ruta = inicializar_bd()
            conn = obtener_conexion(ruta)
            try:
                conn.execute("DELETE FROM reservas")
                conn.commit()
            finally:
                conn.close()
            return 0
        inicializar_bd()
        return 0
    except Exception:
        return 1


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada CLI."""
    if argv is None:
        argv = sys.argv[1:]
    if not argv or argv[0] != "init-db":
        return 1
    reset = False
    yes = False
    for arg in argv[1:]:
        if arg == "--reset":
            reset = True
        elif arg == "--yes":
            yes = True
    return cmd_init_db(reset=reset, yes=yes)
