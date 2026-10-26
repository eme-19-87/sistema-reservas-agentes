# Verificación de persistencia tras reinicio

**Fecha:** 2026-10-26.

**Estado:** completado.

**Requisito:** RF-11 y `spec.md` §13: las reservas activas y canceladas se conservan en
SQLite y se recuperan al reiniciar la aplicación, con sus datos y estados.

## Entorno

- Windows, Python 3.13.11, Reflex 0.10.0, pytest 8.3.4, ruff 0.8.4.
- Navegador: Microsoft Edge 156.0.4314.42 en modo headless, controlado por CDP.
- Base temporal: `C:\Users\espin\AppData\Local\Temp\opencode\reservas-paso21.db`.
- Aplicación en `http://localhost:3010/`; backend en `http://localhost:8010/`.

## Procedimiento

1. Se creó una base SQLite temporal vacía y se inició la app con `RESERVAS_DB`
   apuntando a ella:

   ```powershell
   $env:RESERVAS_DB = 'C:\Users\espin\AppData\Local\Temp\opencode\reservas-paso21.db'
   .\.venv\Scripts\python.exe -m reflex run --frontend-port 3010 --backend-port 8010
   ```

2. Desde la UI se creó la reserva activa:
   - unidad `MIC-01`;
   - solicitante `Activa Persistente`;
   - inicio `2026-10-28T10:00`;
   - fin `2026-10-28T11:00`.

3. Desde la UI se creó la reserva que se cancelaría:
   - unidad `MIC-02`;
   - solicitante `Cancelada Persistente`;
   - inicio `2026-10-28T12:00`;
   - fin `2026-10-28T13:00`.

4. Se pulsó `Cancelar` sobre la segunda reserva. La interfaz mostró
   `Reserva cancelada.` y la fila pasó a `CANCELADA`.

5. Se detuvo el proceso de `reflex run` y se comprobó que no quedara un listener en
   `3010/8010`. Se volvió a iniciar la app con el mismo `RESERVAS_DB`.

6. Se abrió una página nueva después del reinicio y se compararon los datos de la tabla
   y el contenido directo de SQLite.

## Resultados esperados y observados

| Comprobación | Esperado | Observado |
| --- | --- | --- |
| Alta de la reserva activa | Éxito con ID asignado | `Reserva creada con ID 1.`; `MIC-01`/`Activa Persistente`/`ACTIVA` |
| Alta de la reserva cancelable | Éxito con ID asignado | `Reserva creada con ID 2.`; `MIC-02`/`Cancelada Persistente`/`ACTIVA` antes de cancelar |
| Cancelación desde la UI | La fila conserva ID y datos, y pasa a `CANCELADA` | `Reserva cancelada.`; ID 2 pasó a `CANCELADA` y desapareció su botón `Cancelar` |
| Reinicio de la app | La app vuelve a cargar sin borrar datos | La app respondió `200` en `3010` después del reinicio |
| Contenido después del reinicio | Las dos reservas siguen presentes, con el mismo ID, datos y estado | Las dos filas reaparecieron con los valores de la tabla siguiente |
| Consulta directa a SQLite | Los dos registros coinciden con la UI | Las dos filas coincidieron con la UI |

**Estado observado después del reinicio:**

| ID | Unidad | Solicitante | Inicio | Fin | Estado |
| --- | --- | --- | --- | --- | --- |
| 1 | MIC-01 | Activa Persistente | 2026-10-28T10:00 | 2026-10-28T11:00 | ACTIVA |
| 2 | MIC-02 | Cancelada Persistente | 2026-10-28T12:00 | 2026-10-28T13:00 | CANCELADA |

La reserva activa conservó su botón `Cancelar`; la cancelada conservó su estado y sus
datos, sin volver a `ACTIVA`.

## Evidencia

- Captura antes del reinicio:
  `C:\Users\espin\AppData\Local\Temp\opencode\paso21-antes.png`.
- Captura después del reinicio:
  `C:\Users\espin\AppData\Local\Temp\opencode\paso21-despues.png`.
- Base temporal:
  `C:\Users\espin\AppData\Local\Temp\opencode\reservas-paso21.db`.
- Logs del primer y segundo arranque:
  `reflex-paso21-1.out.log`, `reflex-paso21-1.err.log`,
  `reflex-paso21-2.out.log` y `reflex-paso21-2.err.log` en el directorio temporal.
- Los logs no mostraron `Traceback`, `ERROR`, `EBUSY` ni excepciones.

## Pruebas automatizadas

```text
$ .\.venv\Scripts\python.exe -m pytest
66 passed in 17.29s
```

La suite incluye `tests/test_persistencia.py`, que verifica la reapertura de una base
temporal con una reserva activa y otra cancelada.

## Resultado

La persistencia tras reinicio quedó verificada: una reserva activa y una cancelada,
creadas y canceladas desde la UI, sobrevivieron a la detención y al nuevo arranque de
`reflex run`, con sus datos y estados intactos.

## Limitaciones

- La interacción se ejecutó con un navegador real, pero los clics y la escritura se
  automatizaron mediante CDP; no hubo una sesión manual humana.
- La detención se hizo terminando el árbol de procesos con `taskkill /T /F`, no con una
  interrupción manual `Ctrl+C`; las transacciones ya estaban confirmadas en SQLite.
- No se reinició el sistema operativo ni se probaron dos sesiones concurrentes.
- La base usada es temporal y no forma parte del repositorio.
