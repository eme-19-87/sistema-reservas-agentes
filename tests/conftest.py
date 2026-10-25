"""Fixtures para las pruebas. Sin servidor Reflex, sin navegador, sin red."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    """Ruta a una base de datos SQLite temporal."""
    ruta = tmp_path / "reservas_test.db"
    return ruta


@pytest.fixture
def db_url(db_path: Path) -> str:
    """Cadena de conexión tipo archivo SQLite para pruebas."""
    return f"file:{db_path}"


@pytest.fixture
def reloj_fijo() -> datetime:
    """Reloj fijo para pruebas deterministas (hora local sin zona)."""
    return datetime(2026, 10, 22, 10, 0)


@pytest.fixture(autouse=False)
def env_db_temporal(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Configura la variable de entorno con una base temporal."""
    monkeypatch.setenv("RESERVAS_DB", str(db_path))
    yield db_path
    monkeypatch.delenv("RESERVAS_DB", raising=False)
