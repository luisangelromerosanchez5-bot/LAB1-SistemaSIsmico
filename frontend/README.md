# Frontend · Bitácora Sísmica CEET

Aplicación móvil desarrollada en **Flutter + Dart** para la detección, registro local y sincronización de eventos de impacto del acelerómetro.

## Arquitectura del Proyecto

```
frontend/
├── lib/
│   ├── core/                  # Errores, conectividad, permisos
│   ├── datos/
│   │   ├── local/             # Cola sin conexión (SQLite `cola_local.dart`)
│   │   └── servicios/         # `vigia_impactos.dart`, `api_eventos.dart`, `identidad_dispositivo.dart`
│   ├── dominio/
│   │   └── entidades/         # Modelo de datos `evento_impacto.dart`
│   └── presentacion/
│       └── paginas/           # `pagina_bitacora.dart` (Interfaz principal)
├── pubspec.yaml
└── README.md
```

## Requisitos Funcionales Implementados

- **RF-01 (Detección sin gravedad):** Lectura continua de `userAccelerometerEventStream` descartando la aceleración de la gravedad.
- **RF-02 (Geolocalización):** Captura de latitud, longitud y precisión con `Geolocator`. Tolerante a fallos/ausencia de GPS (timeout 4s).
- **RF-03 (Confirmación Háptica):** Vibración diferenciada (`HapticFeedback.lightImpact()` para leve/moderado y `heavyImpact()` para fuerte).
- **RF-04 (Almacenamiento Local):** Persistencia en SQLite antes de intentar cualquier envío.
- **RF-05 (Sincronización en Segundo Plano):** Envío automático cuando hay conectividad disponible.
- **RF-06 (Histórico y Estado):** Visualización de eventos ordenados cronológicamente con indicación visual de sincronización.

## Requisitos de Ejecución

1. Tener Flutter SDK 3.x instalado.
2. Instalar dependencias:
   ```bash
   flutter pub get
   ```
3. Configurar la URL base de la API en `lib/datos/servicios/api_eventos.dart`:
   - **Emulador Android:** `http://10.0.2.2:8000`
   - **Celular Físico USB (Misma Wi-Fi):** `http://<IP-DE-TU-PC>:8000` (Ej. `http://192.168.1.50:8000`)
4. Ejecutar la aplicación:
   ```bash
   flutter run
   ```
