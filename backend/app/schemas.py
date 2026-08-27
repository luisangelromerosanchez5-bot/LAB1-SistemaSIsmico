"""
Esquemas Pydantic: validan lo que entra por la API y dan forma a lo que sale.
Equivalen a la validación manual que la guía hace en Node.js/Express.
"""
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DispositivoCrear(BaseModel):
    identificador: str
    modelo: Optional[str] = None


class DispositivoSalida(BaseModel):
    id: UUID
    identificador: str
    modelo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EventoCrear(BaseModel):
    dispositivo_id: UUID
    clave_cliente: str  # UUID generado en el cliente para idempotencia
    magnitud: float = Field(ge=0)
    severidad: Literal["leve", "moderado", "fuerte"]
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    precision_m: Optional[float] = None
    ocurrido_en: datetime

    @field_validator("dispositivo_id", mode="before")
    @classmethod
    def validar_dispositivo_id(cls, v):
        import uuid as _uuid
        if isinstance(v, UUID):
            return v
        try:
            return UUID(str(v))
        except (ValueError, TypeError):
            return _uuid.uuid5(_uuid.NAMESPACE_DNS, str(v))


class EventoSalida(BaseModel):
    id: UUID
    dispositivo_id: UUID
    magnitud: float
    severidad: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    precision_m: Optional[float] = None
    ocurrido_en: datetime
    recibido_en: datetime
    clave_cliente: str

    model_config = ConfigDict(from_attributes=True)


class ResumenSeveridad(BaseModel):
    severidad: str
    dia: datetime
    total: int
