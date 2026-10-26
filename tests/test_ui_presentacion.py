"""Pruebas de la capa de presentación (funciones puras)."""

from __future__ import annotations

import logging

from reservas import dominio, servicio
from reservas.repositorio import inicializar_bd
from reservas_ui import presentacion


def test_mensaje_por_cada_excepcion(env_db_temporal, reloj_fijo):
    inicializar_bd()

    def reloj():
        return reloj_fijo

    try:
        servicio.crear_reserva(
            "NOPE", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
        )
    except Exception as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg

    try:
        servicio.crear_reserva(
            "MIC-01", "   ", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
        )
    except Exception as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg

    try:
        servicio.crear_reserva(
            "MIC-01", "Ana", "2026/10/23 10:00", "2026-10-23T11:00", reloj=reloj
        )
    except Exception as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg

    try:
        servicio.crear_reserva(
            "MIC-01", "Ana", "2026-10-23T11:00", "2026-10-23T10:00", reloj=reloj
        )
    except Exception as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg

    try:
        servicio.crear_reserva(
            "MIC-01", "Ana", "2026-10-21T10:00", "2026-10-21T11:00", reloj=reloj
        )
    except Exception as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg

    res1 = servicio.crear_reserva(
        "MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
    )
    try:
        servicio.crear_reserva(
            "MIC-01", "Luis", "2026-10-23T10:30", "2026-10-23T11:30", reloj=reloj
        )
    except dominio.Superposicion as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg
        assert str(res1["id"]) in msg

    try:
        servicio.cancelar_reserva(9999, reloj=reloj)
    except Exception as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg

    res = servicio.crear_reserva(
        "MIC-01", "Marta", "2026-10-23T11:00", "2026-10-23T12:00", reloj=reloj
    )
    servicio.cancelar_reserva(res["id"], reloj=reloj)
    try:
        servicio.cancelar_reserva(res["id"], reloj=reloj)
    except Exception as exc:
        msg = presentacion.mensaje_error(exc)
        assert isinstance(msg, str) and msg


def test_reservar_exito_con_id(env_db_temporal, reloj_fijo):
    inicializar_bd()

    def reloj():
        return reloj_fijo

    res = presentacion.reservar(
        servicio, "MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
    )
    assert res["ok"] is True
    assert "mensaje" in res
    assert res.get("reserva") and res["reserva"]["id"]
    assert str(res["reserva"]["id"]) in res["mensaje"]


def test_consultar_disponible_y_no_disponible(env_db_temporal, reloj_fijo):
    inicializar_bd()

    def reloj():
        return reloj_fijo

    r1 = presentacion.consultar(
        servicio, "MIC-01", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
    )
    assert r1["disponible"] is True
    assert "disponible" in r1["mensaje"].lower()

    servicio.crear_reserva(
        "MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
    )
    r2 = presentacion.consultar(
        servicio, "MIC-01", "2026-10-23T10:30", "2026-10-23T11:30", reloj=reloj
    )
    assert r2["disponible"] is False
    assert "no disponible" in r2["mensaje"].lower()
    assert "conflictos" in r2


def test_listar_filas_activa_cancelada(env_db_temporal, reloj_fijo):
    inicializar_bd()

    def reloj():
        return reloj_fijo

    res = servicio.crear_reserva(
        "MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=reloj
    )
    servicio.cancelar_reserva(res["id"], reloj=reloj)
    filas = presentacion.listar_filas(servicio)
    estados = {f["estado"] for f in filas}
    assert "ACTIVA" in estados or "CANCELADA" in estados
    assert any(f["estado"] == "CANCELADA" for f in filas)


def test_error_inesperado_muestra_mensaje_generico_y_se_registra(caplog):
    excepcion = RuntimeError("fallo interno xyz")
    with caplog.at_level(logging.ERROR, logger=presentacion.__name__):
        mensaje = presentacion.mensaje_error(excepcion)
    assert mensaje == presentacion.MENSAJE_ERROR_INESPERADO
    assert "fallo interno xyz" not in mensaje
    assert "fallo interno xyz" in caplog.text
