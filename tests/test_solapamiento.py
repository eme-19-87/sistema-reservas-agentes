from __future__ import annotations

from datetime import datetime

import pytest

from reservas.dominio import (
    Superposicion,
    hay_solapamiento,
    validar_solicitud_intervalo,
)

AHORA = datetime(2026, 10, 22, 10, 0)


def inventario_test():
    return {
        "MIC-01": {"id": "MIC-01", "equipo": "Microscopio digital"},
        "MIC-02": {"id": "MIC-02", "equipo": "Microscopio digital"},
        "OSC-01": {"id": "OSC-01", "equipo": "Osciloscopio"},
        "MUL-01": {"id": "MUL-01", "equipo": "Multímetro"},
        "FUE-01": {"id": "FUE-01", "equipo": "Fuente de alimentación"},
    }


def test_hay_solapamiento_semiabierto():
    a_i = datetime(2026, 10, 22, 10, 0)
    a_f = datetime(2026, 10, 22, 11, 0)
    b_i = datetime(2026, 10, 22, 10, 30)
    b_f = datetime(2026, 10, 22, 11, 30)
    assert hay_solapamiento(a_i, a_f, b_i, b_f) is True


def test_solapamiento_1030_1130_con_1000_1100():
    reservas_activas = [
        {
            "id": 1,
            "unidad_id": "MIC-01",
            "inicio": "2026-10-22T10:00",
            "fin": "2026-10-22T11:00",
            "estado": "ACTIVA",
        }
    ]
    with pytest.raises(Superposicion):
        validar_solicitud_intervalo(
            "MIC-01",
            "2026-10-22T10:30",
            "2026-10-22T11:30",
            "Ana",
            ahora=AHORA,
            inventario=inventario_test(),
            reservas_activas=reservas_activas,
        )


def test_solapamiento_contenido_total():
    reservas_activas = [
        {
            "id": 1,
            "unidad_id": "MIC-01",
            "inicio": "2026-10-22T10:00",
            "fin": "2026-10-22T11:00",
            "estado": "ACTIVA",
        }
    ]
    with pytest.raises(Superposicion):
        validar_solicitud_intervalo(
            "MIC-01",
            "2026-10-22T10:15",
            "2026-10-22T10:45",
            "Ana",
            ahora=AHORA,
            inventario=inventario_test(),
            reservas_activas=reservas_activas,
        )


def test_solapamiento_intervalo_identico():
    reservas_activas = [
        {
            "id": 1,
            "unidad_id": "MIC-01",
            "inicio": "2026-10-22T10:00",
            "fin": "2026-10-22T11:00",
            "estado": "ACTIVA",
        }
    ]
    with pytest.raises(Superposicion):
        validar_solicitud_intervalo(
            "MIC-01",
            "2026-10-22T10:00",
            "2026-10-22T11:00",
            "Ana",
            ahora=AHORA,
            inventario=inventario_test(),
            reservas_activas=reservas_activas,
        )


def test_limite_consecutivo_1100_1200_permitido():
    reservas_activas = [
        {
            "id": 1,
            "unidad_id": "MIC-01",
            "inicio": "2026-10-22T10:00",
            "fin": "2026-10-22T11:00",
            "estado": "ACTIVA",
        }
    ]
    validar_solicitud_intervalo(
        "MIC-01",
        "2026-10-22T11:00",
        "2026-10-22T12:00",
        "Ana",
        ahora=AHORA,
        inventario=inventario_test(),
        reservas_activas=reservas_activas,
    )


def test_limite_consecutivo_0900_1000_permitido():
    reservas_activas = [
        {
            "id": 1,
            "unidad_id": "MIC-01",
            "inicio": "2026-10-22T10:00",
            "fin": "2026-10-22T11:00",
            "estado": "ACTIVA",
        }
    ]
    validar_solicitud_intervalo(
        "MIC-01",
        "2026-10-22T09:00",
        "2026-10-22T10:00",
        "Ana",
        ahora=datetime(2026, 10, 22, 8, 0),
        inventario=inventario_test(),
        reservas_activas=reservas_activas,
    )


def test_unidades_distintas_simultaneas():
    reservas_activas = [
        {
            "id": 1,
            "unidad_id": "MIC-01",
            "inicio": "2026-10-22T10:00",
            "fin": "2026-10-22T11:00",
            "estado": "ACTIVA",
        }
    ]
    validar_solicitud_intervalo(
        "MIC-02",
        "2026-10-22T10:00",
        "2026-10-22T11:00",
        "Ana",
        ahora=AHORA,
        inventario=inventario_test(),
        reservas_activas=reservas_activas,
    )


def test_reserva_cancelada_no_bloquea():
    reservas_activas = [
        {
            "id": 1,
            "unidad_id": "MIC-01",
            "inicio": "2026-10-22T10:00",
            "fin": "2026-10-22T11:00",
            "estado": "CANCELADA",
        }
    ]
    validar_solicitud_intervalo(
        "MIC-01",
        "2026-10-22T10:30",
        "2026-10-22T11:30",
        "Ana",
        ahora=AHORA,
        inventario=inventario_test(),
        reservas_activas=reservas_activas,
    )
