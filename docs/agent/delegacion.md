# Delegación al agente — episodios

Registro de episodios **reales** de delegación, con el formato que exige
`specs/reservas-laboratorio/plan.md` §12. Objetivo: que la persona autora pueda auditar qué
se delegó, con qué instrucción, qué produjo el agente, qué decidió la persona y dónde está
la evidencia.

## Reglas de este registro

- Solo se registran episodios que ocurrieron. **No se inventan fallas ni correcciones.**
- Un episodio se considera completo cuando enlaza a un commit, archivo o prueba verificable.
- Las correcciones se anotan únicamente si existieron, indicando qué se corrigió y por qué.
- No se incluyen transcripciones completas de conversaciones, credenciales ni datos reales.
- El objetivo del producto es reunir **tres episodios** (Paso 24). Los episodios candidatos
  del plan son: (1) regla de solapamiento y casos de borde, (2) persistencia SQLite y
  verificación tras reinicio, (3) interfaz Reflex y `State` que delega en el servicio.

## Formato de cada episodio

```text
### Episodio N — Título

- Objetivo y requisito:
- Contexto e instrucción (extracto):
- Resultado del agente:
- Decisión humana: aceptar / corregir / rechazar — motivo
- Evidencia: commit, archivo o prueba
```

---

## Episodio 1 — Regla de solapamiento con intervalos semiabiertos (Paso 6)

- **Objetivo y requisito:** implementar `hay_solapamiento` con intervalos semiabiertos
  `[inicio, fin)` y que `validar_solicitud_intervalo` use esa misma regla, con pruebas
  primero en `tests/test_solapamiento.py` y los casos de borde obligatorios (adaptación
  «turnos consecutivos»): 10:00–11:00 seguido de 11:00–12:00 **permitido** y de
  10:30–11:30 **rechazado**; contención, intervalo idéntico y unidades distintas
  simultáneas (RF-03, RF-04, RF-05).
- **Contexto e instrucción (extracto):** `tasks.md` Paso 6 — «Pruebas primero
  (`test_solapamiento.py`): 10:30–11:30 rechazado con 10:00–11:00; contención; intervalo
  idéntico; 11:00–12:00 permitido; 09:00–10:00 permitido; unidades distintas simultáneas» y
  «Ejecutar los casos de borde obligatorios y registrarlos». `CLAUDE.md` — «Implementa
  únicamente la primera tarea pendiente», «Escribe primero la prueba de la regla de
  negocio y después la implementación» y la adaptación 1 que obliga a ejecutar esos dos
  casos ante cualquier cambio en la lógica de solapamiento.
- **Resultado del agente:** `hay_solapamiento` ya existía en `src/reservas/dominio.py`
  (creado en el Paso 5) con la fórmula `a.inicio < b.fin AND b.inicio < a.fin`; se
  comprobó que era la función que usaba `validar_solicitud_intervalo` y se integró
  `tests/test_solapamiento.py` con los ocho casos exigidos. En esa sesión **no** se
  ejecutaron `pytest -q` ni `ruff check .` porque Python no estaba disponible, y así lo
  registró `progreso.md`; la suite que incluye esos tests se ejecutó en las sesiones
  posteriores (58 → 63 → 66 pruebas) y se volvió a ejecutar en la sesión del Paso 24.
  Después se aplicó una limpieza de code smells de `dominio.py` (5 commits de refactor
  que extraen validaciones y añaden `ContextoValidacion`), sin cambio de comportamiento.
- **Decisión humana:** **aceptar** — sin rechazo registrado; el contenido quedó integrado
  en la rama mediante el merge `48d459a` (autor `eme-19-87`, 2026-10-25) que incluye
  `f8eb24c` y los refactorings. Corrección aplicada durante la tarea (sí ocurrió): la
  limpieza de code smells de `dominio.py`, motivada por la regla «sin code smells» y
  registrada en `progreso.md` («Limpieza de code smells (dominio)», 2026-10-25); no se
  corrigió ninguna falla funcional porque no se registró ninguna.
- **Evidencia:** commits `f8eb24c`, `454f6cb`, `1d02e63`, `5fcd066`, `d7dc051`,
  `598cd07`, `38bb93d`, merge `48d459a`; archivos `tests/test_solapamiento.py`,
  `src/reservas/dominio.py`; `docs/agent/progreso.md` (Pasos 5 y 6, «Limpieza de code
  smells (dominio)»).

## Episodio 2 — Persistencia SQLite y verificación tras reinicio (Pasos 7, 9 y 21)

- **Objetivo y requisito:** crear el repositorio SQLite con esquema `unidades`/`reservas`,
  restricciones, `PRAGMA foreign_keys = ON`, índice e siembra idempotente; inserción dentro
  de `BEGIN IMMEDIATE`; `tests/test_persistencia.py` (crear activas y una cancelada, cerrar,
  reabrir y comparar) y la verificación manual tras reiniciar `reflex run` (RF-11,
  adaptación 2 «Procedimiento de persistencia» de `CLAUDE.md`).
- **Contexto e instrucción (extracto):** `tasks.md` Pasos 7, 9 y 21 — «Pruebas
  (`test_repositorio.py`): esquema creado, siembra repetida sin duplicados, ID nunca
  reutilizado», «`test_persistencia.py`: crear activas y una cancelada, cerrar conexión,
  reabrir sobre el mismo archivo y comparar contenido» y «reservar y cancelar desde la
  UI, detener `reflex run`, volver a ejecutarlo y comprobar que activas y canceladas siguen
  presentes». `CLAUDE.md` — «Prohibido guardar estado solo en memoria» y «tras cambios en
  repositorio o interfaz, correr `tests/test_persistencia.py`».
- **Resultado del agente:** se crearon `src/reservas/repositorio.py`,
  `src/reservas/servicio.py`, `src/reservas/cli.py` y `src/reservas/__main__.py`, con las
  pruebas `test_repositorio.py`, `test_servicio`/`test_creacion.py`, `test_cancelacion.py`,
  `test_disponibilidad.py`, `test_persistencia.py` y `test_cli.py`. Se ajustó el servicio
  para asegurar el esquema si falta. Resultados registrados en `progreso.md`: 3/3, 7/7, 1/1
  y 3/3 pruebas en los Pasos 7, 8, 9 y 10. La verificación manual (Paso 21) creó la reserva
  activa ID 1 y la cancelada ID 2 desde la UI, detuvo el proceso con `taskkill /T /F`,
  reinició con el mismo `RESERVAS_DB` y observó las dos filas intactas (esperado vs.
  observado en `docs/agent/verificacion-persistencia.md`), con la suite en 66/66. En la
  sesión del Paso 24 se volvió a ejecutar la suite completa: 66 pruebas, código de salida
  0.
- **Decisión humana:** **aceptar** — sin rechazo registrado; los Pasos 7–12 entraron por el
  merge `48d459a` y el Paso 21 por el merge `5c79089` (ambos autor `eme-19-87`,
  2026-10-25/26). No se registraron correcciones de lógica de persistencia en
  `progreso.md`; el único ajuste (asegurar el esquema si falta la base) quedó documentado
  como parte de la implementación del Paso 9.
- **Evidencia:** commits `e25bbd6` (Pasos 7–12), `ac6894b` (Paso 21), merges `48d459a` y
  `5c79089`; archivos `src/reservas/repositorio.py`, `src/reservas/servicio.py`,
  `tests/test_repositorio.py`, `tests/test_persistencia.py`,
  `docs/agent/verificacion-persistencia.md`; `docs/agent/progreso.md` (Pasos 7, 8, 9, 10 y
  21).

## Episodio 3 — Interfaz Reflex con `State` delgado (Pasos 13 a 20)

- **Objetivo y requisito:** capa de presentación con funciones puras, `rx.State` sin
  reglas de negocio y con handlers delgados que delegan en `presentacion.py`, componentes y
  página con formularios, filtros y tabla de reservas, prueba de humo y comprobación manual
  en navegador (RF-15, RF-16, RF-17, RF-18).
- **Contexto e instrucción (extracto):** `tasks.md` Pasos 13 a 20 — «funciones que reciben
  el servicio y devuelven mensajes y filas listos para mostrar», «vars tipadas y
  declaradas (sin parchear vars de clase)», «handler delgado que delega en presentación»,
  «Labels asociados a campos, navegación por teclado, estados de foco básicos», «sin
  lógica de negocio en componentes». `CLAUDE.md` — «Los componentes llaman a handlers del
  `State`; el `State` llama a `presentacion.py`, que llama al servicio», «después de cada
  operación se recarga desde SQLite» y «los errores de dominio se capturan en el handler y
  se muestran como mensaje en pantalla (sin stack traces)».
- **Resultado del agente:** `reservas_ui/presentacion.py`, `reservas_ui/estado.py`,
  `reservas_ui/componentes.py` y `reservas_ui/reservas_ui.py`, con
  `tests/test_ui_presentacion.py`, `tests/test_ui_estado.py`,
  `tests/test_ui_estado_disp.py` y `tests/test_ui_humo.py`. Pruebas registradas en
  `progreso.md`: 5/5 (Paso 15), 8/8 (Paso 16), 12/12 (Paso 17), 63/63 (Paso 18) y 66/66
  (Paso 19); comprobación manual en navegador del Paso 20 con BD temporal en los puertos
  3010/8010. En la sesión del Paso 24 la suite completa volvió a pasar: 66 pruebas, código
  de salida 0.
- **Decisión humana:** **aceptar, con dos correcciones que sí ocurrieron**: (1) limpieza de
  code smells en `presentacion.py` y `estado.py` (Complex Method, Bumpy Road y duplicación)
  registrada en `progreso.md` tras el Paso 15, sin cambio de comportamiento; (2) corrección
  del fallo `EBUSY` al reservar y de los reinicios de backend por escrituras de SQLite en
  las rutas de hot reload — causa raíz documentada (npm 11 lee `-d` como `--loglevel info`,
  y `data/` estaba en los `Reload paths`), arreglo en `reflex.lock/package.json` y
  `rxconfig.py` (`REFLEX_HOT_RELOAD_EXCLUDE_PATHS="data"`), verificado con una reserva
  real desde la interfaz y con `pytest -q` → 66 pruebas; registrado y versionado en
  `05808ed` y `b9b55a6`. Además se documentó (sin cambio de código) la incidencia de
  «dispatch function missing» causada por una pestaña con frontend obsoleto (`306c27c`).
  La integración se hizo mediante los merges `48d459a` (PR #1), `e481b3c` (PR #3),
  `3acc745` (PR #9) y `5c79089` (PR #10), todos de `eme-19-87`. No se registró ningún
  rechazo.
- **Evidencia:** commits `7eee5ad` (Paso 13), `778017f` (14), `c710b27` (15), `3fa362a`
  (16), `a16e551` (17), `4cfc567` (18), `4ea75c3` (19), `e576d7f` (20), `05808ed`,
  `b9b55a6`, `306c27c` y los merges `48d459a`, `e481b3c`, `3acc745`, `5c79089`; archivos
  `reservas_ui/presentacion.py`, `reservas_ui/estado.py`, `reservas_ui/componentes.py`,
  `tests/test_ui_presentacion.py`, `tests/test_ui_estado.py`, `tests/test_ui_estado_disp.py`,
  `tests/test_ui_humo.py`; `docs/agent/progreso.md` (Pasos 13 a 20, incidencia de dispatch
  y «Corrección — EBUSY al reservar»).

---

## Episodios ya ocurridos (fuera de los tres obligatorios)

Se anotan aquí solo si aportan trazabilidad; no sustituyen a los tres episodios del Paso 24.

### Paso 1 — Repositorio y especificación inicial

- **Objetivo y requisito:** dejar Git, `.gitignore` y la versión inicial de la especificación
  versionados (Paso 1 de `tasks.md`).
- **Contexto e instrucción (extracto):** «Inicializar Git y `.gitignore` (`.venv/`,
  `data/*.db`, `.web/`, `.states/`, `assets/external/`, `__pycache__/`)» e «Incorporar
  `CLAUDE.md`, `spec.md`, `plan.md` y `tasks.md`», con la instrucción de implementar solo la
  primera tarea pendiente.
- **Resultado del agente:** encontró el repositorio ya inicializado pero con `plan.md` y
  `tasks.md` como marcadores de una línea; versionó la especificación completa, amplió
  `.gitignore` y verificó las seis reglas con `git check-ignore`. No reescribió historial.
- **Decisión humana:** pendiente de revisión del `git diff` y de los commits `b4e7ebe`,
  `7d014a2` y `9587e2c`.
- **Evidencia:** `docs/agent/progreso.md` (entrada del Paso 1), commits `b4e7ebe`,
  `7d014a2`, `9587e2c`.

### Paso 2 — Preparación del agente y registro

- **Objetivo y requisito:** documentar entorno, modelo, instrucciones, contexto y permisos;
  crear la plantilla de delegación; incorporar el skill `reflex-rules` (Paso 2).
- **Contexto e instrucción (extracto):** «Crear `docs/agent/preparacion-agente.md`:
  entorno, versión y modelo (o «no visible»), función, motivo de la elección, instrucciones
  usadas … contexto incluido y excluido, herramientas y permisos, aprobaciones previstas».
- **Resultado del agente:** creó `preparacion-agente.md` y este archivo; versionó en commits
  separados un cambio de especificación y el renombrado del skill que ya estaban preparados
  en el árbol de trabajo por la persona autora. Detectó que Python no está instalado.
- **Decisión humana:** pendiente de revisión.
- **Evidencia:** `docs/agent/preparacion-agente.md`, commits `1d35404`, `5116390` y el
  commit de cierre del Paso 2.
