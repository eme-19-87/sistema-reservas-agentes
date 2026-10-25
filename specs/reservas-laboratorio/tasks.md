# Tareas — Sistema de reservas de laboratorio

> Ejecutar las tareas en orden. No comenzar la siguiente hasta implementar y validar la actual. Marcar `[x]` solo con pruebas pasando y con la entrada correspondiente en `docs/agent/[progreso.md](http://progreso.md)` (comando, versiones, resultado real, incluidos fallos o pasos no ejecutados).

## Fase 0 — Especificación y preparación del agente

- \[x\] **Paso 1 — Repositorio y especificación inicial**
  - Inicializar Git y `.gitignore` (`.venv/`, `data/*.db`, `.web/`, `.states/`, `assets/external/`, `__pycache__/`).
  - Incorporar [`CLAUDE.md`](http://CLAUDE.md), `specs/reservas-laboratorio/[spec.md](http://spec.md)`, [`plan.md`](http://plan.md) y [`tasks.md`](http://tasks.md).
  - Commit inicial con la versión inicial de la especificación (base para recuperar su evolución).
- \[x\] **Paso 2 — Preparación del agente y registro**
  - Crear `docs/agent/preparacion-agente.md`: entorno, versión y modelo (o «no visible»), función, motivo de la elección, instrucciones usadas (extracto saneado de [`CLAUDE.md`](http://CLAUDE.md)), contexto incluido y excluido, herramientas y permisos, aprobaciones previstas.
  - Crear `docs/agent/progreso.md`(memoria versionada) y `docs/agent/delegacion.md` (plantilla de episodios).
  - Incorporar el skill `.claude/skills/reflex-rules/SKILL.md` y registrar su uso real como adaptación específica.

## Fase 1 — Núcleo (sin Reflex)

- \[x\] **Paso 3 — Proyecto Python y herramientas**
  - `pyproject.toml` (`requires-python >=3.11`), `requirements-dev.txt` con `reflex==0.10.0`, `pytest` y `ruff` fijados.
  - Estructura `src/reservas/` y `tests/` con [`conftest.py`](http://conftest.py) (BD temporal y reloj fijo).
  - Validar `pytest -q` (sin pruebas aún) y `ruff check .`; registrar versiones de Python, Reflex, pytest y ruff.
- \[x\] **Paso 4 — Inventario**
  - `data/inventario.json` con `MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`.
  - [`inventario.py`](http://inventario.py) de solo lectura.
  - Prueba (`test_inventario.py`): se leen las 5 unidades con sus equipos.
- \[x\] **Paso 5 — Dominio: validaciones**
  - Entidades, excepciones de dominio y parseo de fechas `YYYY-MM-DDTHH:MM`.
  - Pruebas primero (`test_validaciones.py`): unidad desconocida, solicitante vacío o solo espacios, fecha inválida, fecha con offset, `inicio >= fin`, fecha pasada, duración máxima, anticipación máxima; límites exactos válidos (8 h, 90 días, inicio = ahora).
- \[x\] **Paso 6 — Dominio: solapamiento**
  - `hay_solapamiento` con intervalos `[inicio, fin)` y `validar_solicitud_intervalo`.
  - Pruebas primero (`test_solapamiento.py`): 10:30–11:30 rechazado con 10:00–11:00; contención; intervalo idéntico; 11:00–12:00 permitido; 09:00–10:00 permitido; unidades distintas simultáneas.
  - Ejecutar los casos de borde obligatorios y registrarlos (adaptación «turnos consecutivos»).
- \[x\] **Paso 7 — Repositorio SQLite**
  - Esquema `unidades` y `reservas` con restricciones, `PRAGMA foreign_keys = ON`, índice.
  - Siembra de unidades idempotente; inserción dentro de `BEGIN IMMEDIATE`.
  - Pruebas (`test_repositorio.py`): esquema creado, siembra repetida sin duplicados, ID nunca reutilizado.
- \[x\] **Paso 8 — Servicio de reservas**
  - `crear_reserva`, `cancelar_reserva`, `listar_reservas` (filtros por unidad y estado) y `consultar_disponibilidad` usando la **misma** validación y regla de solapamiento. `listar_reservas` ordena por inicio y luego ID; los conflictos (ID, solicitante, intervalo) se exponen para los mensajes.
  - Pruebas: `test_creacion.py`, `test_cancelacion.py` (conserva ID y datos, libera horario, doble cancelación e ID inexistente rechazados, cancelar reserva ya iniciada permitido), `test_disponibilidad.py` (misma decisión que reservar; cancelada no bloquea; no crea reservas).
- \[x\] **Paso 9 — Persistencia tras reinicio (automática)**
  - `test_persistencia.py`: crear activas y una cancelada, cerrar conexión, reabrir sobre el mismo archivo y comparar contenido.
  - Registrar la ejecución (adaptación «procedimiento de persistencia»).
- \[x\] **Paso 10 — CLI de mantenimiento** `init-db`
  - `python -m reservas init-db` idempotente; `--reset` con confirmación y `--yes`.
  - Pruebas (`test_cli.py`): idempotente; reset borra reservas; sin `--reset` no las toca.
- \[x\] **Paso 11 — Frontera de capas**
  - `test_frontera_reflex.py`: ningún módulo de `src/reservas/` importa `reflex`.

## Fase 2 — Interfaz Reflex

- \[x\] **Paso 12 — Scaffold de Reflex** *(requiere aprobación humana de acceso a red)*
  - `reflex init`, [`rxconfig.py`](http://rxconfig.py) con `app_name = "reservas_ui"`, módulo `reservas_ui/` con una página `/` mínima.
  - Verificar que `reflex run` arranca (manual, con BD temporal) y registrar versión de Reflex realmente instalada.
  - Confirmar que los artefactos de Reflex están ignorados en Git.
- \[ \] **Paso 13 — Capa de presentación (funciones puras)**
  - `reservas_ui/presentacion.py`: funciones que reciben el servicio y devuelven mensajes y filas listos para mostrar (consultar, reservar, cancelar, listar con filtros); mapeo de cada excepción de dominio a mensaje en español.
  - Pruebas primero (`test_ui_presentacion.py`): un mensaje por excepción (el de superposición nombra la reserva en conflicto); éxito con ID; filas ACTIVA/CANCELADA; «disponible» / «no disponible» con conflictos.
- \[ \] **Paso 14 —** `State`**: carga inicial**
  - `reservas_ui/estado.py`: vars tipadas y declaradas (sin parchear vars de clase), `on_load` que lee unidades y reservas desde SQLite.
  - Confirmar y registrar la técnica de prueba de handlers con Reflex 0.10.
  - Pruebas (`test_ui_estado.py`): `on_load` carga 5 unidades y las reservas existentes en BD temporal.
- \[ \] **Paso 15 —** `State`**: consultar disponibilidad**
  - Handler delgado que delega en presentación.
  - Pruebas: disponible; ocupado; entrada inválida muestra `mensaje_error`; límites consecutivos disponibles; no crea reservas.
- \[ \] **Paso 16 —** `State`**: reservar**
  - Handler que delega y recarga la lista; tras éxito limpia solicitante, inicio y fin (conserva la unidad) y tras un error conserva los valores ([`spec.md`](http://spec.md)).
  - Pruebas: reserva válida actualiza la lista; solapamiento deja `mensaje_error` y la lista intacta; 11:00–12:00 aceptada; MIC-02 simultánea aceptada; solicitante vacío rechazado; formulario limpio tras éxito y conservado tras error.
- \[ \] **Paso 17 —** `State`**: cancelar y filtros**
  - Handler de cancelación y filtros por unidad y estado.
  - Pruebas: la cancelada sigue en la lista como CANCELADA con sus datos; el horario queda libre; doble cancelación muestra error; filtros devuelven los subconjuntos esperados.
- \[ \] **Paso 18 — Componentes y página**
  - [`componentes.py`](http://componentes.py) y `reservas_ui.py`: formulario de disponibilidad, formulario de reserva, tabla de reservas con botón «Cancelar» solo en activas, zona de mensajes.
  - Labels asociados a campos, navegación por teclado, estados de foco básicos.
  - Sin lógica de negocio en componentes.
- \[ \] **Paso 19 — Prueba de humo de la app**
  - `test_ui_humo.py`: `reservas_ui` se importa, la página `/` está registrada, el `State` declara todas sus vars.
  - Ejecutar la suite completa (`pytest -q`) y `ruff check .`.
- \[ \] **Paso 20 — Comprobación manual en navegador**
  - Con una BD temporal, ejecutar el procedimiento: reservar 10:00–11:00 en MIC-01 → rechazar 10:30–11:30 → aceptar 11:00–12:00 → reservar MIC-02 10:00–11:00 → cancelar y verificar liberación.
  - Registrar resultados **esperados y observados**, y los pasos no ejecutados.

## Fase 3 — Verificación, documentación y entrega

- \[ \] **Paso 21 — Persistencia manual tras reinicio**
  - `docs/agent/verificacion-persistencia.md`: reservar y cancelar desde la UI, detener `reflex run`, volver a ejecutarlo y comprobar que activas y canceladas siguen presentes.
  - Registrar resultados esperados y observados.
- \[ \] **Paso 22 — README: Especificación y Solución**
  - Sección 1: problema, alcance, requisitos verificables, reglas, supuestos (zona horaria, formato, fechas pasadas, límites), criterios de aceptación; enlace a [`spec.md`](http://spec.md).
  - Sección 2: estructura, decisiones, requisitos previos y versiones (Python, Reflex, red solo en la instalación inicial), instalación, carga y reinicio de datos con advertencia de borrado, comandos, ejemplo de entrada y salida, ubicación de los datos, pendientes y limitaciones (incluido que los clics del navegador no se automatizan).
- \[ \] **Paso 23 — README: Preparación del agente y decisiones**
  - Sección 3: entorno y modelo, instrucciones, contexto, permisos, adaptaciones con enlaces a evidencia real.
  - Sección 4: decisiones significativas con motivos, alternativas y consecuencias (SQLite vs JSON, Reflex sin `rx.Model`, intervalos semiabiertos, handlers delgados).
- \[ \] **Paso 24 — Tres episodios de delegación**
  - Registrar en `docs/agent/delegacion.md` tres episodios **reales** (objetivo y requisito → contexto y extracto de instrucción → resultado del agente → decisión humana con motivo → enlace a commit, archivo o prueba).
  - Registrar correcciones solo si ocurrieron.
- \[ \] **Paso 25 — Convergencia final del SDD**
  - Releer [`spec.md`](http://spec.md) y [`plan.md`](http://plan.md); comparar con la implementación; corregir faltantes e inconsistencias (cambios de especificación en commits propios con motivo).
  - Ejecutar `pytest -q` y `ruff check .` desde un entorno limpio y registrar comandos, versiones y resultados.
  - Confirmar que no hay secretos, datos reales ni transcripciones completas en el repositorio.
- \[ \] **Paso 26 — Entrega**
  - Verificar que el repositorio sea accesible y revisar permisos; identificar rama y commit.
  - Enviar el enlace a [`dgaifirst@gmail.com`](mailto:dgaifirst@gmail.com) con el asunto exacto «Challenge IA».
