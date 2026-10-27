"""Pruebas de navegador para los requisitos verificables de la especificación."""

from __future__ import annotations

import ast

from e2e.pagina import PaginaReservas, fecha_futura
from e2e.servidor import ServidorReflex


def test_rf01_inventario_de_cinco_unidades(pagina: PaginaReservas) -> None:
    """RF-01: el selector de reserva contiene las cinco unidades."""
    assert set(pagina.opciones_unidad()) == {
        "MIC-01",
        "MIC-02",
        "OSC-01",
        "MUL-01",
        "FUE-01",
    }


def test_rf02_reserva_activa_con_id(pagina: PaginaReservas) -> None:
    """RF-02: una reserva válida aparece como ACTIVA con ID."""
    inicio = fecha_futura("10:00")
    fin = fecha_futura("11:00")

    pagina.reservar("MIC-01", "Ana Pérez", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada con ID")

    fila = pagina.filas()[0]
    assert fila["id"] == "1"
    assert fila["unidad"] == "MIC-01"
    assert fila["solicitante"] == "Ana Pérez"
    assert fila["inicio"] == inicio
    assert fila["fin"] == fin
    assert fila["estado"] == "ACTIVA"


def test_rf03_solapamiento_rechazado(pagina: PaginaReservas) -> None:
    """RF-03: se rechaza una superposición en la misma unidad."""
    pagina.reservar("MIC-01", "Ana", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_reserva("Reserva creada")

    pagina.reservar(
        "MIC-01",
        "Beto",
        fecha_futura("10:30"),
        fecha_futura("11:30"),
    )
    pagina.esperar_error_reserva("Superposición con la reserva activa 1.")

    assert len(pagina.filas()) == 1


def test_rf04_limites_consecutivos(pagina: PaginaReservas) -> None:
    """RF-04: dos reservas consecutivas de la misma unidad son válidas."""
    pagina.reservar("MIC-01", "Ana", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.reservar("MIC-01", "Beto", fecha_futura("11:00"), fecha_futura("12:00"))
    pagina.esperar_exito_reserva("Reserva creada")

    filas = pagina.filas()
    assert [fila["estado"] for fila in filas] == ["ACTIVA", "ACTIVA"]
    assert filas[0]["fin"] == filas[1]["inicio"]


def test_rf05_unidades_distintas_simultaneas(pagina: PaginaReservas) -> None:
    """RF-05: dos unidades distintas se reservan en el mismo intervalo."""
    inicio = fecha_futura("10:00")
    fin = fecha_futura("11:00")

    pagina.reservar("MIC-01", "Ana", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.reservar("MIC-02", "Beto", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")

    filas = pagina.filas()
    assert {fila["unidad"] for fila in filas} == {"MIC-01", "MIC-02"}
    assert len(filas) == 2


def test_rf06_entradas_invalidas(pagina: PaginaReservas) -> None:
    """RF-06: la interfaz rechaza entradas inválidas sin crear filas."""
    pagina.reservar("MIC-01", "", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_error_reserva("Solicitante inválido.")

    pagina.reservar(
        "MIC-01",
        "Ana",
        fecha_futura("11:00"),
        fecha_futura("10:00"),
    )
    pagina.esperar_error_reserva("Intervalo inválido.")

    pagina.reservar(
        "MIC-01",
        "Ana",
        fecha_futura("10:00", dias=-1),
        fecha_futura("11:00", dias=-1),
    )
    pagina.esperar_error_reserva("Límite excedido.")

    pagina.reservar(
        "MIC-01",
        "Ana",
        fecha_futura("09:00"),
        fecha_futura("18:00"),
    )
    pagina.esperar_error_reserva("Límite excedido.")

    pagina.reservar(
        "MIC-01",
        "Ana",
        fecha_futura("10:00", dias=91),
        fecha_futura("11:00", dias=91),
    )
    pagina.esperar_error_reserva("Límite excedido.")

    assert pagina.filas() == []


def test_rf07_cancelacion_conserva_datos(pagina: PaginaReservas) -> None:
    """RF-07: cancelar conserva ID, datos y cambia el estado."""
    inicio = fecha_futura("10:00")
    fin = fecha_futura("11:00")
    pagina.reservar("MIC-01", "Ana", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")
    original = pagina.filas()[0]

    pagina.cancelar(1)
    cancelada = pagina.fila(1)

    assert cancelada["id"] == original["id"]
    assert cancelada["unidad"] == original["unidad"]
    assert cancelada["solicitante"] == original["solicitante"]
    assert cancelada["inicio"] == original["inicio"]
    assert cancelada["fin"] == original["fin"]
    assert cancelada["estado"] == "CANCELADA"
    assert not pagina.tiene_boton_cancelar(1)


def test_rf08_cancelacion_libera_intervalo(pagina: PaginaReservas) -> None:
    """RF-08: después de cancelar se puede reservar el mismo intervalo."""
    inicio = fecha_futura("10:00")
    fin = fecha_futura("11:00")
    pagina.reservar("MIC-01", "Ana", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.cancelar(1)

    pagina.reservar("MIC-01", "Beto", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")

    filas = pagina.filas()
    assert [(fila["id"], fila["estado"]) for fila in filas] == [
        ("1", "CANCELADA"),
        ("2", "ACTIVA"),
    ]


def test_rf09_cancelada_no_bloquea_disponibilidad(
    pagina: PaginaReservas,
) -> None:
    """RF-09: una reserva cancelada no bloquea la disponibilidad."""
    inicio = fecha_futura("10:00")
    fin = fecha_futura("11:00")
    pagina.reservar("MIC-01", "Ana", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.cancelar(1)

    pagina.consultar("MIC-01", inicio, fin)
    pagina.esperar_exito_disponibilidad("Disponible.")


def test_rf10_disponibilidad_y_reserva_comparten_reglas(
    pagina: PaginaReservas,
) -> None:
    """RF-10: la consulta detecta el mismo solapamiento que la reserva."""
    pagina.reservar("MIC-01", "Ana", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_reserva("Reserva creada")

    pagina.consultar(
        "MIC-01",
        fecha_futura("10:30"),
        fecha_futura("11:30"),
    )
    pagina.esperar_error_disponibilidad(
        "No disponible: se superpone con la reserva activa 1."
    )

    pagina.consultar("MIC-01", fecha_futura("11:00"), fecha_futura("12:00"))
    pagina.esperar_exito_disponibilidad("Disponible.")


def test_rf11_persistencia_tras_reiniciar(
    pagina: PaginaReservas,
    servidor: ServidorReflex,
) -> None:
    """RF-11: activas y canceladas sobreviven al reinicio del servidor."""
    pagina.reservar("MIC-01", "Ana", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.reservar("MIC-01", "Beto", fecha_futura("11:00"), fecha_futura("12:00"))
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.cancelar(2)

    servidor.reiniciar()
    pagina.abrir()

    estados = {fila["id"]: fila["estado"] for fila in pagina.filas()}
    assert estados == {"1": "ACTIVA", "2": "CANCELADA"}


def test_rf12_id_no_se_reutiliza(pagina: PaginaReservas) -> None:
    """RF-12: una reserva nueva recibe un ID distinto tras cancelar."""
    inicio = fecha_futura("10:00")
    fin = fecha_futura("11:00")
    pagina.reservar("MIC-01", "Ana", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.cancelar(1)

    pagina.reservar("MIC-01", "Beto", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada")

    filas = pagina.filas()
    assert [fila["id"] for fila in filas] == ["1", "2"]
    assert filas[1]["id"] != filas[0]["id"]


def test_rf13_init_db_y_reset(pagina: PaginaReservas, servidor: ServidorReflex) -> None:
    """RF-13: init-db es idempotente y --reset borra las reservas."""
    pagina.reservar("MIC-01", "Ana", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_reserva("Reserva creada")

    idempotente = servidor.ejecutar_cli("init-db")
    assert idempotente.returncode == 0, idempotente.stderr
    pagina.abrir()
    assert len(pagina.filas()) == 1

    reinicio = servidor.ejecutar_cli("init-db", "--reset", "--yes")
    assert reinicio.returncode == 0, reinicio.stderr
    pagina.abrir()
    assert pagina.filas() == []


def test_rf14_dominio_no_depende_de_reflex(servidor: ServidorReflex) -> None:
    """RF-14: el paquete de dominio no importa Reflex."""
    for ruta in sorted((servidor.raiz / "src" / "reservas").glob("*.py")):
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        assert not _importa_reflex(arbol), f"{ruta} importa reflex"


def test_rf15_mensajes_de_error_de_la_interfaz(pagina: PaginaReservas) -> None:
    """RF-15: los errores de validación visibles tienen su mensaje."""
    pagina.reservar("MIC-01", "", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_error_reserva("Solicitante inválido.")

    pagina.reservar(
        "MIC-01",
        "Ana",
        fecha_futura("11:00"),
        fecha_futura("10:00"),
    )
    pagina.esperar_error_reserva("Intervalo inválido.")

    pagina.reservar(
        "MIC-01",
        "Ana",
        fecha_futura("10:00", dias=-1),
        fecha_futura("11:00", dias=-1),
    )
    pagina.esperar_error_reserva("Límite excedido.")


def test_rf16_handlers_consultan_reservan_cancelan_y_filtran(
    pagina: PaginaReservas,
) -> None:
    """RF-16: los handlers permiten consultar, reservar, cancelar y filtrar."""
    pagina.reservar("MIC-01", "Ana", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.reservar("OSC-01", "Beto", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_reserva("Reserva creada")
    pagina.cancelar(1)

    pagina.abrir_pestana("reservas")
    pagina.seleccionar_opcion("filtro-unidad", "MIC-01")
    filas_mic = pagina.filas()
    assert len(filas_mic) == 1
    assert filas_mic[0]["unidad"] == "MIC-01"
    assert filas_mic[0]["estado"] == "CANCELADA"

    pagina.seleccionar_opcion("filtro-estado", "CANCELADA")
    filas_canceladas = pagina.filas()
    assert len(filas_canceladas) == 1
    assert filas_canceladas[0]["estado"] == "CANCELADA"

    pagina.limpiar_filtros()
    assert len(pagina.filas()) == 2

    pagina.seleccionar_opcion("filtro-unidad", "OSC-01")
    filas_osc = pagina.filas()
    assert len(filas_osc) == 1
    assert filas_osc[0]["estado"] == "ACTIVA"


def test_rf17_pagina_raiz_carga(pagina: PaginaReservas) -> None:
    """RF-17: la página / se registra y muestra la interfaz."""
    assert pagina.pagina.locator("#titulo-pagina").text_content() == (
        "Sistema de reservas de laboratorio"
    )
    assert pagina.pagina.locator("#panel-reserva").is_visible()
    assert pagina.pagina.locator("#tab-disponibilidad").is_visible()
    assert pagina.pagina.locator("#tab-reservas").is_visible()


def test_rf18_flujo_completo_en_navegador(pagina: PaginaReservas) -> None:
    """RF-18: crear, detectar conflicto, consultar, cancelar y volver a reservar."""
    inicio = fecha_futura("10:00")
    fin = fecha_futura("11:00")
    pagina.reservar("MIC-01", "Ana", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada con ID 1.")

    pagina.reservar(
        "MIC-01",
        "Beto",
        fecha_futura("10:30"),
        fecha_futura("11:30"),
    )
    pagina.esperar_error_reserva("Superposición con la reserva activa 1.")

    pagina.consultar("MIC-01", inicio, fin)
    pagina.esperar_error_disponibilidad(
        "No disponible: se superpone con la reserva activa 1."
    )

    pagina.reservar("MIC-01", "Beto", fecha_futura("11:00"), fecha_futura("12:00"))
    pagina.esperar_exito_reserva("Reserva creada con ID 2.")

    pagina.cancelar(1)
    pagina.consultar("MIC-01", inicio, fin)
    pagina.esperar_exito_disponibilidad("Disponible.")

    pagina.reservar("MIC-01", "Carla", inicio, fin)
    pagina.esperar_exito_reserva("Reserva creada con ID 3.")

    estados = [(fila["id"], fila["estado"]) for fila in pagina.filas()]
    assert estados == [("1", "CANCELADA"), ("3", "ACTIVA"), ("2", "ACTIVA")]


def test_rf19_tres_pestanas_con_mensajes_propios(pagina: PaginaReservas) -> None:
    """RF-19: las tres pestañas existen y cada formulario conserva su mensaje."""
    assert pagina.pagina.locator("#panel-reserva").is_visible()
    pagina.abrir_pestana("disponibilidad")
    assert pagina.pagina.locator("#panel-disponibilidad").is_visible()
    pagina.abrir_pestana("reservas")
    assert pagina.pagina.locator("#panel-reservas").is_visible()

    pagina.consultar("MIC-01", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_exito_disponibilidad("Disponible.")

    pagina.abrir_pestana("reserva")
    pagina.reservar("MIC-01", "", fecha_futura("10:00"), fecha_futura("11:00"))
    pagina.esperar_error_reserva("Solicitante inválido.")

    pagina.abrir_pestana("disponibilidad")
    assert pagina.texto_visible("#mensaje-exito-disponibilidad") == "Disponible."
    assert pagina.texto_visible("#mensaje-error-reserva") == ""

    pagina.abrir_pestana("reserva")
    assert pagina.texto_visible("#mensaje-error-reserva") == "Solicitante inválido."


def _importa_reflex(arbol: ast.AST) -> bool:
    """Indica si un árbol de sintaxis importa el paquete reflex."""
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            if any(alias.name.split(".")[0] == "reflex" for alias in nodo.names):
                return True
        if isinstance(nodo, ast.ImportFrom):
            modulo = (nodo.module or "").split(".")[0]
            if modulo == "reflex":
                return True
    return False
