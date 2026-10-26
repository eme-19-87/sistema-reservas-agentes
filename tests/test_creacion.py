"""Pruebas de creación de reservas."""

from __future__ import annotations

from reservas import servicio
from reservas.repositorio import inicializar_bd


def test_reserva_valida_crea_activa_con_id(env_db_temporal, reloj_fijo):
    inicializar_bd()
    res = servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    assert res["estado"] == "ACTIVA"
    assert isinstance(res["id"], int)
    assert res["id"] >= 1
    assert res["unidad_id"] == "MIC-01"
    assert res["solicitante"] == "Ana"


def test_listado_ordenado_por_inicio_y_luego_por_id(env_db_temporal, reloj_fijo):
    inicializar_bd()

    def reloj():
        return reloj_fijo

    servicio.crear_reserva(
        "MIC-01", "Ana", "2026-10-23T12:00", "2026-10-23T13:00", reloj=reloj
    )
    servicio.crear_reserva(
        "MIC-01", "Beto", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
    )
    servicio.crear_reserva(
        "MIC-02", "Carla", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
    )
    reservas = servicio.listar_reservas()
    orden = [(r["inicio"], r["id"]) for r in reservas]
    assert len(reservas) == 3
    assert orden == sorted(orden)
    assert [r["id"] for r in reservas] == [2, 3, 1]
