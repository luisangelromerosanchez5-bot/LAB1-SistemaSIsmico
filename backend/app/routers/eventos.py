"""
Endpoints de eventos de impacto.

El punto clave de P1: crear un evento es IDEMPOTENTE. Si el celular
reintenta el envío (por ejemplo tras un corte de red), el mismo
clave_cliente no debe generar un segundo registro. Aquí se resuelve
con un "get-or-create" sobre la restricción única
(dispositivo_id, clave_cliente) — el equivalente en SQLAlchemy
al upsert de Prisma que usa la guía original.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/eventos", tags=["eventos"])


def _crear_o_recuperar_evento(evento: schemas.EventoCrear, db: Session) -> models.EventoImpacto:
    # Validación de contrato antes de tocar la base de datos.
    if evento.ocurrido_en > datetime.now(timezone.utc) + timedelta(minutes=1):
        raise HTTPException(status_code=422, detail="Marca de tiempo en el futuro")

    existente = (
        db.query(models.EventoImpacto)
        .filter(
            models.EventoImpacto.dispositivo_id == evento.dispositivo_id,
            models.EventoImpacto.clave_cliente == evento.clave_cliente,
        )
        .first()
    )
    if existente:
        # Reintento: devolvemos el mismo registro, no creamos uno nuevo.
        return existente

    nuevo = models.EventoImpacto(**evento.model_dump())
    db.add(nuevo)
    try:
        db.commit()
    except IntegrityError:
        # Carrera entre dos reintentos casi simultáneos: alguien más
        # ya insertó el mismo clave_cliente entre el SELECT y el INSERT.
        db.rollback()
        existente = (
            db.query(models.EventoImpacto)
            .filter(
                models.EventoImpacto.dispositivo_id == evento.dispositivo_id,
                models.EventoImpacto.clave_cliente == evento.clave_cliente,
            )
            .first()
        )
        if existente:
            return existente
        raise
    db.refresh(nuevo)
    return nuevo


@router.post("", response_model=schemas.EventoSalida)
def crear_evento(evento: schemas.EventoCrear, db: Session = Depends(get_db)):
    resultado = _crear_o_recuperar_evento(evento, db)
    return resultado


@router.post("/lote")
def crear_lote(eventos: List[schemas.EventoCrear], db: Session = Depends(get_db)):
    """
    Sube la cola pendiente en un solo envío (RF-05 de P1).
    Responde con un resultado por ítem, al estilo 207 Multi-Status,
    para que la app sepa cuáles quedaron aplicados y cuáles fallaron.
    """
    resultados = []
    for evento in eventos:
        try:
            creado = _crear_o_recuperar_evento(evento, db)
            resultados.append({"clave_cliente": evento.clave_cliente, "estado": "ok", "id": str(creado.id)})
        except HTTPException as exc:
            resultados.append(
                {"clave_cliente": evento.clave_cliente, "estado": "error", "detalle": exc.detail}
            )
    return {"resultados": resultados}


@router.get("", response_model=dict)
def listar_eventos(
    desde: Optional[datetime] = Query(default=None),
    hasta: Optional[datetime] = Query(default=None),
    severidad: Optional[str] = Query(default=None),
    pagina: int = Query(default=1, ge=1),
    tamano_pagina: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    consulta = db.query(models.EventoImpacto)
    if desde:
        consulta = consulta.filter(models.EventoImpacto.ocurrido_en >= desde)
    if hasta:
        consulta = consulta.filter(models.EventoImpacto.ocurrido_en <= hasta)
    if severidad:
        consulta = consulta.filter(models.EventoImpacto.severidad == severidad)

    total = consulta.count()
    datos = (
        consulta.order_by(models.EventoImpacto.ocurrido_en.desc())
        .offset((pagina - 1) * tamano_pagina)
        .limit(tamano_pagina)
        .all()
    )
    return {
        "datos": [schemas.EventoSalida.model_validate(e).model_dump() for e in datos],
        "total": total,
    }


@router.get("/resumen")
def resumen(db: Session = Depends(get_db)):
    """Conteo por severidad y por día (RF-06 ampliado: soporta el panel de extensión)."""
    dialecto = db.bind.dialect.name if db.bind else ""
    if dialecto == "sqlite":
        col_dia = func.date(models.EventoImpacto.ocurrido_en).label("dia")
    else:
        col_dia = func.date_trunc("day", models.EventoImpacto.ocurrido_en).label("dia")

    filas = (
        db.query(
            models.EventoImpacto.severidad,
            col_dia,
            func.count().label("total"),
        )
        .group_by(models.EventoImpacto.severidad, col_dia)
        .order_by(col_dia.desc())
        .all()
    )
    return [{"severidad": f.severidad, "dia": f.dia, "total": f.total} for f in filas]
