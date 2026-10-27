"""Componentes de la interfaz de reservas."""

from __future__ import annotations

from typing import Any

import reflex as rx

from reservas_ui.estado import (
    PESTANA_DISPONIBILIDAD,
    PESTANA_RESERVA,
    PESTANA_RESERVAS,
    State,
)


def _campo(etiqueta: str, id_control: str, control: rx.Component) -> rx.Component:
    """Agrupa una etiqueta con su control asociado."""
    return rx.vstack(
        rx.el.label(
            etiqueta,
            html_for=id_control,
            id=f"lbl-{id_control}",
            font_size="14px",
            font_weight="500",
        ),
        control,
        spacing="1",
        align="start",
        width="100%",
    )


def _entrada(
    id_control: str,
    valor: rx.Var[str],
    al_cambiar: rx.EventHandler,
    tipo: str = "text",
    marcador: str = "",
) -> rx.Component:
    """Crea un campo de entrada controlado por el State."""
    return rx.input(
        id=id_control,
        type=tipo,
        value=valor,
        on_change=al_cambiar,
        placeholder=marcador,
        width="100%",
    )


def _selector(
    id_control: str,
    opciones: list[str] | rx.Var[list[str]],
    valor: rx.Var[str],
    al_cambiar: rx.EventHandler,
    marcador: str,
) -> rx.Component:
    """Crea un selector controlado por el State."""
    return rx.select(
        opciones,
        value=valor,
        on_change=al_cambiar,
        placeholder=marcador,
        id=id_control,
        width="100%",
    )


def _zona(
    id_zona: str,
    id_titulo: str,
    titulo: str,
    *contenido: rx.Component,
) -> rx.Component:
    """Agrupa el contenido de una zona en una tarjeta."""
    return rx.card(
        rx.vstack(
            rx.heading(titulo, id=id_titulo, size="5"),
            *contenido,
            align="start",
            spacing="4",
            width="100%",
        ),
        id=id_zona,
        width="100%",
    )


def _conflicto(conflicto: rx.Var[dict[str, Any]]) -> rx.Component:
    return rx.text(
        "Reserva ",
        conflicto["id"],
        " · ",
        conflicto["solicitante"],
        " · ",
        conflicto["inicio"],
        " a ",
        conflicto["fin"],
        size="2",
    )


def _mensajes_formulario(
    prefijo: str,
    exito: rx.Var[str],
    error: rx.Var[str],
) -> rx.Component:
    """Muestra los mensajes propios de un formulario."""
    return rx.vstack(
        rx.cond(
            exito != "",
            rx.callout(
                exito,
                color_scheme="green",
                id=f"mensaje-exito-{prefijo}",
            ),
            rx.fragment(),
        ),
        rx.cond(
            error != "",
            rx.callout(
                error,
                color_scheme="red",
                id=f"mensaje-error-{prefijo}",
            ),
            rx.fragment(),
        ),
        spacing="2",
        width="100%",
    )


def _resultado_disponibilidad() -> rx.Component:
    return rx.vstack(
        _mensajes_formulario(
            "disponibilidad",
            State.mensaje_exito_disponibilidad,
            State.mensaje_error_disponibilidad,
        ),
        rx.cond(
            State.conflictos_disp.length() > 0,
            rx.vstack(
                rx.text("Conflictos detectados", size="2", weight="bold"),
                rx.foreach(State.conflictos_disp, _conflicto),
                align="start",
                id="conflictos-disponibilidad",
                spacing="1",
                width="100%",
            ),
            rx.fragment(),
        ),
        align="start",
        spacing="2",
        width="100%",
    )


def _fila_reserva(reserva: rx.Var[dict[str, Any]]) -> rx.Component:
    activa = reserva["estado"] == "ACTIVA"
    return rx.table.row(
        rx.table.cell(reserva["id"]),
        rx.table.cell(reserva["unidad_id"]),
        rx.table.cell(reserva["solicitante"]),
        rx.table.cell(reserva["inicio"]),
        rx.table.cell(reserva["fin"]),
        rx.table.cell(
            rx.badge(
                reserva["estado"],
                color_scheme=rx.cond(activa, "green", "gray"),
            )
        ),
        rx.table.cell(
            rx.cond(
                activa,
                rx.button(
                    "Cancelar",
                    id=rx.Var.create("cancelar-") + reserva["id"].to_string(),
                    on_click=State.cancelar(reserva["id"]),
                    color_scheme="red",
                    size="1",
                    variant="soft",
                ),
                rx.text("—", color="gray"),
            )
        ),
    )


def _tabla_reservas() -> rx.Component:
    return rx.cond(
        State.reservas.length() == 0,
        rx.text(
            "No hay reservas para los filtros seleccionados.",
            color="gray",
            id="tabla-vacia",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("ID"),
                    rx.table.column_header_cell("Unidad"),
                    rx.table.column_header_cell("Solicitante"),
                    rx.table.column_header_cell("Inicio"),
                    rx.table.column_header_cell("Fin"),
                    rx.table.column_header_cell("Estado"),
                    rx.table.column_header_cell("Acciones"),
                )
            ),
            rx.table.body(rx.foreach(State.reservas, _fila_reserva)),
            id="tabla-reservas",
            width="100%",
        ),
    )


def zona_disponibilidad() -> rx.Component:
    """Formulario y resultado de la consulta de disponibilidad."""
    formulario = rx.el.form(
        rx.vstack(
            _campo(
                "Unidad",
                "disp-unidad",
                _selector(
                    "disp-unidad",
                    State.unidades_ids,
                    State.unidad_seleccionada,
                    State.actualizar_unidad,
                    "Seleccione una unidad",
                ),
            ),
            _campo(
                "Inicio",
                "disp-inicio",
                _entrada(
                    "disp-inicio",
                    State.inicio_disp,
                    State.actualizar_inicio_disp,
                    tipo="datetime-local",
                ),
            ),
            _campo(
                "Fin",
                "disp-fin",
                _entrada(
                    "disp-fin",
                    State.fin_disp,
                    State.actualizar_fin_disp,
                    tipo="datetime-local",
                ),
            ),
            rx.button("Consultar", id="btn-consultar", type="submit"),
            align="start",
            spacing="3",
            width="100%",
        ),
        id="form-disponibilidad",
        on_submit=State.consultar_disponibilidad,
        width="100%",
    )
    return _zona(
        "zona-disponibilidad",
        "titulo-disponibilidad",
        "Disponibilidad",
        formulario,
        _resultado_disponibilidad(),
    )


def zona_reserva() -> rx.Component:
    """Formulario para crear una reserva."""
    formulario = rx.el.form(
        rx.vstack(
            _campo(
                "Unidad",
                "res-unidad",
                _selector(
                    "res-unidad",
                    State.unidades_ids,
                    State.unidad_seleccionada,
                    State.actualizar_unidad,
                    "Seleccione una unidad",
                ),
            ),
            _campo(
                "Solicitante",
                "res-solicitante",
                _entrada(
                    "res-solicitante",
                    State.solicitante,
                    State.actualizar_solicitante,
                    marcador="Nombre del solicitante",
                ),
            ),
            _campo(
                "Inicio",
                "res-inicio",
                _entrada(
                    "res-inicio",
                    State.inicio_res,
                    State.actualizar_inicio_res,
                    tipo="datetime-local",
                ),
            ),
            _campo(
                "Fin",
                "res-fin",
                _entrada(
                    "res-fin",
                    State.fin_res,
                    State.actualizar_fin_res,
                    tipo="datetime-local",
                ),
            ),
            rx.button("Reservar", id="btn-reservar", type="submit"),
            align="start",
            spacing="3",
            width="100%",
        ),
        id="form-reserva",
        on_submit=State.reservar,
        width="100%",
    )
    return _zona(
        "zona-reserva",
        "titulo-reserva",
        "Reservar",
        formulario,
        _mensajes_formulario(
            "reserva",
            State.mensaje_exito_reserva,
            State.mensaje_error_reserva,
        ),
    )


def zona_reservas() -> rx.Component:
    """Filtros y tabla de reservas."""
    filtros = rx.grid(
        _campo(
            "Unidad",
            "filtro-unidad",
            _selector(
                "filtro-unidad",
                State.unidades_ids,
                State.filtro_unidad,
                State.actualizar_filtro_unidad,
                "Todas las unidades",
            ),
        ),
        _campo(
            "Estado",
            "filtro-estado",
            _selector(
                "filtro-estado",
                ["ACTIVA", "CANCELADA"],
                State.filtro_estado,
                State.actualizar_filtro_estado,
                "Todos los estados",
            ),
        ),
        rx.button(
            "Limpiar filtros",
            id="btn-limpiar-filtros",
            on_click=State.limpiar_filtros,
            variant="soft",
        ),
        align="end",
        columns="repeat(auto-fit, minmax(220px, 1fr))",
        spacing="3",
        width="100%",
    )
    return _zona(
        "zona-reservas",
        "titulo-reservas",
        "Reservas",
        filtros,
        _mensajes_formulario(
            "cancelacion",
            State.mensaje_exito_cancelacion,
            State.mensaje_error_cancelacion,
        ),
        _tabla_reservas(),
    )


def pestanas_interfaz() -> rx.Component:
    """Distribuye los formularios y la tabla en tres pestañas."""
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger(
                "Reservar",
                value=PESTANA_RESERVA,
                id="tab-reserva",
            ),
            rx.tabs.trigger(
                "Disponibilidad",
                value=PESTANA_DISPONIBILIDAD,
                id="tab-disponibilidad",
            ),
            rx.tabs.trigger(
                "Reservas",
                value=PESTANA_RESERVAS,
                id="tab-reservas",
            ),
            id="lista-pestanas",
            width="100%",
        ),
        rx.tabs.content(
            zona_reserva(),
            value=PESTANA_RESERVA,
            id="panel-reserva",
            padding_top="4",
        ),
        rx.tabs.content(
            zona_disponibilidad(),
            value=PESTANA_DISPONIBILIDAD,
            id="panel-disponibilidad",
            padding_top="4",
        ),
        rx.tabs.content(
            zona_reservas(),
            value=PESTANA_RESERVAS,
            id="panel-reservas",
            padding_top="4",
        ),
        value=State.pestana_activa,
        on_change=State.cambiar_pestana,
        id="pestanas-interfaz",
        width="100%",
    )
