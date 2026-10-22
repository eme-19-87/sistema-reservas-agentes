# Preparación del agente

Registro de cómo se preparó y delimitó el trabajo delegado al agente, según
`specs/reservas-laboratorio/plan.md` §12. Se actualiza si cambian el entorno, el modelo,
las instrucciones o los permisos.

## 1. Entorno de ejecución (observado el 2026-10-22)

| Elemento                | Valor                                                                 |
| ----------------------- | --------------------------------------------------------------------- |
| Arnés                   | OpenCode, modo código (herramientas de lectura, edición y shell)      |
| Modelo                  | **Big Pickle**, id `opencode/big-pickle`, proveedor OpenCode          |
| Versión del modelo      | **No visible** desde el entorno; el catálogo la publica el 2025-10-17 |
| Sistema operativo       | Windows; shell PowerShell 5.1.26100.9711                              |
| Repositorio             | `...\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes`            |
| Rama de trabajo         | `main`                                                                |
| Git                     | 2.46.2.windows.1                                                      |
| Python                  | **No disponible**: `python` resuelve al alias de Microsoft Store y `py` no existe |
| Reflex / pytest / ruff  | No instalados                                                         |
| Red                     | No utilizada en esta sesión                                           |

Consecuencia: las tareas que requieren ejecutar `pytest` y `ruff` (desde el Paso 3) no
pueden validarse hasta instalar Python 3.12 (mínimo 3.11). Esa instalación es una
aprobación pendiente de la persona autora y queda registrada en `docs/agent/progreso.md`.

## 2. Función del agente

- Implementar **una sola tarea pendiente** de `specs/reservas-laboratorio/tasks.md` por
  indicación, en el orden establecido.
- Leer la especificación, el plan y el progreso antes de escribir código.
- Escribir primero la prueba de la regla de negocio y después la implementación, cuando la
  tarea toque reglas del dominio.
- Ejecutar las pruebas y el linter, corregir los errores y registrar el resultado **real**
  (comando, versiones, salida resumida, fallos y pasos no ejecutados).
- Marcar la casilla de la tarea solo cuando esté terminada y verificada.
- No implementar tareas futuras ni funcionalidades fuera de la especificación.

## 3. Motivo de la elección del agente y del modelo

El proyecto es un ejercicio de **Spec-Driven Development**: la especificación es la fuente
de verdad y el agente debe poder leerla, modificarla solo con aprobación, escribir código,
ejecutar pruebas y dejar rastro en Git. OpenCode con el modelo **Big Pickle** se eligió
porque:

- opera directamente sobre el repositorio local (lectura y edición de archivos, Git, shell),
  que es lo que el protocolo SDD exige para cerrar cada tarea con evidencia;
- no requiere cuenta de modelo ni servicios externos en tiempo de ejecución de la
  aplicación, en línea con el requisito de reproducibilidad de `spec.md` §16;
- el trabajo queda revisable por una persona mediante `git diff`, la salida de `pytest` y
  la comprobación manual en el navegador, sin depender del historial de conversación.

La selección concreta del modelo es una decisión de la persona autora; este documento
registra la que estaba activa al iniciar el trabajo.

## 4. Instrucciones usadas (extracto saneado de `CLAUDE.md`)

Se usaron como instrucciones operativas, entre otras, estas reglas:

- «La especificación es la fuente de verdad». No se escribe código sin respaldo en
  `spec.md` y `plan.md`; si falta algo, se propone el cambio y se espera aprobación humana.
- Implementar **únicamente** la primera tarea pendiente de `tasks.md`.
- Prueba primero e implementación después en las reglas del dominio.
- Ejecutar pruebas y linter; no declarar «pruebas pasan» sin haber corrido el comando en la
  sesión, ni afirmar que la interfaz funciona sin haber levantado `reflex run`.
- Dominio, servicio y repositorio usan solo la biblioteca estándar y **no importan
  `reflex`**; persistencia en SQLite con `sqlite3`, sin `rx.Model`.
- El `rx.State` no contiene reglas de negocio ni es fuente de verdad; cada operación
  recarga desde SQLite y el reloj se inyecta.
- Errores de dominio con excepciones propias y mensajes en español; nunca trazas al usuario.
- Solo solicitantes ficticios; sin secretos, tokens, credenciales ni transcripciones en el
  repositorio.
- Cambios de `spec.md` o `plan.md` en commits propios, con el motivo, y con aprobación
  humana previa.
- Permisos: leer y editar `src/`, `reservas_ui/`, `tests/`, `docs/` y marcar casillas en
  `tasks.md`; ejecutar `pytest`, `ruff` y la CLI sobre bases temporales; `git status`,
  `git diff`, `git add` y `git commit`.

## 5. Skill `reflex-rules` y uso real

- **Archivo:** `.claude/skills/reflex-rules/SKILL.md` (el Paso 1 lo encontró con el nombre
  `react-rules`; se renombró porque su contenido siempre fue de Reflex 0.10).
- **Contenido:** reglas de interfaz Reflex 0.10 para este proyecto (versión fijada, sin
  `rx.Model`, frontera de capas, declaración de vars del `State`, handlers delgados,
  `presentacion.py`, formularios `datetime-local`, tabla con «Cancelar» solo en activas,
  accesibilidad mínima y pruebas sin servidor ni navegador).
- **Uso real en esta sesión:** se leyó el archivo completo para extraer las instrucciones de
  esta preparación. No se aplicó a código porque la interfaz comienza en el Paso 12 y aún no
  existe `reservas_ui/`.
- **Adaptación específica:** el arnés OpenCode de esta sesión no expone este archivo como
  skill registrado (sus skills disponibles son `opencode` y `report`), por lo que se usa
  como **documento de reglas del proyecto**: se consulta explícitamente antes de cada tarea
  de interfaz y sus reglas se verifican contra `CLAUDE.md` y `plan.md`.
- **Cuándo se usará:** Pasos 12 a 20 (scaffold, `presentacion.py`, `State`, componentes,
  página, humo y comprobación manual en navegador).

## 6. Contexto incluido y excluido

**Incluido:** `CLAUDE.md`, `specs/reservas-laboratorio/spec.md`, `plan.md`, `tasks.md`,
`docs/agent/progreso.md`, el skill `reflex-rules`, el historial de Git del repositorio y los
archivos de código y pruebas existentes en cada momento.

**Excluido:** variables de entorno y archivos `.env`, credenciales o tokens, datos reales de
estudiantes, conversaciones completas, bases de datos con datos de producción y cualquier
acceso a red no aprobado. En esta sesión no se leyó ningún secreto ni se usó la cuenta del
modelo del autor.

## 7. Herramientas, permisos y aprobaciones previstas

**Permitido sin preguntar:** leer archivos del repositorio; crear y editar archivos de
`src/`, `reservas_ui/`, `tests/` y `docs/`; marcar casillas en `tasks.md`; ejecutar
`pytest`, `ruff` y `python -m reservas ...` sobre bases temporales o de prueba; `git status`,
`git diff`, `git add` y `git commit` en la rama de trabajo.

**Requiere aprobación humana explícita:**

- instalar dependencias o Python, y ejecutar `reflex init` o cualquier comando con red;
- cambiar `spec.md` o `plan.md` (propuesta primero, edición después);
- borrar o reiniciar `data/reservas.db` o ejecutar comandos destructivos;
- `git push`, cambios de rama o reescritura de historial;
- levantar `reflex run` de forma prolongada.

**Prohibido:** acceso a red fuera de la instalación aprobada, lectura de secretos y
escritura fuera del repositorio.

**Aprobaciones pendientes al cerrar esta preparación:**

1. Instalar Python 3.12 (o 3.11+) para poder ejecutar `pytest` y `ruff` desde el Paso 3.
2. Aprobar el acceso a red de `reflex init` antes del Paso 12.
3. Confirmar que el cambio de especificación del solicitante (commit `1d35404`) se
   implementará en el Paso 5 tal como quedó redactado.

## 8. Revisión humana antes de aceptar cada resultado

La persona autora revisa el `git diff` completo, la salida real de `pytest`, que la regla
afectada coincida con `spec.md` y, en los cambios de interfaz, una comprobación manual en el
navegador con resultados esperados y observados. El agente distingue siempre lo que informa
de lo que ejecutó.

## 9. Limitaciones conocidas

- Sin Python en el entorno, la validación automática de las tareas del núcleo está bloqueada.
- La comprobación de clics reales en el navegador es manual y no se automatiza.
- El skill `reflex-rules` no se carga automáticamente como skill del arnés; su cumplimiento
  depende de consultarlo y verificarlo en cada tarea de interfaz.
