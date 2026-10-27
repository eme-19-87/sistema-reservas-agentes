"""Fixtures de las pruebas de navegador."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
from playwright.sync_api import Browser, Playwright, sync_playwright

from e2e.pagina import PaginaReservas
from e2e.servidor import ServidorReflex

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def servidor() -> Iterator[ServidorReflex]:
    """Servidor Reflex único para toda la suite de navegador."""
    instancia = ServidorReflex(RAIZ)
    instancia.iniciar()
    try:
        yield instancia
    finally:
        instancia.detener()


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    """Instancia de Playwright compartida por los tests."""
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def navegador(playwright_instance: Playwright) -> Iterator[Browser]:
    """Navegador Chromium compartido por los tests."""
    browser = playwright_instance.chromium.launch(headless=True)
    try:
        yield browser
    finally:
        browser.close()


@pytest.fixture
def pagina(servidor: ServidorReflex, navegador: Browser) -> Iterator[PaginaReservas]:
    """Página limpia, con base de datos nueva, para cada requisito."""
    servidor.asegurar()
    servidor.limpiar_bd()
    contexto = navegador.new_context(locale="es-ES")
    pagina_navegador = contexto.new_page()
    pagina_navegador.set_default_timeout(10000)
    objeto = PaginaReservas(pagina_navegador, servidor.url)
    objeto.abrir()
    try:
        yield objeto
    finally:
        contexto.close()
