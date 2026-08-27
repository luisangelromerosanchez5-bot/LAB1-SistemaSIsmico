import os
import uuid
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Usar SQLite con StaticPool para compartir la base de datos en memoria entre hilos/conexiones
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.main import app
from app.database import Base, get_db

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_salud():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "ok"
    assert data["servicio"] == "bitacora-sismica-api"


def test_registrar_dispositivo():
    payload = {
        "identificador": "EQUIPO-LAB-01",
        "modelo": "Motorola Moto G54"
    }
    response = client.post("/api/dispositivos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["identificador"] == "EQUIPO-LAB-01"
    device_id = data["id"]

    # Reintento con el mismo identificador debe retornar el mismo registro
    response_retry = client.post("/api/dispositivos", json=payload)
    assert response_retry.status_code == 201
    assert response_retry.json()["id"] == device_id


def test_crear_evento_e_idempotencia():
    # 1. Registrar dispositivo
    dev_resp = client.post("/api/dispositivos", json={"identificador": "EQUIPO-LAB-02"})
    device_id = dev_resp.json()["id"]

    clave_cliente = str(uuid.uuid4())
    ahora_iso = datetime.now(timezone.utc).isoformat()

    evento_payload = {
        "dispositivo_id": device_id,
        "clave_cliente": clave_cliente,
        "magnitud": 18.5,
        "severidad": "moderado",
        "latitud": 4.6097,
        "longitud": -74.0817,
        "precision_m": 5.0,
        "ocurrido_en": ahora_iso
    }

    # Primer envío
    resp1 = client.post("/api/eventos", json=evento_payload)
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["clave_cliente"] == clave_cliente
    evento_id = data1["id"]

    # Reintento del mismo evento con la misma clave_cliente (Idempotencia)
    resp2 = client.post("/api/eventos", json=evento_payload)
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["id"] == evento_id
    assert data2["clave_cliente"] == clave_cliente


def test_crear_lote():
    dev_resp = client.post("/api/dispositivos", json={"identificador": "EQUIPO-LAB-03"})
    device_id = dev_resp.json()["id"]

    e1 = {
        "dispositivo_id": device_id,
        "clave_cliente": str(uuid.uuid4()),
        "magnitud": 12.0,
        "severidad": "leve",
        "ocurrido_en": datetime.now(timezone.utc).isoformat()
    }
    e2 = {
        "dispositivo_id": device_id,
        "clave_cliente": str(uuid.uuid4()),
        "magnitud": 38.0,
        "severidad": "fuerte",
        "ocurrido_en": datetime.now(timezone.utc).isoformat()
    }

    resp = client.post("/api/eventos/lote", json=[e1, e2])
    assert resp.status_code == 200
    resultados = resp.json()["resultados"]
    assert len(resultados) == 2
    assert all(r["estado"] == "ok" for r in resultados)


def test_listar_y_resumen():
    dev_resp = client.post("/api/dispositivos", json={"identificador": "EQUIPO-LAB-04"})
    device_id = dev_resp.json()["id"]

    client.post("/api/eventos", json={
        "dispositivo_id": device_id,
        "clave_cliente": str(uuid.uuid4()),
        "magnitud": 25.0,
        "severidad": "moderado",
        "ocurrido_en": datetime.now(timezone.utc).isoformat()
    })

    # Listar
    list_resp = client.get("/api/eventos")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    # Resumen
    res_resp = client.get("/api/eventos/resumen")
    assert res_resp.status_code == 200
    assert isinstance(res_resp.json(), list)
