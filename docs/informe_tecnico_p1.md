# INFORME TÉCNICO DE IMPLEMENTACIÓN · P1 BITÁCORA SÍSMICA CEET
**Actividad No. 5 · SENA · Tecnología en Análisis y Desarrollo de Software (ADSO)**  
**Stack Tecnológico:** Flutter 3.x + Dart 3.x | FastAPI + PostgreSQL / SQLite  
**Fecha de Entrega:** Semana 6  

---

## 1. Resumen Ejecutivo y Alcance del Sistema

El proyecto **Bitácora Sísmica CEET** surge de la necesidad del área de seguridad e inventarios del centro para auditar el transporte de equipos de laboratorio de alta precisión entre ambientes de formación. La solución móvil captura impactos mecánicos y vibraciones anómalas utilizando los sensores integrados en teléfonos inteligentes Android, garantizando la persistencia local de los datos ante pérdidas de conectividad y su posterior sincronización idempotente hacia un servidor centralizado.

---

## 2. Decisiones de Calibración de Hardware y Filtros de Señal

### 2.1. Detección de Impactos sin Gravedad (RF-01)
El motor de monitoreo (`VigiaImpactos`) se suscribe a la transmisión `userAccelerometerEventStream` provista por el paquete `sensors_plus`. Esta transmisión aplica un filtro de paso alto en hardware/firmware que descuenta la aceleración gravitacional constante ($\approx 9.81 \text{ m/s}^2$).

$$M = \sqrt{a_x^2 + a_y^2 + a_z^2}$$

- **Calibración del Umbral ($15.0 \text{ m/s}^2$):** En estado de reposo sobre mesa, el sensor registra un ruido de fondo de entre $0.12$ y $0.85 \text{ m/s}^2$. Durante el traslape en caminata continua, la oscilación normal se mantiene por debajo de $6.8 \text{ m/s}^2$. Se fijó un umbral de $15.0 \text{ m/s}^2$ para discriminar ruidos normales y responder exclusivamente a colisiones o caídas mecánicas.
- **Ventana de Reposo entre Impactos ($900 \text{ ms}$):** Un choque físico transmite ondas elásticas y rebotes mecánicos secundarios durante $200$–$700 \text{ ms}$. La constante de reposo $900 \text{ ms}$ actúa como un filtro temporal *de-bounce*, previniendo la duplicación de lecturas ante un único impacto.

### 2.2. Manejo y Tolerancia a la Ausencia de GPS (RF-02)
La geolocalización utiliza la librería `geolocator`. Para evitar que la falta de cobertura o el retardo del receptor GPS bloquee la captura crítica de un evento sísmico, la función `_obtenerPosicion()` implementa un tiempo límite de $4 \text{ segundos}$. Si el GPS no responde o está desactivado, el evento se almacena con `latitud: null`, `longitud: null` y `precision_m: null`, preservando intactos la magnitud y el sello de tiempo (`ocurrido_en`).

---

## 3. Arquitectura de Persistencia, Cola Offline e Idempotencia

### 3.1. Persistencia Local y Cola de Espera (RF-04 / RF-05)
La app móvil adopta el patrón *Offline-First*. Todo evento capturado se escribe inmediatamente en la base de datos relacional SQLite del celular (`cola_local.dart`) con la bandera `sincronizado = 0`. El servicio de red (`ApiEventos`) intenta enviar la cola pendiente en segundo plano; si la petición falla por falta de señal o caída del servidor, el evento permanece seguro en SQLite para ser reintentado en la siguiente reconexión.

### 3.2. Idempotencia y Prevención de Duplicados en el Servidor
Para evitar filas duplicadas al reintentar envíos tras cortes de red intermitentes, el cliente genera un identificador único global `clave_cliente` (UUID v4) previo al almacenamiento local. El backend FastAPI en PostgreSQL impone una restricción única compuesta:

$$\text{UNIQUE}(\text{dispositivo\_id}, \text{clave\_cliente})$$

El router de FastAPI implementa una lógica *get-or-create*: al recibir un evento repetido con la misma `clave_cliente`, recupera y retorna el registro preexistente (código HTTP 200/201), garantizando la exactitud del histórico.

---

## 4. Limitaciones Declaradas y Trabajos Futuros

1. **Variabilidad de Sensores entre Fabricantes:** Dispositivos de gama baja pueden presentar ligeras variaciones en la tasa de muestreo del acelerómetro; sin embargo, el umbral de $15.0 \text{ m/s}^2$ absorbe las desviaciones.
2. **Consumo de Batería:** El muestreo continuo `SensorInterval.gameInterval` genera consumo de energía; se implementó el método `detener()` para cancelar explícitamente la suscripción al pausar el monitoreo o salir de la pantalla (`dispose()`).
