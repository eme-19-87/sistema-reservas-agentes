# Skill: reflex-rules

**Description:** Genera o modifica la interfaz web de un proyecto Reflex (Python) respetando la arquitectura por capas, las restricciones de Reflex 0.10 y las reglas del proyecto de reservas de laboratorio.

## Activation Triggers

Usar este skill cuando el usuario:

- Pida crear o modificar la aplicación Reflex (`reservas_ui/`, [`rxconfig.py`](http://rxconfig.py))
- Pida crear o modificar páginas, componentes, `rx.State` o handlers de eventos
- Agregue o modifique formularios, mensajes, tablas o filtros de la interfaz
- Escriba o modifique pruebas de la capa de presentación o de los handlers del `State`

No usar para reglas de dominio, servicio o repositorio (`src/reservas/`): esas capas no dependen de Reflex.

---

## Instructions

### Versión y lenguaje

- Utiliza **Python 3.12** (mínimo 3.11) y **Reflex 0.10.0** (`reflex==0.10.0`), fijado en `requirements-dev.txt`.
- Antes de scaffoldear, verifica la versión realmente instalada (`pip show reflex`) y regístrala en `docs/agent/[progreso.md](http://progreso.md)`. No actualices Reflex sin aprobación humana.
- Utiliza **SQLite** con `sqlite3` de la stdlib como única persistencia. No uses `rx.Model`, `rx.session()`, `reflex db` ni el extra `reflex[db]`.
- No agregues dependencias nuevas sin aprobación humana.
- `reflex init` y cualquier comando que descargue paquetes requieren aprobación de acceso a red.

### Arquitectura y frontera de capas

- Flujo: componentes → handlers del `State` → `reservas_ui/[presentacion.py](http://presentacion.py)` → servicio (`src/reservas/`) → repositorio.
- Ningún módulo de `src/reservas/` importa `reflex`. Verifícalo con `grep -rn "import reflex" src/` (debe no devolver resultados).
- Las reglas de negocio (validaciones, solapamiento, límites de tiempo) **nunca** se implementan en componentes, `State` ni [`presentacion.py`](http://presentacion.py): se delegan en el servicio.
- Disponibilidad y reserva usan la misma validación del dominio; la UI no la reimplementa.

### Estado (`rx.State`)

- El `State` solo guarda estado de pantalla: campos del formulario, mensajes, filtros y la lista mostrada. **No es fuente de verdad**: es en memoria y por sesión.
- Declara **todas** las vars en la clase, con tipos explícitos. Las que no deban enviarse al cliente llevan prefijo `_`.
- Valores mutables por defecto (listas, diccionarios) con `default_factory`.
- No guardes conexiones SQLite ni objetos no serializables en vars. Cada handler usa el servicio, que abre y cierra su propia conexión.
- `on_load` y cada handler que modifica datos recargan la lista desde SQLite.
- Reflex 0.10:
  - No asignes vars a través de la clase (`Estado.campo = ...`) ni las parchees con `monkeypatch`/`patch.object`: lanza `TypeError`.
  - Leer una var de backend desde la clase devuelve su descriptor `Field`, no su valor.
  - Asignar un atributo no declarado lanza `SetUndefinedStateVarError` fuera de modo prod.

```python
import reflex as rx

class Estado(rx.State):
    # formulario de reserva
    unidad: str = ""
    solicitante: str = ""
    inicio: str = ""
    fin: str = ""
    # pestaña y mensajes propios de cada formulario
    pestana_activa: str = "reserva"
    mensaje_exito_reserva: str = ""
    mensaje_error_reserva: str = ""
    mensaje_exito_disponibilidad: str = ""
    mensaje_error_disponibilidad: str = ""
    mensaje_exito_cancelacion: str = ""
    mensaje_error_cancelacion: str = ""
    filas: list[dict[str, str]] = rx.field(default_factory=list)

```

> Confirma la sintaxis exacta de vars con la documentación de Reflex 0.10 al implementar y registra la decisión en `docs/agent/[progreso.md](http://progreso.md)`.

### Handlers delgados y capa de presentación

- Un handler hace tres cosas: lee las vars del formulario, llama a una función de [`presentacion.py`](http://presentacion.py) y asigna el resultado a las vars. Nada más.
- [`presentacion.py`](http://presentacion.py) contiene **funciones puras** que reciben el servicio y los datos de entrada y devuelven mensajes y filas listos para mostrar. Captura las excepciones de dominio y las traduce a mensajes en español.
- Los errores de dominio se muestran en el mensaje de error del formulario correspondiente; nunca como trazas. Un error inesperado se registra en el log y se muestra un mensaje genérico.
- Cada formulario tiene su propio par de mensajes; una operación no debe borrar ni reutilizar el mensaje de otro formulario.

```python
def reservar(self) -> None:
    resultado = presentacion.reservar(
        servicio_por_defecto(), self.unidad, self.solicitante, self.inicio, self.fin
    )
    if resultado["ok"]:
        self.mensaje_exito_reserva = resultado["mensaje"]
        self.mensaje_error_reserva = ""
        self.filas = presentacion.listar_filas(servicio_por_defecto())
        # spec §14: limpiar solicitante, inicio y fin; conservar unidad
        self.solicitante = self.inicio = self.fin = ""
    else:
        self.mensaje_error_reserva = resultado["mensaje"]
        self.mensaje_exito_reserva = ""

```

### Formularios y fechas

- Los campos de fecha usan `rx.input(type="datetime-local")`, que entrega `YYYY-MM-DDTHH:MM`. El servicio valida igualmente la cadena recibida.
- Tras reservar con éxito: limpiar solicitante, inicio y fin y conservar la unidad. Tras un error: conservar todos los valores.
- Selectores de unidad alimentados con el inventario leído desde el servicio.

### Componentes

- Mantén componentes **pequeños, simples y con una sola responsabilidad** ([`componentes.py`](http://componentes.py)).
- Una sola página (`/`) con tres pestañas: reservar (activa por defecto), disponibilidad y reservas. Usa `rx.tabs` controlado por `State.pestana_activa`.
- Usa `rx.foreach` y `rx.cond` para listas y condicionales sobre vars del `State`; no uses condicionales de Python sobre vars reactivas.
- El botón «Cancelar» aparece solo en reservas `ACTIVA`; las canceladas permanecen visibles en la tabla.
- Cada formulario y la tabla de cancelación muestran sus propios mensajes de éxito y error; no existe un área global de mensajes.
- Accesibilidad mínima: pestañas navegables por teclado, etiqueta asociada a cada campo, navegación por teclado y estados de foco visibles.
- Estilos con las props de los componentes de Reflex; sin CSS personalizado salvo lo necesario para foco y legibilidad.

### Pruebas de la interfaz

- Pruebas automáticas, **sin servidor Reflex, sin navegador y sin red**: `test_ui_[presentacion.py](http://presentacion.py)`, `test_ui_[estado.py](http://estado.py)`, `test_ui_[humo.py](http://humo.py)`.
- BD temporal por prueba y reloj fijo; sin parchear vars de clase.
- Confirma la técnica de invocación de handlers contra la documentación de Reflex 0.10 (Paso 14 de [`tasks.md`](http://tasks.md)) y regístrala en `docs/agent/[progreso.md](http://progreso.md)`.
- El recorrido de clics en el navegador es manual, con resultados esperados y observados. No declares que la interfaz funciona sin haber levantado `reflex run` con una BD temporal.

### Registro

- Al cerrar cada tarea de interfaz: entrada en `docs/agent/[progreso.md](http://progreso.md)` con comando, versiones (Python, Reflex, pytest), resultado real y pasos no ejecutados.

---

## Project Structure (referencia)

```
reservas_ui/
├── reservas_ui.py     # rx.App, páginas y rutas
├── estado.py          # rx.State y handlers (delgados)
├── presentacion.py    # funciones puras: servicio → mensajes/filas
└── componentes.py     # pestañas, formularios, tabla y mensajes
rxconfig.py            # app_name = "reservas_ui"
tests/
├── test_ui_presentacion.py
├── test_ui_estado.py
└── test_ui_humo.py

```