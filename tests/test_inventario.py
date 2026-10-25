from __future__ import annotations

import json
from pathlib import Path

from reservas.inventario import cargar_inventario, obtener_inventario


def test_inventario_tiene_cinco_unidades_con_sus_equipos(tmp_path: Path) -> None:
    datos = cargar_inventario()
    assert len(datos) == 5

    por_id = obtener_inventario()
    assert set(por_id.keys()) == {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"}
    assert por_id["MIC-01"]["equipo"] == "Microscopio digital"
    assert por_id["MIC-02"]["equipo"] == "Microscopio digital"
    assert por_id["OSC-01"]["equipo"] == "Osciloscopio"
    assert por_id["MUL-01"]["equipo"] == "Multímetro"
    assert por_id["FUE-01"]["equipo"] == "Fuente de alimentación"


def test_inventario_es_de_solo_lectura_desde_json(tmp_path: Path) -> None:
    ruta = tmp_path / "inventario.json"
    contenido = [
        {"id": "MIC-01", "equipo": "Microscopio digital"},
        {"id": "MIC-02", "equipo": "Microscopio digital"},
        {"id": "OSC-01", "equipo": "Osciloscopio"},
        {"id": "MUL-01", "equipo": "Multímetro"},
        {"id": "FUE-01", "equipo": "Fuente de alimentación"},
    ]
    ruta.write_text(json.dumps(contenido, ensure_ascii=False), encoding="utf-8")
    datos = cargar_inventario(ruta)
    assert len(datos) == 5
