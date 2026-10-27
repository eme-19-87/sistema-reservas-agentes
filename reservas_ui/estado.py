"""Estado de la aplicación (handlers delgados)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import reflex as rx

from reservas import servicio
from reservas.repositorio import inicializar_bd
from reservas_ui import presentacion

PESTANA_RESERVA = "reserva"
PESTANA_DISPONIBILIDAD = "disponibilidad"
PESTANA_RESERVAS = "reservas"
PESTANAS = frozenset({PESTANA_RESERVA, PESTANA_DISPONIBILIDAD, PESTANA_RESERVAS})


@dataclass(frozen=True)
class MensajesFormulario:
    """Nombres de los campos de mensaje de un formulario."""

    exito: str
    error: str


MENSAJES_RESERVA = MensajesFormulario("mensaje_exito_reserva", "mensaje_error_reserva")
MENSAJES_DISPONIBILIDAD = MensajesFormulario(
    "mensaje_exito_disponibilidad", "mensaje_error_disponibilidad"
)
MENSAJES_CANCELACION = MensajesFormulario(
    "mensaje_exito_cancelacion", "mensaje_error_cancelacion"
)


class State(rx.State):
    unidades: list[dict[str, Any]] = []
    reservas: list[dict[str, Any]] = []
    unidad_seleccionada: str = ""
    solicitante: str = ""
    inicio_disp: str = ""
    fin_disp: str = ""
    inicio_res: str = ""
    fin_res: str = ""
    filtro_unidad: str = ""
    filtro_estado: str = ""
    pestana_activa: str = PESTANA_RESERVA
    mensaje_exito_reserva: str = ""
    mensaje_error_reserva: str = ""
    mensaje_exito_disponibilidad: str = ""
    mensaje_error_disponibilidad: str = ""
    mensaje_exito_cancelacion: str = ""
    mensaje_error_cancelacion: str = ""
    conflictos_disp: list[dict[str, Any]] = []

    @rx.var
    def unidades_ids(self) -> list[str]:
        return [unidad["id"] for unidad in self.unidades]

    def on_load(self):
        inicializar_bd()
        try:
            from reservas.inventario import obtener_inventario

            inv = obtener_inventario()
            self.unidades = [
                {"id": k, "equipo": v.get("equipo")} for k, v in inv.items()
            ]
            if self.unidades and not self.unidad_seleccionada:
                self.unidad_seleccionada = self.unidades[0]["id"]
        except Exception:
            self.unidades = []
        self._recargar_reservas()
        self._limpiar_todos_los_mensajes()

    def _asignar_var(self, attr: str, value: Any) -> None:
        try:
            object.__setattr__(self, attr, value)
        except Exception:
            try:
                setattr(self, attr, value)
            except Exception:
                pass

    def _limpiar_mensajes(self, campos: MensajesFormulario) -> None:
        self._asignar_var(campos.exito, "")
        self._asignar_var(campos.error, "")

    def _limpiar_todos_los_mensajes(self) -> None:
        for campos in (
            MENSAJES_RESERVA,
            MENSAJES_DISPONIBILIDAD,
            MENSAJES_CANCELACION,
        ):
            self._limpiar_mensajes(campos)
        self._asignar_var("conflictos_disp", [])

    def _mostrar_exito(self, campos: MensajesFormulario, mensaje: str) -> None:
        self._asignar_var(campos.error, "")
        self._asignar_var(campos.exito, mensaje)

    def _mostrar_error(self, campos: MensajesFormulario, mensaje: str) -> None:
        self._asignar_var(campos.exito, "")
        self._asignar_var(campos.error, mensaje)

    def _mostrar_exito_disponibilidad(self, mensaje: str) -> None:
        self._mostrar_exito(MENSAJES_DISPONIBILIDAD, mensaje)
        self._asignar_var("conflictos_disp", [])

    def _mostrar_error_disponibilidad(
        self, mensaje: str, conflictos: list[Any] | None = None
    ) -> None:
        self._mostrar_error(MENSAJES_DISPONIBILIDAD, mensaje)
        self._asignar_var("conflictos_disp", conflictos or [])

    def _unidad_desde_lista(self, unidades: list[Any]) -> str:
        if not unidades:
            return ""
        unidad = unidades[0]
        if isinstance(unidad, dict):
            return unidad.get("id") or ""
        return getattr(unidad, "id", "") or ""

    def _obtener_unidad_consulta(self) -> str:
        try:
            unidades = getattr(self, "unidades", None) or []
            if getattr(self, "unidad_seleccionada", ""):
                return self.unidad_seleccionada
            unidad_id = self._unidad_desde_lista(unidades)
            if unidad_id:
                return unidad_id
        except Exception:
            pass
        return getattr(self, "unidad_seleccionada", "") or ""

    def _aplicar_error_disp(self, res: dict[str, Any]) -> None:
        self._mostrar_error_disponibilidad(
            res.get("mensaje", ""), res.get("conflictos") or []
        )

    def _aplicar_disponible_disp(self, res: dict[str, Any]) -> None:
        self._mostrar_exito_disponibilidad(res.get("mensaje", "Disponible."))

    def _aplicar_no_disponible_disp(self, res: dict[str, Any]) -> None:
        self._mostrar_error_disponibilidad(
            res.get("mensaje", "No disponible."),
            res.get("conflictos") or [],
        )

    def _aplicar_resultado_disp(self, res: dict[str, Any]) -> None:
        if res.get("error"):
            self._aplicar_error_disp(res)
            return
        if res.get("disponible"):
            self._aplicar_disponible_disp(res)
            return
        self._aplicar_no_disponible_disp(res)

    def _mensaje_de_error(self, exc: Exception) -> str:
        try:
            return presentacion.mensaje_error(exc)
        except Exception:
            return str(exc)

    def cambiar_pestana(self, pestana: str) -> None:
        if pestana not in PESTANAS:
            return
        self.pestana_activa = pestana

    def actualizar_unidad(self, valor: str) -> None:
        self.unidad_seleccionada = valor

    def actualizar_solicitante(self, valor: str) -> None:
        self.solicitante = valor

    def actualizar_inicio_disp(self, valor: str) -> None:
        self.inicio_disp = valor

    def actualizar_fin_disp(self, valor: str) -> None:
        self.fin_disp = valor

    def actualizar_inicio_res(self, valor: str) -> None:
        self.inicio_res = valor

    def actualizar_fin_res(self, valor: str) -> None:
        self.fin_res = valor

    def consultar_disponibilidad(self):
        self._limpiar_mensajes(MENSAJES_DISPONIBILIDAD)
        self._asignar_var("conflictos_disp", [])
        unidad = self._obtener_unidad_consulta()
        try:
            res = presentacion.consultar(
                servicio,
                unidad,
                getattr(self, "inicio_disp", ""),
                getattr(self, "fin_disp", ""),
            )
            self._aplicar_resultado_disp(res)
        except Exception as exc:
            self._mostrar_error_disponibilidad(self._mensaje_de_error(exc))

    def _limpiar_campos_reserva(self) -> None:
        for attr in ("solicitante", "inicio_res", "fin_res"):
            self._asignar_var(attr, "")

    def _recargar_reservas(self) -> None:
        try:
            self.reservas = presentacion.listar_filas(
                servicio,
                unidad_id=getattr(self, "filtro_unidad", "") or None,
                estado=getattr(self, "filtro_estado", "") or None,
            )
        except Exception:
            self.reservas = []

    def _aplicar_resultado_reserva(self, res: dict[str, Any]) -> None:
        if not res.get("ok"):
            self._mostrar_error(
                MENSAJES_RESERVA, res.get("mensaje", "No se pudo crear la reserva.")
            )
            return
        self._mostrar_exito(MENSAJES_RESERVA, res.get("mensaje", "Reserva creada."))
        self._recargar_reservas()
        self._limpiar_campos_reserva()

    def reservar(self):
        self._limpiar_mensajes(MENSAJES_RESERVA)
        unidad = self._obtener_unidad_consulta()
        try:
            res = presentacion.reservar(
                servicio,
                unidad,
                getattr(self, "solicitante", ""),
                getattr(self, "inicio_res", ""),
                getattr(self, "fin_res", ""),
            )
        except Exception as exc:
            self._mostrar_error(MENSAJES_RESERVA, self._mensaje_de_error(exc))
            return
        self._aplicar_resultado_reserva(res)

    def _aplicar_resultado_cancelacion(self, res: dict[str, Any]) -> None:
        if not res.get("ok"):
            self._mostrar_error(
                MENSAJES_CANCELACION,
                res.get("mensaje", "No se pudo cancelar la reserva."),
            )
            return
        self._mostrar_exito(
            MENSAJES_CANCELACION, res.get("mensaje", "Reserva cancelada.")
        )
        self._recargar_reservas()

    def cancelar(self, reserva_id: int):
        self._limpiar_mensajes(MENSAJES_CANCELACION)
        try:
            res = presentacion.cancelar(servicio, reserva_id)
        except Exception as exc:
            self._mostrar_error(MENSAJES_CANCELACION, self._mensaje_de_error(exc))
            return
        self._aplicar_resultado_cancelacion(res)

    def aplicar_filtros(self):
        self._recargar_reservas()

    def actualizar_filtro_unidad(self, valor: str) -> None:
        self.filtro_unidad = valor
        self.aplicar_filtros()

    def actualizar_filtro_estado(self, valor: str) -> None:
        self.filtro_estado = valor
        self.aplicar_filtros()

    def limpiar_filtros(self) -> None:
        self.filtro_unidad = ""
        self.filtro_estado = ""
        self.aplicar_filtros()
