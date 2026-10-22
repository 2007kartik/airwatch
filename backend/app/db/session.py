"""
AirWatch — Database Session Management
Provides a synchronous SQLAlchemy engine and session factory.
Phase 2: synchronous sessions used throughout (async can be added later if needed).
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# pool_pre_ping=True ensures stale connections are detected and reconnected
# automatically, which is important for long-running services.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=(settings.app_env == "development"),  # Log SQL in dev mode
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# FastAPI Dependency
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session and guarantee it is closed afterward.
    Use as a FastAPI dependency: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """
    Attempt a lightweight query to verify database connectivity.
    Returns True if successful, False otherwise.
    Used by the /api/health endpoint.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
