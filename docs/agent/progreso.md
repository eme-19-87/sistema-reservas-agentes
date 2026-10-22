# Progreso del agente — Sistema de reservas de laboratorio

Memoria versionada entre sesiones. Cada entrada registra fecha, tarea, comandos de
verificación, versiones, resultado real (incluidos fallos y pasos no ejecutados) y
decisiones tomadas.

## Entorno

- Fecha de la sesión: 2026-10-22
- Sistema: Windows (PowerShell 5.1.26100.9711), repositorio en `C:\Users\espin\OneDrive\Documentos\LISI\Topicos Avanzados De Ingenieria De Software\SDD\Desarrollo-de-un-sistema-de-reservas-con-agentes`
- Rama de trabajo: `main`; Git 2.46.2.windows.1
- Arnés: OpenCode (modo código). Modelo: **Big Pickle**, id `opencode/big-pickle`, proveedor
  OpenCode. La versión interna del modelo no es visible desde el entorno; el catálogo lo
  publica con fecha 2025-10-17.
- Python del sistema: **no disponible** en esta sesión. El comando `python` resuelve al
  alias de Microsoft Store (`WindowsApps\python.exe`) y `py` no existe. Esto bloquea la
  ejecución de `pytest` y `ruff` a partir del Paso 3; se requiere instalar Python 3.12
  (mínimo 3.11) antes de continuar.
- Reflex: no instalado (Paso 12 requiere aprobación humana de acceso a red).
- pytest / ruff: no instalados.
- Red: no utilizada en esta sesión.

## Paso 1 — Repositorio y especificación inicial

**Estado:** completado.

**Objetivo:** dejar el repositorio versionado con `.gitignore` del proyecto y la versión
inicial completa de la especificación, como base recuperable de su evolución.

**Trabajo realizado:**

- Se comprobó que Git ya estaba inicializado con el commit `8fed87e Initial commit`, que
  contenía `CLAUDE.md`, `spec.md`, `README.md`, `.gitignore` y un skill, pero con
  `plan.md` y `tasks.md` como marcadores de una línea.
- Se incorporó al control de versiones la versión inicial completa de
  `specs/reservas-laboratorio/plan.md` y `specs/reservas-laboratorio/tasks.md`
  (estaban solo en el árbol de trabajo) y la normalización de enlaces de `CLAUDE.md`.
- Se añadieron a `.gitignore` las entradas del proyecto: `.venv/`, `__pycache__/`,
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

**Resultado:** las seis reglas requeridas por la tarea están activas y verificadas con
`git check-ignore`. `git status --short` queda limpio tras los commits de la tarea.

**Pasos no ejecutados:** `pytest -q` y `ruff check .`. No aplican al Paso 1 (no hay código
ni pruebas todavía) y además Python no está disponible en el entorno (ver «Entorno»).

**Decisiones:**

- No se reescribió el historial (`git commit --amend` o rebase) para «arreglar» el commit
  inicial, porque la reescritura de historial requiere aprobación humana. El estado
  inicial completo de la especificación se registró en commits posteriores, de modo que
  el commit inicial sigue siendo recuperable.
- El `.gitignore` existente era una plantilla genérica de Node; se conservó y se amplió
  en lugar de reemplazarlo.
- Los cambios de documentación/especificación se separaron en commits propios de los
  cambios de configuración, según el protocolo SDD.
- Se creó este archivo con la entrada del Paso 1 porque el protocolo exige registrar el
  progreso antes de marcar una tarea; el resto del contenido del Paso 2
  (`preparacion-agente.md`, `delegacion.md`, skill) queda pendiente para su propia tarea.

## Paso 2 — Preparación del agente y registro

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
  (objetivo → contexto → resultado → decisión humana → evidencia). Los tres episodios
  obligatorios quedan marcados como **pendientes**; no se inventó ningún resultado. Se
  añadieron, como trazabilidad, los episodios reales de los Pasos 1 y 2.
- Skill: el archivo existía como `.claude/skills/react-rules/SKILL.md`, pero su contenido
  siempre fue de Reflex 0.10 y `plan.md`/`tasks.md` lo referencian como `reflex-rules`. Se
  registró el renombrado en un commit propio. Se leyó completo y su uso real quedó
  documentado: se usa como documento de reglas del proyecto (el arnés OpenCode de esta
  sesión no lo expone como skill registrado) y regirá los Pasos 12–20.
- Cambios preexistentes en el árbol de trabajo: al iniciar el Paso 2, `git status` mostró
  cambios preparados que no había producido esta sesión: una precisión de la validación del
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

Además se comprobó que solo los Pasos 1 y 2 están marcados con `[x]` y que el skill
referenciado por `plan.md` y `tasks.md` (`.claude/skills/reflex-rules/SKILL.md`) existe y
comienza con el título `# Skill: reflex-rules`.

**Resultado:** existen los tres documentos de `docs/agent/`, el skill está en la ruta que
citan `plan.md` y `tasks.md`, y no quedan cambios preexistentes sin versionar. El cambio de
especificación del solicitante no se implementó (corresponde al Paso 5).

**Pasos no ejecutados:** `pytest -q` y `ruff check .`. No aplican al Paso 2 (no hay código ni
pruebas) y Python no está disponible en el entorno. Tampoco se ejecutó `reflex init` ni
ningún comando de red.

**Decisiones:**

- Se respetó el cambio de especificación encontrado en el árbol de trabajo en lugar de
  descartarlo; se aisló en su propio commit con el motivo, como exige el protocolo SDD, y se
  dejó constancia de que no lo redactó esta sesión.
- El motivo de la elección del agente/modelo se documenta a partir de las restricciones del
  proyecto (SDD, ejecución local, sin cuenta de modelo en ejecución); la elección concreta
  del modelo queda atribuida a la persona autora.
- No se inventaron episodios de delegación: los tres obligatorios quedan pendientes hasta
  que ocurran (Paso 24).
- Persisten tres aprobaciones pendientes: instalar Python (bloquea el Paso 3), aprobar la red
  de `reflex init` (Paso 12) y confirmar la implementación de la nueva validación del
  solicitante (Paso 5).
