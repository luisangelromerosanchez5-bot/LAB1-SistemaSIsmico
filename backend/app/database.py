"""
Configuración de conexión a base de datos con SQLAlchemy.

Soporta PostgreSQL (producción/sustentación) y SQLite (desarrollo local / pruebas).
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Si no hay DATABASE_URL en .env, se usa SQLite local para facilitar la ejecución directa
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./bitacora_sismica.db",
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True if not DATABASE_URL.startswith("sqlite") else False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión y la cierra siempre al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
