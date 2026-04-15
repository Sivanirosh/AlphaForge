"""FastAPI dependency injection providers."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlalchemy.orm import Session

from db.session import SessionLocal


def get_db() -> Generator[Session, Any, None]:
    """Yield a database session scoped to a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
