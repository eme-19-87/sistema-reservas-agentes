

# Especificación del producto — Sistema de reservas de laboratorio

## 1. Visión del producto

Construir una aplicación local pequeña y verificable para que la coordinación de un laboratorio consulte disponibilidad, reserve y cancele equipos sin perder el historial.

Hoy los pedidos se registran en mensajes y una planilla: a veces se confirma la misma unidad para horarios superpuestos y otras veces una cancelación sigue bloqueando el horario. La aplicación reemplaza ese registro por una única fuente de verdad que aplica siempre las mismas reglas.

La interfaz es una aplicación web local construida con Reflex. Los datos persisten en SQLite y se recuperan al reiniciar.

---

## 2. Alcance

### Dentro del alcance

- Leer el inventario precargado.
- Consultar disponibilidad por unidad e intervalo.
- Crear una reserva identificable (una unidad por reserva).
- Cancelar una reserva conservando su identificador y sus datos, y liberando el intervalo.
- Listar reservas activas y canceladas.
- Persistir reservas y estados para recuperarlos al reiniciar la aplicación.

### Fuera de alcance

- Administración del inventario (alta, baja o modificación de unidades).
- Autenticación y roles reales.
- Notificaciones, pagos e integraciones externas.
- Despliegue obligatorio, interfaz gráfica compleja y escalabilidad de producción.
- Concurrencia distribuida.
- Reservas de varias unidades en una sola operación.
- Edición de una reserva existente (se cancela y se vuelve a crear).

---

## 3. Actor

### Persona coordinadora

Es el único actor. No hay inicio de sesión ni roles. Puede:

- ver el inventario;
- consultar disponibilidad de una unidad en un intervalo;
- crear reservas a nombre de un solicitante ficticio;
- cancelar reservas activas;
- listar y filtrar reservas.

---

## 4. Inventario

El inventario está precargado en `data/inventario.json` y es de solo lectura. Cada ID identifica una **unidad física distinta**.


| ID de unidad | Equipo                 |
| ------------ | ---------------------- |
| `MIC-01`     | Microscopio digital    |
| `MIC-02`     | Microscopio digital    |
| `OSC-01`     | Osciloscopio           |
| `MUL-01`     | Multímetro             |
| `FUE-01`     | Fuente de alimentación |


`MIC-01` y `MIC-02` son equipos del mismo tipo pero unidades independientes: la ocupación de una no afecta a la otra.

---

## 5. Información de una reserva

Cada reserva contiene:

- identificador;
- unidad;
- solicitante;
- inicio;
- fin;
- estado;
- fecha y hora de creación;
- fecha y hora de cancelación (solo si está cancelada).

### Identificador

Entero secuencial que comienza en 1. **No se reutiliza nunca**, ni siquiera después de una cancelación.

### Estado

Valores:

- `ACTIVA`
- `CANCELADA`

Una reserva nace `ACTIVA`. Solo puede pasar de `ACTIVA` a `CANCELADA`; no existe la transición inversa.

### Solicitante

Texto de un solicitante **ficticio**. Se almacena sin espacios al inicio ni al final. No se registran datos reales de estudiantes.

---

## 6. Reglas de ocupación e intervalos

### Intervalos semiabiertos

Cada reserva ocupa el intervalo `[inicio, fin)`: incluye el inicio y excluye el fin.

Dos reservas **activas de la misma unidad** se superponen si y solo si:

text

```text
a.inicio < b.fin  Y  b.inicio < a.fin
```

### Reglas

- Una reserva `ACTIVA` ocupa su intervalo.
- Una reserva `CANCELADA` no bloquea disponibilidad.
- Se rechazan las superposiciones entre reservas activas de la misma unidad.
- Se permiten límites consecutivos (el fin de una coincide con el inicio de otra).
- Se permiten reservas simultáneas de unidades distintas.

### Ejemplo

Con `MIC-01` reservado de 10:00 a 11:00:


| Solicitud            | Resultado | Motivo                       |
| -------------------- | --------- | ---------------------------- |
| `MIC-01` 10:30–11:30 | Rechazada | Se superpone con 10:30–11:00 |
| `MIC-01` 10:00–11:00 | Rechazada | Intervalo idéntico           |
| `MIC-01` 10:15–10:45 | Rechazada | Contenida en la reserva      |
| `MIC-01` 09:30–10:30 | Rechazada | Se superpone con 10:00–10:30 |
| `MIC-01` 11:00–12:00 | Permitida | Límite consecutivo           |
| `MIC-01` 09:00–10:00 | Permitida | Límite consecutivo           |
| `MIC-02` 10:00–11:00 | Permitida | Unidad distinta              |


---

## 7. Validaciones

La creación de una reserva y la consulta de disponibilidad aplican **las mismas validaciones, en el mismo orden**, mediante la misma función de dominio. La primera que falla determina el error.

1. **Unidad conocida:** el ID existe en el inventario.
2. **Solicitante:** no vacío, no compuesto sólo por números, sin caracteres especiales, sí se permiten acentos y diéresis, no compuesto solo por espacios. *(Se omite en la consulta de disponibilidad, que no recibe solicitante.)*
3. **Fechas y horas válidas:** formato `YYYY-MM-DDTHH:MM`, fecha de calendario existente, sin zona horaria.
4. **Orden:** `inicio` estrictamente anterior a `fin`.
5. **Límites de tiempo:** fecha pasada, duración máxima y anticipación máxima (ver sección 8).
6. **Sin superposición** con reservas activas de la misma unidad.

### Errores de dominio


| Condición                                                                           | Error                 |
| ----------------------------------------------------------------------------------- | --------------------- |
| Unidad inexistente                                                                  | `UnidadDesconocida`   |
| Solicitante vacío, o solo espacios, o con caracteres especiales, o sólo con números | `SolicitanteInvalido` |
| Fecha con formato o calendario inválido, o con offset                               | `FechaInvalida`       |
| `inicio >= fin`                                                                     | `IntervaloInvalido`   |
| Inicio en el pasado, duración o anticipación excedidas                              | `LimiteExcedido`      |
| Superposición con una reserva activa                                                | `Superposicion`       |
| Reserva inexistente al cancelar                                                     | `ReservaNoEncontrada` |
| Reserva ya cancelada al cancelar                                                    | `ReservaYaCancelada`  |


Cada error tiene un mensaje claro en español. El mensaje de `Superposicion` identifica la reserva activa en conflicto (su ID).

---

## 8. Fechas, zona horaria y límites

Supuestos adoptados para resolver lo no especificado:

- **Formato:** ISO 8601 local, `YYYY-MM-DDTHH:MM` (por ejemplo `2026-11-02T10:00`). No se admiten segundos.
- **Zona horaria:** hora local del laboratorio, sin conversión. Las entradas con offset (`Z`, `+hh:mm`) se rechazan como `FechaInvalida`.
- **«Ahora»:** hora local del sistema donde corre la aplicación, truncada al minuto. En las pruebas el reloj es fijo.
- **Fechas pasadas:** se rechazan. El inicio no puede ser anterior a «ahora». Un inicio igual a «ahora» es válido.
- **Duración máxima:** 8 horas por reserva (`fin - inicio <= 8 h`). Exactamente 8 horas es válido.
- **Anticipación máxima:** 90 días (`inicio <= ahora + 90 días`). Exactamente 90 días es válido.
- **Duración mínima:** cualquier duración positiva (cubierta por `inicio < fin`). No se exige una granularidad de minutos.
- **Cancelación:** se puede cancelar cualquier reserva `ACTIVA`, incluso cuando su intervalo ya comenzó o terminó.

---

## 9. Consulta de disponibilidad

La persona indica:

- unidad;
- inicio;
- fin.

Aplica las validaciones de la sección 7 (excepto solicitante) y las reglas de la sección 6.

Resultado:

- **Disponible:** el intervalo es válido y no se superpone con reservas activas de la unidad.
- **No disponible:** el intervalo es válido pero se superpone; el mensaje indica las reservas activas en conflicto (ID, solicitante e intervalo).
- **Error de validación:** el mensaje del error correspondiente.

Garantías:

- Si la consulta responde «Disponible», crear la reserva equivalente es aceptado (salvo que otra operación cambie los datos entre ambas).
- La consulta **no crea ni modifica** reservas.
- Una reserva cancelada nunca hace que una consulta responda «No disponible».

---

## 10. Creación de reservas

La persona indica:

- unidad;
- solicitante;
- inicio;
- fin.

Comportamiento:

- Se aplican las validaciones de la sección 7.
- La verificación de superposición y la inserción se realizan de forma **atómica** (una transacción), para impedir confirmar dos reservas superpuestas.
- Si es válida, se crea una reserva `ACTIVA` con ID nuevo y se informa el ID asignado.
- Si no es válida, no se crea nada y se informa el error.

---

## 11. Cancelación de reservas

La persona indica el ID de una reserva.

- Solo puede cancelarse una reserva `ACTIVA`.
- La reserva **no se borra**: cambia a `CANCELADA` y registra la fecha y hora de cancelación.
- Se conservan ID, unidad, solicitante, inicio, fin y fecha de creación.
- El intervalo queda libre: una nueva reserva en ese horario y unidad es aceptada.
- Cancelar una reserva ya cancelada produce `ReservaYaCancelada`.
- Cancelar un ID inexistente produce `ReservaNoEncontrada`.

---

## 12. Listado de reservas

Se listan todas las reservas, activas y canceladas, ordenadas por inicio ascendente y luego por ID.

Filtros combinables:

- por unidad;
- por estado (`ACTIVA` / `CANCELADA`).

Cada fila muestra: ID, unidad, solicitante, inicio, fin y estado.

---

## 13. Persistencia

- Las reservas y sus estados se guardan en SQLite, en `data/reservas.db` (archivo ignorado por Git).
- Al reiniciar la aplicación se recuperan **todas** las reservas, activas y canceladas, con sus datos.
- No se usa estado solo en memoria. El estado de la interfaz (`rx.State`) no es fuente de verdad: se recarga desde la base.
- La ruta de la base puede elegirse con la variable de entorno `RESERVAS_DB`. Las pruebas usan una base temporal.

---

## 14. Interfaz web (Reflex)

Una página principal (`/`) con tres pestañas: «Reservar», «Disponibilidad» y «Reservas». La pestaña activa por defecto es «Reservar».

La separación en pestañas y los mensajes independientes por formulario son una **decisión humana** tomada después de revisar el código de la interfaz en el Paso 26: las tres zonas compartían una sola página vertical y un único par de mensajes, lo que mezclaba flujos y hacía que un mensaje apareciera fuera de contexto.

### Pestaña «Reservar»

- Selector de unidad, solicitante, inicio y fin.
- Botón «Reservar».
- Elementos propios para el mensaje de éxito y el de error de este formulario.
- Éxito: muestra el ID asignado, actualiza la tabla y limpia solicitante, inicio y fin (conserva la unidad).
- Error: muestra el mensaje y conserva los valores ingresados.

### Pestaña «Disponibilidad»

- Selector de unidad, campo de inicio y campo de fin.
- Botón «Consultar».
- Elementos propios para el mensaje de éxito y el de error de este formulario.
- Muestra «Disponible» o «No disponible» con detalle de conflictos; los errores de validación usan su propio mensaje.

### Pestaña «Reservas»

- Tabla con ID, unidad, solicitante, inicio, fin y estado.
- Filtros por unidad y estado.
- Botón «Cancelar» únicamente en reservas activas; las canceladas permanecen visibles.
- Elementos propios para el mensaje de éxito y el de error de la cancelación.

### Comportamiento general

- Al cargar la página se leen unidades y reservas desde la base.
- Cada operación que modifica datos recarga la lista desde la base.
- Cada formulario conserva y muestra únicamente sus propios mensajes; una operación de un formulario no borra los mensajes de otro.
- Los errores se muestran como mensajes en pantalla; nunca como trazas técnicas. Un error inesperado se registra en el log y se muestra un mensaje genérico.
- Los campos de fecha usan el control `datetime-local` del navegador, que entrega el formato definido en la sección 8; el servicio valida igualmente el valor recibido.
- Accesibilidad mínima: pestañas navegables por teclado, etiquetas asociadas a cada campo, navegación por teclado y estados de foco visibles.
- Las reglas de negocio no se implementan en la interfaz: se delegan en el servicio.

---

## 15. Mantenimiento de datos

Comando: `python -m reservas init-db [--reset] [--yes]`.

- Crea el esquema y carga las unidades desde `data/inventario.json`.
- Es **idempotente**: ejecutarlo de nuevo no duplica unidades ni modifica reservas.
- `--reset` **borra todas las reservas** y recrea el esquema; solicita confirmación, salvo que se indique `--yes`.
- Código de salida `0` en caso de éxito y `1` en caso de error.

---

## 16. Requisitos no funcionales

- **Reproducibilidad:** la aplicación y las pruebas se ejecutan sin la cuenta de modelo del autor. La única necesidad de red es la instalación inicial de dependencias y del runtime de Reflex.
- **Ejecución local:** sin servicios externos en ejecución.
- **Datos ficticios:** solo solicitantes ficticios en ejemplos, pruebas y datos. Sin secretos ni credenciales en el repositorio.
- **Separación de capas:** el dominio, el servicio y el repositorio no importan `reflex`.
- **Pruebas:** las pruebas de dominio, servicio, persistencia, presentación y handlers del `State` corren sin servidor Reflex, sin navegador y sin red.

---

## 17. Requisitos verificables


| ID    | Requisito                                                                      | Verificación                                                            |
| ----- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| RF-01 | Se lee el inventario de 5 unidades                                             | `test_[inventario.py](http://inventario.py)`                            |
| RF-02 | Reserva válida crea una reserva `ACTIVA` con ID                                | `test_[creacion.py](http://creacion.py)`                                |
| RF-03 | Se rechaza la superposición en la misma unidad                                 | `test_[solapamiento.py](http://solapamiento.py)`                        |
| RF-04 | Se permiten límites consecutivos                                               | `test_[solapamiento.py](http://solapamiento.py)`                        |
| RF-05 | Se permiten reservas simultáneas de unidades distintas                         | `test_[solapamiento.py](http://solapamiento.py)`                        |
| RF-06 | Se rechazan entradas inválidas (unidad, solicitante, fechas, orden, límites)   | `test_[validaciones.py](http://validaciones.py)`                        |
| RF-07 | La cancelación conserva ID y datos y cambia el estado                          | `test_[cancelacion.py](http://cancelacion.py)`                          |
| RF-08 | La cancelación libera el intervalo                                             | `test_[cancelacion.py](http://cancelacion.py)`                          |
| RF-09 | Una reserva cancelada no bloquea la disponibilidad                             | `test_[disponibilidad.py](http://disponibilidad.py)`                    |
| RF-10 | Disponibilidad y reserva comparten reglas                                      | `test_[disponibilidad.py](http://disponibilidad.py)`                    |
| RF-11 | Activas y canceladas persisten tras cerrar y reabrir                           | `test_[persistencia.py](http://persistencia.py)` y `e2e/test_requisitos.py` |
| RF-12 | El ID de reserva no se reutiliza                                               | `test_[repositorio.py](http://repositorio.py)`                          |
| RF-13 | `init-db` es idempotente y `--reset` borra reservas                            | `test_[cli.py](http://cli.py)` y `e2e/test_requisitos.py`               |
| RF-14 | El dominio no depende de Reflex                                                | `test_frontera_[reflex.py](http://reflex.py)` y `e2e/test_requisitos.py` |
| RF-15 | La capa de presentación mapea cada error de dominio a su mensaje               | `test_ui_[presentacion.py](http://presentacion.py)`                     |
| RF-16 | Los handlers del `State` consultan, reservan, cancelan y filtran correctamente | `test_ui_[estado.py](http://estado.py)`                                 |
| RF-17 | La app Reflex se importa y registra la página `/`                              | `test_ui_[humo.py](http://humo.py)`                                     |
| RF-18 | El flujo completo funciona en el navegador                                     | `e2e/test_requisitos.py`                                                |
| RF-19 | Reserva, disponibilidad y reservas están en tres pestañas, con mensajes propios por formulario | `e2e/test_requisitos.py`, `test_ui_[humo.py](http://humo.py)` y `test_ui_[estado.py](http://estado.py)` |

La suite `e2e/test_requisitos.py` contiene 19 pruebas Playwright, una por RF: usa un
servidor Reflex aislado, una base temporal y Chromium headless. RF-13 y RF-14 se validan
también con la CLI y un análisis estático, respectivamente.


---

## 18. Supuestos

- Una reserva ocupa una única unidad.
- La hora es local del laboratorio y no se convierte entre zonas.
- No se aplican horarios de apertura del laboratorio ni feriados.
- Los límites de 8 horas y 90 días son decisiones razonables del autor, documentadas en el README.
- Los nombres de solicitantes son ficticios y no se validan contra ningún directorio.
- La aplicación la usa una persona a la vez; no se modela concurrencia distribuida (sí se protege la confirmación atómica de reservas en un mismo equipo).

---

## 19. Registro de evolución de la especificación

La versión inicial y cada cambio significativo se registran en Git, con el motivo en el mensaje del commit. Los cambios en [`spec.md`](http://spec.md) y [`plan.md`](http://plan.md) se hacen en commits propios y requieren aprobación humana antes de implementarlos.

---

## 20. Criterios de aceptación finales

El producto está funcionalmente terminado cuando:

- se puede leer el inventario precargado de 5 unidades;
- se puede consultar la disponibilidad por unidad e intervalo con las mismas reglas que la reserva;
- se pueden crear reservas válidas con ID, unidad, solicitante, inicio y fin;
- se rechazan las superposiciones de reservas activas de la misma unidad;
- se permiten límites consecutivos y reservas simultáneas de unidades distintas;
- se rechazan unidad desconocida, solicitante vacío o solo espacios, fechas inválidas, `inicio >= fin`, fechas pasadas, duraciones mayores a 8 horas y anticipaciones mayores a 90 días;
- se puede cancelar una reserva activa conservando su ID y sus datos;
- una reserva cancelada libera el intervalo y no bloquea la disponibilidad;
- las reservas activas y canceladas se recuperan tras detener y reiniciar la aplicación sin borrar datos;
- la interfaz Reflex permite consultar, reservar, cancelar y listar con filtros;
- la interfaz separa reserva, disponibilidad y reservas en tres pestañas, y cada formulario muestra sus propios mensajes de éxito y error;
- `init-db` carga el inventario de forma idempotente y `--reset` advierte que borra reservas;
- las pruebas automáticas (dominio, servicio, persistencia, presentación, handlers del `State` y humo de la app) pasan con comandos y resultados registrados;
- existe un procedimiento manual de navegador con resultados esperados y observados;
- el README tiene las cuatro secciones del challenge y los tres episodios de delegación enlazan a evidencia real;
- no existen errores bloqueantes conocidos ni secretos o datos reales en el repositorio.
