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


@pytest.fixture
def reloj_en_consulta(monkeypatch: pytest.MonkeyPatch, reloj_fijo):
    """Fija el reloj de la consulta de disponibilidad en el handler."""
    monkeypatch.setattr(
        estado.presentacion,
        "consultar",
        partial(estado.presentacion.consultar, reloj=lambda: reloj_fijo),
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
    assert st.mensaje_error_reserva == ""
    assert "ID" in st.mensaje_exito_reserva
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
    assert "Superposición" in st.mensaje_error_reserva
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
    assert st.mensaje_error_reserva == ""
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
    assert st.mensaje_error_reserva == ""
    assert len(st.reservas) == 2


def test_reservar_solicitante_vacio_rechazado(env_db_temporal, reloj_en_presentacion):
    inicializar_bd()
    st = _state_reserva("MIC-01", "", *_rango("10:00", "11:00"))
    st.reservar()
    assert "Solicitante" in st.mensaje_error_reserva
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
    assert st.mensaje_error_reserva
    assert st.solicitante == "Ana"
    assert st.inicio_res == inicio
    assert st.fin_res == fin


def test_handlers_de_campos_actualizan_el_estado():
    st = estado.State()
    st.actualizar_unidad("MIC-02")
    st.actualizar_solicitante("Ana")
    st.actualizar_inicio_disp("2026-10-23T10:00")
    st.actualizar_fin_disp("2026-10-23T11:00")
    st.actualizar_inicio_res("2026-10-23T12:00")
    st.actualizar_fin_res("2026-10-23T13:00")
    assert st.unidad_seleccionada == "MIC-02"
    assert st.solicitante == "Ana"
    assert st.inicio_disp == "2026-10-23T10:00"
    assert st.fin_disp == "2026-10-23T11:00"
    assert st.inicio_res == "2026-10-23T12:00"
    assert st.fin_res == "2026-10-23T13:00"


def test_pestana_inicia_en_reserva_y_acepta_solo_pestanas_conocidas():
    st = estado.State()
    assert st.pestana_activa == estado.PESTANA_RESERVA

    st.cambiar_pestana(estado.PESTANA_DISPONIBILIDAD)

    assert st.pestana_activa == estado.PESTANA_DISPONIBILIDAD

    st.cambiar_pestana("desconocida")

    assert st.pestana_activa == estado.PESTANA_DISPONIBILIDAD


def test_mensajes_de_cada_formulario_son_independientes(
    env_db_temporal, reloj_en_presentacion, reloj_en_consulta
):
    inicializar_bd()
    st = _state_reserva("MIC-01", "Ana", *_rango("10:00", "11:00"))
    st.reservar()

    exito_reserva = st.mensaje_exito_reserva
    assert exito_reserva

    st.inicio_disp, st.fin_disp = _rango("12:00", "13:00")
    st.consultar_disponibilidad()

    assert st.mensaje_exito_disponibilidad == "Disponible."
    assert st.mensaje_error_disponibilidad == ""
    assert st.mensaje_exito_reserva == exito_reserva

    st.solicitante = ""
    st.inicio_res, st.fin_res = _rango("14:00", "15:00")
    st.reservar()

    assert st.mensaje_error_reserva
    assert st.mensaje_exito_disponibilidad == "Disponible."


def test_consulta_invalida_usa_el_mensaje_de_disponibilidad(
    env_db_temporal, reloj_en_consulta
):
    inicializar_bd()
    st = estado.State()
    st.unidad_seleccionada = "MIC-01"
    st.inicio_disp = "2026-10-21T10:00"
    st.fin_disp = "2026-10-21T11:00"

    st.consultar_disponibilidad()

    assert st.mensaje_error_disponibilidad
    assert st.mensaje_error_reserva == ""


def _crear_reserva(
    unidad: str, solicitante: str, inicio_hora: str, fin_hora: str, reloj_fijo
) -> dict:
    inicio, fin = _rango(inicio_hora, fin_hora)
    return servicio.crear_reserva(
        unidad, solicitante, inicio, fin, reloj=lambda: reloj_fijo
    )


def test_cancelar_conserva_fila_cancelada_con_datos(env_db_temporal, reloj_fijo):
    inicializar_bd()
    creada = _crear_reserva("MIC-01", "Ana", "10:00", "11:00", reloj_fijo)
    st = estado.State()
    st.on_load()
    st.cancelar(creada["id"])
    assert st.mensaje_error_cancelacion == ""
    assert st.mensaje_exito_cancelacion
    fila = next(r for r in st.reservas if r["id"] == creada["id"])
    assert fila["estado"] == "CANCELADA"
    assert fila["unidad_id"] == "MIC-01"
    assert fila["solicitante"] == "Ana"
    assert fila["inicio"] == creada["inicio"]
    assert fila["fin"] == creada["fin"]


def test_cancelar_libera_horario(env_db_temporal, reloj_fijo):
    inicializar_bd()
    creada = _crear_reserva("MIC-01", "Ana", "10:00", "11:00", reloj_fijo)
    st = estado.State()
    st.on_load()
    st.cancelar(creada["id"])
    nueva = _crear_reserva("MIC-01", "Luis", "10:00", "11:00", reloj_fijo)
    assert nueva["id"] != creada["id"]
    assert nueva["estado"] == "ACTIVA"


def test_doble_cancelacion_muestra_error(env_db_temporal, reloj_fijo):
    inicializar_bd()
    creada = _crear_reserva("MIC-01", "Ana", "10:00", "11:00", reloj_fijo)
    st = estado.State()
    st.on_load()
    st.cancelar(creada["id"])
    antes = len(st.reservas)
    st.cancelar(creada["id"])
    assert "ya cancelada" in st.mensaje_error_cancelacion.lower()
    assert len(st.reservas) == antes
    fila = next(r for r in st.reservas if r["id"] == creada["id"])
    assert fila["estado"] == "CANCELADA"


def test_filtros_por_unidad_y_estado(env_db_temporal, reloj_fijo):
    inicializar_bd()
    res_mic01_activa = _crear_reserva("MIC-01", "Ana", "10:00", "11:00", reloj_fijo)
    res_mic01_cancelada = _crear_reserva("MIC-01", "Luis", "11:00", "12:00", reloj_fijo)
    res_mic02_activa = _crear_reserva("MIC-02", "Ana", "10:00", "11:00", reloj_fijo)
    servicio.cancelar_reserva(res_mic01_cancelada["id"], reloj=lambda: reloj_fijo)

    st = estado.State()
    st.on_load()

    st.actualizar_filtro_unidad("MIC-01")
    assert {r["id"] for r in st.reservas} == {
        res_mic01_activa["id"],
        res_mic01_cancelada["id"],
    }

    st.actualizar_filtro_unidad("")
    st.actualizar_filtro_estado("CANCELADA")
    assert {r["id"] for r in st.reservas} == {res_mic01_cancelada["id"]}

    st.actualizar_filtro_unidad("MIC-01")
    st.actualizar_filtro_estado("ACTIVA")
    assert {r["id"] for r in st.reservas} == {res_mic01_activa["id"]}

    st.limpiar_filtros()
    assert {r["id"] for r in st.reservas} == {
        res_mic01_activa["id"],
        res_mic01_cancelada["id"],
        res_mic02_activa["id"],
    }
