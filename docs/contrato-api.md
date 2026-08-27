# Contrato de la API · P1 Bitácora sísmica CEET

Backend: FastAPI + PostgreSQL (SQLAlchemy). Base URL local: `http://localhost:8000`.

| Método | Ruta | Descripción | Respuesta |
|---|---|---|---|
| POST | `/api/dispositivos` | Registra el equipo y devuelve su UUID | 201 · `{ id, identificador, modelo }` |
| POST | `/api/eventos` | Crea un evento. Idempotente por `clave_cliente` | 200/201 · evento |
| POST | `/api/eventos/lote` | Sube la cola pendiente en un solo envío | 200 · resultado por ítem |
| GET | `/api/eventos?desde=&hasta=&severidad=&pagina=&tamano_pagina=` | Consulta paginada del histórico | 200 · `{ datos, total }` |
| GET | `/api/eventos/resumen` | Conteo por severidad y por día | 200 · arreglo agregado |

## Ejemplo — crear evento

```json
POST /api/eventos
{
  "dispositivo_id": "3a7e...-uuid",
  "clave_cliente": "b1f0...-uuid-generado-en-el-celular",
  "magnitud": 22.4,
  "severidad": "moderado",
  "latitud": 4.678,
  "longitud": -74.055,
  "precision_m": 8.2,
  "ocurrido_en": "2026-08-26T15:04:00Z"
}
```

Respuesta 200/201:
```json
{
  "id": "c9de...-uuid-generado-por-el-servidor",
  "dispositivo_id": "3a7e...-uuid",
  "magnitud": 22.4,
  "severidad": "moderado",
  "latitud": 4.678,
  "longitud": -74.055,
  "precision_m": 8.2,
  "ocurrido_en": "2026-08-26T15:04:00Z",
  "recibido_en": "2026-08-26T15:04:03Z",
  "clave_cliente": "b1f0...-uuid-generado-en-el-celular"
}
```

Reenviar la misma petición con el mismo `clave_cliente` devuelve el mismo registro, sin crear un duplicado.
