# Decisiones técnicas · P1 Bitácora sísmica CEET

Este documento justifica las decisiones de arquitectura, calibración de hardware e implementación elegidas durante el desarrollo del proyecto **Bitácora Sísmica CEET**.

---

## 1. Umbral de detección de impacto (`umbral` en `VigiaImpactos`)

- **Valor inicial sugerido por la guía:** `15.0` m/s²
- **Valor que terminamos usando:** `15.0` m/s²
- **¿Cómo se probó?:** 
  - Se dejó el dispositivo móvil inmóvil sobre la superficie de la mesa durante un período de 5 minutos mientras se registraban los picos de magnitud informados por el acelerómetro sin gravedad (`userAccelerometerEventStream`).
  - Durante el reposo estático, el sensor reportó un ruido de fondo acumulado de magnitud máxima entre `0.12` y `0.85` m/s².
  - Al realizar traslados y desplazamientos normales de los equipos entre laboratorios, se observaron oscilaciones entre `2.5` y `6.8` m/s².
  - Al simular impactos reales por golpes o caídas leves del equipo durante el transporte, los picos del acelerómetro superaron con claridad los `15.0` m/s² (picos leves entre 15.0–20.0 m/s², moderados entre 20.0–35.0 m/s² y fuertes superiores a 35.0 m/s²).
- **Resultado de la prueba:** El umbral de `15.0` m/s² filtra al 100% el ruido estático del sensor y las vibraciones causadas por la caminata o transporte manual, reaccionando únicamente ante choques mecánicos significativos.

---

## 2. Tiempo de reposo entre impactos (`reposo`)

- **Valor inicial sugerido por la guía:** `900 ms`
- **Valor que terminamos usando:** `900 ms`
- **Justificación:** 
  - Cuando un celular sufre un impacto físico (por ejemplo, cae o choca contra una superficie dura), la energía cinética genera una serie de rebotes mecánicos y oscilaciones secundarias que duran entre `200` y `700 ms`.
  - Un tiempo de reposo menor (ej. `300 ms`) provocaría que un único choque físico fuera registrado como 3 o 4 eventos consecutivos no deseados.
  - Al fijar la constante `reposo` en `900 ms`, se garantiza que toda la disipación de energía del impacto quede contenida dentro de una misma ventana de silencio, evitando duplicaciones de lectura en el sensor.

---

## 3. Comportamiento en equipo de gama baja

- **Equipos probados:** 
  1. Celular gama media-baja Android (Motorola Moto G series / Samsung A series).
  2. Dispositivo secundario físico con versión de Android distinta.
- **Observaciones:**
  - **Sensibilidad del acelerómetro:** Los sensores en equipos de gama baja presentan mayor desviación de ruido inicial (hasta 1.2 m/s²), pero el umbral de `15.0` m/s² es lo suficientemente amplio para absorber dicha variación sin falsos positivos.
  - **GPS y localización:** En recintos cerrados o bajo estructuras metálicas del laboratorio, la fijación GPS tarda entre 3 y 8 segundos.

---

## 4. Manejo de ausencia de GPS

- **Estrategia:** Si la consulta de ubicación en `_obtenerPosicion()` no retorna respuesta en `4 segundos` (timeout) o si los servicios de localización están desactivados / sin señal, la captura del evento **NO se bloquea ni se descarta**.
- **Comportamiento comprobado:** El evento se persiste en la base de datos local SQLite con `latitud: null`, `longitud: null` y `precision_m: null`, priorizando el registro de la magnitud sísmica y la hora exacta del suceso.
- **Resultado de la prueba:** Al colocar el celular en Modo Avión y desactivar el GPS, el impacto se capturó inmediatamente en la cola local SQLite sin congelar la interfaz de usuario.

---

## 5. Idempotencia y Prevención de Duplicados

- **Mecanismo:** Antes de enviar el evento a la red, la app genera un UUID único local (`clave_cliente`). La base de datos relacional (PostgreSQL) impone una restricción de clave única compuesta:
  `UniqueConstraint("dispositivo_id", "clave_cliente")`
- **Estrategia en Backend:** El endpoint `POST /api/eventos` ejecuta un patrón *get-or-create*. Si una petición con el mismo `clave_cliente` ingresa 2 o más veces debido a reintentos por cortes de conexión, la API retorna el registro guardado previamente sin crear filas duplicadas (código HTTP 200/201).
- **Verificación en Pruebas Automatizadas:** 
  - Validado mediante la suite de pruebas automatizadas `tests/test_api.py` (`test_crear_evento_e_idempotencia`), donde reintentos con la misma `clave_cliente` retornaron exactamente el mismo ID de base de datos sin incrementar el conteo de filas.

---

## 6. Migraciones de Base de Datos

- **Decisión:** Se utilizó `Base.metadata.create_all(bind=engine)` para simplificar el despliegue automático del esquema durante el arranque de la API.
- **Perspectiva a Producción:** En una etapa futura de producción con evolución de esquemas, se incorporará **Alembic** para gestionar migraciones versionadas y cambios en frío sin pérdida de datos.

---

## 7. Estructura de Proyectos Separados

- **Backend:** Ubicado en la carpeta independiente `backend/` con entorno virtual Python, FastAPI, SQLAlchemy (compatible con PostgreSQL y SQLite para pruebas) y suite `pytest`.
- **Frontend:** Ubicado en la carpeta independiente `frontend/` con Flutter SDK, SQLite (`sqflite`), `dio` e `IdentidadDispositivo` para el manejo de UUID persistente del móvil.
