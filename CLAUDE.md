<!-- reflex managed begin (do not edit inside this block; add custom content outside the markers) -->
# Agents

This project uses the **Reflex agent skills** � up-to-date knowledge for building full-stack Python web apps with [Reflex](https://reflex.dev). Install them first, then use them as described below.

## Installing the Skills

Before working on this project, make sure the Reflex skills are available to you.

### Claude Code

If the skills are not already available, install them yourself by running these shell commands:

```bash
claude plugin marketplace add reflex-dev/agent-skills
claude plugin install reflex@reflex-agent-skills
```

Newly installed plugins load on the next session. After installing, tell the user to restart the session so the skills auto-load; until then, read the skill files directly from `~/.claude/plugins/` when you need them.

### Other agents (Cursor, OpenCode, Codex, Pi)

```
npx skills add reflex-dev/agent-skills
```

Or clone https://github.com/reflex-dev/agent-skills and copy the `skills/` folders into your agent's skill directory (see the repo README for paths).

### Verifying

Before writing or editing any Reflex code, confirm these three skills are available: `reflex-docs`, `setup-python-env`, and `reflex-process-management`. If they are not, STOP and run the install step above � do not proceed without them.

## Using the Skills

### Reflex documentation

For anything about Reflex APIs � components, state management, events, styling, database, routing, authentication � use the **reflex-docs** skill rather than relying on memory. It carries current, version-accurate docs.

### Initializing a new Reflex project

When starting a new Reflex project or setting up a development environment, you **must** follow the **setup-python-env** skill before doing anything else.

Do not skip any steps. Do not assume a virtual environment or Reflex is already available � always verify first by following the skill's instructions in order.

After the environment is ready and Reflex is installed, run:

```bash
reflex init
```

Then proceed with the user's request.

### Managing a Reflex process

When you need to compile, run, reload, or debug a Reflex application, follow the **reflex-process-management** skill for the correct sequence and error investigation steps.
<!-- reflex managed end -->

# [CLAUDE.md](http://CLAUDE.md)

## Proyecto

Sistema local de reservas de equipos de laboratorio (challenge «Desarrollo de un sistema de reservas con agentes»). Permite consultar disponibilidad por unidad e intervalo, reservar y cancelar conservando el historial, con persistencia entre reinicios. La interfaz es una aplicación web local construida con **Reflex**.

Este proyecto utiliza **Spec-Driven Development (SDD)**. La especificación es la fuente de verdad.

## Documentos de referencia (leer antes de escribir código)

- `specs/reservas-laboratorio/spec.md` — qué se construye, reglas, supuestos y criterios de aceptación.
- `specs/reservas-laboratorio/plan.md` — cómo se construye (arquitectura, decisiones técnicas).
- `specs/reservas-laboratorio/tasks.md` — tareas ordenadas y su estado.
- `docs/agent/progreso.md` — progreso y decisiones vigentes (memoria versionada entre sesiones).

## Protocolo SDD (ESTRICTO)

1. ANTES de crear o modificar código fuente, lee [`spec.md`](http://spec.md), [`plan.md`](http://plan.md), [`tasks.md`](http://tasks.md) y `docs/agent/progreso.md`.
2. No escribas código que no esté respaldado por [`spec.md`](http://spec.md) y [`plan.md`](http://plan.md). Si falta algo, propón el cambio a la especificación y espera aprobación humana; no lo resuelvas en silencio.
3. Identifica la primera tarea pendiente de [`tasks.md`](http://tasks.md) e implementa **únicamente** esa tarea.
4. Escribe primero la prueba de la regla de negocio y después la implementación cuando la tarea toque reglas del dominio.
5. Ejecuta las pruebas y el linter. Corrige los errores antes de continuar.
6. Marca la tarea como `[x]` solo después de que las pruebas pasen con éxito, y registra el resultado real (comando, versión, salida resumida) en `docs/agent/progreso.md`.
7. No implementes tareas futuras salvo petición explícita del usuario.
8. Todo cambio en la especificación se hace en un commit propio, con el motivo en el mensaje, para que la evolución sea recuperable en Git.

## Reglas de dominio (resumen; la versión normativa está en [spec.md](http://spec.md))

- Cada ID del inventario (`MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`) es una **unidad física distinta**. Una reserva = una unidad.
- Intervalos **semiabiertos** `[inicio, fin)`: dos reservas activas de la misma unidad se superponen si y solo si `a.inicio < b.fin` y `b.inicio < a.fin`.
- Límites consecutivos permitidos (11:00–12:00 después de 10:00–11:00). Unidades distintas pueden reservarse a la misma hora.
- Solo las reservas **activas** bloquean. Una cancelada conserva ID y datos, cambia de estado y libera el intervalo.
- Validar: unidad conocida, solicitante no vacío ni solo espacios, fecha/hora válidas, `inicio < fin` estricto, y los límites de duración/anticipación/fechas pasadas definidos en [`spec.md`](http://spec.md).
- La **consulta de disponibilidad y la creación de reservas usan la misma función de validación y detección de solapamiento**. No duplicar la regla.

## Reglas de arquitectura

- **Python 3.12** (mínimo 3.11) con **Reflex 0.10.0** (`reflex==0.10.0`, fijado en `requirements-dev.txt`) como framework de interfaz web local. No actualizar Reflex sin aprobación humana y sin registrar el motivo en [`progreso.md`](http://progreso.md).
- Dominio, servicio y repositorio usan **solo biblioteca estándar** y **no importan** `reflex`.
- Persistencia en **SQLite** (`sqlite3` de la stdlib), archivo en `data/reservas.db`. No se usa `rx.Model` ni las migraciones de Reflex. Prohibido guardar estado solo en memoria.
- Interfaz: **páginas y componentes Reflex** (`reservas_ui/`). Una CLI mínima (`python -m reservas init-db`) solo para cargar o reiniciar datos.
- Capas separadas: `domain` (reglas puras) → `services` (casos de uso) → `repository` (SQLite) → `reservas_ui` (State de Reflex + componentes). Los componentes llaman a handlers del `State`; el `State` llama a [`presentacion.py`](http://presentacion.py), que llama al servicio.
- El `rx.State` **no contiene reglas de negocio** ni es fuente de verdad: solo guarda estado de pantalla (campos del formulario, mensajes, lista mostrada). Después de cada operación se recarga desde SQLite, y `on_load` lee siempre de la base.
- No guardar conexiones SQLite ni objetos no serializables en vars del `State`; cada handler abre y cierra su propia conexión mediante el servicio.
- Vars del `State` con tipos explícitos y **todas declaradas** en la clase; las que no deban enviarse al cliente usan prefijo `_`. Valores mutables por defecto con `default_factory`.
- Reflex 0.10: no asignar vars a través de la clase (`Estado.campo = ...`) ni parchearlas con `monkeypatch`/`patch.object` (lanza `TypeError`); no leer vars de backend desde la clase.
- Los handlers del `State` son delgados: delegan en `reservas_ui/[presentacion.py](http://presentacion.py)` (funciones puras que reciben el servicio) y asignan el resultado.
- Los errores de dominio se capturan en el handler y se muestran como mensaje en pantalla (sin stack traces).
- El reloj se **inyecta** (no llamar a `[datetime.now](http://datetime.now)()` dentro del dominio) para que las pruebas sean deterministas.
- El inventario se carga desde `data/inventario.json` (solo lectura; no hay administración de inventario).
- Las pruebas del dominio, servicio, persistencia, presentación y handlers del `State` deben ejecutarse **sin servidor Reflex en ejecución, sin navegador, sin red y sin cuenta de modelo**. Solo el recorrido de clics en el navegador es manual.

## Reglas de implementación

- Analiza el código existente antes de modificarlo; prefiere cambios pequeños e incrementales.
- No agregues funcionalidades fuera de la tarea actual (sin autenticación, notificaciones, pagos, integraciones, concurrencia distribuida).
- Tipado estático (`type hints`) en todo el código público; nombres explícitos, sin abreviaturas.
- Errores de validación mediante excepciones de dominio propias, con mensaje claro.
- Usar solo solicitantes **ficticios** en ejemplos, pruebas y datos. Nunca datos reales de estudiantes.
- No incluir secretos, tokens, credenciales ni transcripciones completas de conversaciones en el repositorio.
- Ignorar en Git los artefactos generados por Reflex (`.web/`, `.states/`, `assets/external/`, `*.db`).

## Comandos

- Crear entorno: `python -m venv .venv && source .venv/bin/activate`
- Instalar dependencias: `pip install -r requirements-dev.txt`
- Inicializar Reflex (una sola vez; **requiere red** para descargar el runtime del frontend): `reflex init`
- Ejecutar pruebas: `pytest -q`
- Linter: `ruff check .`
- Cargar inventario / reiniciar datos: `python -m reservas init-db` (el reinicio con `--reset` **borra reservas**; requiere confirmación humana)
- Aplicación: `reflex run` (frontend en [`http://localhost:3000`](http://localhost:3000), backend en `:8000`)

## Permisos y aprobaciones del agente

**Permitido sin preguntar:** leer archivos del repositorio; crear y editar archivos de `src/`, `reservas_ui/`, `tests/` y `docs/`, y marcar casillas en `specs/reservas-laboratorio/[tasks.md](http://tasks.md)`; ejecutar `pytest`, `ruff`, `python -m reservas ...` sobre una base temporal o de prueba; `git status`, `git diff`, `git add`, `git commit` en la rama de trabajo.

**Requiere aprobación humana explícita:**

- Instalar o agregar dependencias nuevas, y ejecutar `reflex init` o cualquier comando que descargue paquetes (acceso a red).
- Cambiar [`spec.md`](http://spec.md) o [`plan.md`](http://plan.md) (propuesta primero, edición después).
- Borrar o reiniciar `data/reservas.db`, o cualquier comando destructivo (`rm`, `git reset --hard`, `git push --force`).
- `git push`, cambios de rama o reescritura de historial.
- Levantar `reflex run` de forma prolongada (se hace con una base temporal o de prueba).

**Prohibido:** acceso a red fuera de la instalación aprobada, lectura de variables de entorno con secretos, escribir fuera del repositorio.

## Revisión humana

Antes de aceptar un resultado del agente, la persona revisa: el `git diff` completo, la salida real de `pytest`, que la regla afectada coincida con [`spec.md`](http://spec.md) y, para cambios de interfaz, una comprobación manual en el navegador con los resultados esperados y observados. El agente **distingue** lo que informa de lo que efectivamente ejecutó: nunca declara «pruebas pasan» sin haber corrido el comando en esa sesión, y no afirma que la interfaz funciona sin haberla levantado.

## Adaptaciones específicas para este proyecto (con evidencia de uso)

1. **Turnos consecutivos:** ante cualquier cambio en la lógica de solapamiento, ejecutar obligatoriamente los casos de borde: `10:00–11:00` seguido de `11:00–12:00` (permitido) y de `10:30–11:30` (rechazado). Evidencia en `tests/test_[solapamiento.py](http://solapamiento.py)` y en `docs/agent/[progreso.md](http://progreso.md)`.
2. **Procedimiento de persistencia:** tras cambios en repositorio o interfaz, correr `tests/test_[persistencia.py](http://persistencia.py)` (crea reservas, cancela una, cierra la conexión, reabre y compara) y el procedimiento manual de `docs/agent/[verificacion-persistencia.md](http://verificacion-persistencia.md)` (reservar y cancelar desde la UI, detener y volver a ejecutar `reflex run`, y comprobar que activas y canceladas siguen presentes) con resultados esperados y observados.
3. **Frontera Reflex:** antes de aceptar cambios en `reservas_ui/`, comprobar que ningún módulo de `src/reservas/` importa `reflex` (`grep -rn "import reflex" src/` debe no devolver resultados).

## Registro de progreso y delegación

- Al cerrar cada tarea, añade una entrada a `docs/agent/[progreso.md](http://progreso.md)`: fecha, tarea, comando de verificación, versión de Python/Reflex/pytest, resultado (incluidos fallos o pasos no ejecutados) y decisiones tomadas.
- Cuando se delegue una pieza significativa al agente, registra un episodio en `docs/agent/[delegacion.md](http://delegacion.md)` con: objetivo y requisito → contexto e instrucción (extracto) → resultado del agente → decisión humana (aceptar/corregir/rechazar y motivo) → enlace a commit, archivo o prueba. Registrar correcciones **solo si ocurrieron**; no inventar fallas.

## Regla de finalización

Una tarea está terminada cuando:

- su implementación cumple [`spec.md`](http://spec.md) y respeta [`plan.md`](http://plan.md);
- las pruebas automáticas correspondientes pasan y el linter no reporta errores;
- si toca la interfaz, las pruebas `test_ui_*` pasan, la aplicación Reflex arranca y la comprobación manual registrada coincide con lo esperado;
- no quedan errores bloqueantes conocidos;
- la casilla de [`tasks.md`](http://tasks.md) está marcada y `docs/agent/[progreso.md](http://progreso.md)` actualizado con evidencia real;
- el cambio está en un commit con mensaje descriptivo.
