"""
Alembic environment configuration for AirWatch.

This env.py:
  - Reads DATABASE_URL from app.core.config (which loads from .env)
  - Imports all models via app.models so Alembic can auto-detect schema changes
  - Supports both offline (SQL script) and online (direct DB) migrations

Note: We create the engine directly from settings rather than using
config.set_main_option("sqlalchemy.url", ...) to avoid configparser
percent-interpolation errors when the URL contains encoded characters like %40.
"""

from __future__ import annotations

import sys
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

# ---------------------------------------------------------------------------
# Make sure the backend/ directory is on sys.path so "app.*" imports resolve
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Import application settings and declarative base
# ---------------------------------------------------------------------------
from app.core.config import settings          # noqa: E402
from app.db.base import Base                  # noqa: E402

# Import all models so their tables are registered on Base.metadata.
import app.models  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Alembic Config object (wraps alembic.ini)
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use our application metadata for autogenerate support.
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline migration (generates SQL script without connecting to DB)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in offline mode (emits SQL to stdout)."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (connects to DB and applies migrations directly)
# ---------------------------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in online mode (applies to live database)."""
    # Create engine directly from settings — avoids configparser % interpolation.
    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()