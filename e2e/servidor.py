"""Servidor Reflex aislado para las pruebas de navegador."""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import IO


class ServidorReflex:
    """Levanta una instancia de Reflex con una base temporal."""

    def __init__(
        self,
        raiz: Path,
        puerto_frontend: int = 3020,
        puerto_backend: int = 8020,
    ) -> None:
        self.raiz = raiz
        self.puerto_frontend = puerto_frontend
        self.puerto_backend = puerto_backend
        self.directorio_evidencia = raiz / ".evidencia" / "paso27"
        self.directorio_evidencia.mkdir(parents=True, exist_ok=True)
        self.ruta_bd = self.directorio_evidencia / "reservas-e2e.db"
        self.ruta_log = self.directorio_evidencia / "servidor.log"
        self.proceso: subprocess.Popen[str] | None = None
        self._log: IO[str] | None = None

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.puerto_frontend}/"

    def iniciar(self, limpiar_bd: bool = True) -> None:
        """Inicia el servidor si no está activo."""
        if self.proceso is not None and self.proceso.poll() is None:
            return
        if limpiar_bd:
            self.ruta_bd.unlink(missing_ok=True)
        self._log = self.ruta_log.open("w", encoding="utf-8")
        self.proceso = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "reflex",
                "run",
                "--frontend-port",
                str(self.puerto_frontend),
                "--backend-port",
                str(self.puerto_backend),
            ],
            cwd=self.raiz,
            env=self._entorno(),
            stdout=self._log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self._esperar()

    def detener(self) -> None:
        """Detiene el servidor y libera la base de datos."""
        if self.proceso is not None and self.proceso.poll() is None:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(self.proceso.pid), "/T", "/F"],
                    capture_output=True,
                    check=False,
                )
            else:
                self.proceso.terminate()
            try:
                self.proceso.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.proceso.kill()
                self.proceso.wait(timeout=5)
        self.proceso = None
        if self._log is not None:
            self._log.close()
            self._log = None

    def reiniciar(self) -> None:
        """Reinicia el servidor conservando la base de datos."""
        self.detener()
        self.iniciar(limpiar_bd=False)

    def asegurar(self) -> None:
        """Garantiza que el servidor esté activo para el siguiente test."""
        if self.proceso is None or self.proceso.poll() is not None:
            self.iniciar(limpiar_bd=True)

    def limpiar_bd(self) -> None:
        """Borra la base temporal para empezar un test con estado limpio."""
        self.ruta_bd.unlink(missing_ok=True)

    def ejecutar_cli(self, *argumentos: str) -> subprocess.CompletedProcess[str]:
        """Ejecuta la CLI contra la base temporal del servidor."""
        return subprocess.run(
            [sys.executable, "-m", "reservas", *argumentos],
            cwd=self.raiz,
            env=self._entorno(),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def _entorno(self) -> dict[str, str]:
        entorno = os.environ.copy()
        entorno["RESERVAS_DB"] = str(self.ruta_bd)
        entorno["REFLEX_HOT_RELOAD_EXCLUDE_PATHS"] = "data"
        return entorno

    def _esperar(self) -> None:
        limite = time.monotonic() + 90
        while time.monotonic() < limite:
            if self.proceso is None:
                raise RuntimeError("No se pudo iniciar el servidor de pruebas.")
            if self.proceso.poll() is not None:
                raise RuntimeError(
                    "El servidor de pruebas terminó antes de estar listo.\n"
                    f"{self.ruta_log.read_text(encoding='utf-8', errors='replace')}"
                )
            try:
                with urllib.request.urlopen(self.url, timeout=2) as respuesta:
                    if respuesta.status == 200:
                        time.sleep(1.5)
                        return
            except (OSError, urllib.error.URLError):
                # Durante el arranque del servidor, errores de conexión son
                # transitorios; reintentamos hasta agotar el tiempo límite.
                continue
            time.sleep(0.5)
        raise RuntimeError(
            "El servidor de pruebas no respondió dentro del límite de 90 segundos.\n"
            f"{self.ruta_log.read_text(encoding='utf-8', errors='replace')}"
        )
