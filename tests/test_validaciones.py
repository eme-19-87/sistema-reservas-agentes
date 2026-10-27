from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest

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


INICIO_VALIDO = "2026-10-22T11:00"
FIN_VALIDO = "2026-10-22T12:00"


@dataclass(frozen=True)
class CasoInvalido:
    """Datos de un escenario de validación que debe ser rechazado."""

    excepcion: type[Exception]
    unidad: str = "MIC-01"
    inicio: str = INICIO_VALIDO
    fin: str = FIN_VALIDO
    solicitante: str = "Ana"


CASOS_INVALIDOS = [
    pytest.param(
        CasoInvalido(UnidadDesconocida, unidad="NOEXISTE"),
        id="unidad-desconocida",
    ),
    pytest.param(
        CasoInvalido(SolicitanteInvalido, solicitante=""),
        id="solicitante-vacio",
    ),
    pytest.param(
        CasoInvalido(SolicitanteInvalido, solicitante="   "),
        id="solicitante-solo-espacios",
    ),
    pytest.param(
        CasoInvalido(SolicitanteInvalido, solicitante="12345"),
        id="solicitante-solo-numeros",
    ),
    pytest.param(
        CasoInvalido(SolicitanteInvalido, solicitante="Ana@Lopez"),
        id="solicitante-caracteres-especiales",
    ),
    pytest.param(
        CasoInvalido(FechaInvalida, inicio="22/10/2026 11:00"),
        id="fecha-formato-invalido",
    ),
    pytest.param(
        CasoInvalido(FechaInvalida, inicio="2026-10-22T11:00Z"),
        id="fecha-con-offset",
    ),
    pytest.param(
        CasoInvalido(
            FechaInvalida,
            inicio="2026-02-30T11:00",
            fin="2026-02-30T12:00",
        ),
        id="fecha-calendario-invalida",
    ),
    pytest.param(
        CasoInvalido(
            LimiteExcedido,
            inicio="2026-10-22T09:59",
            fin="2026-10-22T10:30",
        ),
        id="fecha-pasada",
    ),
    pytest.param(
        CasoInvalido(
            LimiteExcedido,
            inicio="2026-10-22T10:00",
            fin="2026-10-22T18:01",
        ),
        id="duracion-mayor-a-8-horas",
    ),
]


@pytest.mark.parametrize("caso", CASOS_INVALIDOS)
def test_solicitudes_invalidas(caso: CasoInvalido) -> None:
    with pytest.raises(caso.excepcion):
        validar_solicitud_intervalo(
            caso.unidad,
            caso.inicio,
            caso.fin,
            caso.solicitante,
            ahora=AHORA,
            inventario=inventario_test(),
        )


def test_solicitante_con_acentos_y_dieresis_valido():
    validar_solicitud_intervalo(
        "MIC-01",
        "2026-10-22T11:00",
        "2026-10-22T12:00",
        "María Núñez",
        ahora=AHORA,
        inventario=inventario_test(),
    )


def test_inicio_mayor_igual_fin():
    with pytest.raises(IntervaloInvalido):
        validar_solicitud_intervalo(
            "MIC-01",
            "2026-10-22T12:00",
            "2026-10-22T11:00",
            "Ana",
            ahora=AHORA,
            inventario=inventario_test(),
        )
    with pytest.raises(IntervaloInvalido):
        validar_solicitud_intervalo(
            "MIC-01",
            "2026-10-22T11:00",
            "2026-10-22T11:00",
            "Ana",
            ahora=AHORA,
            inventario=inventario_test(),
        )


def test_inicio_igual_a_ahora_valido():
    validar_solicitud_intervalo(
        "MIC-01",
        "2026-10-22T10:00",
        "2026-10-22T11:00",
        "Ana",
        ahora=AHORA,
        inventario=inventario_test(),
    )


def test_duracion_maxima_8_horas_valido():
    validar_solicitud_intervalo(
        "MIC-01",
        "2026-10-22T10:00",
        "2026-10-22T18:00",
        "Ana",
        ahora=AHORA,
        inventario=inventario_test(),
    )


def test_anticipacion_maxima_90_dias_valido():
    inicio = (AHORA + timedelta(days=90)).strftime("%Y-%m-%dT%H:%M")
    fin = (AHORA + timedelta(days=90, hours=1)).strftime("%Y-%m-%dT%H:%M")
    validar_solicitud_intervalo(
        "MIC-01", inicio, fin, "Ana", ahora=AHORA, inventario=inventario_test()
    )


def test_anticipacion_mayor_a_90_dias():
    inicio = (AHORA + timedelta(days=90, minutes=1)).strftime("%Y-%m-%dT%H:%M")
    fin = (AHORA + timedelta(days=90, minutes=2)).strftime("%Y-%m-%dT%H:%M")
    with pytest.raises(LimiteExcedido):
        validar_solicitud_intervalo(
            "MIC-01", inicio, fin, "Ana", ahora=AHORA, inventario=inventario_test()
        )
