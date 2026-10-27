# Sistema de reservas de laboratorio — SDD

Aplicación web local para que la coordinación de un laboratorio consulte
disponibilidad, reserve y cancele equipos sin perder el historial. Sustituye los
mensajes y la planilla por una única fuente de verdad que aplica siempre las mismas
reglas.

El proyecto se desarrolla con **Spec-Driven Development (SDD)** y un agente de
programación. La especificación es la fuente normativa; el plan técnico y el registro
de progreso se mantienen en el repositorio.

> **Estado:** aplicación implementada y verificada hasta el fix de interfaz
> (Paso 26). El README tiene completas las cuatro secciones, incluidos los tres
> episodios de delegación del Paso 24; queda el Paso 27 (pruebas de navegador con
> Playwright).

**Documentos de referencia:** [especificación](specs/reservas-laboratorio/spec.md),
[plan técnico](specs/reservas-laboratorio/plan.md),
[lista de tareas](specs/reservas-laboratorio/tasks.md),
[instrucciones del agente](CLAUDE.md) y
[progreso](docs/agent/progreso.md).

El README se organiza en las cuatro secciones del challenge:
[Especificación breve](#1-especificación-breve),
[Solución](#2-solución),
[Preparación del agente](#3-preparación-del-agente) y
[Registro de decisiones y delegación](#4-registro-de-decisiones-y-delegación).

## 1. Especificación breve

### Problema

Hoy los pedidos se registran en mensajes y una planilla. A veces se confirma la misma
unidad para horarios superpuestos y otras veces una cancelación sigue bloqueando el
horario. La aplicación debe registrar reservas, hacer cumplir las reglas de ocupación y
conservar el historial de las cancelaciones.

La versión normativa, con todos los detalles y ejemplos, está en
[`spec.md`](specs/reservas-laboratorio/spec.md).

### Alcance

**Incluye:**

- leer el inventario precargado de cinco unidades;
- consultar disponibilidad por unidad e intervalo;
- crear una reserva para una unidad;
- cancelar una reserva conservando su identificador y sus datos;
- listar reservas activas y canceladas, con filtros por unidad y estado;
- persistir reservas y estados en SQLite y recuperarlos al reiniciar la aplicación.

**No incluye:** administración del inventario, autenticación o roles, notificaciones,
pagos, integraciones externas, despliegue de producción, concurrencia distribuida,
reservas de varias unidades en una operación ni edición de reservas existentes. Para
cambiar una reserva se cancela y se crea otra.

### Reglas

- Cada ID del inventario identifica una **unidad física distinta**. `MIC-01` y `MIC-02`
  son equipos del mismo tipo, pero unidades independientes.
- Los intervalos son **semiabiertos** `[inicio, fin)`. Dos reservas activas de la misma
  unidad se superponen si y solo si `a.inicio < b.fin` y `b.inicio < a.fin`.
- Se rechazan las superposiciones de reservas activas de la misma unidad.
- Se permiten límites consecutivos, por ejemplo `10:00–11:00` y `11:00–12:00`.
- Se permiten reservas simultáneas de unidades distintas.
- Una reserva cancelada conserva ID, unidad, solicitante, inicio, fin y fecha de
  creación; cambia a `CANCELADA`, registra la fecha de cancelación y libera el
  intervalo.
- Los IDs son secuenciales y no se reutilizan, ni siquiera después de cancelar.
- La consulta de disponibilidad y la creación de reservas aplican la misma función y el
  mismo orden de validaciones; la consulta omite el solicitante.
- La creación verifica la superposición y guarda la reserva dentro de una transacción,
  para impedir confirmar dos reservas superpuestas.
- Una reserva cancelada nunca bloquea una consulta de disponibilidad.
- El listado incluye activas y canceladas, ordenadas por inicio y luego por ID.

### Supuestos y límites

- **Formato:** ISO 8601 local `YYYY-MM-DDTHH:MM`, por ejemplo
  `2026-11-02T10:00`. No se admiten segundos ni offsets (`Z`, `+hh:mm`).
- **Zona horaria:** hora local del laboratorio, sin conversión. El «ahora» es la hora
  local del sistema donde corre la aplicación, truncada al minuto.
- **Fechas pasadas:** se rechazan. El inicio no puede ser anterior a «ahora»; un inicio
  igual a «ahora» es válido.
- **Duración máxima:** 8 horas por reserva. Exactamente 8 horas es válido.
- **Anticipación máxima:** 90 días desde «ahora» hasta el inicio. Exactamente 90 días es
  válido.
- **Duración mínima:** cualquier duración positiva; no se exige una granularidad de
  minutos.
- No se modelan horarios de apertura, feriados ni calendarios especiales.
- Los solicitantes son ficticios. No se registran datos reales, secretos ni
  credenciales.
- La aplicación está pensada para una persona a la vez y una base SQLite local; no se
  modela concurrencia distribuida.
- Se puede cancelar una reserva activa incluso si su intervalo ya comenzó o terminó.

### Requisitos verificables

La tabla completa de requisitos está en
[`spec.md`](specs/reservas-laboratorio/spec.md#17-requisitos-verificables); el detalle
de los criterios de aceptación finales está en
[`spec.md`](specs/reservas-laboratorio/spec.md#20-criterios-de-aceptación-finales). El
estado actual es **72 pruebas automatizadas aprobadas**; el flujo de navegador con las
tres pestañas y la persistencia se verificaron por separado de forma manual.

| ID | Requisito | Evidencia principal |
| --- | --- | --- |
| RF-01 | Se lee el inventario de 5 unidades | `tests/test_inventario.py` |
| RF-02 | Una reserva válida crea una reserva `ACTIVA` con ID | `tests/test_creacion.py` |
| RF-03 | Se rechaza la superposición en la misma unidad | `tests/test_solapamiento.py` |
| RF-04 | Se permiten límites consecutivos | `tests/test_solapamiento.py` |
| RF-05 | Se permiten reservas simultáneas de unidades distintas | `tests/test_solapamiento.py` |
| RF-06 | Se rechazan entradas inválidas | `tests/test_validaciones.py` |
| RF-07 | La cancelación conserva ID y datos y cambia el estado | `tests/test_cancelacion.py` |
| RF-08 | La cancelación libera el intervalo | `tests/test_cancelacion.py` |
| RF-09 | Una cancelada no bloquea la disponibilidad | `tests/test_disponibilidad.py` |
| RF-10 | Disponibilidad y reserva comparten reglas | `tests/test_disponibilidad.py` |
| RF-11 | Activas y canceladas persisten al reabrir | `tests/test_persistencia.py` y `docs/agent/verificacion-persistencia.md` |
| RF-12 | El ID de reserva no se reutiliza | `tests/test_repositorio.py` |
| RF-13 | `init-db` es idempotente y `--reset` borra reservas | `tests/test_cli.py` |
| RF-14 | El dominio no depende de Reflex | `tests/test_frontera_reflex.py` |
| RF-15 | Cada error de dominio tiene su mensaje | `tests/test_ui_presentacion.py` |
| RF-16 | Los handlers del `State` consultan, reservan, cancelan y filtran | `tests/test_ui_estado.py` y `tests/test_ui_estado_disp.py` |
| RF-17 | La app Reflex se importa y registra la página `/` | `tests/test_ui_humo.py` |
| RF-18 | El flujo completo funciona en el navegador | procedimiento manual en `docs/agent/progreso.md` |
| RF-19 | Tres pestañas con mensajes propios por formulario | `tests/test_ui_humo.py`, `tests/test_ui_estado.py` y procedimiento manual |

### Criterios de aceptación

El producto se considera funcionalmente terminado cuando:

- se lee el inventario de cinco unidades y se consulta disponibilidad con las mismas
  reglas que la reserva;
- se crean reservas válidas con ID, unidad, solicitante, inicio y fin;
- se rechazan las superposiciones de reservas activas de la misma unidad;
- se permiten límites consecutivos y reservas simultáneas de unidades distintas;
- se rechazan unidad desconocida, solicitante inválido, fechas inválidas,
  `inicio >= fin`, fechas pasadas, duraciones mayores a 8 horas y anticipaciones
  mayores a 90 días;
- se cancela una reserva activa conservando su ID y sus datos, y el intervalo queda
  libre;
- las reservas activas y canceladas se recuperan tras detener y reiniciar la
  aplicación;
- la interfaz Reflex permite consultar, reservar, cancelar y filtrar;
- `init-db` carga el inventario de forma idempotente y `--reset` advierte que borra
  reservas;
- las pruebas automáticas y el procedimiento manual de navegador quedan registrados;
- el README tiene las cuatro secciones y los tres episodios de delegación enlazan
  evidencia real;
- no hay errores bloqueantes conocidos, secretos ni datos reales en el repositorio.

## 2. Solución

### Estructura

La aplicación separa la interfaz Reflex del núcleo de negocio:

```text
reservas_ui/ (páginas, componentes y State)
      │
      ▼
reservas_ui/presentacion.py (mensajes y filas para la UI)
      │
      ▼
src/reservas/servicio.py (casos de uso)
      │
      ├── dominio.py (validaciones y solapamiento)
      └── repositorio.py (SQLite)
```

El `State` de Reflex solo traduce eventos de la interfaz y recarga la lista; **SQLite es
la fuente de verdad**. Las reglas de negocio viven en `src/reservas/`, que no importa
`reflex`.

```text
.
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── requirements-dev.txt
├── rxconfig.py
├── data/
│   ├── inventario.json            # inventario versionado y de solo lectura
│   └── reservas.db                # generado; ignorado por Git
├── specs/reservas-laboratorio/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── docs/agent/
│   ├── progreso.md
│   ├── preparacion-agente.md
│   ├── delegacion.md
│   └── verificacion-persistencia.md
├── reservas_ui/
│   ├── reservas_ui.py             # app y página /
│   ├── estado.py                  # State y handlers delgados
│   ├── presentacion.py            # funciones puras de presentación
│   └── componentes.py             # pestañas, formularios, tabla y mensajes
├── src/reservas/
│   ├── dominio.py                 # reglas puras
│   ├── servicio.py                # casos de uso
│   ├── repositorio.py             # SQLite
│   ├── inventario.py              # lectura del inventario
│   └── cli.py                     # init-db
└── tests/
    ├── conftest.py
    └── test_*.py
```

También forman parte del repositorio el skill del agente
`.claude/skills/reflex-rules/SKILL.md`, el lock de dependencias del frontend
`reflex.lock/`, los recursos de `assets/` y los flujos de `.github/`.

### Decisiones técnicas

| Decisión | Motivo |
| --- | --- |
| Reflex 0.10.0 con una página `/` | Permite una interfaz web local en Python, sin mantener un frontend separado. |
| Interfaz en tres pestañas con mensajes por formulario | Separa reserva, disponibilidad y reservas, y evita que un mensaje aparezca fuera de su flujo; fue una decisión humana tras revisar el código (Paso 26). |
| SQLite mediante `sqlite3` de la biblioteca estándar, sin `rx.Model` | Ofrece persistencia transaccional sin acoplar el dominio ni las pruebas a Reflex. |
| Núcleo en `src/reservas/` y UI en `reservas_ui/` | Mantiene las reglas independientes de la interfaz; la frontera se prueba automáticamente. |
| `State` delgado y SQLite como fuente de verdad | Los handlers solo traducen eventos y recargan desde la base; no duplican reglas de negocio. |
| Intervalos semiabiertos `[inicio, fin)` | Los límites consecutivos no se consideran superposición y el modelo coincide con la regla de negocio. |
| `BEGIN IMMEDIATE` al crear una reserva | La verificación y la inserción son atómicas, incluso con dos sesiones locales. |
| Inventario en JSON y reservas en SQLite | El inventario es pequeño, versionado y de solo lectura; las reservas necesitan historial y transacciones. |
| Variable `RESERVAS_DB` para la ruta de la base | Las pruebas y las verificaciones usan bases temporales sin tocar los datos locales. |
| `init-db` idempotente y `--reset` con confirmación | La carga inicial es segura; el borrado destructivo exige una acción explícita. |

Los motivos, alternativas y consecuencias se amplían en la sección 4 y en
[`plan.md`](specs/reservas-laboratorio/plan.md).

### Requisitos previos y versiones

| Componente | Versión o requisito |
| --- | --- |
| Sistema operativo | Windows 10/11 es el entorno verificado; los comandos también se indican para macOS/Linux cuando difieren. |
| Python | 3.11 o superior; probado con **3.13.11**. `pyproject.toml` exige `>=3.11`. |
| Reflex | **0.10.0**, fijado en `requirements-dev.txt`. |
| pytest | **8.3.4**, fijado en `requirements-dev.txt`. |
| ruff | **0.8.4**, fijado en `requirements-dev.txt`. |
| Node/bun | Los gestiona Reflex; no se instalan a mano. |
| Base de datos | SQLite incluido en Python; no hace falta un servidor de base de datos. |
| Red | Solo para la instalación inicial de dependencias y del runtime de Reflex; después la app y las pruebas corren localmente. |

La instalación inicial necesita red porque Reflex descarga su runtime de frontend
(Node/bun y paquetes JavaScript). Una vez compilada la aplicación, el uso normal no
depende de servicios externos.

### Instalación

Desde PowerShell, en la raíz del repositorio:

```powershell
git clone https://github.com/eme-19-87/sistema-reservas-agentes.git
cd sistema-reservas-agentes

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .

python -m reservas init-db
```

En macOS/Linux, la creación y activación del entorno son:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Después se ejecutan los mismos comandos de `pip` e `init-db`. Si PowerShell bloquea
`Activate.ps1`, se puede habilitar solo para la sesión actual con
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

`python -m pip install -e .` es necesario para que `python -m reservas` y la app
encuentren el paquete editable de `src/reservas/`.

### Carga, reinicio y borrado de datos

La carga inicial crea el esquema y siembra las cinco unidades desde
`data/inventario.json`. Es **idempotente**: ejecutarla otra vez no duplica unidades ni
modifica las reservas existentes.

```powershell
python -m reservas init-db
reflex run
```

La aplicación abre en `http://localhost:3000/` (el backend de Reflex usa el puerto
8000). La primera ejecución de `reflex run` puede descargar y compilar el frontend.

Para **reiniciar** la aplicación se detiene `reflex run` con `Ctrl+C` y se vuelve a
ejecutar `reflex run`. Las reservas se recuperan desde `data/reservas.db`; no hay que
volver a ejecutar `init-db` si la base ya existe.

Para **borrar el historial** hay que usar `--reset`. La operación elimina todas las
reservas y no se puede deshacer:

```powershell
# ADVERTENCIA: borra todas las reservas.
python -m reservas init-db --reset

# Uso no interactivo, por ejemplo en un script:
python -m reservas init-db --reset --yes
```

Sin `--yes`, el comando pide confirmación. `--reset` vuelve a inicializar el esquema y
vacía la tabla de reservas; las unidades del inventario se conservan. Los IDs no se
reutilizan después del borrado.

Para usar otra ubicación de base de datos, se define `RESERVAS_DB` antes de los
comandos y de `reflex run`:

```powershell
$env:RESERVAS_DB = "C:\datos\reservas-laboratorio.db"
python -m reservas init-db
reflex run
```

### Comandos

```powershell
# Iniciar la aplicación web local
reflex run

# Ejecutar todas las pruebas
python -m pytest

# Ejecutar solo la prueba de persistencia
python -m pytest tests/test_persistencia.py

# Revisar estilo y errores estáticos
ruff check .
```

La suite usa bases temporales y un reloj fijo; no necesita red, servidor Reflex ni
navegador. El flujo completo de navegador es un procedimiento manual hasta que el Paso 27
incorpore Playwright.

### Ejemplo de entrada y salida

Los datos siguientes son ficticios. Para probar, se debe elegir una fecha futura dentro
del límite de 90 días.

**Alta de una reserva**

```text
Unidad:      MIC-01
Solicitante: Ana Pérez (ficticio)
Inicio:      2026-11-02T10:00
Fin:         2026-11-02T11:00
```

Salida en pantalla:

```text
Reserva creada con ID 1.
```

La tabla muestra la fila `1 | MIC-01 | Ana Pérez | 2026-11-02T10:00 |
2026-11-02T11:00 | ACTIVA`.

**Intento de superposición**

```text
Unidad:      MIC-01
Solicitante: Luis Gómez (ficticio)
Inicio:      2026-11-02T10:30
Fin:         2026-11-02T11:30
```

Salida:

```text
Superposición con la reserva activa 1.
```

No se crea una segunda fila. La consulta de disponibilidad para el mismo intervalo
responde `No disponible: se superpone con la reserva activa 1.`, mientras que
`MIC-01` de `11:00` a `12:00` responde `Disponible.`.

**Cancelación**

Al pulsar `Cancelar` en la reserva ID 1, la pantalla muestra `Reserva cancelada.`. La
fila permanece visible como `CANCELADA`, conserva sus datos y el intervalo `10:00–11:00`
queda libre para una nueva reserva.

### Ubicación de los datos

- `data/inventario.json`: inventario versionado y de solo lectura.
- `data/reservas.db`: base SQLite generada; está en `.gitignore` y contiene las
  reservas y sus estados.
- `RESERVAS_DB`: variable de entorno opcional que reemplaza la ruta anterior. Las
  pruebas usan bases temporales.
- Si se elimina `data/reservas.db` sin respaldo, se pierde el historial. Para conservar
  una copia, se puede copiar el archivo con la aplicación detenida.

### Estado de verificación

- Suite automatizada: **72 pruebas aprobadas** con `python -m pytest`.
- Flujo de navegador: verificado con resultados esperados y observados en
  `docs/agent/progreso.md` (Paso 20); las tres pestañas y los mensajes independientes se
  verificaron en el Paso 26.
- Persistencia: reserva activa y cancelada recuperadas después de detener y reiniciar
  `reflex run`; evidencia en `docs/agent/verificacion-persistencia.md` (Paso 21).
- `ruff check .` y `ruff format --check .` **sin hallazgos** desde el fix de interfaz
  (Paso 26); los hallazgos preexistentes de estilo se corrigieron sin cambiar el
  comportamiento y la suite siguió en verde.

### Pendientes y limitaciones

**Pendiente:**

- implementar y ejecutar las pruebas de navegador con Playwright (Paso 27).

**Fuera del alcance o limitaciones conocidas:**

- no hay administración del inventario, autenticación, roles, notificaciones, pagos ni
  integraciones externas;
- no se edita una reserva: se cancela y se crea otra;
- no se reservan varias unidades en una sola operación;
- no se modela concurrencia distribuida; la atomicidad protege las operaciones locales
  sobre SQLite;
- no se aplican horarios de apertura, feriados ni zonas horarias;
- el flujo completo de clics del navegador **no se automatiza todavía**: las pruebas
  cubren dominio, servicio, persistencia, presentación, handlers y humo de la app; el
  flujo de navegador se documenta como procedimiento manual con resultados observados y
  el Paso 27 lo automatizará con Playwright;
- `--reset` borra el historial de forma irreversible;
- la aplicación es local y de un solo usuario; no está pensada para despliegue de
  producción.

## 3. Preparación del agente

La preparación inicial se registró el 2026-10-22 en
[`docs/agent/preparacion-agente.md`](docs/agent/preparacion-agente.md). Ese documento
conserva el entorno de la primera sesión, en la que Python y Reflex aún no estaban
instalados. La actualización al 2026-10-26 está en la
[§10 del mismo documento](docs/agent/preparacion-agente.md#10-actualización-al-2026-10-26)
y en el [`progreso`](docs/agent/progreso.md).

### 3.1 Entorno y modelo

| Elemento | Valor observado |
| --- | --- |
| Arnés | OpenCode, modo código (lectura, edición y shell) |
| Modelo | **Big Pickle**, id `opencode/big-pickle`, proveedor OpenCode |
| Versión del modelo | No visible desde el entorno; la versión interna no se declara |
| Sistema operativo y shell | Windows; PowerShell |
| Repositorio | https://github.com/eme-19-87/sistema-reservas-agentes.git |
| Rama de trabajo | `features_documentacion` |
| Python | 3.13.11 en `.venv` |
| Reflex | 0.10.0 |
| pytest / ruff | 8.3.4 / 0.8.4 |
| Red | Solo instalación inicial; la app, las pruebas y la documentación son locales |

Las versiones se confirmaron con el intérprete del entorno virtual y con
`pip show reflex pytest ruff`. El registro inicial anotó Python no disponible y el
runtime de Reflex sin instalar; esas condiciones se resolvieron en las sesiones
posteriores, cuyos resultados están en [`progreso.md`](docs/agent/progreso.md).

### 3.2 Instrucciones

Las instrucciones operativas son [`CLAUDE.md`](CLAUDE.md), la
[§4 de la preparación](docs/agent/preparacion-agente.md#4-instrucciones-usadas-extracto-saneado-de-claudemd)
y la skill [`reflex-rules`](.claude/skills/reflex-rules/SKILL.md). Las reglas aplicadas
fueron:

- la especificación es la fuente de verdad; no se escribe código sin respaldo en
  `spec.md` y `plan.md`;
- se implementa **una sola tarea pendiente** por indicación, en el orden de `tasks.md`, y
  no se avanza a la siguiente;
- se leen la especificación, el plan, las tareas y el progreso antes de tocar código;
- en las reglas del dominio se escribe primero la prueba y después la implementación;
- se ejecutan `pytest` y `ruff`; no se declara que las pruebas pasan sin haber ejecutado
  el comando en la sesión;
- el dominio, el servicio y el repositorio usan solo la biblioteca estándar y no importan
  `reflex`; la persistencia usa SQLite y no `rx.Model`;
- el `State` es delgado, no contiene reglas de negocio ni es fuente de verdad;
- se usan solicitantes ficticios y no se incluyen secretos, credenciales ni
  transcripciones completas;
- los cambios de `spec.md` o `plan.md` se harían en un commit propio y con aprobación
  humana; en el Paso 23 no se modificaron.

El skill [`reflex-rules`](.claude/skills/reflex-rules/SKILL.md) contiene las reglas de la
interfaz Reflex 0.10. Se usa como documento de reglas del proyecto; el arnés no asume que
se cargue automáticamente como skill, tal como se registró en la
[§5 de la preparación](docs/agent/preparacion-agente.md#5-skill-reflex-rules-y-uso-real).

### 3.3 Contexto suministrado

**Incluido:** [`CLAUDE.md`](CLAUDE.md),
[`spec.md`](specs/reservas-laboratorio/spec.md),
[`plan.md`](specs/reservas-laboratorio/plan.md),
[`tasks.md`](specs/reservas-laboratorio/tasks.md),
[`progreso.md`](docs/agent/progreso.md), la preparación, la plantilla de delegación, el
skill `reflex-rules`, el código y las pruebas existentes, el historial de Git y la salida
real de las comprobaciones.

**Excluido:** variables de entorno y archivos `.env`, credenciales o tokens, datos reales
de estudiantes, conversaciones completas, bases de datos de producción y cualquier acceso
a red no aprobado. El detalle está en la
[§6 de la preparación](docs/agent/preparacion-agente.md#6-contexto-incluido-y-excluido).
El repositorio no contiene secretos ni datos reales.

### 3.4 Permisos y aprobaciones

| Categoría | Regla aplicada |
| --- | --- |
| Permitido sin preguntar | Leer el repositorio; editar `src/`, `reservas_ui/`, `tests/`, `docs/` y el README; marcar casillas en `tasks.md`; ejecutar pruebas, linter y la CLI sobre bases temporales; `git status`, `git diff`, `git add` y `git commit` en la rama de trabajo. |
| Requiere aprobación humana | Instalar o agregar dependencias y ejecutar comandos con red; cambiar `spec.md` o `plan.md`; borrar o reiniciar `data/reservas.db`; `git push`, cambios de rama o reescritura de historial; levantar `reflex run` de forma prolongada. |
| Prohibido | Acceso a red fuera de la instalación aprobada; lectura de secretos; escritura fuera del repositorio. |

El detalle está en [`CLAUDE.md`](CLAUDE.md) y en la
[§7 de la preparación](docs/agent/preparacion-agente.md#7-herramientas-permisos-y-aprobaciones-previstas).
El registro inicial dejó pendientes la instalación de Python y la descarga del runtime de
Reflex; la instalación se completó en sesiones posteriores. En el Paso 23 no se instalaron
dependencias, no se usó red, no se modificaron `spec.md` ni `plan.md`, no se reinició la
base de datos, no se hizo `git push` y no se ejecutaron comandos destructivos.

### 3.5 Adaptaciones con evidencia real

| Adaptación | Aplicación en el proyecto | Evidencia |
| --- | --- | --- |
| Turnos consecutivos | Se probaron los límites `10:00–11:00` + `11:00–12:00` (permitido) y `10:00–11:00` + `10:30–11:30` (rechazado). | [`tests/test_solapamiento.py`](tests/test_solapamiento.py), [`progreso.md`](docs/agent/progreso.md) (Paso 6) y commit `f8eb24c`. |
| Persistencia tras reinicio | Se ejecutó la prueba automática y el procedimiento manual de reservar, cancelar, detener y volver a iniciar `reflex run`. | [`tests/test_persistencia.py`](tests/test_persistencia.py), [`verificacion-persistencia.md`](docs/agent/verificacion-persistencia.md) y commit `ac6894b`. |
| Frontera Reflex | `src/reservas/` no importa `reflex`; la comprobación automática y la búsqueda de imports no encontraron dependencias. | [`tests/test_frontera_reflex.py`](tests/test_frontera_reflex.py), [`plan.md`](specs/reservas-laboratorio/plan.md). |
| Skill `reflex-rules` | Se conserva como documento de reglas de la UI; no se asume carga automática por el arnés. | [`.claude/skills/reflex-rules/SKILL.md`](.claude/skills/reflex-rules/SKILL.md) y [`preparacion-agente.md`](docs/agent/preparacion-agente.md). |
| Revisión humana | Se revisan `git diff`, pruebas, coincidencia con `spec.md` y, en la UI, la comprobación manual del navegador. | [`progreso.md`](docs/agent/progreso.md) (Pasos 20 y 21) y [`CLAUDE.md`](CLAUDE.md). |

No se registran correcciones que no hayan ocurrido. Los tres episodios obligatorios
están registrados en la sección 4.2; esta sección no los sustituye.

### 3.6 Retención del progreso y limitaciones

El progreso se conserva versionado en [`docs/agent/progreso.md`](docs/agent/progreso.md),
con entradas para las tareas cerradas, comandos, versiones, resultados y pasos no
ejecutados. Cada tarea cerrada queda además en un commit y el protocolo de revisión
humana exige revisar el `git diff` y la salida de las pruebas antes de aceptar el
resultado.

Limitaciones conocidas: la versión interna del modelo no es visible; la comprobación de
clics del navegador es manual y no se automatiza; el skill `reflex-rules` no se carga
automáticamente como skill del arnés; y la instalación inicial requiere red para el
runtime de Reflex.

## 4. Registro de decisiones y delegación

### 4.1 Decisiones significativas

#### SQLite para reservas y JSON solo para el inventario

- **Motivo:** las reservas necesitan transacciones, restricciones y consultas; SQLite es
  parte de la biblioteca estándar y evita un servidor. El inventario es pequeño, estático
  y de solo lectura.
- **Alternativas descartadas:** usar JSON plano también para las reservas, descartado
  porque no ofrece transacciones ni restricciones y aumenta el riesgo de perder
  actualizaciones o confirmar solapamientos; usar un motor de base de datos externo,
  innecesario para una aplicación local.
- **Consecuencias:** el esquema y los índices se crean en `repositorio.py`;
  `data/reservas.db` se ignora en Git, se puede respaldar y se reinicia con `--reset`; no
  se cubre concurrencia distribuida.
- **Evidencia:** [`repositorio.py`](src/reservas/repositorio.py),
  [`inventario.py`](src/reservas/inventario.py),
  [`test_repositorio.py`](tests/test_repositorio.py) y
  [`test_persistencia.py`](tests/test_persistencia.py).

#### Reflex sin `rx.Model`

- **Motivo:** mantener dominio, servicio y repositorio en Python estándar, verificables
  sin levantar Reflex y sin acoplar las reglas a las migraciones del framework.
- **Alternativas descartadas:** `rx.Model` o SQLModel, descartados por el acoplamiento de
  la lógica y las pruebas al ORM y a Reflex.
- **Consecuencias:** el esquema se mantiene a mano en `repositorio.py`; el `State` no
  contiene un modelo ORM; no se usa `reflex.db`; la UI y el núcleo se prueban por separado.
- **Evidencia:** [`test_frontera_reflex.py`](tests/test_frontera_reflex.py),
  [`rxconfig.py`](rxconfig.py) y [`estado.py`](reservas_ui/estado.py).

#### Intervalos semiabiertos

- **Motivo:** modelar `[inicio, fin)` permite que dos reservas consecutivas compartan un
  límite sin superponerse y refleja la regla del laboratorio.
- **Alternativas descartadas:** intervalos cerrados `[inicio, fin]`, que rechazarían
  `10:00–11:00` seguido de `11:00–12:00`; comparaciones de cadenas sin parsear, que no
  validarían correctamente fechas y límites.
- **Consecuencias:** la superposición se calcula con
  `a.inicio < b.fin Y b.inicio < a.fin`; los límites consecutivos y las reservas
  simultáneas de unidades distintas son válidos; el cálculo vive en el dominio y no en la
  UI.
- **Evidencia:** [`dominio.py`](src/reservas/dominio.py),
  [`test_solapamiento.py`](tests/test_solapamiento.py) y commit `f8eb24c`.

#### Handlers delgados en el `State`

- **Motivo:** el `State` debe contener estado de pantalla, no reglas de negocio. SQLite es
  la fuente de verdad y `presentacion.py` concentra mensajes y filas para la UI.
- **Alternativas descartadas:** implementar reglas en los handlers o en los componentes
  Reflex, descartado porque duplicaría la lógica, dificultaría las pruebas sin servidor y
  abriría la puerta a mensajes inconsistentes.
- **Consecuencias:** hay una capa adicional (`presentacion.py`); cada operación recarga
  desde SQLite; las pruebas de handlers usan una base temporal y no necesitan navegador.
- **Evidencia:** [`estado.py`](reservas_ui/estado.py),
  [`presentacion.py`](reservas_ui/presentacion.py),
  [`test_ui_estado.py`](tests/test_ui_estado.py) y
  [`test_ui_presentacion.py`](tests/test_ui_presentacion.py).

#### Reflex para la interfaz y CLI solo para mantenimiento

- **Motivo:** el alcance pide una interfaz web local; Reflex permite construirla en Python
  y el CLI `init-db` resuelve la carga y el reinicio de datos.
- **Alternativas descartadas:** una aplicación solo de consola, descartada porque no cubre
  la interfaz solicitada; un frontend JavaScript separado, descartado por el costo de
  mantener dos pilas.
- **Consecuencias:** la primera ejecución requiere red para el runtime de frontend; la
  comprobación de clics es manual; el CLI queda limitado a `init-db`.
- **Evidencia:** [`reservas_ui/`](reservas_ui/), [`rxconfig.py`](rxconfig.py),
  [`test_ui_humo.py`](tests/test_ui_humo.py) y la sección 2 de este README.

#### Pestañas y mensajes por formulario (decisión humana del Paso 26)

- **Motivo:** al revisar el código de la interfaz, la persona responsable observó que
  disponibilidad, reserva y tabla compartían una sola página vertical y un único par de
  mensajes. Eso mezclaba flujos y hacía que el mensaje de una operación apareciera fuera
  de contexto. **La decisión humana fue separar la interfaz en tres pestañas y dar a cada
  formulario sus propios mensajes de éxito y error.**
- **Alternativas descartadas:** mantener las tres zonas con desplazamiento y mensajes
  globales, descartado porque conserva el problema de contexto; usar modales para cada
  formulario, descartado por añadir fricción y complejidad innecesaria.
- **Consecuencias:** la interfaz usa `rx.tabs` controlado por `State.pestana_activa`; hay
  seis vars de mensaje (reserva, disponibilidad y cancelación); la tabla de reservas
  muestra los mensajes de cancelación; desaparece el área global `zona_mensajes`; los
  handlers limpian solo los mensajes de su propio formulario.
- **Evidencia:** [`componentes.py`](reservas_ui/componentes.py),
  [`estado.py`](reservas_ui/estado.py),
  [`test_ui_estado.py`](tests/test_ui_estado.py) y
  [`test_ui_humo.py`](tests/test_ui_humo.py).

### 4.2 Delegación

Los tres episodios obligatorios están registrados con el formato de `plan.md` §12 en
[`docs/agent/delegacion.md`](docs/agent/delegacion.md), cada uno con objetivo,
instrucción, resultado, decisión humana y evidencia verificable:

| Episodio | Alcance | Evidencia principal |
| --- | --- | --- |
| 1 | Regla de solapamiento con intervalos semiabiertos y casos de borde (Paso 6) | [`tests/test_solapamiento.py`](tests/test_solapamiento.py), commits `f8eb24c` y `48d459a` |
| 2 | Persistencia SQLite y verificación tras reinicio (Pasos 7, 9 y 21) | [`tests/test_persistencia.py`](tests/test_persistencia.py), [`verificacion-persistencia.md`](docs/agent/verificacion-persistencia.md), commits `e25bbd6`, `ac6894b` y `5c79089` |
| 3 | Interfaz Reflex con `State` delgado (Pasos 13 a 20) | [`tests/test_ui_presentacion.py`](tests/test_ui_presentacion.py), [`tests/test_ui_estado.py`](tests/test_ui_estado.py), commits `7eee5ad` a `e576d7f` y corrección `05808ed` |

Las reglas para no inventar resultados y los episodios auxiliares (Pasos 1 y 2) están en
el mismo archivo.

## Comenzar con Claude Code

Abre Claude Code desde la raíz del repositorio y utiliza:

```text
Lee CLAUDE.md y todos los documentos del directorio
specs/reservas-laboratorio/.

Analiza la especificación, el plan técnico y la lista de tareas.

Comienza únicamente con la primera tarea pendiente de tasks.md.
No avances a la siguiente tarea hasta que te lo indique.
```

Para continuar posteriormente:

```text
Continúa con la siguiente tarea pendiente de tasks.md.

Consulta spec.md, plan.md y docs/agent/progreso.md cuando sea necesario.
Implementa únicamente esa tarea, valida los cambios, registra el resultado
real en docs/agent/progreso.md y márcala como completada cuando esté
correctamente terminada.

No avances a la siguiente tarea.
```

Algunas tareas requieren aprobación humana explícita antes de ejecutarse (por ejemplo,
la instalación inicial de Reflex, que descarga paquetes; ver
[`CLAUDE.md`](CLAUDE.md)).
