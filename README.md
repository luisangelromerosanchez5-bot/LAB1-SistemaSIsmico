# P1 · Bitácora sísmica CEET

Miniproyecto de la Actividad No. 5 (SENA · ADSO) — Registro y sincronización de eventos de vibración e impacto detectados por el acelerómetro de un celular Android.

## Estructura del Repositorio (Proyectos Independientes)

El proyecto está dividido en dos proyectos principales completamente autónomos:

```
proyecto-p1/
├── backend/     # API REST autónoma en Python + FastAPI + SQLAlchemy + pytest
├── frontend/    # Aplicación móvil autónoma en Flutter + Dart + SQLite + dio
└── docs/        # Documentación de contrato de API y decisiones técnicas (decisiones.md)
```

---

## 1. Backend (`backend/`)

1. **Crear entorno virtual e instalar dependencias:**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
2. **Base de Datos:**
   - Si cuentas con PostgreSQL corriendo localmente, configura `.env` copiando desde `.env.example`:
     `DATABASE_URL=postgresql+psycopg://usuario:clave@localhost:5432/bitacora_sismica`
   - Si no tienes PostgreSQL local, el backend usará automáticamente la base de datos SQLite local (`sqlite:///./bitacora_sismica.db`).
3. **Levantar el servidor:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. **Swagger UI:** `http://localhost:8000/docs`
5. **Ejecutar Pruebas Automatizadas:**
   ```bash
   .\venv\Scripts\python -m pytest tests/test_api.py -v
   ```

---

## 2. Frontend (`frontend/`)

1. **Instalar dependencias:**
   ```bash
   cd frontend
   flutter pub get
   ```
2. **Ejecutar análisis estático:**
   ```bash
   flutter analyze
   ```
3. **Ejecutar la app:**
   - Con celular físico Android conectado por USB (depuración USB activada):
     ```bash
     flutter run
     ```
   - Nota de red: En emulador la app apunta a `http://10.0.2.2:8000`. Si usas un celular físico en la misma red Wi-Fi, ajusta `baseUrl` en `lib/datos/servicios/api_eventos.dart` con la IP de tu PC (ej. `http://192.168.1.50:8000`).

---

## Checklist de Criterios Bloqueantes (100% Verificados)

- [x] **Registro sin conexión:** La app registra el evento localmente en SQLite cuando no hay red y lo sincroniza automáticamente al recuperar conexión.
- [x] **Idempotencia:** La restricción de clave única `(dispositivo_id, clave_cliente)` y el patrón *get-or-create* evitan filas duplicadas al reenviar.
- [x] **Constantes justificadas:** `umbral` (`15.0`) y `reposo` (`900 ms`) están completamente explicados y justificados con datos en `docs/decisiones.md`.
- [x] **Sin fugas de memoria:** La suscripción a `userAccelerometerEventStream` se cancela explícitamente en `detener()` y `dispose()`.
- [x] **Archivos de entorno:** Existe `.env.example` y no se versionan credenciales reales en Git.
