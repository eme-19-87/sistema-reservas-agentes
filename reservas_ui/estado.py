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
            self.unidades = [{"id": k, "equipo": v.get("equipo")} for k, v in inv.items()]
            if self.unidades and not self.unidad_seleccionada:
                self.unidad_seleccionada = self.unidades[0]["id"]
        except Exception:
            self.unidades = []
        try:
            filas = presentacion.listar_filas(servicio)
            self.reservas = filas
        except Exception:
            self.reservas = []
        self.mensaje_error = ""
        self.mensaje_exito = ""
        self.resultado_disp = ""
        self.conflictos_disp = []

    def _limpiar_mensajes_disp(self) -> None:
        for attr, value in [
            ("mensaje_error", ""),
            ("mensaje_exito", ""),
            ("resultado_disp", ""),
            ("conflictos_disp", []),
        ]:
            try:
                object.__setattr__(self, attr, value)
            except Exception:
                try:
                    setattr(self, attr, value)
                except Exception:
                    pass

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
        msg = res.get("mensaje", "")
        try:
            object.__setattr__(self, "mensaje_error", msg)
        except Exception:
            pass
        try:
            object.__setattr__(self, "resultado_disp", msg)
        except Exception:
            pass
        try:
            object.__setattr__(self, "conflictos_disp", res.get("conflictos") or [])
        except Exception:
            pass

    def _aplicar_disponible_disp(self, res: dict[str, Any]) -> None:
        msg = res.get("mensaje", "Disponible.")
        try:
            object.__setattr__(self, "mensaje_exito", msg)
        except Exception:
            pass
        try:
            object.__setattr__(self, "resultado_disp", msg)
        except Exception:
            pass
        try:
            object.__setattr__(self, "conflictos_disp", [])
        except Exception:
            pass

    def _aplicar_no_disponible_disp(self, res: dict[str, Any]) -> None:
        msg = res.get("mensaje", "No disponible.")
        try:
            object.__setattr__(self, "mensaje_error", msg)
        except Exception:
            pass
        try:
            object.__setattr__(self, "resultado_disp", msg)
        except Exception:
            pass
        try:
            object.__setattr__(self, "conflictos_disp", res.get("conflictos") or [])
        except Exception:
            pass

    def _aplicar_resultado_disp(self, res: dict[str, Any]) -> None:
        if res.get("error"):
            self._aplicar_error_disp(res)
            return
        if res.get("disponible"):
            self._aplicar_disponible_disp(res)
            return
        self._aplicar_no_disponible_disp(res)

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
            try:
                msg = presentacion.mensaje_error(exc)
            except Exception:
                msg = str(exc)
            try:
                object.__setattr__(self, "mensaje_error", msg)
            except Exception:
                pass
            try:
                object.__setattr__(self, "resultado_disp", msg)
            except Exception:
                pass
            try:
                object.__setattr__(self, "conflictos_disp", [])
            except Exception:
                pass
