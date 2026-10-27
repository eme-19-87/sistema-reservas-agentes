# Plan técnico — Sistema de reservas de laboratorio

## 1. Arquitectura

Aplicación web local en Reflex con capas separadas y dependencias en un solo sentido.

```text
Páginas y componentes Reflex (reservas_ui/)
      │  eventos (on_click, on_change, on_load)
      ▼
rx.State (estado de pantalla + handlers delgados)
      │
      ▼
reservas_ui/presentacion.py (funciones puras)
      │
      ▼
Servicio de reservas (casos de uso)
      │
      ▼
Dominio (reglas puras: validación, solapamiento)
      ▲
      │
Repositorio SQLite  ← data/reservas.db
      ▲
Inventario JSON     ← data/inventario.json (solo lectura)

```

- El **dominio** no conoce SQLite ni Reflex.
- El **servicio** orquesta: valida con el dominio, consulta el repositorio, persiste.
- El **State de Reflex** solo traduce eventos de la UI ↔ funciones de [`presentacion.py`](http://presentacion.py) (que llaman al servicio) ↔ variables de pantalla. No contiene reglas de negocio y **no es fuente de verdad**: la fuente de verdad es SQLite.
- Una **CLI mínima** (`python -m reservas init-db`) carga o reinicia datos.

## 2. Tecnologías


| Elemento     | Decisión                                                              | Motivo                                                                                          |
| ------------ | --------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Lenguaje     | **Python 3.12** (mínimo 3.11; Reflex 0.10 dejó de soportar 3.10)      | Reflex define el rango soportado; 3.12 queda dentro de él                                       |
| Interfaz     | **Reflex 0.10.0** (`reflex==0.10.0`), web local con `reflex run`      | Última versión estable publicada (8-oct-2026); decisión de la persona autora: UI en Python puro |
| Persistencia | SQLite vía `sqlite3` (stdlib), sin `rx.Model`                         | Mantiene dominio/servicio/repositorio sin dependencia de Reflex y verificables sin red          |
| Pruebas      | `pytest`                                                              | Estándar, fixtures para BD temporal                                                             |
| Linter       | `ruff`                                                                | Rápido, una sola herramienta                                                                    |
| Dependencias | `reflex==0.10.0`, `pytest`, `ruff`, con `requirements-dev.txt` fijado | Reproducible sin cuenta de modelo                                                               |


Versiones verificadas el 21-oct-2026 en las notas de versión de Reflex (GitHub Releases): última estable **0.10.0**; la línea 0.9 sigue recibiendo parches (0.9.13). Las versiones exactas de `pytest` y `ruff` no se verificaron aquí: se fijan al generar `requirements-dev.txt` y se registran en `docs/agent/[progreso.md](http://progreso.md)`. No se instala el extra `reflex[db]` porque no se usa `rx.Model`.

Cambios de Reflex 0.10 que condicionan el diseño y las pruebas del `State`:

- Asignar una var a través de la clase (`Estado.campo = x`) lanza `TypeError`, y también `monkeypatch.setattr`/`patch.object` sobre una var: **las pruebas no deben parchear vars de clase**.
- Leer una var de backend desde la clase (`Estado._x`) devuelve su descriptor `Field`, no el valor por defecto.
- Los valores mutables por defecto se copian en profundidad; usar `default_factory` para listas/diccionarios.
- Asignar un atributo no declarado lanza `SetUndefinedStateVarError` fuera de modo prod: declarar todas las vars del `State`.

Requisito previo adicional: Reflex descarga su runtime de frontend (Node/bun y paquetes JS) durante `reflex init`, por lo que **la instalación inicial requiere red**; luego la aplicación y las pruebas corren localmente. Se declara en el README.

Alternativas descartadas (registrar en README §4): JSON plano como almacenamiento (sin transacciones, riesgo de corrupción); `rx.Model`/SQLModel de Reflex para persistir (acopla las reglas y las pruebas a Reflex y a sus migraciones); CLI pura (válida para el alcance, pero se prefirió Reflex como tecnología de interfaz).

## 3. Restricciones

- Sin autenticación, roles, notificaciones, pagos ni despliegue obligatorio. Sin red en ejecución; la única descarga es la instalación aprobada de dependencias y runtime de Reflex.
- Sin administración de inventario (solo lectura del precargado).
- Sin estado solo en memoria: todo debe sobrevivir a un reinicio (el `State` de Reflex es en memoria y por sesión, por eso no se usa como almacenamiento).
- No incluir datos reales ni secretos; solicitantes ficticios.
- No implementar nada fuera de [`spec.md`](http://spec.md).
- Ningún módulo de `src/reservas/` importa `reflex`.

## 4. Estructura del repositorio

```text
.
├── CLAUDE.md
├── .claude/skills/reflex-rules/SKILL.md   # reglas de la interfaz Reflex
├── README.md                      # 4 secciones del challenge
├── pyproject.toml
├── requirements-dev.txt           # versiones fijadas
├── rxconfig.py                    # configuración de Reflex (app_name = "reservas_ui")
├── data/
│   ├── inventario.json            # inventario inicial (versionado)
│   └── reservas.db                # generado; en .gitignore
├── specs/reservas-laboratorio/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── docs/agent/
│   ├── progreso.md                # progreso y decisiones (memoria versionada)
│   ├── delegacion.md              # 3 episodios de delegación
│   ├── preparacion-agente.md      # entorno, modelo, permisos, contexto
│   └── verificacion-persistencia.md
├── reservas_ui/                   # aplicación Reflex
│   ├── __init__.py
│   ├── reservas_ui.py             # rx.App, páginas y rutas
│   ├── estado.py                  # rx.State y handlers (delgados)
│   ├── presentacion.py            # funciones puras: servicio → mensajes/filas para la UI
│   └── componentes.py             # formulario, tabla, mensajes
├── src/reservas/
│   ├── __init__.py
│   ├── __main__.py
│   ├── dominio.py                 # entidades, reglas, excepciones
│   ├── servicio.py                # casos de uso
│   ├── repositorio.py             # SQLite
│   ├── inventario.py              # carga de inventario.json
│   └── cli.py                     # solo init-db
└── tests/
    ├── conftest.py                # BD temporal, reloj fijo
    ├── test_creacion.py
    ├── test_solapamiento.py
    ├── test_validaciones.py
    ├── test_inventario.py
    ├── test_repositorio.py
    ├── test_cli.py
    ├── test_cancelacion.py
    ├── test_disponibilidad.py
    ├── test_persistencia.py
    ├── test_frontera_reflex.py    # ningún módulo de src/ importa reflex
    ├── test_ui_presentacion.py    # funciones puras de la capa de presentación
    ├── test_ui_estado.py          # handlers del rx.State contra BD temporal
    └── test_ui_humo.py            # la app Reflex se importa y registra su página

```

Nota: Reflex exige que el módulo de la app coincida con `app_name` de [`rxconfig.py`](http://rxconfig.py); por eso `reservas_ui/` vive en la raíz y `src/reservas/` queda como núcleo independiente.

## 5. Modelo de datos

Entidades:

- **Unidad** (`id`, `equipo`): cargada desde JSON; tabla `unidades` sembrada por `init-db`.
- **Reserva** (`id`, `unidad_id`, `solicitante`, `inicio`, `fin`, `estado`, `creada_en`, `cancelada_en`).

```text
Unidad 1 --- * Reserva

```

`estado` ∈ {`ACTIVA`, `CANCELADA`}.

Definición de tablas:

```sql
CREATE TABLE unidades (
  id TEXT PRIMARY KEY,
  equipo TEXT NOT NULL
);

CREATE TABLE reservas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unidad_id TEXT NOT NULL REFERENCES unidades(id),
  solicitante TEXT NOT NULL,
  inicio TEXT NOT NULL,        -- ISO 8601 'YYYY-MM-DDTHH:MM'
  fin TEXT NOT NULL,
  estado TEXT NOT NULL CHECK (estado IN ('ACTIVA','CANCELADA')),
  creada_en TEXT NOT NULL,
  cancelada_en TEXT,
  CHECK (inicio < fin)
);

CREATE INDEX idx_reservas_unidad_estado ON reservas(unidad_id, estado, inicio);

```

El ID de reserva es secuencial y **nunca se reutiliza** (AUTOINCREMENT), de modo que una cancelada conserva su identificador.

## 6. Reglas de dominio

### 6.1 Intervalos

Intervalos semiabiertos `[inicio, fin)`. Dos intervalos de la misma unidad se superponen si y solo si:

```text
a.inicio < b.fin  AND  b.inicio < a.fin

```

Consecuencias: 10:00–11:00 y 11:00–12:00 **no** se superponen; 10:00–11:00 y 10:30–11:30 **sí**.

### 6.2 Validaciones (orden fijo)

1. Unidad existe en el inventario.
2. Solicitante: `str.strip()` no vacío (se almacena sin espacios en los extremos).
3. Fechas parseables con formato `YYYY-MM-DDTHH:MM` (fecha calendario válida, sin zona horaria).
4. `inicio < fin` estricto.
5. Límites de tiempo (valores definidos en [`spec.md`](http://spec.md) §8; los límites exactos son válidos):
   - fecha/hora de inicio no anterior al «ahora» inyectado, truncado al minuto (**fechas pasadas rechazadas**);
   - duración máxima: 8 horas;
   - anticipación máxima: 90 días (sobre el inicio);
   - duración mínima: &gt; 0 (cubierta por `inicio < fin`).
6. Sin solapamiento con reservas **ACTIVAS** de la misma unidad.

### 6.3 Disponibilidad y reserva comparten regla

`servicio.consultar_disponibilidad(unidad, inicio, fin)` y `servicio.crear_reserva(...)` invocan la **misma** función `dominio.validar_solicitud_intervalo(...)` y `dominio.hay_solapamiento(...)`. Una consulta de disponibilidad que devuelve «disponible» implica que la reserva equivalente sería aceptada (en ausencia de cambios entre ambas llamadas). La validación del solicitante se ejecuta solo en `crear_reserva` (en su posición 2 del orden). Cuando hay conflicto, `Superposicion` y la respuesta «no disponible» incluyen las reservas activas en conflicto (ID, solicitante, intervalo) para armar el mensaje. La UI no reimplementa la regla: ambos botones llaman al servicio.

### 6.4 Cancelación

- Solo reservas `ACTIVA` pueden cancelarse (incluso si su intervalo ya comenzó o terminó); cancelar una ya cancelada o inexistente es un error de dominio explícito.
- La cancelación cambia `estado`, registra `cancelada_en` y **no borra** la fila.
- Una reserva cancelada deja de participar en el cálculo de solapamiento.

### 6.5 Atomicidad

Crear reserva = verificar solapamiento + insertar dentro de **una transacción** (`BEGIN IMMEDIATE`) para evitar doble confirmación incluso con dos procesos locales o dos sesiones de navegador (Reflex puede atender eventos de varias sesiones a la vez; cada handler abre su propia conexión). No se aborda concurrencia distribuida.

## 7. Tiempo y formato de fechas

- Formato de entrada y salida: ISO 8601 local sin offset, `YYYY-MM-DDTHH:MM` (segundos no admitidos). El campo `datetime-local` de HTML (`rx.input(type="datetime-local")`) entrega este mismo formato; el servicio valida igualmente la cadena recibida.
- Zona horaria: **hora local del laboratorio, sin conversión** (se documenta como supuesto; entradas con offset `Z`/`+hh:mm` se rechazan).
- El reloj se inyecta (`Callable[[], datetime]`); en pruebas es fijo, en la app es la hora local del sistema.
- Comparaciones sobre `datetime` parseados, no sobre cadenas.

## 8. Interfaz Reflex

Una página principal (`/`) con tres pestañas controladas por `State.pestana_activa`: «Reservar» (activa por defecto), «Disponibilidad» y «Reservas». La separación y los mensajes independientes son una decisión humana del Paso 26, tomada después de revisar el código de la interfaz.

1. **Reservar**: selector de unidad, solicitante, inicio y fin; botón «Reservar» → confirmación con ID o mensaje de error en elementos propios del formulario.
2. **Disponibilidad**: selector de unidad, inicio y fin; botón «Consultar» → mensaje «Disponible» / «No disponible: …» / error de validación en elementos propios del formulario.
3. **Reservas**: tabla ordenada por inicio y luego ID, con ID, unidad, solicitante, inicio, fin y estado, filtros por unidad y estado, y botón «Cancelar» en las reservas activas (las canceladas siguen visibles); los mensajes de cancelación tienen sus propios elementos.

Comportamiento del `State`:

- Vars de formulario, `pestana_activa` y mensajes independientes (`mensaje_exito_reserva`, `mensaje_error_reserva`, `mensaje_exito_disponibilidad`, `mensaje_error_disponibilidad`, `mensaje_exito_cancelacion`, `mensaje_error_cancelacion`) con tipos explícitos; lista de reservas cargada desde el servicio.
- `cambiar_pestana` solo acepta las tres pestañas conocidas y actualiza `pestana_activa`.
- Los handlers son **delgados**: llaman a funciones de `reservas_ui/[presentacion.py](http://presentacion.py)` (que reciben el servicio y devuelven mensajes y filas listos para mostrar) y asignan el resultado a las vars. Así la lógica de la UI se prueba sin levantar Reflex y los handlers se prueban con una BD temporal.
- `on_load` y cada handler que modifique datos recargan la lista desde SQLite.
- Cada operación limpia y actualiza solo los mensajes de su formulario; no usa un par de mensajes global.
- Los handlers capturan las excepciones de dominio (§9) y las convierten en el mensaje del formulario correspondiente; ninguna excepción llega al usuario como traza.
- El inventario de unidades para el selector se lee con el servicio.

Mantenimiento:

```text
python -m reservas init-db [--reset] [--yes]
reflex run

```

- Variable opcional `RESERVAS_DB` para elegir el archivo de BD (por defecto `data/reservas.db`); las pruebas usan una BD temporal.
- `init-db` es idempotente; `--reset` borra reservas y requiere confirmación (`--yes` para uso no interactivo). Códigos de salida de `init-db`: `0` éxito, `1` error.

## 9. Errores

Excepciones de dominio: `UnidadDesconocida`, `SolicitanteInvalido`, `FechaInvalida`, `IntervaloInvalido`, `LimiteExcedido`, `Superposicion`, `ReservaNoEncontrada`, `ReservaYaCancelada`. Cada una con mensaje en español claro (el de `Superposicion` identifica la reserva en conflicto); el `State` las traduce a un mensaje visible en pantalla. No se muestran stack traces al usuario; los errores inesperados se registran en el log y se muestra un mensaje genérico.

## 10. Persistencia y reinicio

- Archivo SQLite `data/reservas.db` (ignorado por Git). No se usa la base `reflex.db` de Reflex porque no se definen `rx.Model`.
- `init-db` crea el esquema y siembra unidades desde `data/inventario.json` sin tocar reservas existentes.
- `PRAGMA foreign_keys = ON` en cada conexión.
- Persistencia verificada: crear activas + cancelada → cerrar → reabrir → comparar contenido (automática en `test_[persistencia.py](http://persistencia.py)` y en RF-11 de `e2e/test_requisitos.py`); el procedimiento manual histórico está en `docs/agent/[verificacion-persistencia.md](http://verificacion-persistencia.md)`.

## 11. Estrategia de pruebas

Cada prueba usa BD temporal (`tmp_path`) y reloj fijo. Las pruebas de reglas se hacen sobre servicio y dominio, sin levantar Reflex.


| Requisito            | Archivo                                              | Casos mínimos                                                                                                                                                                                      |
| -------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Creación válida      | `test_[creacion.py](http://creacion.py)`             | Reserva válida devuelve ID y estado ACTIVA                                                                                                                                                         |
| Superposición        | `test_[solapamiento.py](http://solapamiento.py)`     | 10:30–11:30 rechazada con MIC-01 10:00–11:00; contención total; mismo intervalo exacto                                                                                                             |
| Límites consecutivos | `test_[solapamiento.py](http://solapamiento.py)`     | 11:00–12:00 permitida; 09:00–10:00 permitida                                                                                                                                                       |
| Unidades distintas   | `test_[solapamiento.py](http://solapamiento.py)`     | MIC-02 10:00–11:00 permitida con MIC-01 ocupado                                                                                                                                                    |
| Entradas inválidas   | `test_[validaciones.py](http://validaciones.py)`     | Unidad desconocida, solicitante vacío/espacios, fecha inválida o con offset, inicio ≥ fin, fecha pasada, duración y anticipación excedidas; límites exactos (8 h, 90 días, inicio = ahora) válidos |
| Inventario           | `test_[inventario.py](http://inventario.py)`         | Se leen las 5 unidades con sus equipos                                                                                                                                                             |
| Repositorio          | `test_[repositorio.py](http://repositorio.py)`       | Esquema creado; siembra repetida sin duplicados; ID nunca reutilizado                                                                                                                              |
| CLI `init-db`        | `test_[cli.py](http://cli.py)`                       | Idempotente; `--reset` borra reservas; sin `--reset` no las toca                                                                                                                                   |
| Cancelación          | `test_[cancelacion.py](http://cancelacion.py)`       | Conserva ID y datos; libera horario; doble cancelación e ID inexistente rechazados; cancelar reserva ya iniciada permitido                                                                         |
| Disponibilidad       | `test_[disponibilidad.py](http://disponibilidad.py)` | Misma decisión que `reservar`; cancelada no bloquea; «no disponible» lista los conflictos; no crea reservas                                                                                        |
| Persistencia         | `test_[persistencia.py](http://persistencia.py)`     | Activas y canceladas sobreviven a cierre y reapertura                                                                                                                                              |
| Frontera de capas    | `test_frontera_[reflex.py](http://reflex.py)`        | Ningún módulo de `src/reservas/` importa `reflex`                                                                                                                                                  |


Interfaz Reflex (pruebas **automáticas**, sin navegador):


| Qué se verifica      | Archivo                                             | Casos mínimos                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Capa de presentación | `test_ui_[presentacion.py](http://presentacion.py)` | Cada excepción de dominio → mensaje esperado; éxito de reservar → mensaje con ID; filas con estado ACTIVA/CANCELADA; consulta «disponible» / «no disponible»                                                                                                                                                                                                                                           |
| Handlers del `State` | `test_ui_[estado.py](http://estado.py)`             | `on_load` carga unidades y reservas; reservar válido actualiza la lista; reservar con solapamiento deja `mensaje_error_reserva` y no cambia la lista; límites consecutivos aceptados; cancelar mantiene la fila como CANCELADA y libera el horario; filtros por unidad y estado; tras reservar con éxito se limpian solicitante, inicio y fin (se conserva la unidad) y tras un error se conservan los valores; `cambiar_pestana` acepta solo pestañas conocidas; los mensajes de reserva, disponibilidad y cancelación son independientes |
| Humo de la app       | `test_ui_[humo.py](http://humo.py)`                 | `reservas_ui` se importa, la página `/` está registrada, el `State` declara todas sus vars y la interfaz incluye las tres pestañas y los seis elementos de mensaje                                                                                                                                                                                                                                      |


Reglas para estas pruebas: BD temporal por prueba, reloj fijo, **sin parchear vars de clase** (ver §2) y sin levantar el servidor. La técnica concreta para invocar los handlers (instanciar el `State` y llamar a la función del handler) se confirma contra la documentación de Reflex 0.10 al ejecutar la tarea y se registra en `docs/agent/[progreso.md](http://progreso.md)`.

Además, la suite **Playwright** `e2e/test_requisitos.py` automatiza el flujo real en
Chromium headless: crear 10:00–11:00 en MIC-01; rechazo de 10:30–11:30; aceptación de
11:00–12:00; reserva simultánea en MIC-02; cancelación y liberación; persistencia tras
reiniciar `reflex run`; cambio entre las tres pestañas y conservación de los mensajes
propios de cada formulario. La suite levanta un servidor aislado en los puertos 3020/8020
con una base temporal, de modo que no toca `data/reservas.db`. Los resultados manuales
anteriores siguen registrados en `docs/agent/[progreso.md](http://progreso.md)`.

Registrar en `docs/agent/[progreso.md](http://progreso.md)` el comando, versiones (Python, Reflex, pytest) y resultado real de cada ejecución.

## 12. Trazabilidad con el agente

- **Preparación** (`docs/agent/[preparacion-agente.md](http://preparacion-agente.md)`): entorno, versión y modelo (o «no visible»), función, instrucciones usadas (extracto saneado de [`CLAUDE.md`](http://CLAUDE.md) y del skill `reflex-rules`), contexto incluido/excluido, permisos y aprobaciones aplicadas (incluida la aprobación del acceso a red para `reflex init`), qué se revisó antes de aceptar.
- **Progreso** (`docs/agent/[progreso.md](http://progreso.md)`): memoria versionada entre sesiones.
- **Delegación** (`docs/agent/[delegacion.md](http://delegacion.md)`): tres episodios reales con el formato objetivo → contexto/instrucción → resultado del agente → decisión humana → enlace verificable (commit/prueba).
- Episodios candidatos (confirmar según lo ocurrido realmente): (1) implementación de la regla de solapamiento y sus casos de borde; (2) capa de persistencia SQLite y verificación tras reinicio; (3) interfaz Reflex y `State` que delega en el servicio.
- Commits pequeños por tarea; cambios de especificación en commits separados con el motivo.

## 13. Estructura del README (entregable)

1. **Especificación breve**: problema, alcance, requisitos verificables, reglas, supuestos, criterios de aceptación; enlace a [`spec.md`](http://spec.md).
2. **Solución**: estructura, decisiones técnicas (incluida la elección de Reflex), requisitos previos y versiones (Python, Reflex, Node/bun gestionado por Reflex; red necesaria solo para la instalación inicial), instalación, carga/reinicio de datos (con advertencia de borrado), comandos (`reflex run`, `pytest`), ejemplo de entrada y salida (campos del formulario y mensajes resultantes), ubicación de los datos, pendientes y limitaciones.
3. **Preparación del agente**: entorno/modelo, instrucciones, contexto, permisos, adaptación, retención del progreso, con enlaces a evidencia.
4. **Registro de decisiones y delegación**: decisiones, motivos, alternativas, consecuencias y los tres episodios.

## 14. Definición de terminado

Una tarea está terminada cuando:

- cumple [`spec.md`](http://spec.md) y respeta este plan;
- las pruebas correspondientes pasan (comando y resultado registrados) y `ruff check .` no reporta errores;
- si toca la interfaz, la suite Playwright y/o la comprobación manual registrada coincide con lo esperado;
- no quedan errores bloqueantes;
- su checkbox se actualiza en [`tasks.md`](http://tasks.md) y hay una entrada en `docs/agent/[progreso.md](http://progreso.md)`.

El proyecto está terminado cuando, además, el README cumple las cuatro secciones, la persistencia se verificó tras reinicio, existen los tres episodios de delegación con evidencia enlazada y el repositorio es accesible y reproducible sin la cuenta de modelo del autor.
