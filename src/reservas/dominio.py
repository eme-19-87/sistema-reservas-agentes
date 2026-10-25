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


def validar_solicitante(solicitante: str) -> str:
    """Valida y normaliza el solicitante."""
    if not isinstance(solicitante, str):
        raise SolicitanteInvalido("Solicitante inválido.")
    if solicitante.strip() == "":
        raise SolicitanteInvalido("Solicitante inválido.")
    normalizado = solicitante.strip()
    # No solo espacios ya verificado
    # No compuesto solo por números
    if normalizado.isdigit():
        raise SolicitanteInvalido("Solicitante inválido.")
    # Sin caracteres especiales - permitir letras (incluyendo acentos y diéresis), espacios, guiones
    # Patrón: solo letras unicode, espacios, guiones
    if re.search(r"[^A-Za-zÁÉÍÓÚÜáéíóúüÑñ\s\-']", normalizado):
        raise SolicitanteInvalido("Solicitante inválido.")
    if re.match(r"^[\s\-\d]+$", normalizado):
        raise SolicitanteInvalido("Solicitante inválido.")
    return normalizado


def validar_unidad_conocida(unidad_id: str, inventario: dict[str, dict] | None = None) -> str:
    if inventario is None:
        inventario = obtener_inventario()
    if unidad_id not in inventario:
        raise UnidadDesconocida("Unidad desconocida.")
    return unidad_id


def truncar_al_minuto(fecha: datetime) -> datetime:
    return fecha.replace(second=0, microsecond=0)


def validar_solicitud_intervalo(
    unidad_id: str,
    inicio: str | datetime,
    fin: str | datetime,
    solicitante: str | None = None,
    ahora: datetime | None = None,
    reloj: Callable[[], datetime] | None = None,
    inventario: dict[str, dict] | None = None,
    reservas_activas: Iterable[dict] | None = None,
) -> tuple[datetime, datetime]:
    """Valida una solicitud. Si solicitante es None, se omite (consulta)."""
    if inventario is None:
        inventario = obtener_inventario()
    validar_unidad_conocida(unidad_id, inventario)

    if solicitante is not None:
        validar_solicitante(solicitante)

    if isinstance(inicio, str):
        inicio_dt = parsear_fecha_hora(inicio)
    else:
        inicio_dt = truncar_al_minuto(inicio)
    if isinstance(fin, str):
        fin_dt = parsear_fecha_hora(fin)
    else:
        fin_dt = truncar_al_minuto(fin)

    if inicio_dt >= fin_dt:
        raise IntervaloInvalido("Intervalo inválido.")

    if reloj is not None and ahora is None:
        ahora = reloj()
    if ahora is None:
        ahora = datetime.now()
    ahora_trunc = truncar_al_minuto(ahora)

    if inicio_dt < ahora_trunc:
        raise LimiteExcedido("Límite excedido.")

    duracion = fin_dt - inicio_dt
    if duracion > timedelta(hours=DURACION_MAXIMA_HORAS):
        raise LimiteExcedido("Límite excedido.")
    if inicio_dt > ahora_trunc + timedelta(days=ANTICIPACION_MAXIMA_DIAS):
        raise LimiteExcedido("Límite excedido.")

    # Sin solapamiento con reservas activas de la misma unidad
    if reservas_activas:
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

    return inicio_dt, fin_dt


def hay_solapamiento(a_inicio: datetime, a_fin: datetime, b_inicio: datetime, b_fin: datetime) -> bool:
    """Intervalos semiabiertos [inicio, fin): solapan si a.inicio < b.fin y b.inicio < a.fin."""
    return a_inicio < b_fin and b_inicio < a_fin
