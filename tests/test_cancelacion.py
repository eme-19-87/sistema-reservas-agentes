"""Pruebas de cancelación de reservas."""

from __future__ import annotations

from datetime import datetime

from reservas import servicio
from reservas.dominio import ReservaNoEncontrada, ReservaYaCancelada
from reservas.repositorio import inicializar_bd


def test_cancelacion_conserva_id_y_datos_libera_horario(env_db_temporal, reloj_fijo):
    inicializar_bd()
    res = servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    res_id = res["id"]
    cancelada = servicio.cancelar_reserva(res_id, reloj=lambda: reloj_fijo)
    assert cancelada["id"] == res_id
    assert cancelada["estado"] == "CANCELADA"
    assert cancelada["unidad_id"] == "MIC-01"
    assert cancelada["solicitante"] == "Ana"
    assert cancelada["inicio"] == "2026-10-23T10:00"
    assert cancelada["fin"] == "2026-10-23T11:00"
    assert cancelada["cancelada_en"] is not None
    # libera horario
    disp = servicio.consultar_disponibilidad(
        "MIC-01", "2026-10-23T10:00", "2026-10-23T11:00", reloj=lambda: reloj_fijo
    )
    assert disp["disponible"] is True


def test_doble_cancelacion_y_id_inexistente_rechazados(env_db_temporal, reloj_fijo):
    inicializar_bd()
    res = servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    servicio.cancelar_reserva(res["id"], reloj=lambda: reloj_fijo)
    try:
        servicio.cancelar_reserva(res["id"], reloj=lambda: reloj_fijo)
        assert False, "debería lanzar"
    except ReservaYaCancelada:
        pass
    try:
        servicio.cancelar_reserva(99999, reloj=lambda: reloj_fijo)
        assert False, "debería lanzar"
    except ReservaNoEncontrada:
        pass


def test_cancelar_reserva_ya_iniciada_permitido(env_db_temporal):
    inicializar_bd()
    res = servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-22T09:00",
        "2026-10-22T10:00",
        reloj=lambda: datetime(2026, 10, 22, 8, 0),
    )
    # cancelar con reloj posterior al inicio
    cancelada = servicio.cancelar_reserva(
        res["id"], reloj=lambda: datetime(2026, 10, 22, 9, 30)
    )
    assert cancelada["estado"] == "CANCELADA"
