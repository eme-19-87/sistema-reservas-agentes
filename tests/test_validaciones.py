from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from reservas import dominio
from reservas.dominio import (
    FechaInvalida,
    IntervaloInvalido,
    LimiteExcedido,
    SolicitanteInvalido,
    UnidadDesconocida,
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


def test_unidad_desconocida():
    with pytest.raises(UnidadDesconocida):
        validar_solicitud_intervalo("NOEXISTE", "2026-10-22T11:00", "2026-10-22T12:00", "Ana", ahora=AHORA, inventario=inventario_test())


def test_solicitante_vacio():
    with pytest.raises(SolicitanteInvalido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T11:00", "2026-10-22T12:00", "", ahora=AHORA, inventario=inventario_test())


def test_solicitante_solo_espacios():
    with pytest.raises(SolicitanteInvalido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T11:00", "2026-10-22T12:00", "   ", ahora=AHORA, inventario=inventario_test())


def test_solicitante_solo_numeros():
    with pytest.raises(SolicitanteInvalido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T11:00", "2026-10-22T12:00", "12345", ahora=AHORA, inventario=inventario_test())


def test_solicitante_con_caracteres_especiales():
    with pytest.raises(SolicitanteInvalido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T11:00", "2026-10-22T12:00", "Ana@Lopez", ahora=AHORA, inventario=inventario_test())


def test_solicitante_con_acentos_y_dieresis_valido():
    validar_solicitud_intervalo("MIC-01", "2026-10-22T11:00", "2026-10-22T12:00", "María Núñez", ahora=AHORA, inventario=inventario_test())


def test_fecha_invalida_formato():
    with pytest.raises(FechaInvalida):
        validar_solicitud_intervalo("MIC-01", "22/10/2026 11:00", "2026-10-22T12:00", "Ana", ahora=AHORA, inventario=inventario_test())


def test_fecha_invalida_con_offset():
    with pytest.raises(FechaInvalida):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T11:00Z", "2026-10-22T12:00", "Ana", ahora=AHORA, inventario=inventario_test())


def test_fecha_invalida_calendario():
    with pytest.raises(FechaInvalida):
        validar_solicitud_intervalo("MIC-01", "2026-02-30T11:00", "2026-02-30T12:00", "Ana", ahora=AHORA, inventario=inventario_test())


def test_inicio_mayor_igual_fin():
    with pytest.raises(IntervaloInvalido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T12:00", "2026-10-22T11:00", "Ana", ahora=AHORA, inventario=inventario_test())
    with pytest.raises(IntervaloInvalido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T11:00", "2026-10-22T11:00", "Ana", ahora=AHORA, inventario=inventario_test())


def test_fecha_pasada():
    with pytest.raises(LimiteExcedido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T09:59", "2026-10-22T10:30", "Ana", ahora=AHORA, inventario=inventario_test())


def test_inicio_igual_a_ahora_valido():
    validar_solicitud_intervalo("MIC-01", "2026-10-22T10:00", "2026-10-22T11:00", "Ana", ahora=AHORA, inventario=inventario_test())


def test_duracion_maxima_8_horas_valido():
    validar_solicitud_intervalo("MIC-01", "2026-10-22T10:00", "2026-10-22T18:00", "Ana", ahora=AHORA, inventario=inventario_test())


def test_duracion_mayor_a_8_horas():
    with pytest.raises(LimiteExcedido):
        validar_solicitud_intervalo("MIC-01", "2026-10-22T10:00", "2026-10-22T18:01", "Ana", ahora=AHORA, inventario=inventario_test())


def test_anticipacion_maxima_90_dias_valido():
    inicio = (AHORA + timedelta(days=90)).strftime("%Y-%m-%dT%H:%M")
    fin = (AHORA + timedelta(days=90, hours=1)).strftime("%Y-%m-%dT%H:%M")
    validar_solicitud_intervalo("MIC-01", inicio, fin, "Ana", ahora=AHORA, inventario=inventario_test())


def test_anticipacion_mayor_a_90_dias():
    inicio = (AHORA + timedelta(days=90, minutes=1)).strftime("%Y-%m-%dT%H:%M")
    fin = (AHORA + timedelta(days=90, minutes=2)).strftime("%Y-%m-%dT%H:%M")
    with pytest.raises(LimiteExcedido):
        validar_solicitud_intervalo("MIC-01", inicio, fin, "Ana", ahora=AHORA, inventario=inventario_test())
