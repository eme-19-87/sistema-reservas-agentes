"""Pruebas de creación de reservas."""
from __future__ import annotations

from datetime import datetime

from reservas import servicio


def test_reserva_valida_crea_activa_con_id(env_db_temporal, reloj_fijo):
    servicio.inicializar_bd = lambda: None  # ensure db initialized
    from reservas.repositorio import inicializar_bd

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
