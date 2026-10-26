"""Estado de la aplicación (handlers delgados)."""
from __future__ import annotations

from typing import Any

import reflex as rx

from reservas import servicio
from reservas.repositorio import inicializar_bd
from reservas_ui import presentacion


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
    mensaje_error: str = ""
    mensaje_exito: str = ""
    resultado_disp: str = ""
    conflictos_disp: list[dict[str, Any]] = []

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
        self._limpiar_mensajes_disp()

    def _asignar_var(self, attr: str, value: Any) -> None:
        try:
            object.__setattr__(self, attr, value)
        except Exception:
            try:
                setattr(self, attr, value)
            except Exception:
                pass

    def _limpiar_mensajes(self) -> None:
        self._asignar_var("mensaje_error", "")
        self._asignar_var("mensaje_exito", "")

    def _limpiar_mensajes_disp(self) -> None:
        self._limpiar_mensajes()
        self._asignar_var("resultado_disp", "")
        self._asignar_var("conflictos_disp", [])

    def _asignar_vars_disp(
        self, campo_mensaje: str, msg: str, conflictos: list[Any]
    ) -> None:
        self._asignar_var(campo_mensaje, msg)
        self._asignar_var("resultado_disp", msg)
        self._asignar_var("conflictos_disp", conflictos)

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
        self._asignar_vars_disp(
            "mensaje_error", res.get("mensaje", ""), res.get("conflictos") or []
        )

    def _aplicar_disponible_disp(self, res: dict[str, Any]) -> None:
        self._asignar_vars_disp(
            "mensaje_exito", res.get("mensaje", "Disponible."), []
        )

    def _aplicar_no_disponible_disp(self, res: dict[str, Any]) -> None:
        self._asignar_vars_disp(
            "mensaje_error",
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

    def consultar_disponibilidad(self):
        self._limpiar_mensajes_disp()
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
            self._asignar_vars_disp("mensaje_error", self._mensaje_de_error(exc), [])

    def _limpiar_campos_reserva(self) -> None:
        for attr in ("solicitante", "inicio_res", "fin_res"):
            self._asignar_var(attr, "")

    def _recargar_reservas(self) -> None:
        try:
            self.reservas = presentacion.listar_filas(servicio)
        except Exception:
            self.reservas = []

    def _aplicar_exito_reserva(self, res: dict[str, Any]) -> None:
        self._asignar_var("mensaje_error", "")
        self._asignar_var("mensaje_exito", res.get("mensaje", "Reserva creada."))
        self._limpiar_campos_reserva()
        self._recargar_reservas()

    def _aplicar_error_reserva(self, mensaje: str) -> None:
        self._asignar_var("mensaje_exito", "")
        self._asignar_var("mensaje_error", mensaje)

    def _aplicar_resultado_reserva(self, res: dict[str, Any]) -> None:
        if res.get("ok"):
            self._aplicar_exito_reserva(res)
            return
        self._aplicar_error_reserva(res.get("mensaje", "No se pudo crear la reserva."))

    def reservar(self):
        self._limpiar_mensajes()
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
            self._aplicar_error_reserva(self._mensaje_de_error(exc))
            return
        self._aplicar_resultado_reserva(res)
