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

    def consultar_disponibilidad(self):
        try:
            object.__setattr__(self, "mensaje_error", "")
        except Exception:
            try:
                self.mensaje_error = ""
            except Exception:
                pass
        try:
            object.__setattr__(self, "mensaje_exito", "")
        except Exception:
            try:
                self.mensaje_exito = ""
            except Exception:
                pass
        try:
            object.__setattr__(self, "resultado_disp", "")
        except Exception:
            try:
                self.resultado_disp = ""
            except Exception:
                pass
        try:
            object.__setattr__(self, "conflictos_disp", [])
        except Exception:
            try:
                self.conflictos_disp = []
            except Exception:
                pass
        try:
            unidades = getattr(self, "unidades", None) or []
            unidad = getattr(self, "unidad_seleccionada", "") or (unidades[0].get("id") if unidades else "")
        except Exception:
            unidad = getattr(self, "unidad_seleccionada", "") or ""
        try:
            res = presentacion.consultar(servicio, unidad, getattr(self, "inicio_disp", ""), getattr(self, "fin_disp", ""))
            if res.get("error"):
                try:
                    object.__setattr__(self, "mensaje_error", res.get("mensaje", ""))
                except Exception:
                    pass
                try:
                    object.__setattr__(self, "resultado_disp", res.get("mensaje", ""))
                except Exception:
                    pass
                try:
                    object.__setattr__(self, "conflictos_disp", res.get("conflictos") or [])
                except Exception:
                    pass
                return
            if res.get("disponible"):
                try:
                    object.__setattr__(self, "mensaje_exito", res.get("mensaje", "Disponible."))
                except Exception:
                    pass
                try:
                    object.__setattr__(self, "resultado_disp", res.get("mensaje", "Disponible."))
                except Exception:
                    pass
                try:
                    object.__setattr__(self, "conflictos_disp", [])
                except Exception:
                    pass
                return
            try:
                object.__setattr__(self, "mensaje_error", res.get("mensaje", "No disponible."))
            except Exception:
                pass
            try:
                object.__setattr__(self, "resultado_disp", res.get("mensaje", "No disponible."))
            except Exception:
                pass
            try:
                object.__setattr__(self, "conflictos_disp", res.get("conflictos") or [])
            except Exception:
                pass
        except Exception as exc:
            try:
                msg = presentacion.mensaje_error(exc)
                object.__setattr__(self, "mensaje_error", msg)
            except Exception:
                pass
            try:
                object.__setattr__(self, "resultado_disp", getattr(self, "mensaje_error", ""))
            except Exception:
                pass
            try:
                object.__setattr__(self, "conflictos_disp", [])
            except Exception:
                pass
