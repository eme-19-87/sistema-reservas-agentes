"""Prueba de humo de la aplicación Reflex."""

from __future__ import annotations

import importlib

import reflex as rx
from reflex.utils.format import format_route

from reservas_ui import componentes
from reservas_ui.estado import State

VARS_DECLARADAS = frozenset(
    {
        "unidades",
        "reservas",
        "unidad_seleccionada",
        "solicitante",
        "inicio_disp",
        "fin_disp",
        "inicio_res",
        "fin_res",
        "filtro_unidad",
        "filtro_estado",
        "pestana_activa",
        "mensaje_exito_reserva",
        "mensaje_error_reserva",
        "mensaje_exito_disponibilidad",
        "mensaje_error_disponibilidad",
        "mensaje_exito_cancelacion",
        "mensaje_error_cancelacion",
        "conflictos_disp",
    }
)
VARS_CALCULADAS = frozenset({"unidades_ids"})


def test_reservas_ui_se_importa() -> None:
    modulo = importlib.import_module("reservas_ui.reservas_ui")

    assert isinstance(modulo.app, rx.App)


def test_pagina_raiz_registrada() -> None:
    modulo = importlib.import_module("reservas_ui.reservas_ui")
    ruta = format_route("/")
    pagina = modulo.app._unevaluated_pages.get(ruta)

    assert ruta in modulo.app._page_routes
    assert pagina is not None
    assert pagina.route == ruta


def test_state_declara_todas_sus_vars() -> None:
    faltantes = VARS_DECLARADAS - set(State.__annotations__)
    calculadas_faltantes = VARS_CALCULADAS - set(State.computed_vars)
    mensaje_calculadas = f"Faltan vars calculadas: {sorted(calculadas_faltantes)}"

    assert not faltantes, f"Faltan vars declaradas: {sorted(faltantes)}"
    assert not calculadas_faltantes, mensaje_calculadas


def test_interfaz_tiene_pestanas_y_mensajes_por_formulario() -> None:
    interfaz = str(componentes.pestanas_interfaz())
    identificadores = (
        "tab-reserva",
        "tab-disponibilidad",
        "tab-reservas",
        "panel-reserva",
        "panel-disponibilidad",
        "panel-reservas",
        "form-reserva",
        "form-disponibilidad",
        "mensaje-exito-reserva",
        "mensaje-error-reserva",
        "mensaje-exito-disponibilidad",
        "mensaje-error-disponibilidad",
        "mensaje-exito-cancelacion",
        "mensaje-error-cancelacion",
    )

    faltantes = [
        identificador
        for identificador in identificadores
        if identificador not in interfaz
    ]

    assert not faltantes, f"Faltan identificadores en la interfaz: {faltantes}"
