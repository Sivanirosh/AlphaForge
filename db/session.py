"""SQLAlchemy engine, session factory, and FastAPI dependency."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base

_engine: Engine | None = None
_session_factory: sessionmaker | None = None


def get_engine() -> Engine:
    """Return the global engine, creating it lazily from config."""
    global _engine
    if _engine is None:
        from config import settings

        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_session_factory() -> sessionmaker:
    """Return the global session factory, creating it lazily."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(), autocommit=False, autoflush=False
        )
    return _session_factory


def SessionLocal() -> Session:  # noqa: N802
    """Create a new session from the global factory."""
    return get_session_factory()()


def init_db() -> None:
    """Create all tables defined in the ORM if they don't exist."""
    Base.metadata.create_all(bind=get_engine())


def get_db() -> Generator[Session, Any, None]:
    """Yield a DB session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
