"""Pruebas del repositorio SQLite."""

from __future__ import annotations

from reservas.repositorio import crear_esquema, obtener_conexion, sembrar_unidades


def test_esquema_creado(db_path):
    conn = obtener_conexion(db_path)
    try:
        crear_esquema(conn)
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tablas = {row[0] for row in cur.fetchall()}
        assert "unidades" in tablas
        assert "reservas" in tablas
    finally:
        conn.close()


def test_siembra_repetida_sin_duplicados(db_path):
    conn = obtener_conexion(db_path)
    try:
        crear_esquema(conn)
        sembrar_unidades(conn)
        cur = conn.execute("SELECT COUNT(*) as cnt FROM unidades")
        cnt1 = cur.fetchone()["cnt"]
        sembrar_unidades(conn)
        cur = conn.execute("SELECT COUNT(*) as cnt FROM unidades")
        cnt2 = cur.fetchone()["cnt"]
        assert cnt1 == cnt2
        assert cnt1 == 5
    finally:
        conn.close()


def test_id_nunca_reutilizado(db_path):
    conn = obtener_conexion(db_path)
    try:
        crear_esquema(conn)
        sembrar_unidades(conn)
        cur = conn.execute(
            """
            INSERT INTO reservas (
                unidad_id, solicitante, inicio, fin, estado, creada_en
            )
            VALUES (
                'MIC-01', 'Ana', '2026-10-23T10:00', '2026-10-23T11:00',
                'ACTIVA', '2026-10-22T10:00'
            )
            """
        )
        reserva_id = cur.lastrowid
        conn.execute(
            "UPDATE reservas SET estado='CANCELADA', "
            "cancelada_en='2026-10-22T11:00' WHERE id=?",
            (reserva_id,),
        )
        conn.execute(
            """
            INSERT INTO reservas (
                unidad_id, solicitante, inicio, fin, estado, creada_en
            )
            VALUES (
                'MIC-01', 'Ana', '2026-10-23T12:00', '2026-10-23T13:00',
                'ACTIVA', '2026-10-22T11:00'
            )
            """
        )
        cur2 = conn.execute("SELECT id FROM reservas ORDER BY id")
        ids = [row[0] for row in cur2.fetchall()]
        assert ids[0] == reserva_id
        assert ids[1] != reserva_id
        conn.commit()
    finally:
        conn.close()
