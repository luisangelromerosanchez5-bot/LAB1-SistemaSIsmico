"""
Modelo de datos de P1 · Bitácora sísmica CEET.

Traducción a SQLAlchemy del modelo de datos que trae la guía
(originalmente en Prisma/Node.js). Los nombres de tabla y columna
se mantienen en español, igual que en el documento de la actividad.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    UUID,
)
from sqlalchemy.orm import relationship

from .database import Base


class Dispositivo(Base):
    __tablename__ = "dispositivo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identificador = Column(String, unique=True, nullable=False)  # id anónimo del equipo
    modelo = Column(String, nullable=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    eventos = relationship("EventoImpacto", back_populates="dispositivo")


class EventoImpacto(Base):
    __tablename__ = "evento_impacto"
    __table_args__ = (
        # Idempotencia: el mismo dispositivo no puede repetir la misma clave_cliente.
        UniqueConstraint("dispositivo_id", "clave_cliente", name="uq_dispositivo_clave_cliente"),
        CheckConstraint("magnitud >= 0", name="ck_magnitud_no_negativa"),
        CheckConstraint(
            "severidad IN ('leve','moderado','fuerte')", name="ck_severidad_valida"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dispositivo_id = Column(UUID(as_uuid=True), ForeignKey("dispositivo.id"), nullable=False)
    magnitud = Column(Numeric(6, 2), nullable=False)
    severidad = Column(String, nullable=False)
    latitud = Column(Numeric, nullable=True)
    longitud = Column(Numeric, nullable=True)
    precision_m = Column(Numeric, nullable=True)
    ocurrido_en = Column(DateTime(timezone=True), nullable=False)  # hora del evento en el equipo
    recibido_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    clave_cliente = Column(String, nullable=False)  # UUID generado en el cliente

    dispositivo = relationship("Dispositivo", back_populates="eventos")
