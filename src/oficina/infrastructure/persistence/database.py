from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from oficina.config import get_settings

class Base(DeclarativeBase):
    pass

def build_engine(url: str | None = None):
    database_url = url or get_settings().database_url
    kwargs = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=kwargs, pool_pre_ping=True)

engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def create_schema(target_engine=None):
    from oficina.infrastructure.persistence import models  # noqa: F401
    Base.metadata.create_all(bind=target_engine or engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
