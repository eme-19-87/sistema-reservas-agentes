"""Aplicación Reflex para el sistema de reservas."""
import reflex as rx


class State(rx.State):
    """Estado de la aplicación."""

    pass


def index() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("Sistema de reservas de laboratorio", size="9"),
            rx.text("Aplicación local con Reflex"),
            align="center",
            spacing="7",
        ),
        height="85vh",
    )


app = rx.App()
app.add_page(index)
