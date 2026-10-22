

# Sistema de reservas de laboratorio — SDD

Proyecto base para desarrollar un sistema local de reservas de equipos de laboratorio utilizando **Spec-Driven Development (SDD)** con un agente de programación (Claude Code).

> **Estado:** commit inicial (Paso 1 de [`tasks.md`](http://tasks.md)). Contiene la especificación, el plan técnico, la lista de tareas y las instrucciones del agente. El código y las pruebas se incorporan tarea por tarea. Las secciones marcadas como *pendiente* se completan al avanzar el proyecto.

El README se organiza en las cuatro secciones del challenge: [Especificación breve](#1-especificaci%C3%B3n-breve), [Solución](#2-soluci%C3%B3n), [Preparación del agente](#3-preparaci%C3%B3n-del-agente) y [Registro de decisiones y delegación](#4-registro-de-decisiones-y-delegaci%C3%B3n).

## Estructura

Contenido de este commit:

text

```text
.
├── README.md
├── CLAUDE.md
├── .gitignore
└── specs/
    └── reservas-laboratorio/
        ├── spec.md
        ├── plan.md
        └── tasks.md
        
```

Se incorporarán durante el desarrollo (ver [`plan.md`](http://plan.md) §4): `.claude/skills/reflex-rules/[SKILL.md](http://SKILL.md)` y `docs/agent/` (Paso 2), `src/reservas/`, `data/inventario.json` y `tests/` (Fase 1) y `reservas_ui/` con [`rxconfig.py`](http://rxconfig.py) (Fase 2).

## Documentos

### [`CLAUDE.md`](http://CLAUDE.md)

Contiene las instrucciones permanentes que el agente debe seguir durante el desarrollo: protocolo SDD, reglas de dominio y de arquitectura, permisos y aprobaciones, revisión humana y regla de finalización.

### [`spec.md`](http://spec.md)

Define **qué debe hacer la aplicación**: inventario, reservas, reglas de ocupación de intervalos, validaciones, fechas y límites, disponibilidad, cancelación, persistencia, interfaz, requisitos verificables y criterios de aceptación.

### [`plan.md`](http://plan.md)

Define **cómo se construirá técnicamente**: arquitectura por capas, Python 3.12 con Reflex 0.10.0, SQLite, modelo de datos, interfaz, errores, estrategia de pruebas y trazabilidad con el agente.

### [`tasks.md`](http://tasks.md)

Divide la implementación en una secuencia incremental de 26 tareas con casillas que se marcan solo con pruebas pasando.

## 1. Especificación breve

La coordinación de un laboratorio registra pedidos en mensajes y una planilla: a veces confirma la misma unidad para horarios superpuestos y otras veces una cancelación sigue bloqueando el horario. El sistema permite **consultar disponibilidad, reservar y cancelar** sin perder el historial.

Reglas principales (versión normativa en [`spec.md`](http://spec.md)):

- Cada ID del inventario es una unidad física distinta; una reserva ocupa una sola unidad.
- Intervalos semiabiertos `[inicio, fin)`: se rechaza la superposición de reservas activas de la misma unidad; se permiten límites consecutivos y reservas simultáneas de unidades distintas.
- Una reserva cancelada conserva su identificador y sus datos, y libera el intervalo.
- La disponibilidad y la reserva aplican las mismas validaciones.
- Las reservas persisten y se recuperan al reiniciar.

Ejemplo: con `MIC-01` reservado de 10:00 a 11:00, se rechaza 10:30–11:30 y se permite 11:00–12:00; `MIC-02` puede reservarse de 10:00 a 11:00.

Supuestos, límites de fechas y criterios de aceptación: ver [`spec.md`](http://spec.md) §8 y §20. La versión inicial y sus cambios significativos se recuperan en el historial de Git.

## 2. Solución

*Pendiente (se completa en el Paso 22).* Incluirá: estructura final, decisiones técnicas, requisitos previos y versiones, instalación, carga y reinicio de datos (con advertencia de borrado), comandos de la aplicación y de las pruebas, ejemplo de entrada y salida, ubicación de los datos, pendientes y limitaciones.

Decisiones técnicas previstas en [`plan.md`](http://plan.md): Python 3.12, Reflex 0.10.0 para la interfaz web local, SQLite con `sqlite3`, `pytest` y `ruff`.

## 3. Preparación del agente

*Pendiente (se completa en los Pasos 2 y 23).* Incluirá: entorno y modelo, instrucciones usadas, contexto suministrado, permisos y aprobaciones, adaptaciones específicas y retención del progreso, con enlaces a evidencia de uso real (`docs/agent/`).

## 4. Registro de decisiones y delegación

*Pendiente (se completa en los Pasos 23 y 24).* Incluirá: decisiones significativas con motivos, alternativas y consecuencias, y tres episodios reales de delegación con enlaces a commits, archivos o pruebas.

## Comenzar con Claude Code

Abre Claude Code desde la raíz del repositorio y utiliza:

text

```text
Lee CLAUDE.md y todos los documentos del directorio
specs/reservas-laboratorio/.

Analiza la especificación, el plan técnico y la lista de tareas.

Comienza únicamente con la primera tarea pendiente de tasks.md.
No avances a la siguiente tarea hasta que te lo indique.
```

Para continuar posteriormente:

text

```text
Continúa con la siguiente tarea pendiente de tasks.md.

Consulta spec.md, plan.md y docs/agent/progreso.md cuando sea necesario.
Implementa únicamente esa tarea, valida los cambios, registra el resultado
real en docs/agent/progreso.md y márcala como completada cuando esté
correctamente terminada.

No avances a la siguiente tarea.
```

Algunas tareas requieren aprobación humana explícita antes de ejecutarse (por ejemplo, `reflex init`, que descarga paquetes; ver [`CLAUDE.md`](http://CLAUDE.md)).
