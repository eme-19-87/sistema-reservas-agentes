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
