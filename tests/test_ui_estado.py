"""Pruebas de handlers del State."""
from __future__ import annotations

from reservas import servicio
from reservas.repositorio import inicializar_bd
from reservas_ui import estado


def test_on_load_carga_unidades_y_reservas(env_db_temporal, reloj_fijo):
    inicializar_bd()
    servicio.crear_reserva("MIC-01", "Ana", "2026-10-23T10:00", "2026-10-23T11:00", reloj=lambda: reloj_fijo)
    st = estado.State()
    st.on_load()
    assert len(st.unidades) == 5
    assert any(r.get("unidad_id") == "MIC-01" or r.get("unidad") == "MIC-01" for r in st.reservas)
