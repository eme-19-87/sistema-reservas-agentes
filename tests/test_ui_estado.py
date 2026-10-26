"""Pruebas de handlers del State."""
from __future__ import annotations

from functools import partial

import pytest

from reservas import servicio
from reservas.repositorio import inicializar_bd
from reservas_ui import estado

_DIA = "2026-10-23"


def _rango(inicio_hora: str, fin_hora: str) -> tuple[str, str]:
    return f"{_DIA}T{inicio_hora}", f"{_DIA}T{fin_hora}"


@pytest.fixture
def reloj_en_presentacion(monkeypatch: pytest.MonkeyPatch, reloj_fijo):
    """Fija el reloj usado por el handler al delegar en presentación."""
    monkeypatch.setattr(
        estado.presentacion,
        "reservar",
        partial(estado.presentacion.reservar, reloj=lambda: reloj_fijo),
    )


def _state_reserva(
    unidad: str, solicitante: str, inicio: str, fin: str
) -> estado.State:
    st = estado.State()
    st.unidad_seleccionada = unidad
    st.solicitante = solicitante
    st.inicio_res = inicio
    st.fin_res = fin
    return st


def test_on_load_carga_unidades_y_reservas(env_db_temporal, reloj_fijo):
    inicializar_bd()
    servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    st = estado.State()
    st.on_load()
    assert len(st.unidades) == 5
    assert any(
        r.get("unidad_id") == "MIC-01" or r.get("unidad") == "MIC-01"
        for r in st.reservas
    )


def test_reservar_valido_actualiza_lista(env_db_temporal, reloj_en_presentacion):
    inicializar_bd()
    st = _state_reserva("MIC-01", "Ana", *_rango("10:00", "11:00"))
    st.reservar()
    assert st.mensaje_error == ""
    assert "ID" in st.mensaje_exito
    assert len(st.reservas) == 1
    assert st.reservas[0].get("unidad_id") == "MIC-01"


def test_reservar_solapamiento_deja_error_y_lista_intacta(
    env_db_temporal, reloj_en_presentacion, reloj_fijo
):
    inicializar_bd()
    servicio.crear_reserva(
        "MIC-01", "Ana", *_rango("10:00", "11:00"), reloj=lambda: reloj_fijo
    )
    st = estado.State()
    st.on_load()
    antes = len(st.reservas)
    st.unidad_seleccionada = "MIC-01"
    st.solicitante = "Luis"
    st.inicio_res, st.fin_res = _rango("10:30", "11:30")
    st.reservar()
    assert "Superposición" in st.mensaje_error
    assert len(st.reservas) == antes


def test_reservar_limites_consecutivos_aceptado(
    env_db_temporal, reloj_en_presentacion, reloj_fijo
):
    inicializar_bd()
    servicio.crear_reserva(
        "MIC-01", "Ana", *_rango("10:00", "11:00"), reloj=lambda: reloj_fijo
    )
    st = _state_reserva("MIC-01", "Luis", *_rango("11:00", "12:00"))
    st.reservar()
    assert st.mensaje_error == ""
    assert len(st.reservas) == 2


def test_reservar_mic02_simultanea_aceptada(
    env_db_temporal, reloj_en_presentacion, reloj_fijo
):
    inicializar_bd()
    servicio.crear_reserva(
        "MIC-01", "Ana", *_rango("10:00", "11:00"), reloj=lambda: reloj_fijo
    )
    st = _state_reserva("MIC-02", "Luis", *_rango("10:00", "11:00"))
    st.reservar()
    assert st.mensaje_error == ""
    assert len(st.reservas) == 2


def test_reservar_solicitante_vacio_rechazado(env_db_temporal, reloj_en_presentacion):
    inicializar_bd()
    st = _state_reserva("MIC-01", "", *_rango("10:00", "11:00"))
    st.reservar()
    assert "Solicitante" in st.mensaje_error
    assert st.reservas == []


def test_reservar_exito_limpia_formulario_y_conserva_unidad(
    env_db_temporal, reloj_en_presentacion
):
    inicializar_bd()
    st = _state_reserva("MIC-01", "Ana", *_rango("10:00", "11:00"))
    st.reservar()
    assert st.solicitante == ""
    assert st.inicio_res == ""
    assert st.fin_res == ""
    assert st.unidad_seleccionada == "MIC-01"


def test_reservar_error_conserva_valores_del_formulario(
    env_db_temporal, reloj_en_presentacion
):
    inicializar_bd()
    inicio, fin = "2026-10-21T10:00", "2026-10-21T11:00"
    st = _state_reserva("MIC-01", "Ana", inicio, fin)
    st.reservar()
    assert st.mensaje_error
    assert st.solicitante == "Ana"
    assert st.inicio_res == inicio
    assert st.fin_res == fin
