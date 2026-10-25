"""Servicio de reservas."""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable

from . import dominio
from . import repositorio
from .dominio import (
    FechaInvalida,
    IntervaloInvalido,
    LimiteExcedido,
    ReservaNoEncontrada,
    ReservaYaCancelada,
    SolicitanteInvalido,
    Superposicion,
    UnidadDesconocida,
    truncar_al_minuto,
    validar_solicitud_intervalo,
)
from .inventario import obtener_inventario
from .repositorio import inicializar_bd, obtener_conexion


def _obtener_conexion_actual() -> sqlite3.Connection:
    ruta = repositorio.ruta_bd()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conn = obtener_conexion(ruta)
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reservas'")
        if cur.fetchone() is None:
            from .repositorio import crear_esquema, sembrar_unidades

            crear_esquema(conn)
            sembrar_unidades(conn)
    except Exception:
        pass
    return conn


def _obtener_ahora(reloj: Callable[[], datetime] | None = None) -> datetime:
    if reloj is not None:
        ahora = reloj()
    else:
        ahora = datetime.now()
    return truncar_al_minuto(ahora)


def _formatear_fecha(dt: datetime) -> str:
    return dt.strftime(dominio.FORMATO_FECHA)


def _obtener_reservas_activas_unidad(conn: sqlite3.Connection, unidad_id: str) -> list[dict[str, Any]]:
    cur = conn.execute(
        """
        SELECT id, unidad_id, solicitante, inicio, fin, estado, creada_en, cancelada_en
        FROM reservas
        WHERE unidad_id = ? AND estado = 'ACTIVA'
        """,
        (unidad_id,),
    )
    return [dict(row) for row in cur.fetchall()]


def consultar_disponibilidad(
    unidad_id: str,
    inicio: str | datetime,
    fin: str | datetime,
    reloj: Callable[[], datetime] | None = None,
    inventario: dict[str, dict] | None = None,
) -> dict[str, Any]:
    """Consulta disponibilidad sin crear reservas."""
    if inventario is None:
        inventario = obtener_inventario()
    conn = _obtener_conexion_actual()
    try:
        reservas_activas = _obtener_reservas_activas_unidad(conn, unidad_id)
        try:
            validar_solicitud_intervalo(
                unidad_id,
                inicio,
                fin,
                solicitante=None,
                reloj=reloj,
                inventario=inventario,
                reservas_activas=reservas_activas,
            )
            return {"disponible": True, "conflictos": []}
        except Superposicion as exc:
            return {"disponible": False, "conflictos": exc.reservas_conflicto}
    finally:
        conn.close()


def crear_reserva(
    unidad_id: str,
    solicitante: str,
    inicio: str | datetime,
    fin: str | datetime,
    reloj: Callable[[], datetime] | None = None,
    inventario: dict[str, dict] | None = None,
) -> dict[str, Any]:
    """Crea una reserva activa."""
    if inventario is None:
        inventario = obtener_inventario()
    ahora_trunc = _obtener_ahora(reloj)
    conn = _obtener_conexion_actual()
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            reservas_activas = _obtener_reservas_activas_unidad(conn, unidad_id)
            inicio_dt, fin_dt = validar_solicitud_intervalo(
                unidad_id,
                inicio,
                fin,
                solicitante=solicitante,
                reloj=reloj,
                inventario=inventario,
                reservas_activas=reservas_activas,
            )
            creada_en = _formatear_fecha(ahora_trunc)
            cur = conn.execute(
                """
                INSERT INTO reservas (unidad_id, solicitante, inicio, fin, estado, creada_en, cancelada_en)
                VALUES (?, ?, ?, ?, 'ACTIVA', ?, NULL)
                """,
                (
                    unidad_id,
                    solicitante.strip() if isinstance(solicitante, str) else solicitante,
                    _formatear_fecha(inicio_dt),
                    _formatear_fecha(fin_dt),
                    creada_en,
                ),
            )
            reserva_id = cur.lastrowid
            conn.commit()
            return {
                "id": reserva_id,
                "unidad_id": unidad_id,
                "solicitante": solicitante.strip() if isinstance(solicitante, str) else solicitante,
                "inicio": _formatear_fecha(inicio_dt),
                "fin": _formatear_fecha(fin_dt),
                "estado": "ACTIVA",
                "creada_en": creada_en,
                "cancelada_en": None,
            }
        except Exception:
            conn.rollback()
            raise
    finally:
        conn.close()


def cancelar_reserva(reserva_id: int, reloj: Callable[[], datetime] | None = None) -> dict[str, Any]:
    """Cancela una reserva activa."""
    ahora_trunc = _obtener_ahora(reloj)
    conn = _obtener_conexion_actual()
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            cur = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,))
            reserva = cur.fetchone()
            if reserva is None:
                raise ReservaNoEncontrada("Reserva no encontrada.")
            reserva_dict = dict(reserva)
            if reserva_dict.get("estado") == "CANCELADA":
                raise ReservaYaCancelada("Reserva ya cancelada.")
            if reserva_dict.get("estado") != "ACTIVA":
                raise ReservaYaCancelada("Reserva ya cancelada.")
            cancelada_en = _formatear_fecha(ahora_trunc)
            conn.execute(
                "UPDATE reservas SET estado = 'CANCELADA', cancelada_en = ? WHERE id = ?",
                (cancelada_en, reserva_id),
            )
            conn.commit()
            reserva_dict["estado"] = "CANCELADA"
            reserva_dict["cancelada_en"] = cancelada_en
            return reserva_dict
        except Exception:
            conn.rollback()
            raise
    finally:
        conn.close()


def listar_reservas(
    unidad_id: str | None = None,
    estado: str | None = None,
) -> list[dict[str, Any]]:
    """Lista reservas ordenadas por inicio y luego por ID."""
    conn = _obtener_conexion_actual()
    try:
        query = "SELECT * FROM reservas WHERE 1=1"
        params: list[Any] = []
        if unidad_id is not None:
            query += " AND unidad_id = ?"
            params.append(unidad_id)
        if estado is not None:
            query += " AND estado = ?"
            params.append(estado)
        query += " ORDER BY inicio ASC, id ASC"
        cur = conn.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
