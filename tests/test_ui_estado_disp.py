"""Pruebas de consultar disponibilidad en State."""

from __future__ import annotations

from reservas import servicio
from reservas.repositorio import inicializar_bd


def test_consultar_disponible(env_db_temporal, reloj_fijo):
    inicializar_bd()
    from reservas_ui import presentacion

    res = presentacion.consultar(
        servicio,
        "MIC-01",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    assert res.get("disponible") is True


def test_consultar_ocupado(env_db_temporal, reloj_fijo):
    inicializar_bd()
    servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    from reservas_ui import presentacion

    res = presentacion.consultar(
        servicio,
        "MIC-01",
        "2026-10-23T10:30",
        "2026-10-23T11:30",
        reloj=lambda: reloj_fijo,
    )
    assert res.get("disponible") is False


def test_consultar_entrada_invalida_muestra_mensaje_error(env_db_temporal, reloj_fijo):
    inicializar_bd()
    from reservas_ui import presentacion

    res = presentacion.consultar(
        servicio,
        "MIC-01",
        "2026-10-23T11:00",
        "2026-10-23T10:00",
        reloj=lambda: reloj_fijo,
    )
    assert res.get("error") or res.get("mensaje")


def test_limites_consecutivos_disponibles(env_db_temporal, reloj_fijo):
    inicializar_bd()
    servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    from reservas_ui import presentacion

    res = presentacion.consultar(
        servicio,
        "MIC-01",
        "2026-10-23T11:00",
        "2026-10-23T12:00",
        reloj=lambda: reloj_fijo,
    )
    assert res.get("disponible") is True


def test_consultar_no_crea_reservas(env_db_temporal, reloj_fijo):
    inicializar_bd()
    from reservas.repositorio import obtener_conexion
    from reservas_ui import presentacion

    presentacion.consultar(
        servicio,
        "MIC-01",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    conn = obtener_conexion()
    try:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM reservas")
        assert cur.fetchone()["cnt"] == 0
    finally:
        conn.close()
