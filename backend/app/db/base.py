"""
AirWatch — SQLAlchemy Declarative Base
All models must import and use this Base so Alembic can discover them.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all SQLAlchemy models."""
    pass
