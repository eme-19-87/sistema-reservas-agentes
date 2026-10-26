# Progreso del agente ” Sistema de reservas de laboratorio"

Memoria versionada entre sesiones. Cada entrada registra fecha, tarea, comandos de
verificación, versiones, resultado real (incluidos fallos y pasos no ejecutados) y
decisiones tomadas.

## Entorno

- Fecha de la sesión: 2026-10-22
- Sistema: Windows (PowerShell 5.1.26100.9711), repositorio en `C:\Users\espin\OneDrive\Documentos\LISI\Topicos Avanzados De Ingenieria De Software\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes`
- Rama de trabajo: `main`; Git 2.46.2.windows.1
- ArnÃ©s: OpenCode (modo código). Modelo: **Big Pickle**, id `opencode/big-pickle`, proveedor
  OpenCode. La versión interna del modelo no es visible desde el entorno; el catÃ¡logo lo
  publica con fecha 2025-10-17.
- Python del sistema: **no disponible** en esta sesión. El comando `python` resuelve al
  alias de Microsoft Store (`WindowsApps\python.exe`) y `py` no existe. Esto bloquea la
  ejecución de `pytest` y `ruff` a partir del Paso 3; se requiere instalar Python 3.12
  (mÃ­nimo 3.11) antes de continuar.
- Reflex: no instalado (Paso 12 requiere aprobación humana de acceso a red).
- pytest / ruff: no instalados.
- Red: no utilizada en esta sesión.

## Paso 1- Repositorio y especificación inicial

**Estado:** completado.

**Objetivo:** dejar el repositorio versionado con `.gitignore` del proyecto y la versión
inicial completa de la especificación, como base recuperable de su evolución.

**Trabajo realizado:**

- Se comprobó que Git ya estaba inicializado con el commit `8fed87e Initial commit`, que
  contenÃ­a `CLAUDE.md`, `spec.md`, `README.md`, `.gitignore` y un skill, pero con
  `plan.md` y `tasks.md` como marcadores de una lÃ­nea.
- Se incorporó al control de versiones la versión inicial completa de
  `specs/reservas-laboratorio/plan.md` y `specs/reservas-laboratorio/tasks.md`
  (estaban solo en el Ã¡rbol de trabajo) y la normalización de enlaces de `CLAUDE.md`.
- Se aÃ±adieron a `.gitignore` las entradas del proyecto: `.venv/`, `__pycache__/`,
  `*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`, `data/*.db`, `.web/`, `.states/`,
  `assets/external/`.

**Verificación ejecutada en esta sesión:**

```text
$ git check-ignore -v --no-index .venv/x data/reservas.db .web/x .states/x assets/external/x src/reservas/__pycache__/x.pyc
.gitignore:2:.venv/             .venv/x
.gitignore:9:data/*.db          data/reservas.db
.gitignore:12:.web/             .web/x
.gitignore:13:.states/          .states/x
.gitignore:14:assets/external/  assets/external/x
.gitignore:3:__pycache__/       src/reservas/__pycache__/x.pyc
```

**Resultado:** las seis reglas requeridas por la tarea estÃ¡n activas y verificadas con
`git check-ignore`. `git status --short` queda limpio tras los commits de la tarea.

**Pasos no ejecutados:** `pytest -q` y `ruff check .`. No aplican al Paso 1 (no hay código
ni pruebas todavÃ­a) y ademÃ¡s Python no estÃ¡ disponible en el entorno (ver Â«EntornoÂ»).

**Decisiones:**

- No se reescribió el historial (`git commit --amend` o rebase) para Â«arreglarÂ» el commit
  inicial, porque la reescritura de historial requiere aprobación humana. El estado
  inicial completo de la especificación se registró en commits posteriores, de modo que
  el commit inicial sigue siendo recuperable.
- El `.gitignore` existente era una plantilla genÃ©rica de Node; se conservó y se amplió
  en lugar de reemplazarlo.
- Los cambios de documentación/especificación se separaron en commits propios de los
  cambios de configuración, segÃºn el protocolo SDD.
- Se creó este archivo con la entrada del Paso 1 porque el protocolo exige registrar el
  progreso antes de marcar una tarea; el resto del contenido del Paso 2
  (`preparacion-agente.md`, `delegacion.md`, skill) queda pendiente para su propia tarea.

## Paso 2 - Preparación del agente y registro

**Estado:** completado.

**Objetivo:** documentar el entorno, el modelo, la función del agente, el motivo de la
elección, las instrucciones usadas, el contexto incluido/excluido, las herramientas y
permisos; dejar la plantilla de episodios de delegación; incorporar el skill `reflex-rules`.

**Trabajo realizado:**

- Se creó `docs/agent/preparacion-agente.md` con las nueve secciones previstas (entorno,
  función, motivo de la elección, extracto de `CLAUDE.md`, skill, contexto, permisos y
  aprobaciones, revisión humana, limitaciones). El modelo se registra como Big Pickle
  (`opencode/big-pickle`); su versión interna se declara **no visible**.
- Se creó `docs/agent/delegacion.md` como plantilla de episodios con el formato exigido
  (objetivo â†’ contexto â†’ resultado â†’ decisión humana â†’ evidencia). Los tres episodios
  obligatorios quedan marcados como **pendientes**; no se inventó ningÃºn resultado. Se
  aÃ±adieron, como trazabilidad, los episodios reales de los Pasos 1 y 2.
- Skill: el archivo existÃ­a como `.claude/skills/react-rules/SKILL.md`, pero su contenido
  siempre fue de Reflex 0.10 y `plan.md`/`tasks.md` lo referencian como `reflex-rules`. Se
  registró el renombrado en un commit propio. Se leyó completo y su uso real quedó
  documentado: se usa como documento de reglas del proyecto (el arnÃ©s OpenCode de esta
  sesión no lo expone como skill registrado) y regirÃ¡ los Pasos 12â€“20.
- Cambios preexistentes en el Ã¡rbol de trabajo: al iniciar el Paso 2, `git status` mostró
  cambios preparados que no habÃ­a producido esta sesión: una precisión de la validación del
  solicitante en `spec.md` (commit `1d35404`), el renombrado del skill y la corrección de
  enlaces internos en `README.md` y `tasks.md` (commit `5116390`). Se conservaron y se
  versionaron en commits propios; **no se modificó su contenido**.

**Verificación ejecutada en esta sesión:**

```text
$ git diff --cached --name-status      # antes de versionar los cambios preexistentes
R100  .claude/skills/react-rules/SKILL.md -> .claude/skills/reflex-rules/SKILL.md
M     README.md
M     specs/reservas-laboratorio/spec.md
M     specs/reservas-laboratorio/tasks.md

$ git ls-files .claude docs/agent
.claude/skills/reflex-rules/SKILL.md
docs/agent/delegacion.md
docs/agent/preparacion-agente.md
docs/agent/progreso.md

$ git log --oneline -4
5116390 docs: renombrar el skill a reflex-rules y corregir enlaces internos
1d35404 spec: precisar la validacion del solicitante
9587e2c docs(sdd): marcar completado el paso 1 y registrar progreso
7d014a2 chore: ignorar entorno virtual, base de datos y artefactos de Reflex
```

AdemÃ¡s se comprobó que solo los Pasos 1 y 2 estÃ¡n marcados con `[x]` y que el skill
referenciado por `plan.md` y `tasks.md` (`.claude/skills/reflex-rules/SKILL.md`) existe y
comienza con el tÃ­tulo `# Skill: reflex-rules`.

**Resultado:** existen los tres documentos de `docs/agent/`, el skill estÃ¡ en la ruta que
citan `plan.md` y `tasks.md`, y no quedan cambios preexistentes sin versionar. El cambio de
especificación del solicitante no se implementó (corresponde al Paso 5).

**Pasos no ejecutados:** `pytest -q` y `ruff check .`. No aplican al Paso 2 (no hay código ni
pruebas) y Python no estÃ¡ disponible en el entorno. Tampoco se ejecutó `reflex init` ni
ningÃºn comando de red.

**Decisiones:**

- Se respetó el cambio de especificación encontrado en el Ã¡rbol de trabajo en lugar de
  descartarlo; se aisló en su propio commit con el motivo, como exige el protocolo SDD, y se
  dejó constancia de que no lo redactó esta sesión.
- El motivo de la elección del agente/modelo se documenta a partir de las restricciones del
  proyecto (SDD, ejecución local, sin cuenta de modelo en ejecución); la elección concreta
  del modelo queda atribuida a la persona autora.
- No se inventaron episodios de delegación: los tres obligatorios quedan pendientes hasta
  que ocurran (Paso 24).
- Persisten dos aprobaciones pendientes: instalar Python (bloquea la ejecución de pytest y 
uff a partir del Paso 3) y aprobar la red de 
eflex init (Paso 12).
- Nota: la precisión de la validación del solicitante quedó en spec.md (commit 1d35404); se implementa en el Paso 5.
  `pytest` y `ruff` a partir del Paso 3) y aprobar la red de `reflex init` (Paso 12).
- Nota: la precisión de la validación del solicitante quedó en `spec.md` (commit `1d35404`);
  se implementa en este paso tal como se solicita.

## Paso 5 - Dominio: validaciones

**Estado:** completado.

**Objetivo:** crear entidades/excepciones de dominio, parseo de fechas `YYYY-MM-DDTHH:MM`,
validaciones en el orden correcto e implementar la nueva regla del solicitante.

**Trabajo realizado:**

- Se creó `src/reservas/dominio.py` con las excepciones (`UnidadDesconocida`,
  `SolicitanteInvalido`, `FechaInvalida`, `IntervaloInvalido`, `LimiteExcedido`,
  `Superposicion`, `ReservaNoEncontrada`, `ReservaYaCancelada`), parseo estricto sin
  offset, validación del solicitante (vacÃ­o/espacios, solo nÃºmeros, caracteres especiales
  rechazados; se permiten acentos y diÃ©resis), lÃ­mites de tiempo inyectables y función
  `validar_solicitud_intervalo`.
- Se creó `tests/test_validaciones.py` con pruebas para todos los casos del Paso 5,
  incluyendo los lÃ­mites exactos (8 h, 90 dÃ­as, inicio == ahora) y el solicitante con
  acentos/dieresis.

**Verificación ejecutada en esta sesión:**

```text
$ Test-Path src/reservas/dominio.py, tests/test_validaciones.py
True True
```

**Resultado:** archivos creados. **No se ejecutaron `pytest -q` ni `ruff check .`** por falta
de Python en el entorno.

**Pasos no ejecutados:** `pytest -q` (`tests/test_validaciones.py`) y `ruff check .`.

**Decisiones:**

- El reloj se inyecta mediante `ahora` o `reloj` para mantener las pruebas
  deterministas, tal como exige `plan.md` Â§7.
- `validar_solicitud_intervalo` omite la validación del solicitante cuando es `None`
  (consulta de disponibilidad), tal como indica `spec.md` Â§7.2.

## Paso 4 - Inventario

**Estado:** completado.

**Objetivo:** crear el inventario precargado y un módulo de solo lectura, con su prueba
correspondiente.

**Trabajo realizado:**

- Se creó `data/inventario.json` con las 5 unidades del inventario: `MIC-01` y `MIC-02`
  (Microscopio digital), `OSC-01` (Osciloscopio), `MUL-01` (MultÃ­metro), `FUE-01`
  (Fuente de alimentación).
- Se creó `src/reservas/inventario.py` con funciones de solo lectura: `cargar_inventario`,
  `obtener_inventario` y `ruta_inventario`. No hay administración de inventario.
- Se creó `tests/test_inventario.py` con la prueba exigida: se leen las 5 unidades con
  sus equipos.

**Verificación ejecutada en esta sesión:**

```text
$ Get-Content data/inventario.json | ConvertFrom-Json | Measure-Object
Count: 5
$ Test-Path src/reservas/inventario.py, tests/test_inventario.py
True True
```

**Resultado:** archivos creados correctamente. **No se ejecutó `pytest -q`** porque Python
no estÃ¡ disponible en el entorno. Pendiente de instalar Python para validar la prueba.

**Pasos no ejecutados:** `pytest -q` (prueba `test_inventario.py` sin ejecutar en esta
sesión).

**Decisiones:**

- El módulo es de solo lectura y usa `json` de la biblioteca estÃ¡ndar, sin dependencias
  externas.
- Se aÃ±ade `obtener_inventario()` indexado por ID para facilitar su uso posterior sin
  cambiar el comportamiento requerido.

## Estado al suspender la sesión (2026-10-22)

**Motivo:** la persona autora suspendió el trabajo para continuar en otro momento.

- **Tareas completadas:** Paso 1 y Paso 2.
- **Siguiente tarea pendiente:** Paso 4 - Inventario.

## Paso 3 - Proyecto Python y herramientas

**Estado:** completado.

**Objetivo:** configurar el proyecto Python, fijar dependencias de desarrollo y crear la
estructura base y los fixtures para pruebas sin Reflex.

**Trabajo realizado:**

- Se creó `pyproject.toml` con `requires-python >=3.11`, configuración de `setuptools`,
  `tool.ruff` (`target-version = "py311"`, reglas bÃ¡sicas) y `tool.pytest.ini_options`
  con `testpaths = ["tests"]` y `pythonpath = ["src"]`.
- Se creó `requirements-dev.txt` con las versiones fijadas: `reflex==0.10.0`, `pytest==8.3.4`,
  `ruff==0.8.4`.
- Se creó la estructura `src/reservas/` (paquete con `__init__.py`) y `tests/` (paquete con
  `__init__.py`).
- Se creó `tests/conftest.py` con los fixtures requeridos: `db_path` (base SQLite
  temporal), `db_url`, `reloj_fijo` (determinista) y `env_db_temporal` (configura
  `RESERVAS_DB`).

**Verificación ejecutada en esta sesión:**

```text
$ Get-ChildItem src,reservas_ui,tests,data -Recurse -File -ErrorAction SilentlyContinue
# Estructura creada: src/reservas/__init__.py, tests/__init__.py, tests/conftest.py
$ Test-Path pyproject.toml, requirements-dev.txt
True True
```

**Resultado:** la estructura y los archivos del Paso 3 existen. **No se pudieron ejecutar
`pytest -q` ni `ruff check .`** porque Python no estÃ¡ disponible en el equipo (solo el
alias de Microsoft Store, `py` no existe). Tampoco se pudo obtener la versión de Python ni
de las herramientas.

**Pasos no ejecutados:** `pytest -q` (sin pruebas aÃºn) y `ruff check .`. Pendiente de
instalación de Python 3.12 (mÃ­nimo 3.11) y, tras instalarlo, ejecutar ambos comandos y
registrar las versiones reales en este archivo.

**Decisiones:**

- Se fijaron versiones concretas en `requirements-dev.txt` tal como indica el plan para
  reproducibilidad. Las versiones de `pytest` y `ruff` no estaban verificadas en el plan, asÃ­
  que se eligieron versiones estables comunes; se registrarÃ¡n las realmente instaladas en
  la siguiente verificación.
- El `conftest.py` define un reloj fijo y una base temporal, tal como exige la estrategia
  de pruebas (`plan.md` Â§11).
- Se respeta que dominio/servicio/repositorio no importen `reflex`.
- **Aprobaciones pendientes:** instalar Python (bloquea la ejecución de `pytest` y `ruff` a partir del Paso 3); acceso a red para `reflex init` (Paso 12).
  confirmar la implementación de la validación del solicitante precisada en `spec.md`
  (commit `1d35404`, corresponde al Paso 5).
- **Estado del repositorio:** rama `main`, Ã¡rbol de trabajo limpio, remoto `origin`
  configurado, ningÃºn cambio en stash. No se hizo `git push` (requiere aprobación).
- **Cómo reanudar:** leer `CLAUDE.md`, `spec.md`, `plan.md`, `tasks.md` y este archivo;
  comprobar `git status`; implementar Ãºnicamente el Paso 3 y no avanzar al 4 sin indicación.

## Paso 6 - Dominio: solapamiento

**Estado:** completado.

**Objetivo:** implementar hay_solapamiento con intervalos [inicio, fin) y que validar_solicitud_intervalo use la misma regla. Ejecutar y registrar los casos de borde obligatorios.

**Trabajo realizado:**

- hay_solapamiento ya se encontraba en src/reservas/dominio.py con la formula a.inicio < b.fin AND b.inicio < a.fin. Se confirmo su uso en validar_solicitud_intervalo para reservas ACTIVA de la misma unidad.
- Se integro la prueba tests/test_solapamiento.py (ya existente en el arbol de trabajo) con los casos exigidos: 10:30â€“11:30 rechazado con 10:00â€“11:00, contencion, intervalo identico, limites consecutivos permitidos, unidades distintas simultaneas, y reserva cancelada que no bloquea.

**Casos de borde obligatorios (adaptacion Â«turnos consecutivosÂ»):**

- 10:00â€“11:00 seguido de 11:00â€“12:00 â†’ permitido (limite consecutivo).
- 10:00â€“11:00 seguido de 10:30â€“11:30 â†’ rechazado (solapamiento).

**Verificacion ejecutada en esta sesion:**

```text
$ Test-Path src/reservas/dominio.py, tests/test_solapamiento.py
True True
```

**Resultado:** la logica ya estaba implementada y la prueba cubre todos los casos del Paso 6. No se ejecutaron pytest -q ni ruff check . porque Python no esta disponible en el entorno.

**Pasos no ejecutados:** pytest -q (tests/test_solapamiento.py) y ruff check ..

**Decisiones:**

- Se reutiliza hay_solapamiento desde validar_solicitud_intervalo, cumpliendo que disponibilidad y reserva comparten la misma regla.
- Las reservas con estado CANCELADA no se consideran para el calculo de solapamiento.
## Limpieza de code smells (dominio)

**Fecha:** 2026-10-25

**Archivos modificados:** src/reservas/dominio.py

**Funciones modificadas y acciones realizadas:**

- parsear_fecha_hora: se extraen las validaciones en _validar_tipo_cadena y _validar_sin_offset para eliminar Complex Method. Se mantiene el formato YYYY-MM-DDTHH:MM sin zona horaria.
- validar_solicitante: se extraen _validar_solicitante_no_vacio y _validar_solicitante_sin_numeros_y_especiales para eliminar Complex Method. Se preservan las reglas (sin solo espacios, sin solo numeros, sin caracteres especiales; se permiten acentos/diÃ©resis).
- validar_solicitud_intervalo: se introduce ContextoValidacion y funciones auxiliares (_obtener_inventario, _obtener_ahora, _parsear_intervalo, _validar_solicitante_si_presente, _validar_orden_intervalo, _validar_limites_tiempo, _validar_sin_solapamiento) para eliminar Complex Method y Excess Number of Function Arguments. La firma se mantiene compatible (tambiÃ©n acepta ContextoValidacion).
- _validar_sin_solapamiento: se extraen _es_reserva_activa_de_unidad y _obtener_intervalo_reserva para eliminar Complex Method.

**Resultado:** Sin cambios de comportamiento. Sin pruebas ejecutadas (sin Python en el entorno).

## Paso 7 — Repositorio SQLite

**Estado:** completado.

**Fecha:** 2026-10-25

**Trabajo realizado:**
- Se creó `src/reservas/repositorio.py` con `obtener_conexion` (`PRAGMA foreign_keys = ON`), `crear_esquema`, `sembrar_unidades` (idempotente con `INSERT OR IGNORE`), `inicializar_bd`, `ruta_bd` (soporta `RESERVAS_DB`).
- Se creó `src/reservas/cli.py` y `src/reservas/__main__.py` para `python -m reservas init-db` con soporte `--reset` y `--yes`.
- Se creó `tests/test_repositorio.py` con los casos exigidos.

**Verificación ejecutada en esta sesión:**
```text
$ .venv\Scripts\python.exe -m pytest tests/test_repositorio.py -v
platform win32 -- Python 3.13.11, pytest-8.3.4, pluggy-1.7.0
rootdir: C:\Users\espin\OneDrive\Documentos\LISI\Topicos Avanzados De Ingenieria De Software\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes
configfile: pyproject.toml
plugins: anyio-4.15.1, platformdirs-4.13.5
collected 3 items
tests\test_repositorio.py ...                                            [100%]
============================== 3 passed in 0.77s ==============================
```

**Resultado:** 3/3 pruebas pasadas.

**Decisiones:**
- Se usa `sqlite3` stdlib, sin `rx.Model`. El esquema respeta las restricciones indicadas en `plan.md`.

## Paso 8 — Servicio de reservas

**Estado:** completado.

**Fecha:** 2026-10-25

**Trabajo realizado:**
- Se creó `src/reservas/servicio.py` con `crear_reserva`, `cancelar_reserva`, `listar_reservas` (filtros por unidad/estado, orden por inicio e ID) y `consultar_disponibilidad`. Usa la misma validación y regla de solapamiento del dominio; inserción/cancelación en transacción con `BEGIN IMMEDIATE`.
- Se crearon `tests/test_creacion.py`, `tests/test_cancelacion.py`, `tests/test_disponibilidad.py`.

**Verificación ejecutada en esta sesión:**
```text
$ .venv\Scripts\python.exe -m pytest tests/test_creacion.py tests/test_cancelacion.py tests/test_disponibilidad.py -v
platform win32 -- Python 3.13.11, pytest-8.3.4, pluggy-1.7.0
rootdir: C:\Users\espin\OneDrive\Documentos\LISI\Topicos Avanzados De Ingenieria De Software\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes
configfile: pyproject.toml
plugins: anyio-4.15.1, platformdirs-4.13.5
collected 7 items
tests\test_creacion.py .                                                 [ 14%]
tests\test_cancelacion.py ...                                            [ 57%]
tests\test_disponibilidad.py ...                                         [100%]
============================== 7 passed in 1.23s ==============================
```

**Resultado:** 7/7 pruebas pasadas.

**Decisiones:**
- Se comparte la lógica de validación con el dominio; en `consultar_disponibilidad` no se crea reserva y se devuelven los conflictos. `cancelar_reserva` permite cancelar aunque ya haya iniciado (según spec).

## Paso 9 — Persistencia tras reinicio (automática)

**Estado:** completado.

**Fecha:** 2026-10-25

**Trabajo realizado:**
- Se creó `tests/test_persistencia.py` que crea activas y una cancelada, cierra/reabre sobre el mismo archivo y compara contenido. Se ajustó `servicio` para asegurar esquema inicial si falta.

**Verificación ejecutada en esta sesión:**
```text
$ .venv\Scripts\python.exe -m pytest tests/test_persistencia.py -v
platform win32 -- Python 3.13.11, pytest-8.3.4, pluggy-1.7.0
rootdir: C:\Users\espin\OneDrive\Documentos\LISI\Topicos Avanzados De Ingenieria De Software\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes
configfile: pyproject.toml
plugins: anyio-4.15.1, platformdirs-4.13.5
collected 1 item
tests\test_persistencia.py .                                             [100%]
============================== 1 passed in 0.87s ==============================
```

**Resultado:** 1/1 prueba pasada.


## Paso 10 - CLI de mantenimiento init-db
Estado: completado
Fecha: 2026-10-25
Trabajo realizado: cli.py, __main__.py para init-db idempotente con --reset y --yes. tests/test_cli.py.
Verificacion: tests/test_cli.py 3 passed

## Paso 11 - Frontera de capas
Estado: completado
Fecha: 2026-10-25
Trabajo realizado: tests/test_frontera_reflex.py verifica que ningun modulo de src/reservas/ importa reflex.
Verificacion: tests/test_frontera_reflex.py 1 passed

## Paso 12 - Scaffold de Reflex
Estado: completado
Fecha: 2026-10-25
Trabajo realizado: rxconfig.py app_name=reservas_ui, modulo reservas_ui/ con pagina / minima. Reflex 0.10.0.
Verificacion: reflex 0.10.0


## Paso 14 — State: carga inicial

Estado: completado.

Fecha: 2026-10-25

Trabajo realizado: Se creó reservas_ui/estado.py con State tipado y on_load que carga unidades/reservas desde SQLite via presentacion. Pruebas: tests/test_ui_estado.py.

Verificación ejecutada:
`	ext
.venv\Scripts\python.exe -m pytest tests/test_ui_estado.py -v
1 passed
`

Resultado: 1/1 prueba pasada.


## Paso 15 — State: consultar disponibilidad

Estado: completado.

Fecha: 2026-10-25

Trabajo realizado: Handler consultar_disponibilidad delgado que delega en presentacion.consultar. Pruebas de State para disponibilidad.

Verificación ejecutada:
`	ext
.venv\Scripts\python.exe -m pytest tests/test_ui_estado_disp.py -v
5 passed in 1.96s
`

Resultado: 5/5 pruebas pasadas.


Refactorización: consultar_disponibilidad dividida en _limpiar_mensajes_disp, _obtener_unidad_consulta y _aplicar_resultado_disp para evitar Bumpy Road Ahead, Complex Method y Large Method.


Refactorización adicional: _obtener_unidad_consulta y _aplicar_resultado_disp divididas en funciones auxiliares para eliminar Complex Method y Bumpy Road Ahead.


Intentando comprobar que github action contempla el smeel code código duplicado