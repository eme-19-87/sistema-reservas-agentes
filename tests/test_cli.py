"""Pruebas del CLI init-db."""

from __future__ import annotations

from reservas import cli, repositorio


def test_init_db_idempotente(env_db_temporal):
    code = cli.cmd_init_db(reset=False)
    assert code == 0
    code2 = cli.cmd_init_db(reset=False)
    assert code2 == 0
    conn = repositorio.obtener_conexion()
    try:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM unidades")
        assert cur.fetchone()["cnt"] == 5
    finally:
        conn.close()


def test_init_db_reset_borra_reservas(env_db_temporal, reloj_fijo):
    from reservas import servicio

    cli.cmd_init_db(reset=False)
    servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    conn = repositorio.obtener_conexion()
    try:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM reservas")
        assert cur.fetchone()["cnt"] == 1
    finally:
        conn.close()
    code = cli.cmd_init_db(reset=True, yes=True)
    assert code == 0
    conn = repositorio.obtener_conexion()
    try:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM reservas")
        assert cur.fetchone()["cnt"] == 0
    finally:
        conn.close()


def test_init_db_sin_reset_no_toca_reservas(env_db_temporal, reloj_fijo):
    from reservas import servicio

    cli.cmd_init_db(reset=False)
    servicio.crear_reserva(
        "MIC-01",
        "Ana",
        "2026-10-23T10:00",
        "2026-10-23T11:00",
        reloj=lambda: reloj_fijo,
    )
    code = cli.cmd_init_db(reset=False)
    assert code == 0
    conn = repositorio.obtener_conexion()
    try:
        cur = conn.execute("SELECT COUNT(*) as cnt FROM reservas")
        assert cur.fetchone()["cnt"] == 1
    finally:
        conn.close()
