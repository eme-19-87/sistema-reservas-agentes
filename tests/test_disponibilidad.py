"""Pruebas de disponibilidad."""
from __future__ import annotations

from reservas import servicio
from reservas.repositorio import inicializar_bd


def test_disponibilidad_misma_decision_que_reservar(env_db_temporal, reloj_fijo):
    inicializar_bd()
    disp = servicio.consultar_disponibilidad("MIC-01", "2026-10-23T10:00", "2026-10-23T11:00", reloj=lambda: reloj_fijo)
    assert disp["disponible"] is True
    res = servicio.crear_reserva("MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=lambda: reloj_fijo)
    assert res["estado"] == "ACTIVA"


def test_cancelada_no_bloquea(env_db_temporal, reloj_fijo):
    inicializar_bd()
    res = servicio.crear_reserva("MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=lambda: reloj_fijo)
    servicio.cancelar_reserva(res["id"], reloj=lambda: reloj_fijo)
    disp = servicio.consultar_disponibilidad("MIC-01", "2026-10-23T10:00", "2026-10-23T11:00", reloj=lambda: reloj_fijo)
    assert disp["disponible"] is True


def test_no_disponible_lista_conflictos_y_no_crea_reservas(env_db_temporal, reloj_fijo):
    inicializar_bd()
    servicio.crear_reserva("MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=lambda: reloj_fijo)
    disp = servicio.consultar_disponibilidad("MIC-01", "2026-10-23T10:30", "2026-10-23T11:30", reloj=lambda: reloj_fijo)
    assert disp["disponible"] is False
    assert len(disp["conflictos"]) >= 1
    # no crea reserva
    from reservas.repositorio import obtener_conexion
    conn = obtener_conexion()
    try:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM reservas")
        assert cur.fetchone()["cnt"] == 1
    finally:
        conn.close()
