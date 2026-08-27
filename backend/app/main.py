from fastapi import FastAPI

from . import models
from .database import Base, engine
from .routers import dispositivos, eventos

# En un proyecto de evaluación con migraciones versionadas usarías Alembic;
# create_all() es suficiente para el alcance de P1 y para arrancar rápido.
# Documenta esta decisión en docs/decisiones.md.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bitácora sísmica CEET · P1",
    description="API del miniproyecto P1 del banco de sensores en Flutter (SENA).",
    version="0.1.0",
)

app.include_router(dispositivos.router)
app.include_router(eventos.router)


@app.get("/")
def salud():
    return {"estado": "ok", "servicio": "bitacora-sismica-api"}
