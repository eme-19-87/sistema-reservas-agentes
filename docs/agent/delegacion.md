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

## Episodio 1 — Pendiente

- **Objetivo y requisito:** por registrar (candidato: regla de solapamiento y casos de
  borde 10:00–11:00 → 11:00–12:00 / 10:30–11:30; RF-03, RF-04, RF-05).
- **Contexto e instrucción (extracto):** por registrar al ejecutar el Paso 6.
- **Resultado del agente:** por registrar.
- **Decisión humana:** por registrar.
- **Evidencia:** por enlazar (commit y `tests/test_solapamiento.py`).

## Episodio 2 — Pendiente

- **Objetivo y requisito:** por registrar (candidato: persistencia SQLite y verificación tras
  reinicio; RF-11).
- **Contexto e instrucción (extracto):** por registrar al ejecutar los Pasos 7, 9 y 21.
- **Resultado del agente:** por registrar.
- **Decisión humana:** por registrar.
- **Evidencia:** por enlazar (commit, `tests/test_persistencia.py` y
  `docs/agent/verificacion-persistencia.md`).

## Episodio 3 — Pendiente

- **Objetivo y requisito:** por registrar (candidato: interfaz Reflex y `State` que delega en
  el servicio; RF-15, RF-16, RF-17, RF-18).
- **Contexto e instrucción (extracto):** por registrar al ejecutar los Pasos 13 a 20.
- **Resultado del agente:** por registrar.
- **Decisión humana:** por registrar.
- **Evidencia:** por enlazar (commit, `tests/test_ui_*.py` y comprobación manual en
  navegador).

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
