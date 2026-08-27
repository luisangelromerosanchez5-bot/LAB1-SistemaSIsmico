from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import Base, engine
from .routers import dispositivos, eventos

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bitácora sísmica CEET · P1",
    description="API del miniproyecto P1 del banco de sensores en Flutter (SENA).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dispositivos.router)
app.include_router(eventos.router)


@app.get("/")
def salud():
    return {"estado": "ok", "servicio": "bitacora-sismica-api"}
