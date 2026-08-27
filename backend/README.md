# Backend · Bitácora Sísmica CEET

API REST construida con **FastAPI** y **SQLAlchemy** para recibir, validar y almacenar eventos de impacto de dispositivos móviles.

## Estructura del Backend

```
backend/
├── app/
│   ├── database.py       # Conexión SQLAlchemy (PostgreSQL / SQLite)
│   ├── main.py           # Punto de entrada de FastAPI
│   ├── models.py         # Modelos de datos (Dispositivo, EventoImpacto)
│   ├── schemas.py        # Esquemas Pydantic de validación
│   └── routers/
│       ├── dispositivos.py # Endpoint POST /api/dispositivos
│       └── eventos.py      # Endpoints de eventos, lotes y resumen
├── tests/
│   └── test_api.py       # Suite de pruebas automatizadas (pytest)
├── .env.example
├── requirements.txt
└── README.md
```

## Requisitos e Instalación

1. Crear entorno virtual de Python:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configurar variables de entorno:
   - Copia `.env.example` a `.env`
   - Si tienes PostgreSQL corriendo: `DATABASE_URL=postgresql+psycopg://usuario:clave@localhost:5432/bitacora_sismica`
   - Si no tienes PostgreSQL localmente, el sistema usará automáticamente SQLite local (`sqlite:///./bitacora_sismica.db`).

## Ejecución del Servidor

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Swagger UI disponible en: `http://localhost:8000/docs`

## Ejecución de Pruebas Automatizadas

```bash
.\venv\Scripts\python -m pytest tests/test_api.py -v
```
