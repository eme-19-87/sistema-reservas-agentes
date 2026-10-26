"""Capa de presentación (funciones puras)."""

from __future__ import annotations

import logging
from typing import Any, Callable

from reservas import dominio

logger = logging.getLogger(__name__)

MENSAJE_ERROR_INESPERADO = (
    "Error inesperado: la operación no se completó. "
    "Consulte el registro del servidor para más detalles."
)


def mensaje_error(exc: Exception) -> str:
    if isinstance(exc, dominio.UnidadDesconocida):
        return "Unidad desconocida."
    if isinstance(exc, dominio.SolicitanteInvalido):
        return "Solicitante inválido."
    if isinstance(exc, dominio.FechaInvalida):
        return "Fecha inválida."
    if isinstance(exc, dominio.IntervaloInvalido):
        return "Intervalo inválido."
    if isinstance(exc, dominio.LimiteExcedido):
        return "Límite excedido."
    if isinstance(exc, dominio.Superposicion):
        conflictos = getattr(exc, "reservas_conflicto", []) or []
        if conflictos:
            cid = conflictos[0].get("id")
            if cid is not None:
                return f"Superposición con la reserva activa {cid}."
        return str(exc) or "Superposición con una reserva activa."
    if isinstance(exc, dominio.ReservaNoEncontrada):
        return "Reserva no encontrada."
    if isinstance(exc, dominio.ReservaYaCancelada):
        return "Reserva ya cancelada."
    logger.error("Error inesperado en la interfaz: %s", exc, exc_info=True)
    return MENSAJE_ERROR_INESPERADO


def consultar(
    servicio: Any,
    unidad_id: str,
    inicio: str,
    fin: str,
    reloj: Callable | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    try:
        res = servicio.consultar_disponibilidad(unidad_id, inicio, fin, reloj=reloj)
        if res.get("disponible"):
            return {"disponible": True, "mensaje": "Disponible.", "conflictos": []}
        conflictos = res.get("conflictos") or []
        if conflictos:
            cid = conflictos[0].get("id")
            if cid is not None:
                msg = f"No disponible: se superpone con la reserva activa {cid}."
            else:
                msg = "No disponible."
        else:
            msg = "No disponible."
        return {"disponible": False, "mensaje": msg, "conflictos": conflictos}
    except Exception as exc:
        return {
            "disponible": None,
            "mensaje": mensaje_error(exc),
            "conflictos": [],
            "error": True,
        }


def reservar(
    servicio: Any,
    unidad_id: str,
    solicitante: str,
    inicio: str,
    fin: str,
    reloj: Callable | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    try:
        res = servicio.crear_reserva(unidad_id, solicitante, inicio, fin, reloj=reloj)
        rid = res.get("id") if isinstance(res, dict) else None
        msg = f"Reserva creada con ID {rid}." if rid is not None else "Reserva creada."
        return {"ok": True, "mensaje": msg, "reserva": res}
    except Exception as exc:
        return {"ok": False, "mensaje": mensaje_error(exc)}


def cancelar(
    servicio: Any, reserva_id: int, reloj: Callable | None = None, **kwargs: Any
) -> dict[str, Any]:
    try:
        res = servicio.cancelar_reserva(reserva_id, reloj=reloj)
        return {"ok": True, "mensaje": "Reserva cancelada.", "reserva": res}
    except Exception as exc:
        return {"ok": False, "mensaje": mensaje_error(exc)}


def listar_filas(
    servicio: Any,
    unidad_id: str | None = None,
    estado: str | None = None,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    reservas = servicio.listar_reservas(unidad_id=unidad_id, estado=estado)
    filas = []
    for r in reservas:
        filas.append(
            {
                "id": r.get("id"),
                "unidad_id": r.get("unidad_id") or r.get("unidad"),
                "solicitante": r.get("solicitante"),
                "inicio": r.get("inicio"),
                "fin": r.get("fin"),
                "estado": r.get("estado"),
            }
        )
    return filas
