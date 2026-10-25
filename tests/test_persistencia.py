"""Pruebas de persistencia tras reinicio."""
from __future__ import annotations

from reservas import servicio
from reservas import repositorio
from reservas.repositorio import obtener_conexion


def test_persistencia_activas_y_canceladas_tras_reabrir(tmp_path, reloj_fijo):
    db_path = tmp_path / "reservas.db"

    original_ruta_bd = repositorio.ruta_bd
    repositorio.ruta_bd = lambda: db_path
    try:
        repositorio.inicializar_bd(db_path)
        res1 = servicio.crear_reserva(
            "MIC-01",
            "Ana",
            "2026-10-23T10:00",
            "2026-10-23T11:00",
            reloj=lambda: reloj_fijo,
        )
        res2 = servicio.crear_reserva(
            "MIC-02",
            "Luis",
            "2026-10-23T12:00",
            "2026-10-23T13:00",
            reloj=lambda: reloj_fijo,
        )
        servicio.cancelar_reserva(res2["id"], reloj=lambda: reloj_fijo)
        # cerrar conexión simulando cierre
        conn = obtener_conexion(db_path)
        conn.close()
        # reabrir
        reservas = servicio.listar_reservas()
        assert len(reservas) == 2
        estados = {r["id"]: r["estado"] for r in reservas}
        assert estados[res1["id"]] == "ACTIVA"
        assert estados[res2["id"]] == "CANCELADA"
    finally:
        repositorio.ruta_bd = original_ruta_bd
