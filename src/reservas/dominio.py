"""Dominio: entidades, excepciones, parseo de fechas y validaciones."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Iterable


from .inventario import obtener_inventario


class ErrorDominio(Exception):
    """Excepción base del dominio."""


class UnidadDesconocida(ErrorDominio):
    """La unidad no existe en el inventario."""


class SolicitanteInvalido(ErrorDominio):
    """El solicitante no cumple las reglas."""


class FechaInvalida(ErrorDominio):
    """La fecha/hora no es válida."""


class IntervaloInvalido(ErrorDominio):
    """El intervalo no es válido."""


class LimiteExcedido(ErrorDominio):
    """Se exceden límites de tiempo."""


class Superposicion(ErrorDominio):
    """Superposición con una reserva activa."""

    def __init__(self, mensaje: str, reservas_conflicto: list[dict] | None = None):
        super().__init__(mensaje)
        self.reservas_conflicto = reservas_conflicto or []


class ReservaNoEncontrada(ErrorDominio):
    """La reserva no existe."""


class ReservaYaCancelada(ErrorDominio):
    """La reserva ya está cancelada."""


FORMATO_FECHA = "%Y-%m-%dT%H:%M"
DURACION_MAXIMA_HORAS = 8
ANTICIPACION_MAXIMA_DIAS = 90


@dataclass
class ContextoValidacion:
    unidad_id: str
    inicio: str | datetime
    fin: str | datetime
    solicitante: str | None = None
    ahora: datetime | None = None
    reloj: Callable[[], datetime] | None = None
    inventario: dict[str, dict] | None = None
    reservas_activas: Iterable[dict] | None = None


def _validar_tipo_cadena(cadena: str) -> None:
    if not isinstance(cadena, str):
        raise FechaInvalida("Fecha inválida.")


def _tiene_offset(cadena: str) -> bool:
    if cadena.endswith("Z"):
        return True
    if "+" in cadena:
        return True
    return False


def _validar_sin_offset(cadena: str) -> None:
    if _tiene_offset(cadena):
        raise FechaInvalida("Fecha inválida.")
    if cadena.count("-") > 2:
        raise FechaInvalida("Fecha inválida.")


def parsear_fecha_hora(cadena: str) -> datetime:
    """Parsea fecha/hora en formato YYYY-MM-DDTHH:MM sin zona horaria."""
    _validar_tipo_cadena(cadena)
    _validar_sin_offset(cadena)
    try:
        fecha = datetime.strptime(cadena, FORMATO_FECHA)
    except ValueError as exc:
        raise FechaInvalida("Fecha inválida.") from exc
    if fecha.strftime(FORMATO_FECHA) != cadena:
        raise FechaInvalida("Fecha inválida.")
    return fecha


def _validar_solicitante_no_vacio(solicitante: str) -> str:
    if not isinstance(solicitante, str):
        raise SolicitanteInvalido("Solicitante inválido.")
    if solicitante.strip() == "":
        raise SolicitanteInvalido("Solicitante inválido.")
    return solicitante.strip()


def _validar_solicitante_sin_numeros_y_especiales(normalizado: str) -> None:
    if normalizado.isdigit():
        raise SolicitanteInvalido("Solicitante inválido.")
    if re.search(r"[^A-Za-zÁÉÍÓÚÜáéíóúüÑñ\s\-']", normalizado):
        raise SolicitanteInvalido("Solicitante inválido.")
    if re.match(r"^[\s\-\d]+$", normalizado):
        raise SolicitanteInvalido("Solicitante inválido.")


def validar_solicitante(solicitante: str) -> str:
    """Valida y normaliza el solicitante."""
    normalizado = _validar_solicitante_no_vacio(solicitante)
    _validar_solicitante_sin_numeros_y_especiales(normalizado)
    return normalizado


def validar_unidad_conocida(unidad_id: str, inventario: dict[str, dict] | None = None) -> str:
    if inventario is None:
        inventario = obtener_inventario()
    if unidad_id not in inventario:
        raise UnidadDesconocida("Unidad desconocida.")
    return unidad_id


def truncar_al_minuto(fecha: datetime) -> datetime:
    return fecha.replace(second=0, microsecond=0)


def _obtener_inventario(contexto: ContextoValidacion) -> dict[str, dict]:
    if contexto.inventario is None:
        return obtener_inventario()
    return contexto.inventario


def _obtener_ahora(contexto: ContextoValidacion) -> datetime:
    if contexto.reloj is not None and contexto.ahora is None:
        ahora = contexto.reloj()
    elif contexto.ahora is not None:
        ahora = contexto.ahora
    else:
        ahora = datetime.now()
    return truncar_al_minuto(ahora)


def _parsear_intervalo(contexto: ContextoValidacion) -> tuple[datetime, datetime]:
    if isinstance(contexto.inicio, str):
        inicio_dt = parsear_fecha_hora(contexto.inicio)
    else:
        inicio_dt = truncar_al_minuto(contexto.inicio)
    if isinstance(contexto.fin, str):
        fin_dt = parsear_fecha_hora(contexto.fin)
    else:
        fin_dt = truncar_al_minuto(contexto.fin)
    return inicio_dt, fin_dt


def _validar_solicitante_si_presente(contexto: ContextoValidacion) -> None:
    if contexto.solicitante is not None:
        validar_solicitante(contexto.solicitante)


def _validar_orden_intervalo(inicio_dt: datetime, fin_dt: datetime) -> None:
    if inicio_dt >= fin_dt:
        raise IntervaloInvalido("Intervalo inválido.")


def _validar_limites_tiempo(inicio_dt: datetime, fin_dt: datetime, ahora_trunc: datetime) -> None:
    if inicio_dt < ahora_trunc:
        raise LimiteExcedido("Límite excedido.")
    duracion = fin_dt - inicio_dt
    if duracion > timedelta(hours=DURACION_MAXIMA_HORAS):
        raise LimiteExcedido("Límite excedido.")
    if inicio_dt > ahora_trunc + timedelta(days=ANTICIPACION_MAXIMA_DIAS):
        raise LimiteExcedido("Límite excedido.")


def _validar_sin_solapamiento(
    unidad_id: str,
    inicio_dt: datetime,
    fin_dt: datetime,
    reservas_activas: Iterable[dict] | None,
) -> None:
    if not reservas_activas:
        return
    for reserva in reservas_activas:
        if reserva.get("unidad_id") != unidad_id and reserva.get("unidad") != unidad_id:
            continue
        if reserva.get("estado") and reserva.get("estado") != "ACTIVA":
            continue
        r_inicio = reserva.get("inicio")
        r_fin = reserva.get("fin")
        if isinstance(r_inicio, str):
            r_inicio = parsear_fecha_hora(r_inicio)
        if isinstance(r_fin, str):
            r_fin = parsear_fecha_hora(r_fin)
        if hay_solapamiento(inicio_dt, fin_dt, r_inicio, r_fin):
            raise Superposicion(
                f"Superposición con la reserva activa {reserva.get('id')}.",
                [reserva],
            )


def validar_solicitud_intervalo(
    unidad_id: str | ContextoValidacion,
    inicio: str | datetime | None = None,
    fin: str | datetime | None = None,
    solicitante: str | None = None,
    ahora: datetime | None = None,
    reloj: Callable[[], datetime] | None = None,
    inventario: dict[str, dict] | None = None,
    reservas_activas: Iterable[dict] | None = None,
) -> tuple[datetime, datetime]:
    """Valida una solicitud. Si solicitante es None, se omite (consulta)."""
    if isinstance(unidad_id, ContextoValidacion):
        contexto = unidad_id
    else:
        contexto = ContextoValidacion(
            unidad_id=unidad_id,
            inicio=inicio,
            fin=fin,
            solicitante=solicitante,
            ahora=ahora,
            reloj=reloj,
            inventario=inventario,
            reservas_activas=reservas_activas,
        )
    inventario_efectivo = _obtener_inventario(contexto)
    validar_unidad_conocida(contexto.unidad_id, inventario_efectivo)
    _validar_solicitante_si_presente(contexto)
    inicio_dt, fin_dt = _parsear_intervalo(contexto)
    _validar_orden_intervalo(inicio_dt, fin_dt)
    ahora_trunc = _obtener_ahora(contexto)
    _validar_limites_tiempo(inicio_dt, fin_dt, ahora_trunc)
    _validar_sin_solapamiento(contexto.unidad_id, inicio_dt, fin_dt, contexto.reservas_activas)
    return inicio_dt, fin_dt


def hay_solapamiento(a_inicio: datetime, a_fin: datetime, b_inicio: datetime, b_fin: datetime) -> bool:
    """Intervalos semiabiertos [inicio, fin): solapan si a.inicio < b.fin y b.inicio < a.fin."""
    return a_inicio < b_fin and b_inicio < a_fin
