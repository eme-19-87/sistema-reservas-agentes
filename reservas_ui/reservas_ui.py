"""Aplicación Reflex para el sistema de reservas."""

import reflex as rx

from reservas_ui import componentes
from reservas_ui.estado import State


def index() -> rx.Component:
    """Página principal con las tres zonas de la interfaz."""
    return rx.center(
        rx.vstack(
            rx.heading(
                "Sistema de reservas de laboratorio",
                id="titulo-pagina",
                size="8",
            ),
            rx.text(
                "Consulta disponibilidad, reserva y cancela equipos del laboratorio.",
                color="gray",
                id="subtitulo-pagina",
            ),
            componentes.zona_mensajes(),
            componentes.zona_disponibilidad(),
            componentes.zona_reserva(),
            componentes.zona_reservas(),
            align="start",
            max_width="1000px",
            spacing="5",
            width="100%",
        ),
        min_height="100vh",
        padding="6",
        width="100%",
    )


app = rx.App()
app.add_page(
    index,
    route="/",
    title="Reservas de laboratorio",
    on_load=State.on_load,
)
