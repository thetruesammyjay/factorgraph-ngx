from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings


def sqlalchemy_database_url(database_url: str) -> str:
    """Use the psycopg 3 SQLAlchemy dialect for standard PostgreSQL URLs."""
    if database_url.startswith("postgres://"):
        return "postgresql+psycopg://" + database_url.removeprefix("postgres://")
    if database_url.startswith("postgresql://"):
        return "postgresql+psycopg://" + database_url.removeprefix("postgresql://")
    return database_url


engine = (
    create_engine(sqlalchemy_database_url(settings.database_url), pool_pre_ping=True)
    if settings.database_url
    else None
)
SessionLocal = sessionmaker(bind=engine) if engine else None

def get_session() -> Generator[Session, None, None]:
    if SessionLocal is None: raise RuntimeError("DATABASE_URL is not configured")
    with SessionLocal() as session: yield session
