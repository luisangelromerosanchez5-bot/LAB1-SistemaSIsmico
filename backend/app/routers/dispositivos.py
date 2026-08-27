import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/dispositivos", tags=["dispositivos"])


@router.post("", response_model=schemas.DispositivoSalida, status_code=201)
def registrar_dispositivo(datos: schemas.DispositivoCrear, db: Session = Depends(get_db)):
    existente = (
        db.query(models.Dispositivo)
        .filter(models.Dispositivo.identificador == datos.identificador)
        .first()
    )
    if existente:
        return existente

    try:
        dev_id = UUID(datos.identificador)
    except (ValueError, TypeError, AttributeError):
        dev_id = uuid.uuid4()

    dispositivo = models.Dispositivo(
        id=dev_id,
        identificador=datos.identificador,
        modelo=datos.modelo,
    )
    db.add(dispositivo)
    db.commit()
    db.refresh(dispositivo)
    return dispositivo
