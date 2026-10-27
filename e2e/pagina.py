"""Acciones de alto nivel sobre la interfaz de reservas."""

from __future__ import annotations

from datetime import date, timedelta

from playwright.sync_api import Page, expect


def fecha_futura(hora: str, dias: int = 2) -> str:
    """Devuelve una fecha futura en el formato que acepta la interfaz."""
    dia = date.today() + timedelta(days=dias)
    return f"{dia.isoformat()}T{hora}"


class PaginaReservas:
    """Envuelve las interacciones de Playwright con la página de reservas."""

    def __init__(self, pagina: Page, url: str) -> None:
        self.pagina = pagina
        self.url = url

    def abrir(self) -> None:
        """Carga la página y espera a que Reflex hidrate los controles."""
        self.pagina.goto(self.url, wait_until="domcontentloaded")
        expect(self.pagina.locator("#titulo-pagina")).to_have_text(
            "Sistema de reservas de laboratorio"
        )
        self.pagina.wait_for_timeout(1500)

    def abrir_pestana(self, clave: str) -> None:
        """Activa una de las tres pestañas."""
        self.pagina.locator(f"#tab-{clave}").click()
        expect(self.pagina.locator(f"#panel-{clave}")).to_be_visible()

    def seleccionar_opcion(self, id_control: str, texto: str) -> None:
        """Abre un selector de Radix y elige una opción por su texto."""
        self.pagina.locator(f"#{id_control}").click()
        opcion = self.pagina.get_by_role("option", name=texto, exact=True)
        expect(opcion).to_be_visible()
        opcion.click()

    def opciones_unidad(self) -> list[str]:
        """Devuelve las unidades disponibles en el selector de reserva."""
        self.abrir_pestana("reserva")
        self.pagina.locator("#res-unidad").click()
        opciones = self.pagina.get_by_role("option")
        expect(opciones).to_have_count(5)
        textos = [texto.strip() for texto in opciones.all_inner_texts()]
        self.pagina.keyboard.press("Escape")
        return textos

    def reservar(
        self,
        unidad: str,
        solicitante: str,
        inicio: str,
        fin: str,
    ) -> None:
        """Completa y envía el formulario de reserva."""
        self.abrir_pestana("reserva")
        self.seleccionar_opcion("res-unidad", unidad)
        self.pagina.locator("#res-solicitante").fill(solicitante)
        self.pagina.locator("#res-inicio").fill(inicio)
        self.pagina.locator("#res-fin").fill(fin)
        self.pagina.locator("#btn-reservar").click()

    def consultar(self, unidad: str, inicio: str, fin: str) -> None:
        """Completa y envía el formulario de disponibilidad."""
        self.abrir_pestana("disponibilidad")
        self.seleccionar_opcion("disp-unidad", unidad)
        self.pagina.locator("#disp-inicio").fill(inicio)
        self.pagina.locator("#disp-fin").fill(fin)
        self.pagina.locator("#btn-consultar").click()

    def cancelar(self, reserva_id: int) -> None:
        """Pulsa el botón Cancelar de una reserva concreta."""
        self.abrir_pestana("reservas")
        self.pagina.locator(f"#cancelar-{reserva_id}").click()
        expect(self.pagina.locator("#mensaje-exito-cancelacion")).to_contain_text(
            "Reserva cancelada."
        )

    def filas(self) -> list[dict[str, str]]:
        """Lee la tabla de reservas y devuelve sus filas como diccionarios."""
        self.abrir_pestana("reservas")
        self.pagina.locator("#tabla-vacia, #tabla-reservas").first.wait_for(
            state="visible"
        )
        if self.pagina.locator("#tabla-vacia").is_visible():
            return []
        filas: list[dict[str, str]] = []
        for fila in self.pagina.locator("#tabla-reservas tbody tr").all():
            celdas = [celda.strip() for celda in fila.locator("td").all_inner_texts()]
            if len(celdas) >= 6:
                filas.append(
                    {
                        "id": celdas[0],
                        "unidad": celdas[1],
                        "solicitante": celdas[2],
                        "inicio": celdas[3],
                        "fin": celdas[4],
                        "estado": celdas[5],
                    }
                )
        return filas

    def fila(self, reserva_id: int) -> dict[str, str]:
        """Devuelve la fila de una reserva concreta."""
        for fila in self.filas():
            if fila["id"] == str(reserva_id):
                return fila
        raise AssertionError(f"No se encontró la reserva {reserva_id}.")

    def tiene_boton_cancelar(self, reserva_id: int) -> bool:
        """Indica si la fila de una reserva ofrece la acción Cancelar."""
        return self.pagina.locator(f"#cancelar-{reserva_id}").count() > 0

    def limpiar_filtros(self) -> None:
        """Pulsa el botón que restablece los filtros de la tabla."""
        self.pagina.locator("#btn-limpiar-filtros").click()

    def esperar_mensaje(
        self, selector: str, texto: str | None = None
    ) -> dict[str, str]:
        """Espera un mensaje visible y devuelve su identificador y contenido."""
        mensaje = self.pagina.locator(selector)
        expect(mensaje).to_be_visible()
        if texto is not None:
            expect(mensaje).to_contain_text(texto)
        return {"selector": selector, "texto": mensaje.inner_text().strip()}

    def esperar_exito_reserva(self, texto: str) -> None:
        self.esperar_mensaje("#mensaje-exito-reserva", texto)

    def esperar_error_reserva(self, texto: str) -> None:
        self.esperar_mensaje("#mensaje-error-reserva", texto)

    def esperar_error_disponibilidad(self, texto: str) -> None:
        self.esperar_mensaje("#mensaje-error-disponibilidad", texto)

    def esperar_exito_disponibilidad(self, texto: str) -> None:
        self.esperar_mensaje("#mensaje-exito-disponibilidad", texto)

    def texto_visible(self, selector: str) -> str:
        """Devuelve el texto de un elemento visible o una cadena vacía."""
        elemento = self.pagina.locator(selector)
        if not elemento.is_visible():
            return ""
        return elemento.inner_text().strip()
